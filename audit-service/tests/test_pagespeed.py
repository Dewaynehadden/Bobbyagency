"""Synthetic provider fixtures for tests only; never production report data."""
import io,json,os,sys,threading,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pagespeed,jobs,app
from auditor import AuditError,report_text

def fixture(strategy='mobile',value=.77):
 return {'loadingExperience':{},'originLoadingExperience':{'overall_category':'AVERAGE','metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':2700,'category':'AVERAGE'}}},'lighthouseResult':{'requestedUrl':'https://example.com/','finalUrl':'https://example.com/','fetchTime':'2026-10-30T12:00:00Z','lighthouseVersion':'13.0.0','categories':{'performance':{'title':'Performance','score':value,'auditRefs':[{'id':'image-delivery-insight'}]},'accessibility':{'title':'Accessibility','score':None,'auditRefs':[{'id':'color-contrast'}]}},'configSettings':{'formFactor':strategy},'audits':{'largest-contentful-paint':{'title':'Largest Contentful Paint','displayValue':'6.6 s','numericValue':6600,'numericUnit':'millisecond','score':.1},'image-delivery-insight':{'title':'Improve image delivery','displayValue':'Est savings of 491 KiB','score':0,'description':'Use efficient images.','details':{'type':'table','headings':[{'key':'url','label':'URL'}],'items':[{'url':'https://example.com/image.jpg','wastedBytes':502784}],'metricSavings':{'LCP':300}}},'color-contrast':{'title':'Contrast needs review','score':0,'description':'Test contrast','details':{'type':'table','items':[]}}}}}
