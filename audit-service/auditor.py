"""Read-only homepage checks. DNS is validated and pinned for each redirect."""
import datetime,html,re,http.client,ipaddress,socket,ssl,time
from html.parser import HTMLParser
from urllib.parse import urlsplit,urlunsplit,urljoin
MAX_BYTES=1500000
class AuditError(ValueError):pass
def validate_url(value):
 if len(value)>2048:raise AuditError('The website address is too long.')
 p=urlsplit(value.strip() if '://' in value else 'https://'+value.strip())
 try:port=p.port
 except ValueError:raise AuditError('Invalid website port.')
 if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or port not in (None,80 if p.scheme=='http' else 443):raise AuditError('Enter a public HTTP or HTTPS website, using its standard port.')
 host=p.hostname.encode('idna').decode()
 if '.' not in host or any(c.isspace() for c in value):raise AuditError('Enter a public website hostname.')
 return urlunsplit((p.scheme,host,p.path or '/',p.query,''))
def public_addresses(host,port):
 try:addresses=list(dict.fromkeys(r[4][0] for r in socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)))
 except socket.gaierror:raise AuditError('We could not find this website. Check its address.')
 if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):raise AuditError('Only publicly accessible websites can be audited.')
 return addresses
class PinnedHTTPS(http.client.HTTPSConnection):
 def __init__(self,host,ip,timeout):super().__init__(host,timeout=timeout,context=ssl.create_default_context());self.ip=ip
 def connect(self):
  self.sock=socket.create_connection((self.ip,443),timeout=self.timeout)
  self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host)
class PinnedHTTP(http.client.HTTPConnection):
 def __init__(self,host,ip,timeout):super().__init__(host,timeout=timeout);self.ip=ip
 def connect(self):self.sock=socket.create_connection((self.ip,80),timeout=self.timeout)
def fetch_public(value, content_type="html"):
 url=validate_url(value);started=time.monotonic()
 for _ in range(5):
  if time.monotonic()-started>22:raise AuditError('The website took too long to respond. Please try later.')
  p=urlsplit(url);ip=public_addresses(p.hostname,443 if p.scheme=='https' else 80)[0]
  connection=(PinnedHTTPS if p.scheme=='https' else PinnedHTTP)(p.hostname,ip,8)
  try:
   connection.request('GET',urlunsplit(('','',p.path or '/',p.query,'')),headers={'User-Agent':'BobbyagencyAudit/1.0 (public homepage review)','Accept':'application/json' if content_type=='json' else 'text/html','Accept-Encoding':'identity'})
   response=connection.getresponse()
   if response.status in (301,302,303,307,308):
    location=response.getheader('Location')
    if not location:raise AuditError('The website returned an incomplete redirect.')
    url=validate_url(urljoin(url,location));continue
   if response.status!=200:raise AuditError('The website returned HTTP '+str(response.status)+'. It may restrict automated checks.')
   returned_type=(response.getheader('Content-Type') or '').lower()
   if content_type=='json' and 'json' not in returned_type:raise AuditError('The public catalogue endpoint did not return JSON.')
   if content_type=='html' and 'text/html' not in returned_type:raise AuditError('This address does not return an HTML webpage.')
   chunks=[];total=0
   while True:
    if time.monotonic()-started>22:raise AuditError('The website took too long to respond.')
    chunk=response.read1(min(65536,MAX_BYTES-total+1))
    if not chunk:break
    chunks.append(chunk);total+=len(chunk)
    if total>MAX_BYTES:raise AuditError('This page is too large for this basic audit. Try its homepage.')
   content=b''.join(chunks)
   charset=response.headers.get_content_charset() or 'utf-8'
   try:text=content.decode(charset,errors='replace')
   except LookupError:text=content.decode('utf-8',errors='replace')
   return url,text
  except (OSError,http.client.HTTPException):raise AuditError('The website could not be reached securely. Check its address or try later.')
  finally:connection.close()
 raise AuditError('The website redirected too many times.')
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.title=[];self.in_title=False;self.title_seen=False;self.svg_depth=0;self.description='';self.viewport='';self.h1=0;self.images=0;self.missing_alt=0;self.canonical='';self.ignored=0;self.has_scripts=False;self.app_root=False;self.visible=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('template','noscript','script','style'):
   if tag=='script' and not self.ignored:self.has_scripts=True
   self.ignored+=1;return
  if self.ignored:return
  if tag=='svg':self.svg_depth+=1
  if self.svg_depth:return
  if (a.get('id') or '').lower() in ('app','root','__next','__nuxt'):self.app_root=True
  if tag=='title' and not self.title_seen:self.in_title=True;self.title_seen=True
  if tag=='meta':
   if (a.get('name') or '').lower()=='description':self.description=(a.get('content') or '').strip()
   if (a.get('name') or '').lower()=='viewport':self.viewport=a.get('content') or ''
  if tag=='h1':self.h1+=1
  if tag=='img':self.images+=1;self.missing_alt+=int('alt' not in a)
  if tag=='link' and 'canonical' in (a.get('rel') or '').lower().split():self.canonical=(a.get('href') or '').strip()
 def handle_endtag(self,tag):
  if tag in ('template','noscript','script','style'):
   self.ignored=max(0,self.ignored-1);return
  if self.ignored:return
  if tag=='svg':self.svg_depth=max(0,self.svg_depth-1);return
  if not self.svg_depth and tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.ignored or self.svg_depth:return
  if self.in_title:self.title.append(data)
  else:self.visible.append(data)
