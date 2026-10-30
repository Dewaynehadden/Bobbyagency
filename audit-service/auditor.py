"""Read-only homepage checks. DNS is validated and pinned for each redirect."""
import datetime,html,http.client,ipaddress,socket,ssl,time
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
def fetch_public(value):
 url=validate_url(value);started=time.monotonic()
 for _ in range(5):
  if time.monotonic()-started>22:raise AuditError('The website took too long to respond. Please try later.')
  p=urlsplit(url);ip=public_addresses(p.hostname,443 if p.scheme=='https' else 80)[0]
  connection=(PinnedHTTPS if p.scheme=='https' else PinnedHTTP)(p.hostname,ip,8)
  try:
   connection.request('GET',urlunsplit(('','',p.path or '/',p.query,'')),headers={'User-Agent':'BobbyagencyAudit/1.0 (public homepage review)','Accept':'text/html','Accept-Encoding':'identity'})
   response=connection.getresponse()
   if response.status in (301,302,303,307,308):
    location=response.getheader('Location')
    if not location:raise AuditError('The website returned an incomplete redirect.')
    url=validate_url(urljoin(url,location));continue
   if response.status!=200:raise AuditError('The website returned HTTP '+str(response.status)+'. It may restrict automated checks.')
   if 'text/html' not in (response.getheader('Content-Type') or '').lower():raise AuditError('This address does not return an HTML webpage.')
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
 def __init__(self):super().__init__();self.title=[];self.in_title=False;self.description='';self.viewport='';self.h1=0;self.images=0;self.missing_alt=0;self.canonical=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='title':self.in_title=True
  if tag=='meta':
   if a.get('name','').lower()=='description':self.description=a.get('content','').strip()
   if a.get('name','').lower()=='viewport':self.viewport=a.get('content','')
  if tag=='h1':self.h1+=1
  if tag=='img':self.images+=1;self.missing_alt+=int('alt' not in a)
  if tag=='link' and 'canonical' in a.get('rel','').lower().split():self.canonical=a.get('href','')
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.in_title:self.title.append(data)
def analyse(url,text):
 p=Page();p.feed(text);title=''.join(p.title).strip();checks=[]
 def check(name,ok,evidence,fix):checks.append({'name':name,'status':'pass' if ok else 'needs_attention','evidence':evidence,'recommendation':fix if not ok else ''})
 check('HTTPS',urlsplit(url).scheme=='https','Final page uses '+urlsplit(url).scheme.upper()+'.','Serve the page over HTTPS with a valid certificate.')
 check('Page title',bool(title),'Title: '+title[:180] if title else 'No non-empty title element was found.','Add a descriptive title for this page.')
 check('Meta description',bool(p.description),'Description present ('+str(len(p.description))+' characters).' if p.description else 'No non-empty meta description was found.','Add a useful, page-specific meta description.')
 check('Mobile viewport','width=device-width' in p.viewport.replace(' ','').lower(),'Viewport: '+p.viewport[:150] if p.viewport else 'No viewport metadata was found.','Add a width=device-width viewport and test on a real mobile device.')
 check('Primary heading',p.h1==1,str(p.h1)+' H1 elements found in the returned HTML.','Review heading structure and give the page a clear primary heading.')
 check('Canonical link',bool(p.canonical),'Canonical: '+p.canonical[:180] if p.canonical else 'No canonical link was found.','Consider a canonical URL where needed to clarify the preferred page address.')
 if p.images:check('Image alt attributes',p.missing_alt==0,str(p.missing_alt)+' of '+str(p.images)+' image elements are missing an alt attribute.','Add meaningful alt text to informative images; use empty alt text for decorative images.')
 else:checks.append({'name':'Image alt attributes','status':'not_assessed','evidence':'No image elements were found in the returned HTML.','recommendation':''})
 assessed=[c for c in checks if c['status']!='not_assessed'];passed=sum(c['status']=='pass' for c in assessed)
 return {'url':url,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'title':title[:180],'passed':passed,'assessed':len(assessed),'checks':checks,'limitations':'This is an automated check of the HTML returned for one public page, not a full-site crawl, Lighthouse score, accessibility certification, security test, or design/conversion review. JavaScript-rendered content may not be included. Empty alt text is allowed for decorative images; image meaning is not assessed. A passed check does not guarantee rankings or sales.'}
def report_text(report,name):
 lines=['Hi '+name+',','','Your Bobbyagency basic website audit is ready.',report['url'],'Checked: '+report['checked_at'],'',str(report['passed'])+' of '+str(report['assessed'])+' basic checks passed.','']
 for check in report['checks']:
  lines.extend([check['name']+' — '+check['status'].replace('_',' '),check['evidence']])
  if check['recommendation']:lines.append('Suggested next step: '+check['recommendation'])
  lines.append('')
 lines.extend([report['limitations'],'','Want help reviewing the findings? Request a written quote: https://dewaynehadden.github.io/Bobbyagency/payment.html#start-project','Contact: dewaynehadden11@gmail.com','You requested this one-time report. You have not been subscribed to marketing emails.'])
 return '\n'.join(lines)
