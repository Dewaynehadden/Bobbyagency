/** Deploy in YOUR Google Apps Script account. No secret belongs in this file. */
function doPost(e) {
  const output = value => ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
  try {
    const expected = PropertiesService.getScriptProperties().getProperty('AUDIT_MAIL_TOKEN');
    if (!expected || expected.length < 24 || !e || !e.postData || e.postData.contents.length > 30000) return output({ok:false});
    const input = JSON.parse(e.postData.contents);
    if (input.token !== expected || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(input.to || '') || /[\r\n]/.test(input.to || '')) return output({ok:false});
    if (input.subject !== 'Your Bobbyagency website audit' || typeof input.body !== 'string' || input.body.length > 20000 || MailApp.getRemainingDailyQuota() < 1) return output({ok:false});
    MailApp.sendEmail({to:input.to,subject:input.subject,body:input.body,name:'Bobbyagency',replyTo:'dewaynehadden11@gmail.com'});
    return output({ok:true});
  } catch (_) { return output({ok:false}); }
}
function doGet() {
  return ContentService.createTextOutput('Bobbyagency mail connector. Use the audit form on the website.');
}