class PageSpeedTests(unittest.TestCase):
 def setUp(self):jobs.JOBS.clear();app.TIMES.clear();app.DAILY.clear()
 def test_measurements_not_guessed(self):
  report=pagespeed.normalize(fixture(),'mobile')
  self.assertEqual(report['categories'][0]['score'],77);self.assertIsNone(report['categories'][1]['score'])
  self.assertEqual(report['metrics'][0]['numericValue'],6600);self.assertEqual(report['metrics'][0]['displayValue'],'6.6 s')
  self.assertEqual(report['audits'][0]['details']['items'][0]['wastedBytes'],502784)
  self.assertEqual(report['field']['scope'],'origin');self.assertFalse(any('agentic' in c['id'] for c in report['categories']))
 def test_no_field_data_is_not_zero(self):
  data=fixture();data.pop('originLoadingExperience');self.assertFalse(pagespeed.normalize(data,'mobile')['field']['available'])
 def test_missing_key_no_results(self):
  with patch.dict(os.environ,{'PAGESPEED_API_KEY':''}):
   with self.assertRaises(AuditError):pagespeed.request_measurements('https://example.com/','mobile')
 def test_provider_error_not_converted_to_scores(self):
  data=fixture();data['lighthouseResult']['runtimeError']={'code':'NO_FCP'}
  with patch.dict(os.environ,{'PAGESPEED_API_KEY':'test-only'}),patch.object(pagespeed.urllib.request,'urlopen') as request:
   request.return_value.__enter__.return_value.read.return_value=json.dumps(data).encode()
   with self.assertRaises(AuditError):pagespeed.request_measurements('https://example.com/','mobile')
 def test_two_real_strategies_and_email(self):
  jobs.JOBS['test']={'created':__import__('time').time(),'status':'queued','raw':{}}
  sent=[]
  with patch.object(jobs,'request_measurements',side_effect=[fixture(),fixture('desktop',.98)]):jobs.run_job('test','https://example.com/','Buyer','buyer@example.com',lambda *args:sent.append(args))
  result=jobs.read_job('test');self.assertEqual(result['status'],'complete');self.assertEqual(result['report']['devices']['desktop']['categories'][0]['score'],98)
  self.assertEqual(len(sent),1);self.assertEqual(jobs.read_job('test','mobile'),fixture());self.assertNotIn('buyer@example.com',json.dumps(result))
  email=report_text(result['report'],'Buyer');self.assertIn('6.6 s',email);self.assertIn('Test time:',email);self.assertIn('Google',email)
 def test_partial_failure_and_delivery_failure(self):
  jobs.JOBS['test']={'created':__import__('time').time(),'status':'queued','raw':{}}
  with patch.object(jobs,'request_measurements',side_effect=[AuditError('mobile failed'),fixture('desktop',.98)]):jobs.run_job('test','https://example.com/','Buyer','buyer@example.com',lambda *args:(_ for _ in ()).throw(OSError()))
  result=jobs.read_job('test');self.assertEqual(result['delivery'],'failed');self.assertNotIn('mobile',result['report']['devices']);self.assertIn('mobile',result['report']['errors'])
 def test_both_fail_no_email_or_fake_report(self):
  jobs.JOBS['test']={'created':__import__('time').time(),'status':'queued','raw':{}}
  with patch.object(jobs,'request_measurements',side_effect=AuditError('quota exhausted')),patch('app.send_report') as send:
   jobs.run_job('test','https://example.com/','Buyer','buyer@example.com',send);self.assertEqual(jobs.read_job('test')['status'],'failed');send.assert_not_called()
 def test_api_requires_key_for_new_engine(self):
  body=json.dumps({'engine':'pagespeed','name':'Test Buyer','email':'buyer@example.com','website':'https://example.com','consent':True}).encode();status=[]
  env={'HTTP_ORIGIN':app.ORIGIN,'REQUEST_METHOD':'POST','PATH_INFO':'/audit','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),'wsgi.input':io.BytesIO(body)}
  with patch.dict(os.environ,{'PAGESPEED_API_KEY':'','SMTP_HOST':'test','SMTP_USER':'test','SMTP_PASSWORD':'test','SMTP_FROM':'test'}):
   data=json.loads(b''.join(app.application(env,lambda s,h:status.append(s))))
  self.assertTrue(status[0].startswith('503'));self.assertIn('PAGESPEED_API_KEY',data['error'])
 def test_request_asks_for_four_categories_and_device(self):
  from urllib.parse import urlsplit,parse_qs
  with patch.dict(os.environ,{'PAGESPEED_API_KEY':'test-only'}),patch.object(pagespeed.urllib.request,'urlopen') as request:
   request.return_value.__enter__.return_value.read.return_value=json.dumps(fixture()).encode()
   data=pagespeed.request_measurements('https://example.com/','desktop')
   query=parse_qs(urlsplit(request.call_args[0][0].full_url).query)
   self.assertEqual(query['strategy'],['desktop']);self.assertEqual(set(query['category']),set(pagespeed.CATEGORIES));self.assertNotIn('key',data)
 def test_job_status_and_raw_api_are_origin_restricted(self):
  import time
  token='a'*43;jobs.JOBS[token]={'created':time.time(),'status':'complete','raw':{'mobile':fixture()}}
  def call(path,origin):
   status=[];body=b''.join(app.application({'PATH_INFO':path,'REQUEST_METHOD':'GET','HTTP_ORIGIN':origin},lambda s,h:status.append(s)));return status[0],json.loads(body)
  status,data=call('/audit/jobs/'+token,app.ORIGIN);self.assertTrue(status.startswith('200'));self.assertNotIn('raw',data)
  status,data=call('/audit/jobs/'+token+'/raw/mobile',app.ORIGIN);self.assertEqual(data,fixture())
  self.assertTrue(call('/audit/jobs/'+token,'https://unrelated.example')[0].startswith('403'))
 def test_all_five_metrics_preserve_zero_values(self):
  data=fixture()
  values={'first-contentful-paint':900,'largest-contentful-paint':6600,'total-blocking-time':0,'cumulative-layout-shift':.01,'speed-index':2500}
  for key,value in values.items():data['lighthouseResult']['audits'][key]={'title':key,'numericValue':value,'numericUnit':'unitless' if key=='cumulative-layout-shift' else 'millisecond','score':1}
  result=pagespeed.normalize(data,'mobile')
  self.assertEqual({m['id']:m['numericValue'] for m in result['metrics']},values)
if __name__=='__main__':unittest.main()
