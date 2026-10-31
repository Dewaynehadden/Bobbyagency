"""Small WSGI audit API. Configure sender secrets on the host, never in GitHub."""
import datetime,json,os,re,smtplib,ssl,threading,time,urllib.request
from urllib.parse import urlsplit
from email.message import EmailMessage
from auditor import AuditError,fetch_public,analyse,report_text
from jobs import start_job,read_job
from store_review import SALES_STATES,CONCERNS
ORIGIN=os.environ.get('AUDIT_ALLOWED_ORIGIN','https://dewaynehadden.github.io')
MAIL_LOCK=threading.Lock();TIMES={};DAILY=[];SLOTS=threading.BoundedSemaphore(2)
EMAIL=re.compile(r'^[^\s@<>\r\n]+@[^\s@<>\r\n]+\.[^\s@<>\r\n]+$')
def send_report(email,name,report):
 if os.environ.get('EMAIL_PROVIDER','smtp')=='google_script':
  url=os.environ.get('GOOGLE_MAIL_URL','');token=os.environ.get('GOOGLE_MAIL_TOKEN','')
  parsed=urlsplit(url)
  if parsed.scheme!='https' or parsed.hostname!='script.google.com' or not parsed.path.startswith('/macros/s/') or len(token)<24:raise RuntimeError('Google mail delivery is not configured.')
  payload=json.dumps({'token':token,'to':email,'subject':'Your Bobbyagency website audit','body':report_text(report,name)}).encode()
  request=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request,timeout=25) as response:result=json.loads(response.read(4096))
   if result.get('ok') is not True:raise RuntimeError('Mail provider rejected the report.')
  except (ValueError,OSError):raise RuntimeError('Mail provider could not be reached.')
  return
 sender=os.environ.get('SMTP_FROM','');user=os.environ.get('SMTP_USER','');password=os.environ.get('SMTP_PASSWORD','');host=os.environ.get('SMTP_HOST','');port=int(os.environ.get('SMTP_PORT','465'))
 if not all((sender,user,password,host)):raise RuntimeError('Email delivery is not configured.')
 message=EmailMessage();message['Subject']='Your Bobbyagency website audit';message['From']=sender;message['To']=email;message['Reply-To']='dewaynehadden11@gmail.com';message.set_content(report_text(report,name))
 if port==465:
  with smtplib.SMTP_SSL(host,port,timeout=20,context=ssl.create_default_context()) as client:client.login(user,password);client.send_message(message)
 else:
  with smtplib.SMTP(host,port,timeout=20) as client:client.starttls(context=ssl.create_default_context());client.login(user,password);client.send_message(message)
