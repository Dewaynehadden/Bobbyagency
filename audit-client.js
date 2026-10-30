'use strict';
(() => {
 const config=window.BOBBY_AUDIT;
 let endpoint;
 try { endpoint=new URL(config?.endpoint);if(endpoint.protocol!=='https:' && !['localhost','127.0.0.1'].includes(endpoint.hostname))return; } catch { return; }
 const $=s=>document.querySelector(s), form=$('#automatic-audit-form');let latestReport;
 config.open=website=>{$('#audit-website').value=website;openDialog($('#audit-dialog'));};
 $('#audit .section-subtitle').textContent='Check your public page for basic technical issues, see the findings, and request a one-time email report.';
 $('#audit-form button[type="submit"]').textContent='Get my free audit →';
 $('#audit-note').textContent='Basic automated homepage checks. Email report with your consent. No passwords or admin access.';
 function display(report){latestReport=report;$('#audit-results').hidden=false;$('#audit-result-summary').textContent=`${report.passed} of ${report.assessed} basic checks passed`;$('#audit-result-url').textContent=report.url;$('#audit-limitations').textContent=report.limitations;$('#audit-checks').replaceChildren(...report.checks.map(check=>{const card=document.createElement('article');card.className='audit-check';card.dataset.status=check.status;const title=document.createElement('h4');title.textContent=`${check.status==='pass'?'✓':check.status==='not_assessed'?'—':'!'} ${check.name}`;const evidence=document.createElement('p');evidence.textContent=check.evidence;card.append(title,evidence);if(check.recommendation){const fix=document.createElement('p');fix.textContent='Suggested next step: '+check.recommendation;card.append(fix);}return card;}));}
 form.addEventListener('submit',async event=>{event.preventDefault();if(!form.reportValidity())return;const d=new FormData(form);const website=normalizeWebsite(d.get('website'));if(!website){$('#automatic-audit-status').textContent='Enter a public HTTP or HTTPS website address.';return;}const button=$('#run-audit');button.disabled=true;button.textContent='Checking your page…';form.setAttribute('aria-busy','true');$('#audit-results').hidden=true;$('#automatic-audit-status').textContent='Checking your public page and preparing the report. Please leave this window open; the service may need a moment to wake.';const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),120000);
  try {const response=await fetch(endpoint.href,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({website,name:d.get('name'),email:d.get('email'),consent:d.get('consent')==='on',company:d.get('company')}),signal:controller.signal,credentials:'omit'});const data=await response.json();if(!response.ok)throw Error(data.error||'The audit could not be completed.');display(data.report);$('#automatic-audit-status').textContent=data.message;}
  catch(error){$('#automatic-audit-status').textContent=error.name==='AbortError'?'The request timed out. Email may still arrive if processing finished. Check your inbox before trying again, or request a personal review.':error.message==='Failed to fetch'?'The audit service is unavailable. Please try later or request a personal review.':error.message;}
  finally{clearTimeout(timer);button.disabled=false;button.textContent='Run audit & email my report →';form.removeAttribute('aria-busy');}
 });
 document.querySelectorAll('#audit-dialog [data-enquire]').forEach(button=>button.addEventListener('click',()=>{
  $('#client-name').value=$('#audit-name').value;$('#client-email').value=$('#audit-email').value;
  $('#client-site').value=$('#audit-website').value;
  if(latestReport && !$('#audit-results').hidden){const issues=latestReport.checks.filter(check=>check.status==='needs_attention').map(check=>check.name).join(', ');$('#client-message').value=`I received a basic audit for ${latestReport.url}. Findings to review: ${issues || 'Please review the site beyond the basic automated checks'}. Please confirm which changes are appropriate, the scope, timeline and cost before work begins.`;}
 }));
 $('#download-audit').addEventListener('click',()=>{if(!latestReport)return;const r=latestReport;const text=[`Bobbyagency basic website audit`,r.url,r.checked_at,`${r.passed} of ${r.assessed} checks passed`,'',...r.checks.flatMap(c=>[c.name+' — '+c.status,c.evidence,c.recommendation||'','']),r.limitations].join('\n');const href=URL.createObjectURL(new Blob([text],{type:'text/plain'}));const link=document.createElement('a');link.href=href;link.download='bobbyagency-website-audit.txt';link.click();setTimeout(()=>URL.revokeObjectURL(href),1000);});
})();
