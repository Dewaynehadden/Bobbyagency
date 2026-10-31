"""Public store observations; never infer private sales from catalogue data."""
import datetime, json, re
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin, urlunsplit
from auditor import fetch_public, AuditError, analyse

SALES_STATES = ('yes', 'no', 'unknown')
CONCERNS = ('traffic', 'conversion', 'abandonment', 'repeat', 'unknown')

class StorePage(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.anchor=None; self.ignored=0; self.ld=False; self.ld_text=[]; self.schemas=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='script' and not self.ignored and (values.get('type') or '').lower()=='application/ld+json':
            self.ld=True; self.ld_text=[]; return
        if tag in ('script','style','template','noscript','svg'):
            self.ignored+=1; return
        if self.ignored or self.ld:return
        if tag=='a':self.anchor={'href':values.get('href') or '', 'label':''}
    def handle_data(self,value):
        if self.ld:self.ld_text.append(value)
        elif not self.ignored and self.anchor:self.anchor['label']+=value
    def handle_endtag(self,tag):
        if tag=='script' and self.ld:
            try:self.schemas.append(json.loads(''.join(self.ld_text)))
            except ValueError:pass
            self.ld=False;return
        if tag in ('script','style','template','noscript','svg'):
            self.ignored=max(0,self.ignored-1);return
        if not self.ignored and tag=='a' and self.anchor:
            self.links.append(self.anchor);self.anchor=None


def schema_products(values):
    found={}
    def walk(value,depth=0):
        if depth>12:return
        if isinstance(value,list):
            for item in value[:500]:walk(item,depth+1)
        elif isinstance(value,dict):
            kind=value.get('@type',[])
            if isinstance(kind,str):kind=[kind]
            if isinstance(kind,list) and 'Product' in kind:
                identity=str(value.get('@id') or value.get('url') or value.get('name') or '')
                if identity:found[identity]={'name':str(value.get('name') or '')[:150]}
            for item in value.values():
                if isinstance(item,(dict,list)):walk(item,depth+1)
    walk(values)
    return found


def catalogue(url,platform):
    parsed=urlsplit(url);origin=urlunsplit((parsed.scheme,parsed.netloc,'','',''));products={};sources=[]
    endpoint='/products.json?limit=50&page=' if platform=='Shopify markers observed' else '/wp-json/wc/store/v1/products?per_page=50&page='
    truncated=False
    for page in (1,2):
        source=origin+endpoint+str(page)
        try:final,body=fetch_public(source,content_type='json')
        except AuditError:
            if products:truncated=True;break
            raise
        if (urlsplit(final).scheme,urlsplit(final).netloc)!=(parsed.scheme,parsed.netloc):raise AuditError('Catalogue redirected to another origin; not counted.')
        try:data=json.loads(body)
        except ValueError:raise AuditError('The catalogue returned invalid JSON.')
        items=data.get('products') if platform=='Shopify markers observed' and isinstance(data,dict) else data
        if not isinstance(items,list) or len(items)>50:raise AuditError('The endpoint did not match the expected public product listing.')
        sources.append(source);before=len(products)
        for item in items:
            if not isinstance(item,dict) or item.get('id') is None:raise AuditError('Product records did not have stable IDs; not counted.')
            products[str(item['id'])]={'id':str(item['id']), 'name':str(item.get('title') or item.get('name') or '')[:150]}
        if len(items)<50:break
        if len(products)==before or page==2:truncated=True;break
    return {'availability':'available','observed_count':len(products),'truncated':truncated,'source_type':'public_catalogue_listing','source_urls':sources,'sample':list(products.values())[:5],'scope':'Distinct public product IDs returned by up to two 50-item listing pages. Variants are not counted separately. This is not the total private inventory or a sales count. '+('The scan stopped at its pagination limit, repeated records or a later-page restriction; the catalogue may contain more products.' if truncated else 'Hidden, private, unpublished or region-restricted products may be excluded. An empty response does not prove the store has no products.')}


def review_store(url,context,devices):
    result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'availability':'unavailable','verified_sales':{'status':'unknown','evidence':'No owner-authorized order or analytics connection is configured. Public products and store activity do not prove orders, revenue, or conversion rate.'},'submitted_context':{'sales_state':context.get('sales_state','unknown'),'concern':context.get('sales_concern','unknown'),'verification':'Requester-submitted answer; not independently verified.'},'external_estimates':{'status':'not_connected','provider':None,'evidence':'No authorized third-party sales-estimate integration is configured. No PPSPY sales figures have been fetched or inferred.'},'catalogue':{'availability':'unavailable','observed_count':None,'source_urls':[],'scope':'No complete catalogue measurement available. Unavailable data is not zero products or zero sales.'},'public_checks':[],'action_plan':[]}
    try:
        final,text=fetch_public(url);analyse(final,text);page=StorePage();page.feed(text);result['url']=final;result['availability']='available'
        markers=text.lower()
        platform='Shopify markers observed' if any(s in markers for s in ('cdn.shopify.com','window.shopify','shopify.theme')) else 'WooCommerce markers observed' if any(s in markers for s in ('woocommerce','wp-content/plugins/woocommerce')) else 'Not identified from this page'
        result['platform']=platform
        if platform!='Not identified from this page':
            try:result['catalogue']=catalogue(final,platform)
            except (AuditError,ValueError,TypeError):result['catalogue']['scope']='The public catalogue endpoint was unavailable, restricted, invalid, or too large. This does not establish the number of products or sales.'
        samples=schema_products(page.schemas)
        result['page_product_schema_count']=len(samples)
        checks=[('shipping','Shipping / delivery link',r'shipping|delivery'),('returns','Returns / refund link',r'return|refund'),('contact','Contact / support link',r'contact|support|mailto:|tel:'),('privacy','Privacy policy link',r'privacy'),('cart','Cart / basket link',r'/cart(?:[/?#]|$)|/basket(?:[/?#]|$)')]
        for key,label,pattern in checks:
            matches=[]
            for link in page.links:
                if re.search(pattern,link['href']+' '+link['label'],re.I):
                    target=urljoin(final,link['href'])
                    if urlsplit(target).scheme in ('http','https','mailto','tel'):matches.append({'label':link['label'].strip()[:100],'url':target})
            result['public_checks'].append({'id':key,'title':label,'status':'observed' if matches else 'not_observed','evidence':matches[:3],'interpretation':'Link observed in returned HTML; its accuracy and usability were not tested.' if matches else 'Not found in the sampled HTML. JavaScript or another page may provide it; confirm in a browser before calling it missing.'})
        result['public_checks'].append({'id':'checkout','title':'Checkout / payment completion','status':'not_assessed','evidence':[],'interpretation':'No checkout submission, test purchase, payment, inventory change, order history or customer record was accessed.'})
    except (AuditError,ValueError,TypeError):result['public_error']='The public storefront could not be inspected. PageSpeed results, if available, remain separate.'
    state=result['submitted_context']['sales_state'];concern=result['submitted_context']['concern']
    if state=='yes':result['action_plan'].append({'basis':'Requester reports existing orders (unverified)','suggestion':'Ask the owner to confirm the reporting period, orders, sessions and conversion rate. Prioritize confirmed friction without assuming technical changes will increase sales.'})
    elif state=='no':result['action_plan'].append({'basis':'Requester reports no orders (unverified)','suggestion':'Confirm the order history and analytics setup, then review traffic quality, offer, pricing and trust before choosing technical work. The public audit did not detect zero sales.'})
    else:result['action_plan'].append({'basis':'Sales status unknown','suggestion':'Request owner-confirmed order and traffic figures, or a future authorized read-only analytics connection. Do not infer sales from catalogue size, visitors, stock changes or site appearance.'})
    suggestions={'traffic':'Review acquisition channels, search visibility and qualified sessions in owner-authorized analytics; traffic was not measured here.','conversion':'Review traffic quality, product offer, pricing and the actual conversion funnel using owner-authorized analytics and a manual product-page review.','abandonment':'Review authorized checkout-abandonment data and payment/shipping error logs. No checkout failure was detected by this audit.','repeat':'Review repeat-purchase cohorts and consented retention activity in the owner’s tools. Repeat purchases were not measured here.'}
    if concern in suggestions:result['action_plan'].append({'basis':'Requester-selected concern (unverified)', 'suggestion':suggestions[concern]})
    for strategy,device in devices.items():
        for item in [a for a in device.get('audits',[]) if a.get('group') in ('insights','diagnostics') and a.get('score') is not None and a['score']<100][:3]:
            result['action_plan'].append({'basis':'Google Lighthouse finding · '+strategy,'suggestion':'Review “'+item['title']+'”'+(' ('+item['displayValue']+')' if item.get('displayValue') else '')+'. Confirm the affected resources and scope before quoting; a measured issue does not establish a cause of lost sales.'})
    store_signals=result.get('platform','Not identified from this page')!='Not identified from this page' or bool(result.get('page_product_schema_count')) or any(check['id']=='cart' and check['status']=='observed' for check in result['public_checks'])
    result['store_evidence_observed']=bool(store_signals and result['availability']=='available')
    for check in result['public_checks']:
        if store_signals and check['id'] in ('shipping','returns','contact') and check['status']=='not_observed':result['action_plan'].append({'basis':'Public link not observed; manual confirmation required','suggestion':'Confirm shoppers can find '+check['title'].lower()+' in the rendered store. Only propose changes after confirming the actual gap.'})
    return result
