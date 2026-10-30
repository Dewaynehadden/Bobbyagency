import io,json,os,sys,unittest
from unittest.mock import patch,MagicMock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import auditor,app
HTML='''<!doctype html><title>Example store</title><meta name="description" content="Shop our products"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="canonical" href="https://example.com/"><h1>Welcome</h1><img src="x.jpg" alt="Product"><img src="decoration.jpg" alt="">'''
class AuditTests(unittest.TestCase):
 def setUp(self):app.TIMES.clear();app.DAILY.clear()
 def call(self,data=None,origin=app.ORIGIN,method='POST',path='/audit'):
  data=data or {'name':'Alex Buyer','email':'buyer@gmail.com','website':'https://example.com','consent':True};raw=json.dumps(data).encode();result={}
  env={'HTTP_ORIGIN':origin,'REQUEST_METHOD':method,'PATH_INFO':path,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),'REMOTE_ADDR':'192.0.2.1','wsgi.input':io.BytesIO(raw)}
  def start(status,headers):result.update(status=int(status.split()[0]),headers=dict(headers))
  result['data']=json.loads(b''.join(app.application(env,start)));return result
 def test_real_observations(self):
  report=auditor.analyse('https://example.com',HTML);self.assertEqual(report['passed'],7);self.assertEqual(report['assessed'],7)
  report=auditor.analyse('http://example.com','<h1>One</h1><h1>Two</h1><img src="p">');self.assertEqual(report['passed'],0);self.assertIn('1 of 1 image elements are missing an alt attribute.',report['checks'][-1]['evidence'])
  report=auditor.analyse('https://example.com','<title>Hello</title>');self.assertEqual(report['checks'][-1]['status'],'not_assessed');self.assertEqual(report['assessed'],6)
 def test_invalid_urls(self):
  for url in ['file:///etc/passwd','ftp://example.com','https://user:pass@example.com','http://example.com:8080','https://example.com/\r\nX:bad']:
   with self.assertRaises(auditor.AuditError):auditor.validate_url(url)
 def test_internal_networks_rejected(self):
  for address in ['127.0.0.1','169.254.169.254','10.0.0.1','192.168.1.5','::1','fc00::1']:
   with patch('socket.getaddrinfo',return_value=[(None,None,None,None,(address,80))]):
    with self.assertRaises(auditor.AuditError):auditor.public_addresses('example.com',80)
 def test_redirects_revalidated(self):
  conn=MagicMock();response=MagicMock();response.status=302;response.getheader.return_value='http://169.254.169.254/';conn.getresponse.return_value=response
  with patch.object(auditor,'public_addresses',side_effect=[['93.184.216.34'],auditor.AuditError('Not public')]) as dns,patch.object(auditor,'PinnedHTTPS',return_value=conn):
   with self.assertRaises(auditor.AuditError):auditor.fetch_public('https://example.com')
   self.assertEqual(dns.call_count,2);conn.close.assert_called()
 def test_pinned_ip_tls(self):
  with patch('socket.create_connection') as connect,patch('ssl.create_default_context') as sslctx:
   connection=auditor.PinnedHTTPS('example.com','93.184.216.34',8);connection.connect();connect.assert_called_once_with(('93.184.216.34',443),timeout=8);sslctx.return_value.wrap_socket.assert_called_once_with(connect.return_value,server_hostname='example.com')
 def test_origin_and_unconfigured(self):
  self.assertEqual(self.call(origin='https://attacker.example')['status'],403)
  with patch.dict(os.environ,{},clear=True):self.assertEqual(self.call()['status'],503)
 def test_email_and_report(self):
  settings={'SMTP_HOST':'smtp.gmail.com','SMTP_USER':'sender@gmail.com','SMTP_PASSWORD':'test-only-not-a-key','SMTP_FROM':'sender@gmail.com'}
  with patch.dict(os.environ,settings),patch.object(app,'fetch_public',return_value=('https://example.com',HTML)),patch.object(app,'send_report') as send:
   result=self.call();self.assertEqual(result['status'],200);self.assertEqual(result['data']['delivery'],'submitted');self.assertEqual(result['data']['report']['passed'],7);send.assert_called_once();self.assertEqual(self.call()['status'],429)
 def test_delivery_failure_keeps_results(self):
  with patch.dict(os.environ,{k:'test' for k in ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD','SMTP_FROM']}),patch.object(app,'fetch_public',return_value=('https://example.com',HTML)),patch.object(app,'send_report',side_effect=OSError('provider offline')):
   result=self.call();self.assertEqual(result['data']['delivery'],'failed');self.assertIn('report',result['data'])
 def test_email_validation(self):
  for email in ['not-an-email','x@example.com\nBcc: victim@example.com']:
   self.assertEqual(self.call({'name':'Test User','email':email,'website':'https://example.com','consent':True})['status'],400)
 def test_smtp_message(self):
  with patch.dict(os.environ,{'SMTP_HOST':'smtp.gmail.com','SMTP_PORT':'465','SMTP_USER':'sender@gmail.com','SMTP_PASSWORD':'test-only','SMTP_FROM':'sender@gmail.com'}),patch.object(app.smtplib,'SMTP_SSL') as smtp:
   app.send_report('buyer@yahoo.com','Alex',auditor.analyse('https://example.com',HTML));message=smtp.return_value.__enter__.return_value.send_message.call_args[0][0];self.assertEqual(message['To'],'buyer@yahoo.com');self.assertIn('not a full-site',message.get_content());self.assertNotIn('test-only',message.get_content())
 def test_google_mail_connector(self):
  settings={'EMAIL_PROVIDER':'google_script','GOOGLE_MAIL_URL':'https://script.google.com/macros/s/testdeployment/exec','GOOGLE_MAIL_TOKEN':'private-test-token-at-least-24'}
  with patch.dict(os.environ,settings),patch.object(app.urllib.request,'urlopen') as request:
   request.return_value.__enter__.return_value.read.return_value=b'{"ok":true}'
   app.send_report('buyer@outlook.com','Alex',auditor.analyse('https://example.com',HTML))
   payload=json.loads(request.call_args[0][0].data);self.assertEqual(payload['to'],'buyer@outlook.com');self.assertEqual(payload['token'],settings['GOOGLE_MAIL_TOKEN']);self.assertNotIn(payload['token'],payload['body'])
   request.return_value.__enter__.return_value.read.return_value=b'{"ok":false}'
   with self.assertRaises(RuntimeError):app.send_report('buyer@outlook.com','Alex',auditor.analyse('https://example.com',HTML))
 def test_svg_titles_are_not_document_title(self):
  document='<head><title>SO IONIC BOTANICALS</title></head><body><svg><title>American Express</title></svg><svg><title>Apple Pay</title></svg><h1>Our store</h1></body>'
  result=auditor.analyse('https://example.com',document)
  self.assertEqual(result['title'],'SO IONIC BOTANICALS')
  self.assertNotIn('American Express',result['checks'][1]['evidence'])
 def test_inactive_template_content_not_counted(self):
  document='<title>Store</title><h1>Welcome</h1><template><h1>Not rendered</h1><img src="x"></template><noscript><h1>Fallback</h1></noscript><svg><title>Logo</title><image href="x"/></svg>'
  result=auditor.analyse('https://example.com',document)
  self.assertEqual(result['title'],'Store');self.assertEqual(result['checks'][4]['status'],'pass');self.assertEqual(result['checks'][-1]['status'],'not_assessed')
 def test_optional_metadata_and_multiple_h1_are_reviews(self):
  report=auditor.analyse('https://example.com','<title>Store</title><h1>First</h1><h1>Second</h1>')
  self.assertEqual(report['checks'][4]['status'],'review');self.assertEqual(report['checks'][5]['status'],'review')
  self.assertIn('not automatically',report['checks'][4]['recommendation'])
 def test_client_shell_missing_content_is_inconclusive(self):
  report=auditor.analyse('https://example.com','<div id="root"></div><script src="app.js"></script>')
  self.assertTrue(report['possible_client_rendering'])
  self.assertEqual(report['checks'][4]['status'],'not_assessed');self.assertEqual(report['checks'][2]['status'],'not_assessed')
 def test_bot_challenge_not_scored_as_website(self):
  with self.assertRaises(auditor.AuditError):auditor.analyse('https://example.com','<title>Just a moment...</title><script src="/cdn-cgi/challenge-platform/x.js"></script>')
 def test_viewport_spacing_is_supported(self):
  report=auditor.analyse('https://example.com','<meta name="viewport" content="width = device-width, initial-scale=1">')
  self.assertEqual(report['checks'][3]['status'],'pass')
if __name__=='__main__':unittest.main()
