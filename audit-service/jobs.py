"""Short-lived background PageSpeed jobs for free-host request limits."""
import datetime, secrets, threading, time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit, quote
from auditor import validate_url, public_addresses, AuditError
from pagespeed import request_measurements, normalize
from store_review import review_store

LOCK = threading.Lock()
WORKERS = ThreadPoolExecutor(max_workers=1)
JOBS = {}
TTL = 1800


def start_job(website, name, email, sender, store_context=None):
    url = validate_url(website)
    parsed = urlsplit(url)
    public_addresses(parsed.hostname, 443 if parsed.scheme == 'https' else 80)
    with LOCK:
        for key in list(JOBS):
            if time.time() - JOBS[key]['created'] > TTL:
                del JOBS[key]
        if any(job['status'] in ('queued', 'running') for job in JOBS.values()):
            raise AuditError('An audit is already running. Please try again in a few minutes.')
        completed_keys = sorted((key for key in JOBS if JOBS[key]['status'] not in ('queued', 'running')), key=lambda key: JOBS[key]['created'])
        for key in completed_keys[:-2]:
            del JOBS[key]
        job_id = secrets.token_urlsafe(32)
        JOBS[job_id] = {'created': time.time(), 'status': 'queued', 'stage': 'Queued for Google PageSpeed', 'completed_steps': [], 'raw': {}}
    WORKERS.submit(run_job, job_id, url, name, email, sender, store_context)
    return job_id


def update(job_id, **values):
    with LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(values)


def run_job(job_id, url, name, email, sender, store_context=None):
    report = {'schema_version': 3, 'source': 'google_pagespeed', 'url': url, 'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'devices': {}, 'errors': {}, 'google_url': 'https://pagespeed.web.dev/analysis?url=' + quote(url, safe=''), 'limitations': 'Google Lighthouse lab measurements are estimates from a particular run, not a guarantee of real-user experience, accessibility compliance, rankings or sales. Mobile and desktop use different test conditions; repeat runs can differ. CrUX field data is shown only when the API returns it and is labeled as page- or origin-level. Missing categories, Agentic Browsing checks and metrics are never invented. The Google website can expose features not available in the public API. Before/after comparisons should use the same URL, strategy, version and comparable test conditions. Store downloaded reports if you need lasting evidence; online preview jobs expire after up to 30 minutes, capacity limits, or a service restart.'}
    completed = []
    try:
        update(job_id, status='running')
        for strategy in ('mobile', 'desktop'):
            update(job_id, stage='Running Google Lighthouse: ' + strategy)
            try:
                raw = request_measurements(url, strategy)
                report['devices'][strategy] = normalize(raw, strategy)
                with LOCK:
                    if job_id in JOBS:
                        JOBS[job_id]['raw'][strategy] = raw
            except AuditError as error:
                report['errors'][strategy] = str(error)
            completed.append(strategy)
            update(job_id, completed_steps=completed[:])
        if store_context is not None:
            update(job_id, stage='Checking public catalogue and store context')
            report['store_review'] = review_store(url, store_context, report['devices'])
            completed.append('store')
            update(job_id, completed_steps=completed[:])
        if not report['devices'] and report.get('store_review', {}).get('availability') != 'available':
            update(job_id, status='failed', stage='Google could not return measurements', error='; '.join(report['errors'].values()))
            return
        update(job_id, stage='Preparing measured report and sending email')
        try:
            sender(email, name, report)
            delivery = 'submitted'
        except Exception:
            delivery = 'failed'
        message = ('Some PageSpeed measurements were unavailable; see the device errors. ' if report.get('errors') else '') + ('The email provider accepted your measured report for sending. Check inbox and spam; delivery is not guaranteed.' if delivery == 'submitted' else 'Your available findings are ready, but email delivery failed. Download your report below.')
        update(job_id, status='complete', stage='Report ready', report=report, delivery=delivery, message=message)
    except Exception:
        update(job_id, status='failed', stage='Audit failed', error='The audit could not be completed. No substitute scores were generated.')


def read_job(job_id, raw_strategy=None):
    with LOCK:
        job = JOBS.get(job_id)
        if not job or time.time() - job['created'] > TTL:
            if job:
                del JOBS[job_id]
            return None
        if raw_strategy:
            return job['raw'].get(raw_strategy)
        return {key: value for key, value in job.items() if key not in ('raw', 'created')}
