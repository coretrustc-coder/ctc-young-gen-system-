import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Enhanced Cyberpunk Glow CSS Rules
glow_css = """
  /* HOVER GLOW MICRO-INTERACTIONS */
  .card, .metric, .stack-step, .letter-card, .metric-value, .hero-chip, .qprompt {
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  }

  .card:hover {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 22px rgba(62, 198, 208, 0.3) !important;
    transform: translateY(-2px);
  }

  .metric:hover {
    border-color: var(--green-l) !important;
    box-shadow: 0 0 22px rgba(29, 158, 117, 0.35) !important;
    transform: translateY(-2px);
  }

  .stack-step:hover {
    border-color: var(--cyan-l) !important;
    box-shadow: 0 0 18px rgba(62, 198, 208, 0.22) !important;
    background: rgba(62, 198, 208, 0.08) !important;
    transform: translateX(4px);
  }

  .letter-card:hover {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 20px rgba(62, 198, 208, 0.25) !important;
  }

  /* GLOWING LINKS & BANK BUTTONS */
  a[target="_blank"], .copy-btn, .hero-chip, .qprompt, .btn {
    transition: all 0.2s ease !important;
  }

  a[target="_blank"]:hover {
    color: var(--cyan-l) !important;
    text-shadow: 0 0 12px rgba(62, 198, 208, 0.8) !important;
  }

  .tbl tr:hover {
    box-shadow: 0 0 15px rgba(62, 198, 208, 0.15) !important;
  }

  /* FLOATING HOVER LINK TOOLTIP ENGINE */
  .glow-tooltip {
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%) translateY(4px);
    background: var(--bg-1);
    border: 1px solid var(--cyan);
    box-shadow: 0 0 20px rgba(62, 198, 208, 0.4);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 11px;
    color: var(--text-1);
    white-space: nowrap;
    z-index: 1000;
    pointer-events: none;
    opacity: 0;
    transition: all 0.2s ease;
  }

  .glow-tooltip-wrap {
    position: relative;
    display: inline-block;
  }

  .glow-tooltip-wrap:hover .glow-tooltip {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
"""

if "/* HOVER GLOW MICRO-INTERACTIONS */" not in html:
    html = html.replace("</style>", glow_css + "\n</style>")

# 2. Add Admin Portal Button in Topbar
admin_btn = '<button class="btn btn-ghost" onclick="location.href=\'admin.html\'" style="border-color:var(--cyan);color:var(--cyan-l);">🛡 Admin Portal</button>'
if "admin.html" not in html:
    html = html.replace('<button class="btn btn-ghost" onclick="showPanel(\'services\')">Book a Call</button>', admin_btn + ' <button class="btn btn-ghost" onclick="showPanel(\'services\')">Book a Call</button>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html glow styling and Admin portal button injected successfully!")