def application(env,start):
 origin=env.get('HTTP_ORIGIN','');method=env.get('REQUEST_METHOD','GET');path=env.get('PATH_INFO','/')
 def reply(status,data):
  body=json.dumps(data).encode();headers=[('Content-Type','application/json'),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Vary','Origin')]
  if origin==ORIGIN:headers += [('Access-Control-Allow-Origin',ORIGIN),('Access-Control-Allow-Methods','GET, POST, OPTIONS'),('Access-Control-Allow-Headers','Content-Type')]
  start(str(status)+' '+{200:'OK',202:'Accepted',204:'No Content',400:'Bad Request',403:'Forbidden',404:'Not Found',405:'Method Not Allowed',413:'Content Too Large',429:'Too Many Requests',503:'Service Unavailable',502:'Bad Gateway'}.get(status,'Error'),headers);return [body]
 if path=='/healthz':return reply(200,{'ok':True})
 if path!='/audit' and not path.startswith('/audit/jobs/'):return reply(404,{'error':'Not found.'})
 if origin!=ORIGIN:return reply(403,{'error':'Use the audit form on Bobbyagency.'})
 if method=='OPTIONS':return reply(200,{'ok':True})
 if path.startswith('/audit/jobs/'):
  parts=path.split('/')
  if method!='GET':return reply(405,{'error':'Use GET to read a report.'})
  if len(parts) not in (4,6) or not re.fullmatch(r'[A-Za-z0-9_-]{30,60}',parts[3]):return reply(404,{'error':'Report not found.'})
  strategy=None
  if len(parts)==6:
   if parts[4]!='raw' or parts[5] not in ('mobile','desktop'):return reply(404,{'error':'Report not found.'})
   strategy=parts[5]
  job=read_job(parts[3],strategy)
  return reply(200,job) if job else reply(404,{'error':'The requested measurement was not returned, or this report expired/restarted. Save downloads after testing to preserve them.'})
 if method!='POST':return reply(405,{'error':'Submit the audit form.'})
 try:
  size=int(env.get('CONTENT_LENGTH') or '0')
  if not 0<size<=5000:return reply(413,{'error':'Request too large or empty.'})
  if env.get('CONTENT_TYPE','').split(';')[0]!='application/json':return reply(400,{'error':'JSON required.'})
  data=json.loads(env['wsgi.input'].read(size))
  if not isinstance(data,dict):return reply(400,{'error':'Invalid request.'})
  name=str(data.get('name','')).strip();email=str(data.get('email','')).strip();website=str(data.get('website','')).strip()
  if data.get('company') or data.get('consent') is not True or not 2<=len(name)<=100 or not EMAIL.fullmatch(email) or len(email)>254 or '\r' in name or '\n' in name:return reply(400,{'error':'Enter your name, a valid email address, and consent to this one-time report.'})
  required=['GOOGLE_MAIL_URL','GOOGLE_MAIL_TOKEN'] if os.environ.get('EMAIL_PROVIDER','smtp')=='google_script' else ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD','SMTP_FROM']
  if not all(os.environ.get(k) for k in required):return reply(503,{'error':'Automatic report delivery is not active yet. Please request a personal review.'})
  if data.get('engine')=='pagespeed' and not os.environ.get('PAGESPEED_API_KEY','').strip():return reply(503,{'error':'Google PageSpeed is not configured yet. Add PAGESPEED_API_KEY to the audit service; no measured scores are available.'})
  # Rate limits are per process; free instances reset them on restart.
  key=(env.get('REMOTE_ADDR','unknown'),email.lower());now=time.time()
  with MAIL_LOCK:
   DAILY[:]=[t for t in DAILY if now-t<86400]
   for old in list(TIMES):
    if now-TIMES[old]>3600:del TIMES[old]
   if len(DAILY)>=int(os.environ.get('AUDIT_DAILY_LIMIT','30')) or any((k[0]==key[0] or k[1]==key[1]) and now-v<600 for k,v in TIMES.items()):return reply(429,{'error':'Please wait before requesting another report. If you already requested one, check your inbox and spam folder.'})
   TIMES[key]=now;DAILY.append(now)
  if data.get('engine')=='pagespeed':
   context={'sales_state':data.get('sales_state','unknown'),'sales_concern':data.get('sales_concern','unknown')}
   if context['sales_state'] not in SALES_STATES or context['sales_concern'] not in CONCERNS:return reply(400,{'error':'Choose valid sales-context options.'})
   try:job_id=start_job(website,name,email,send_report,context)
   except AuditError:
    with MAIL_LOCK:
     TIMES.pop(key,None)
     if now in DAILY:DAILY.remove(now)
    raise
   return reply(202,{'job_id':job_id,'status':'queued'})
  if not SLOTS.acquire(blocking=False):return reply(503,{'error':'The audit service is busy. Please try again in a few minutes.'})
  try:
   url,text=fetch_public(website);report=analyse(url,text)
   try:send_report(email,name,report);delivery='submitted'
   except (OSError,smtplib.SMTPException,RuntimeError):delivery='failed'
   return reply(200,{'report':report,'delivery':delivery,'message':'Your email provider accepted the report for sending. Check your inbox or spam folder; delivery is not guaranteed.' if delivery=='submitted' else 'Your results are ready below, but email delivery failed. Save the report or contact Bobbyagency.'})
  finally:SLOTS.release()
 except AuditError as e:return reply(400,{'error':str(e)})
 except (ValueError,TypeError,KeyError):return reply(400,{'error':'Please check your details and website address.'})
 except Exception:return reply(502,{'error':'The audit could not be completed. Please try again later.'})
