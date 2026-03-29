import re

with open('../gh-pages-work/interview.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace sendResults with API-based submission (no navigation)
NEW_SEND = """async function sendResults() {
  const userMsgs = S.messages.filter(m => m.role === 'user');
  if (userMsgs.length === 0) {
    document.getElementById('done-msg').innerHTML =
      '<b style="color:#FF9800">No answers captured.</b><br>'
      + '<span style="color:#aaa;font-size:.75rem">Please use the manual fallback in the Streamlit tab.</span>';
    return;
  }
  await submitInterview();
}

async function submitInterview() {
  const userMsgs = S.messages.filter(m => m.role === 'user');
  document.getElementById('done-msg').innerHTML =
    '<b style="color:#aaa">Saving your answers...</b>';

  try {
    const response = await fetch('https://ai-interview-api.vercel.app/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interview_id: IV_ID, messages: S.messages })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById('done-msg').innerHTML =
        '<b style="color:#4CAF50">&#10003; Interview completed successfully!</b><br>'
        + '<span style="color:#ccc;font-size:.9rem;line-height:2;">'
        + userMsgs.length + ' answers saved.<br>'
        + '<b style="color:white;">Go back to the Streamlit tab</b>'
        + ' and click <b style="color:#4CAF50;">Check My Result</b>.'
        + '</span>';
    } else {
      throw new Error(result.error || 'Unknown error');
    }
  } catch (error) {
    console.error('Submit failed:', error);
    document.getElementById('done-msg').innerHTML =
      '<b style="color:#FF9800">&#9888; Could not auto-save.</b><br>'
      + '<span style="color:#aaa;font-size:.8rem">'
      + 'Go back to the Streamlit tab and use the manual fallback to enter your answers.'
      + '</span>';
  }
}"""

content = re.sub(
    r'async function sendResults\(\)\s*\{.*?^\}',
    NEW_SEND,
    content,
    flags=re.DOTALL | re.MULTILINE
)

# Also remove any window.location / window.opener navigation lines
content = re.sub(r'.*window\.location\.href\s*=.*\n', '', content)
content = re.sub(r'.*window\.opener\.location\.href\s*=.*\n', '', content)
content = re.sub(r'.*window\.parent\.location\.href\s*=.*\n', '', content)

with open('../gh-pages-work/interview.html', 'w', encoding='utf-8') as f:
    f.write(content)

checks = [
    ('submitInterview', 'submitInterview function'),
    ('vercel.app/api/submit', 'API URL'),
    ('Check My Result', 'completion message'),
]
for check, label in checks:
    print(f"{label}: {'OK' if check in content else 'MISSING'}")
