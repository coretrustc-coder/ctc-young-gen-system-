import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject SCHOOL_CATALOG and Smart Link parser into index.html script block
school_catalog_js = """
const SCHOOL_CATALOG = {
  "utoronto": { name: "University of Toronto (U of T)", aidUrl: "https://future.utoronto.ca/finances/financial-aid/", bursariesUrl: "https://registrar.utoronto.ca/finances-and-funding/awards-and-financial-aid/", sagUrl: "https://future.utoronto.ca/finances/financial-aid/university-of-toronto-financial-aid-utaps/" },
  "york": { name: "York University", aidUrl: "https://sfs.yorku.ca/financialaid", bursariesUrl: "https://sfs.yorku.ca/scholarships", sagUrl: "https://sfs.yorku.ca/financialaid" },
  "waterloo": { name: "University of Waterloo", aidUrl: "https://uwaterloo.ca/undergraduate-entrance-awards/", bursariesUrl: "https://uwaterloo.ca/future-students/financing/scholarships" },
  "mcmaster": { name: "McMaster University", aidUrl: "https://registrar.mcmaster.ca/financial-aid/", bursariesUrl: "https://registrar.mcmaster.ca/award-by-application/" },
  "western": { name: "Western University", aidUrl: "https://www.registrar.uwo.ca/student_finances/index.html", bursariesUrl: "https://www.registrar.uwo.ca/student_finances/work_study.html" },
  "tmu": { name: "Toronto Metropolitan University (Ryerson)", aidUrl: "https://www.torontomu.ca/current-students/financial-aid/", bursariesUrl: "https://www.torontomu.ca/awards/" },
  "ryerson": { name: "Toronto Metropolitan University (Ryerson)", aidUrl: "https://www.torontomu.ca/current-students/financial-aid/", bursariesUrl: "https://www.torontomu.ca/awards/" },
  "queens": { name: "Queen's University", aidUrl: "https://www.queensu.ca/registrar/financial-aid", bursariesUrl: "https://www.queensu.ca/registrar/financial-aid/bursaries" },
  "ottawa": { name: "University of Ottawa", aidUrl: "https://www.uottawa.ca/study/fees-financial-support/bursaries-scholarships" },
  "carleton": { name: "Carleton University", aidUrl: "https://carleton.ca/awards/" },
  "guelph": { name: "University of Guelph", aidUrl: "https://www.uoguelph.ca/registrar/financialservices/" },
  "laurier": { name: "Wilfrid Laurier University", aidUrl: "https://www.wlu.ca/tuition-and-financial-aid/index.html" },
  "humber": { name: "Humber College", aidUrl: "https://humber.ca/admissions/financial-aid.html" },
  "seneca": { name: "Seneca Polytechnic", aidUrl: "https://www.senecapolytechnic.ca/register/financialaid.html" },
  "george brown": { name: "George Brown College", aidUrl: "https://www.georgebrown.ca/financial-aid" },
  "sheridan": { name: "Sheridan College", aidUrl: "https://www.sheridancollege.ca/admissions/financial-aid" },
  "centennial": { name: "Centennial College", aidUrl: "https://www.centennialcollege.ca/admissions/financial-aid" },
  "algonquin": { name: "Algonquin College", aidUrl: "https://www.algonquincollege.com/financial-aid/" }
};

function getSchoolLinks(schoolInput) {
  if (!schoolInput) return null;
  const lower = schoolInput.toLowerCase();
  for (const [key, obj] of Object.entries(SCHOOL_CATALOG)) {
    if (lower.includes(key) || lower.includes(obj.name.toLowerCase())) {
      return obj;
    }
  }
  return null;
}
"""

# Replace script tag start or inject school catalog
if "const SCHOOL_CATALOG =" not in html:
    html = html.replace("<script>\nlet heroActive = true;", "<script>\n" + school_catalog_js + "\nlet heroActive = true;")

# Update addMessage to render smart link cards and markdown links properly
old_add_message = """function addMessage(text, isUser) {
  activateChat();
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg' + (isUser ? ' user' : '');
  const time = new Date().toLocaleTimeString('en-CA', {hour: '2-digit', minute: '2-digit'});
  div.innerHTML = `
    <div class="msg-avatar ${isUser ? 'user' : 'bot'}">${isUser ? 'You' : 'CT'}</div>
    <div>
      <div class="msg-bubble">${text.replace(/\\n/g, '<br>').replace(/\\((\\d)\\)/g, '<span style="color:var(--cyan)">($1)</span>').replace(/→/g, '<span style="color:var(--green)">→</span>')}</div>
      <div class="msg-time">${isUser ? 'You' : 'CoreTrust'} · ${time}</div>
    </div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}"""

new_add_message = """function parseMarkdownLinks(txt) {
  // Replace markdown links [title](url) with clickable buttons
  txt = txt.replace(/\\[([^\\]]+)\\]\\(([^\\)]+)\\)/g, (match, title, url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color:var(--cyan-l);font-weight:600;text-decoration:underline;">${title} ↗</a>`;
  });
  // Convert http/https URLs into clickable links if not already wrapped
  txt = txt.replace(/(^|[^"'])(https?:\\/\\/[^\\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--cyan-l);font-weight:600;text-decoration:underline;">$2 ↗</a>');
  return txt;
}

function addMessage(text, isUser) {
  activateChat();
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg' + (isUser ? ' user' : '');
  const time = new Date().toLocaleTimeString('en-CA', {hour: '2-digit', minute: '2-digit'});
  let formattedText = parseMarkdownLinks(text.replace(/\\n/g, '<br>').replace(/\\((\\d)\\)/g, '<span style="color:var(--cyan)">($1)</span>').replace(/→/g, '<span style="color:var(--green)">→</span>'));
  
  div.innerHTML = `
    <div class="msg-avatar ${isUser ? 'user' : 'bot'}">${isUser ? 'You' : 'CT'}</div>
    <div>
      <div class="msg-bubble">${formattedText}</div>
      <div class="msg-time">${isUser ? 'You' : 'CoreTrust'} · ${time}</div>
    </div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}"""

if "function parseMarkdownLinks" not in html:
    html = html.replace(old_add_message, new_add_message)

# Update submitProfile to dynamically insert school links
old_submit_profile = """  const msg = `📋 PROFILE ANALYSIS — ${school} · ${program} · ${year}"""

new_submit_profile = """  const schoolObj = getSchoolLinks(school);
  let schoolLinksText = "";
  if (schoolObj) {
    schoolLinksText = `\\n🏫 YOUR OFFICIAL SCHOOL PORTALS (${schoolObj.name}):\\n` +
      `→ Official Financial Aid Office: ${schoolObj.aidUrl}\\n` +
      `→ Bursaries & Scholarships Portal: ${schoolObj.bursariesUrl || schoolObj.aidUrl}\\n` +
      (schoolObj.sagUrl ? `→ Student Access Guarantee (SAG) Portal: ${schoolObj.sagUrl}\\n` : '');
  }

  const msg = `📋 PROFILE ANALYSIS — ${school} · ${program} · ${year}${schoolLinksText}`"""

if "const schoolObj = getSchoolLinks(school);" not in html:
    html = html.replace(old_submit_profile, new_submit_profile)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully with school catalog and smart link rendering!")
