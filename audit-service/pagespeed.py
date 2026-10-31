"""Google PageSpeed Insights v5 measurements; never synthesize scores."""
import json, math, os, urllib.error, urllib.parse, urllib.request
from auditor import AuditError, validate_url, public_addresses

CATEGORIES = ('performance', 'accessibility', 'best-practices', 'seo')
METRICS = ('first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time', 'cumulative-layout-shift', 'speed-index')


def request_measurements(url, strategy):
    key = os.environ.get('PAGESPEED_API_KEY', '').strip()
    if not key:
        raise AuditError('PageSpeed measurements are not configured yet. Add PAGESPEED_API_KEY to the audit service; no scores have been generated.')
    query = [('url', url), ('strategy', strategy), ('key', key)]
    query += [('category', category) for category in CATEGORIES]
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode(query)
    try:
        request = urllib.request.Request(endpoint, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(request, timeout=110) as response:
            body = response.read(12_000_001)
        if len(body) > 12_000_000:
            raise AuditError('Google returned a report larger than this service can safely process.')
        data = json.loads(body)
    except urllib.error.HTTPError as error:
        if error.code == 429:
            raise AuditError('Google PageSpeed quota is currently exhausted. Please retry later; no score was generated.')
        if error.code in (400, 401, 403):
            raise AuditError('Google rejected the PageSpeed request. Check API activation, key restrictions and the public website URL in the service settings.')
        raise AuditError('Google PageSpeed could not complete this measurement. Please retry later.')
    except (OSError, ValueError):
        raise AuditError('The PageSpeed request timed out or returned invalid data. No estimated score was substituted.')
    if data.get('error'):
        raise AuditError('Google PageSpeed returned an error. No score was generated.')
    lighthouse = data.get('lighthouseResult') or {}
    if lighthouse.get('runtimeError'):
        raise AuditError('Lighthouse could not test this page: ' + str(lighthouse['runtimeError'].get('code', 'runtime error'))[:100])
    if not lighthouse.get('categories'):
        raise AuditError('Google did not return Lighthouse category measurements for this page.')
    return data


def score(value):
    return int(math.floor(value * 100 + 0.5)) if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1 else None


def normalize(data, strategy):
    lighthouse = data['lighthouseResult']
    audits = lighthouse.get('audits') or {}
    categories = []
    referenced = {}
    source_categories = lighthouse.get('categories') or {}
    ordered_keys = [key for key in CATEGORIES if key in source_categories] + [key for key in source_categories if key not in CATEGORIES]
    for key in ordered_keys:
        category = source_categories[key]
        categories.append({'id': key, 'title': category.get('title', key), 'score': score(category.get('score')), 'description': category.get('description', '')})
        for ref in category.get('auditRefs') or []:
            referenced.setdefault(ref['id'], []).append(key)
    metrics = []
    for key in METRICS:
        audit = audits.get(key)
        if audit:
            metrics.append({'id': key, 'title': audit.get('title', key), 'displayValue': audit.get('displayValue'), 'numericValue': audit.get('numericValue'), 'numericUnit': audit.get('numericUnit'), 'score': score(audit.get('score')), 'description': audit.get('description', '')})
    items = []
    for key, audit in audits.items():
        if key in METRICS or key in ('final-screenshot', 'screenshot-thumbnails', 'full-page-screenshot'):
            continue
        display_mode = audit.get('scoreDisplayMode', '')
        value = score(audit.get('score'))
        details = audit.get('details') or {}
        if display_mode == 'notApplicable':
            group = 'not_applicable'
        elif display_mode == 'manual':
            group = 'manual'
        elif display_mode == 'error':
            group = 'errors'
        elif value == 100:
            group = 'passed'
        elif key.endswith('-insight') or details.get('type') == 'opportunity':
            group = 'insights'
        else:
            group = 'diagnostics'
        # Keep provider details, descriptions, savings and errors intact for evidence.
        items.append({'id': key, 'title': audit.get('title', key), 'description': audit.get('description', ''), 'displayValue': audit.get('displayValue', ''), 'score': value, 'scoreDisplayMode': display_mode, 'details': details, 'categories': referenced.get(key, []), 'group': group, 'errorMessage': audit.get('errorMessage', ''), 'warnings': audit.get('warnings', [])})
    screenshot = (audits.get('final-screenshot') or {}).get('details', {}).get('data')
    if not isinstance(screenshot, str) or not screenshot.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,')) or len(screenshot) > 1_500_000:
        screenshot = None
    experience = data.get('loadingExperience') or {}
    field_scope = 'page'
    if not experience.get('metrics'):
        experience = data.get('originLoadingExperience') or {}
        field_scope = 'origin'
    return {'strategy': strategy, 'requestedUrl': lighthouse.get('requestedUrl'), 'finalUrl': lighthouse.get('finalDisplayedUrl') or lighthouse.get('finalUrl'), 'fetchTime': lighthouse.get('fetchTime') or data.get('analysisUTCTimestamp'), 'lighthouseVersion': lighthouse.get('lighthouseVersion'), 'userAgent': lighthouse.get('userAgent'), 'environment': lighthouse.get('environment', {}), 'configSettings': lighthouse.get('configSettings', {}), 'warnings': lighthouse.get('runWarnings', []), 'categories': categories, 'metrics': metrics, 'audits': items, 'screenshot': screenshot, 'field': {'available': bool(experience.get('metrics')), 'scope': field_scope, 'data': experience if experience.get('metrics') else {}}, 'provider': 'Google PageSpeed Insights API v5 / Lighthouse'}


def text_report(report, name):
    lines = ['Hi ' + name + ',', '', 'Your Bobbyagency PageSpeed report', report['url'], 'Requested: ' + report['checked_at'], 'Source: Google PageSpeed Insights API / Lighthouse', '']
    for strategy in ('mobile', 'desktop'):
        device = report['devices'].get(strategy)
        lines += [strategy.upper()]
        if not device:
            lines += ['Measurement unavailable: ' + report.get('errors', {}).get(strategy, 'Not returned'), '']
            continue
        lines += ['Test time: ' + str(device.get('fetchTime')), 'Final URL: ' + str(device.get('finalUrl')), 'Lighthouse version: ' + str(device.get('lighthouseVersion'))]
        for category in device['categories']:
            lines.append(category['title'] + ': ' + (str(category['score']) if category['score'] is not None else 'Not measured'))
        for metric in device['metrics']:
            lines.append(metric['title'] + ': ' + str(metric.get('displayValue') or 'Not returned'))
        lines.append('Real-user data: ' + (device['field']['scope'] + '-level CrUX data returned' if device['field']['available'] else 'No field data returned by the API'))
        findings = [a for a in device['audits'] if a['group'] in ('insights', 'diagnostics') and a.get('score') != 100]
        for item in findings[:8]:
            lines.append('Review: ' + item['title'] + (' — ' + item['displayValue'] if item['displayValue'] else ''))
        lines.append('')
    store = report.get('store_review')
    if store:
        lines += ['PUBLIC STORE EVIDENCE & SALES CONTEXT', 'Verified sales: UNKNOWN. No authorized order/analytics data connected.', 'Requester answer (unverified): ' + store['submitted_context']['sales_state']]
        catalogue = store['catalogue']
        lines += ['Public catalogue entries observed: ' + (str(catalogue['observed_count']) if catalogue.get('observed_count') is not None else 'Unavailable'), catalogue.get('scope', ''), 'No third-party sales-estimate provider is connected.']
        for action in store['action_plan'][:8]:
            lines += [action['basis'] + ': ' + action['suggestion']]
        lines.append('')
    lines += [report['limitations'], '', 'These findings support a discussion, not an automatic invoice. Agree the scope and fee in writing before work.', 'Request a quote: https://dewaynehadden.github.io/Bobbyagency/payment.html#start-project', 'Open Google PageSpeed for a NEW run (results may differ): ' + report['google_url'], 'You requested this one-time report; no marketing subscription was created.']
    return '\n'.join(lines)[:18000]