def analyse(url,text):
 p=Page();p.feed(text);title=''.join(p.title).strip();checks=[]
 if any(t in title.lower() for t in ['just a moment','verify you are human','attention required']) and any(m in text.lower() for m in ['challenge-platform','cf-chl-','captcha']):
  raise AuditError('The website returned a bot-verification page. Its actual content could not be assessed; no website score or report has been generated.')
 client_shell=p.app_root and p.has_scripts and len(' '.join(p.visible).strip())<200
 def add(name,status,evidence,fix=''):
  checks.append({'name':name,'status':status,'evidence':evidence,'recommendation':fix,'source':'server-returned HTML; JavaScript not executed'})
 def finding(name,found,evidence,fix,uncertain=True):
  status='pass' if found else ('not_assessed' if client_shell and uncertain else 'review')
  add(name,status,evidence,fix if not found else '')
 add('HTTPS','pass' if urlsplit(url).scheme=='https' else 'needs_attention','Final fetched page uses '+urlsplit(url).scheme.upper()+'. This does not establish the security of the whole site.','' if urlsplit(url).scheme=='https' else 'Check whether the site can redirect visitors to a valid HTTPS page.')
 finding('Page title',bool(title),'Title: '+title[:180] if title else 'No non-empty title was found in the returned HTML.','Confirm the title in a rendered browser and search preview before changing it.')
 finding('Meta description',bool(p.description),'Description present ('+str(len(p.description))+' characters).' if p.description else 'No non-empty meta description was found in the returned HTML.','Review the rendered metadata and consider a useful page-specific description. Presence alone does not measure its quality.')
 viewport=bool(re.search(r'(?:^|[,;])\s*width\s*=\s*device-width\s*(?:[,;]|$)',p.viewport,re.I))
 finding('Mobile viewport',viewport,'Viewport metadata: '+p.viewport[:150] if p.viewport else 'No viewport metadata was found in the returned HTML.','Check the rendered page and test its layout on a phone. Metadata alone cannot establish mobile usability.')
 if p.h1==1:add('Primary heading','pass','One H1 element was found in the returned HTML. Heading meaning, visibility and hierarchy were not assessed.')
 else:add('Primary heading','not_assessed' if client_shell and p.h1==0 else 'review',str(p.h1)+' H1 elements found in the returned HTML.','Multiple H1 elements are not automatically an SEO error. Inspect the rendered heading structure before deciding whether a change is needed.' if p.h1>1 else 'Confirm whether JavaScript supplies the heading in the browser before adding one.')
 canonical=urljoin(url,p.canonical) if p.canonical else ''
 valid=bool(canonical and urlsplit(canonical).scheme in ('http','https') and urlsplit(canonical).hostname)
 finding('Canonical link',valid,'Canonical declared: '+p.canonical[:180] if p.canonical else 'No canonical link was found in the returned HTML. A missing canonical is not automatically a fault.','Review duplication and indexing needs before adding or changing a canonical. A declared URL is not proof Google accepts it.')
 if p.images:add('Image alt attributes','pass' if p.missing_alt==0 else 'review',str(p.missing_alt)+' of '+str(p.images)+' image elements are missing an alt attribute. Attribute presence does not establish that the text is useful or that the page is accessible.','Review these images in the rendered page. Informative images need useful alternatives; decorative images can use empty alt text. Alt text quality was not assessed.' if p.missing_alt else '')
 else:add('Image alt attributes','not_assessed','No image elements were found in the returned HTML. JavaScript, CSS backgrounds and picture content may require a rendered browser review.')
 assessed=[c for c in checks if c['status']!='not_assessed'];passed=sum(c['status']=='pass' for c in assessed)
 reviews=sum(c['status'] in ('review','needs_attention') for c in checks)
 return {'schema_version':2,'source':'server_html','url':url,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'title':title[:180],'passed':passed,'assessed':len(assessed),'review_count':reviews,'inconclusive_count':sum(c['status']=='not_assessed' for c in checks),'possible_client_rendering':client_shell,'checks':checks,'limitations':'HTML observations from one public page, not a full-site audit or website quality score. JavaScript was not executed. Speed/Core Web Vitals, visual layout, actual mobile usability, accessibility compliance, security and conversion performance were not measured. Review suggestions need confirmation in a browser; missing optional metadata is not automatically a fault. '+('This page appears to rely on client-side rendering; absent features are inconclusive. ' if client_shell else '')+'Observed markup does not guarantee rankings or sales.'}
def report_text(report,name):
 if report.get('source')=='google_pagespeed':
  from pagespeed import text_report
  return text_report(report,name)
 lines=['Hi '+name+',','','Your Bobbyagency basic website audit is ready.',report['url'],'Checked: '+report['checked_at'],'',str(len(report['checks']))+' HTML observations; '+str(report.get('review_count',0))+' items to review. This is not an overall website score.','']
 for check in report['checks']:
  lines.extend([check['name']+' — '+('observed in HTML' if check['status']=='pass' else check['status'].replace('_',' ')),check['evidence']])
  if check['recommendation']:lines.append('Suggested next step: '+check['recommendation'])
  lines.append('')
 lines.extend([report['limitations'],'','Want help reviewing the findings? Request a written quote: https://dewaynehadden.github.io/Bobbyagency/payment.html#start-project','Contact: dewaynehadden11@gmail.com','You requested this one-time report. You have not been subscribed to marketing emails.'])
 return '\n'.join(lines)
