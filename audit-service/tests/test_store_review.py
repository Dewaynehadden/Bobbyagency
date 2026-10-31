import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from auditor import AuditError
from store_review import review_store,catalogue
PAGE='<title>Shop</title><h1>Our products</h1><script src="https://cdn.shopify.com/theme.js"></script><a href="/policies/shipping-policy">Shipping</a><a href="/contact">Contact</a>'
class StoreTests(unittest.TestCase):
 def test_public_count_is_not_sales(self):
  with patch('store_review.fetch_public',side_effect=[('https://example.com/',PAGE),('https://example.com/products.json?limit=50&page=1',json.dumps({'products':[{'id':1,'title':'Product'},{'id':2,'title':'Another'}]}))]):
   report=review_store('https://example.com/',{'sales_state':'no','sales_concern':'traffic'},{})
  self.assertEqual(report['catalogue']['observed_count'],2);self.assertEqual(report['verified_sales']['status'],'unknown');self.assertIn('not independently verified',report['submitted_context']['verification']);self.assertEqual(report['external_estimates']['status'],'not_connected')
  self.assertIn('did not detect zero sales',report['action_plan'][0]['suggestion'])
 def test_no_catalogue_is_unknown_not_zero(self):
  with patch('store_review.fetch_public',side_effect=AuditError('blocked')):
   report=review_store('https://example.com/',{},{});self.assertIsNone(report['catalogue']['observed_count']);self.assertEqual(report['verified_sales']['status'],'unknown')
 def test_pagination_cap_is_disclosed(self):
  first={'products':[{'id':n,'title':'Product'} for n in range(50)]};second={'products':[{'id':n,'title':'Product'} for n in range(50,100)]}
  with patch('store_review.fetch_public',side_effect=[('https://example.com/products.json',json.dumps(first)),('https://example.com/products.json',json.dumps(second))]):
   result=catalogue('https://example.com/','Shopify markers observed');self.assertEqual(result['observed_count'],100);self.assertTrue(result['truncated']);self.assertEqual(len(result['source_urls']),2)
 def test_variants_are_not_products(self):
  with patch('store_review.fetch_public',return_value=('https://example.com/products.json',json.dumps({'products':[{'id':1,'title':'One','variants':[{'id':2},{'id':3}]}]}))):self.assertEqual(catalogue('https://example.com/','Shopify markers observed')['observed_count'],1)
 def test_missing_links_are_not_declared_broken(self):
  with patch('store_review.fetch_public',return_value=('https://example.com/','<title>Store</title><div id="app"></div>')):report=review_store('https://example.com/',{}, {})
  self.assertTrue(all(c['status'] in ('not_observed','not_assessed') for c in report['public_checks']));self.assertIsNone(report['catalogue']['observed_count'])
 def test_wrong_origin_not_attributed_to_store(self):
  with patch('store_review.fetch_public',return_value=('https://other.example/products.json','{"products":[]}')):
   with self.assertRaises(AuditError):catalogue('https://example.com/','Shopify markers observed')
 def test_empty_listing_is_not_zero_sales(self):
  with patch('store_review.fetch_public',side_effect=[('https://example.com/',PAGE),('https://example.com/products.json','{"products":[]}')]):report=review_store('https://example.com/',{}, {})
  self.assertEqual(report['catalogue']['observed_count'],0);self.assertEqual(report['verified_sales']['status'],'unknown');self.assertIn('does not prove',report['catalogue']['scope'])
 def test_woo_public_listing(self):
  with patch('store_review.fetch_public',return_value=('https://example.com/wp-json/wc/store/v1/products','[{"id":1,"name":"Product"}]')):self.assertEqual(catalogue('https://example.com/','WooCommerce markers observed')['observed_count'],1)
 def test_worker_includes_store_context_and_email_summary(self):
  import jobs,time
  from test_pagespeed import fixture
  from auditor import report_text
  with patch('store_review.fetch_public',side_effect=AuditError('unavailable')):store=review_store('https://example.com/',{'sales_state':'no','sales_concern':'traffic'},{})
  jobs.JOBS['store-job']={'created':time.time(),'status':'queued','raw':{}};sent=[]
  with patch.object(jobs,'request_measurements',side_effect=[fixture(),fixture('desktop',.98)]),patch.object(jobs,'review_store',return_value=store) as review:
   jobs.run_job('store-job','https://example.com/','Test Buyer','buyer@example.test',lambda *args:sent.append(args),{'sales_state':'no','sales_concern':'traffic'})
  result=jobs.read_job('store-job');self.assertEqual(result['status'],'complete');self.assertIn('store',result['completed_steps']);self.assertEqual(result['report']['store_review']['verified_sales']['status'],'unknown');review.assert_called_once()
  self.assertIn('Verified sales: UNKNOWN',report_text(sent[0][2],'Test Buyer'))
if __name__=='__main__':unittest.main()
