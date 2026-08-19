import re

# 1. Update index.html to add PDF download link to sidebar and CTC GEM header
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

sidebar_pdf_link = """      <div class="nav-item" onclick="window.open('/CoreTrust_YoungGen_Guide.html','_blank')"><div class="nav-dot"></div> 📥 Quick Start Guide (PDF)</div>
      <div class="nav-item" onclick="window.open('/CoreTrust_CTC_GEM_Simplified_Guide.html','_blank')" style="color:var(--cyan-l);"><div class="nav-dot"></div> 🎓 CTC GEM Simplified Guide (PDF)</div>"""

if "CoreTrust_CTC_GEM_Simplified_Guide.html" not in html:
    html = html.replace("<div class=\"nav-item\" onclick=\"window.open('/CoreTrust_YoungGen_Guide.html','_blank')\"><div class=\"nav-dot\"></div> 📥 Quick Start Guide (PDF)</div>", sidebar_pdf_link)

# Add button inside CTC GEM Panel Header
panel_btn = """          <div class="ctc-gem-title">CTC GEM</div>
          <div style="margin-top:8px;"><button class="btn btn-cyan" onclick="window.open('/CoreTrust_CTC_GEM_Simplified_Guide.html','_blank')">🎓 Download / Print Simplified PDF Guide ↗</button></div>"""

if "Download / Print Simplified PDF Guide" not in html:
    html = html.replace('<div class="ctc-gem-title">CTC GEM</div>', panel_btn)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update vercel.json routes for static serving of the simplified PDF guide
with open('vercel.json', 'r', encoding='utf-8') as f:
    vjson = f.read()

if 'CoreTrust_CTC_GEM_Simplified_Guide' not in vjson:
    vjson = vjson.replace('"routes": [', '"routes": [\n    { "src": "/CoreTrust_CTC_GEM_Simplified_Guide", "dest": "/CoreTrust_CTC_GEM_Simplified_Guide.html" },')
    with open('vercel.json', 'w', encoding='utf-8') as f:
        f.write(vjson)

print("PDF guide links and vercel routing updated successfully!")
