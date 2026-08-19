import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. CSS for flashing motion text on CTC GEM
flashing_css = """
  /* CTC GEM FLASHING LETTER MOTION EFFECT */
  @keyframes gemFlashMotion {
    0%, 100% {
      color: var(--cyan-l);
      text-shadow: 0 0 10px rgba(62, 198, 208, 0.8), 0 0 20px rgba(62, 198, 208, 0.6);
      transform: scale(1);
    }
    50% {
      color: var(--green-l);
      text-shadow: 0 0 15px rgba(93, 202, 165, 0.9), 0 0 30px rgba(93, 202, 165, 0.7);
      transform: scale(1.02);
    }
  }

  .ctc-gem-title {
    font-size: 22px !important;
    font-weight: 900 !important;
    letter-spacing: 0.12em !important;
    display: inline-block;
    animation: gemFlashMotion 1.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  }

  .gem-pill-header {
    background: rgba(62, 198, 208, 0.08);
    border: 1px solid var(--cyan);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 0 25px rgba(62, 198, 208, 0.2);
  }

  .ascii-diagram {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--cyan-l);
    background: var(--bg-1);
    border: 1px solid var(--border-2);
    border-radius: var(--radius-sm);
    padding: 16px;
    overflow-x: auto;
    white-space: pre;
    line-height: 1.35;
    margin: 14px 0;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
  }
"""

if "/* CTC GEM FLASHING LETTER MOTION EFFECT */" not in html:
    html = html.replace("</style>", flashing_css + "\n</style>")

# 2. Add CTC GEM in Sidebar Nav
sidebar_nav_item = """
    <div class="nav-section">
      <div class="nav-label">Exclusive Founder Blueprint</div>
      <div class="nav-item" onclick="showPanel('ctc-gem')">
        <div class="nav-dot"></div> <strong style="color:var(--cyan-l);">CTC GEM Blueprint</strong>
      </div>
    </div>

    <div class="nav-divider"></div>
"""

if "showPanel('ctc-gem')" not in html:
    html = html.replace('<div class="nav-section">\n      <div class="nav-label">Student Module</div>', sidebar_nav_item + '<div class="nav-section">\n      <div class="nav-label">Student Module</div>')

# 3. HTML for CTC GEM Module
ctc_gem_html = """
      <!-- CTC GEM PANEL (EXCLUSIVE TO LOGGED-IN STUDENTS) -->
      <div class="panel" id="panel-ctc-gem" style="padding:20px;">
        
        <div class="gem-pill-header">
          <div class="ctc-gem-title">CTC GEM</div>
          <div style="font-size:13px;font-weight:700;color:var(--text-1);margin-top:4px;">The Canadian Full Leveraging Blueprint</div>
          <div style="font-size:11px;color:var(--text-2);margin-top:2px;">The Complete Capital & Credit System for Next-Generation Canadian Founders & Operators</div>
          <div style="font-size:10px;color:var(--cyan);margin-top:8px;letter-spacing:0.06em;">
            CASL · PIPEDA · FCAC Compliant · Ontario Consumer Reporting Act · Income Tax Act
          </div>
        </div>

        <div class="card" style="border-color:var(--cyan);background:rgba(62,198,208,0.03);">
          <div class="card-title" style="color:var(--cyan-l);font-size:13px;">The Core Philosophy</div>
          <p style="font-size:12px;color:var(--text-2);line-height:1.7;">
            In Canada, you cannot rent American tradelines or game the system with stated-income loopholes. The Big 6 banking oligopoly and OSFI regulations require verifiable structure, regulatory literacy, and clean debt rotation. This system converts subsidized capital and side income into prime personal and commercial credit lines without triggering personal insolvency or default.
          </p>
        </div>

        <!-- MODULE 0 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-cyan">Module 0</span> The Young Gen Foundation (Ages 18–22) — Turning Subsidized Debt into a Primed Credit File</div>
          
          <div class="ascii-diagram">                     ┌───────────────────────────────────┐
                     │         OSAP Disbursement         │
                     └─────────────────┬─────────────────┘
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
   ┌───────────────────────────┐               ┌───────────────────────────┐
   │    Tuition + Essentials   │               │      OSAP Float Pool      │
   └───────────────────────────┘               └─────────────┬─────────────┘
                                                             │
                      ┌──────────────────────────────────────┼──────────────────────────────────────┐
                      ▼                                      ▼                                      ▼
        ┌───────────────────────────┐          ┌───────────────────────────┐          ┌───────────────────────────┐
        │ Neo Financial ($200–$300) │          │ KOHO Credit ($7/mo Auto)  │          │ Rent Reporting ($8/mo)    │
        │ • Dual-Bureau Reporting   │          │ • Equifax Tradeline       │          │ • $900+/mo Primary Line   │
        │ • Returns 100% Capital    │          │ • 100% On-Time Record     │          │ • Zero Landlord Action    │
        └───────────────────────────┘          └───────────────────────────┘          └───────────────────────────┘</div>

          <div style="font-size:12px;color:var(--text-2);line-height:1.7;">
            <p style="margin-bottom:8px;"><strong style="color:var(--text-1);">The OSAP Float Rule:</strong> Under the post-2026 funding reality (25% grant / 75% loan split), treating student funding as disposable spending creates the Triple Zero Trap (Student Debt + Zero Credit Age + Zero Assets). Unused loan float is placed into zero-risk collateral accounts to jumpstart primary credit age.</p>
            <p style="margin-bottom:8px;"><strong style="color:var(--text-1);">The Dual-Bureau Secured Base:</strong> Deploy $200–$300 into a <a href="https://www.neofinancial.com/credit" target="_blank" style="color:var(--cyan-l);">Neo Financial Secured Card ↗</a> (reports to both Equifax & TransUnion; capital is fully refundable).</p>
            <p><strong style="color:var(--text-1);">The Rent Reporting Tradeline:</strong> Layer <a href="https://www.borrowell.com/rent-advantage" target="_blank" style="color:var(--cyan-l);">Borrowell Rent Advantage ↗</a> or Neo Rent Reporting to report monthly rent payments ($900–$1,500/month) as primary installment lines on Equifax, building multi-year payment depth before graduation.</p>
          </div>
        </div>

        <!-- MODULE 1 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-green">Module 1</span> The Personal Dual-Bureau Stacking Engine — Bypassing Hard Inquiry Collisions</div>
          <p style="font-size:12px;color:var(--text-2);margin-bottom:12px;">Because Canada only operates two primary consumer bureaus, applications must be synchronized so multiple prime applications do not see simultaneous hard inquiries.</p>

          <div class="ascii-diagram">                               ┌──────────────────────────────┐
                               │   720+ Beacon / FICO Score   │
                               └──────────────┬──────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
        ┌──────────────────────────────┐              ┌──────────────────────────────┐
        │    EQUIFAX CANADA PULLERS    │              │   TRANSUNION CANADA PULLERS  │
        ├──────────────────────────────┤              ├──────────────────────────────┤
        │ • CIBC (Aventura / LOC)      │              │ • RBC (Avion / Royal LOC)    │
        │ • TD Canada Trust (LOC/Visa) │              │ • Scotiabank (LOC / Amex)    │
        │ • Desjardins                 │              │ • BMO (Mastercard / LOC)     │
        │ • PC Financial / Meridian CU │              │ • Tangerine / National Bank  │
        └──────────────────────────────┘              └──────────────────────────────┘</div>

          <div style="background:rgba(62,198,208,0.06);border:1px solid var(--border-2);border-radius:var(--radius-sm);padding:12px;margin-top:10px;">
            <div style="font-weight:700;color:var(--cyan-l);font-size:12px;">The Statement Date Arbitrage</div>
            <div style="font-size:11px;color:var(--text-2);margin-top:4px;">Canadian credit bureaus update balances based on the <strong>Statement Date</strong>, not the Payment Due Date.</div>
            <div style="font-family:var(--mono);color:var(--green-l);font-size:13px;margin:8px 0;text-align:center;background:var(--bg-1);padding:8px;border-radius:4px;">
              Reported Utilization = (Statement Balance / Total Credit Limit) × 100
            </div>
            <div style="font-size:11px;color:var(--text-2);">Pay all card balances down to under 3% 2–3 business days before the monthly statement generates. Maintain 0% to 3% utilization across all credit lines before initiating a multi-bank application batch.</div>
          </div>
        </div>

        <!-- MODULE 2 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-amber">Module 2</span> The Proof-of-Income Engine (The ADP Payroll Rotation Play)</div>
          <p style="font-size:12px;color:var(--text-2);margin-bottom:12px;">Converting Irregular Hustle Revenue into Algorithmic Prime Underwriting Triggers. Canadian Tier-1 banks use automated engines that scan linked bank accounts for recurring direct deposits coded as PAY / DIR-DEP or demand verified CRA Notice of Assessments (NOA Line 15000).</p>

          <div class="ascii-diagram">  ┌─────────────────────────┐
  │ Business / Hustle Funds │
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │  Formal Payroll System  │
  │  (ADP / PaymentEvol.)   │
  └────────────┬────────────┘
               │
       ┌───────┴─────────────────────────────────────────┐
       ▼                                                 ▼
┌──────────────────────────────┐          ┌─────────────────────────────┐
│ Direct Deposit to Personal   │          │ CRA Remittances (RP Account) │
│ • Coded: "DIR-DEP / PAY"     │          │ • CPP Deductions             │
│ • Unlocks Tier-1 Auto LOCs   │          │ • Generates Verifiable T4    │
└──────────────────────────────┘          └──────────────────────────────┘</div>

          <div style="font-size:12px;color:var(--text-2);line-height:1.7;">
            <p><strong style="color:var(--text-1);">1. Set Up a Payroll Account:</strong> Connect a business bank account to an automated payroll provider (ADP Canada, PaymentEvolution, or Wagepoint).</p>
            <p><strong style="color:var(--text-1);">2. Execute Scheduled Dispersals:</strong> Set up a bi-weekly or monthly salary dispersal (e.g., $3,500–$5,000/month) to your personal chequing account.</p>
            <p><strong style="color:var(--text-1);">3. Automate CRA Source Deductions:</strong> The payroll processor deducts and remits standard income tax withholdings and Canada Pension Plan (CPP) directly to the CRA via your CRA Payroll (RP) Account.</p>
            <div style="background:rgba(29,158,117,0.08);border:1px solid rgba(29,158,117,0.25);border-radius:var(--radius-sm);padding:10px;margin-top:10px;font-size:11px;color:var(--green-l);">
              <strong>The Strategic Result:</strong> Automated banking algorithms read your account as having stable, full-time corporate employment. You produce legitimate, tamper-proof T4 slips and computer-generated paystubs matching direct deposits on your bank statements, bypassing stated-income scrutiny for lines of credit (LOC) and mortgage pre-approvals.
            </div>
          </div>
        </div>

        <!-- MODULE 3 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-purple">Module 3</span> Sole Proprietorship vs. Corporate Tracks</div>
          
          <table class="tbl" style="margin-top:10px;">
            <thead>
              <tr>
                <th>Feature</th>
                <th>Track A: Sole Proprietorship</th>
                <th>Track B: Federal Corporation (Inc./Corp.)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="bold">Registration</td>
                <td>Ontario Business Registry ($60 Master Business Licence)</td>
                <td>Corporations Canada ($200 Federal + Extra-Provincial)</td>
              </tr>
              <tr>
                <td class="bold">Tax Document</td>
                <td>CRA Schedule T2125 attached to T1 Personal Return</td>
                <td>CRA T2 Corporate Return (separate legal entity)</td>
              </tr>
              <tr>
                <td class="bold">Income Proof</td>
                <td>Line 15000 (Total Income) / Line 13500 (Net Business)</td>
                <td>T4 Salary via Payroll or T5 Dividend Vouchers</td>
              </tr>
              <tr>
                <td class="bold">Liability</td>
                <td>Unlimited personal liability for all debts</td>
                <td>Limited corporate liability (unless personal guaranteed)</td>
              </tr>
              <tr>
                <td class="bold">Small Biz Tax</td>
                <td>Taxed at personal marginal tax bracket (up to 53.53%)</td>
                <td><span class="tag tag-green">12.2% combined tax rate (Ontario)</span> on first $500k active income</td>
              </tr>
              <tr>
                <td class="bold">Commercial Credit</td>
                <td>Tied 100% to personal SIN / credit report</td>
                <td>Separate D&B D-U-N-S & Equifax Commercial profiles</td>
              </tr>
              <tr>
                <td class="bold">Best Used For</td>
                <td>Fast track to $50k–$100k personal unsecured Big 6 LOCs</td>
                <td>Scaling to $250k–$1M+ in corporate facilities & programs</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- MODULE 4 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-cyan">Module 4</span> The Incorporated Enterprise & HoldCo/OpCo Structure</div>
          <p style="font-size:12px;color:var(--text-2);margin-bottom:12px;">Structuring for Asset Protection, Tax Optimization, and Stacking.</p>

          <div class="ascii-diagram">                         ┌──────────────────────────────────────────────┐
                         │              HOLDING COMPANY                 │
                         │          (Asset & Retained Earnings)         │
                         └──────────────────────┬──────────────────────┘
                                                │
                                                │ Inter-corporate Tax-Free Dividends
                                                │
                         ┌──────────────────────┴───────────────────────┐
                         ▼                                              ▼
          ┌──────────────────────────────┐               ┌──────────────────────────────┐
          │      OPERATING CORP A        │               │      OPERATING CORP B        │
          │    (Trading / E-Commerce)    │               │     (Service / Logistics)    │
          ├──────────────────────────────┤               ├──────────────────────────────┤
          │ • D&B Canada D-U-N-S         │               │ • D&B Canada D-U-N-S         │
          │ • Equifax Commercial Profile │               │ • Equifax Commercial Profile │
          │ • Net-30 Vendor Accounts     │               │ • Fleet Cards & Fintech LOCs │
          └──────────────────────────────┘               └──────────────────────────────┘</div>

          <div style="font-size:12px;color:var(--text-2);line-height:1.7;">
            <strong style="color:var(--text-1);">The Canadian Commercial Credit Stack:</strong>
            <ul style="margin-left:18px;margin-top:6px;">
              <li><strong>Uline Canada:</strong> Net-30 invoicing (reports commercial trade data).</li>
              <li><strong>Global Industrial Canada:</strong> Net-30 supplier accounts.</li>
              <li><strong>Esso/Mobil & Shell Fleet Cards:</strong> Fuel cards issued to the corporate entity.</li>
              <li><strong>Corporate Financial Identity:</strong> Register BN9 with Dun & Bradstreet Canada to generate D-U-N-S Number and establish a Paydex score.</li>
            </ul>
          </div>
        </div>

        <!-- MODULE 5 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-green">Module 5</span> Accessing Canadian Institutional & Crown Capital</div>
          
          <table class="tbl" style="margin-top:10px;">
            <thead>
              <tr>
                <th>Funding Source</th>
                <th>Facility Types</th>
                <th>Underwriting Focus & Criteria</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="bold">Big 6 Commercial<br><small style="color:var(--text-3);">(Tier 1 Banks)</small></td>
                <td>• RBC Royal LOC<br>• TD Visa Business<br>• BMO Small Biz LOC</td>
                <td>720+ Personal PG, 2 years corporate T2 filings, minimum $100k annual revenue.</td>
              </tr>
              <tr>
                <td class="bold">CSBFP<br><small style="color:var(--text-3);">(Federal Program)</small></td>
                <td>• Up to $1.15M Total<br>• $500k Equipment<br>• $150k Working Cap</td>
                <td>85% Government-backed loan through Big 6 banks. Requires qualifying assets and leaseholds.</td>
              </tr>
              <tr>
                <td class="bold">BDC<br><small style="color:var(--text-3);">(Crown Corporation)</small></td>
                <td>• Working Capital LOC<br>• Growth & Tech Loans<br>• Equipment Financing</td>
                <td>High emphasis on cash flow margins and market viability. Online micro-loans available for established revenues.</td>
              </tr>
              <tr>
                <td class="bold">Canadian Fintechs</td>
                <td>• Float Financial<br>• Loop / Vault<br>• Merchant Growth</td>
                <td>Automated underwriting based on real-time Canadian corporate bank feeds (Plaid/Flinks), tracking monthly sales.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- MODULE 6 -->
        <div class="card">
          <div class="card-title"><span class="tag tag-red">Module 6</span> Risk Management & The Canadian 25% Reserve Rule</div>
          <div style="font-size:12px;color:var(--text-2);line-height:1.7;">
            <p style="margin-bottom:10px;"><strong style="color:var(--red);">The Personal Guarantee (PG) Warning:</strong> In Canada, small business credit facilities almost universally require a Personal Guarantee. Under the Bankruptcy and Insolvency Act, defaulting on a personal guarantee permits creditors to seize personal non-exempt assets, attach bank accounts, and impact home equity.</p>
            <p><strong style="color:var(--green-l);">The 25% Liquidity Rule:</strong> When borrowing capital to fund or scale an enterprise, hold at least 25% of the total loan balance in a high-interest business savings account (HISA) at an independent credit union. This cash serves as an isolated buffer to service debt obligations if operating revenues experience delays.</p>
          </div>
        </div>

        <!-- CHECKLIST -->
        <div class="card" style="border-color:var(--cyan);background:rgba(62,198,208,0.04);">
          <div class="card-title" style="color:var(--cyan-l);font-size:13px;">Summary Blueprint Checklist</div>
          <div style="display:flex;flex-direction:column;gap:8px;font-size:12px;color:var(--text-1);margin-top:10px;">
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 1: Open Neo Financial Secured ($200) + Borrowell Rent Advantage ($8/mo).</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 2: Pay cards 3 days prior to statement close date (&lt;3% utilization).</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 3: Run hustle revenues through Sole-Prop (T2125) or Corp Payroll (ADP).</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 4: Split personal credit applications between Equifax (CIBC/TD) and TransUnion (RBC/BMO).</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 5: Incorporate federally via Corporations Canada; set up CRA BN/GST/RP accounts.</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 6: Establish Tier-1 Net-30 accounts (Uline, Esso Fleet) to initiate D&B file.</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 7: Apply for Big 6 Small Business lines + BDC / CSBFP expansion loans.</label>
            <label style="display:flex;gap:10px;align-items:center;cursor:pointer;"><input type="checkbox"> Step 8: Lock 25% of borrowed funds in reserve for debt-service protection.</label>
          </div>
        </div>

      </div>
"""

# 4. Inject CTC GEM section right after #panel-chat or before panel-overview
if 'id="panel-ctc-gem"' not in html:
    html = html.replace('<!-- OVERVIEW PANEL -->', ctc_gem_html + '\n      <!-- OVERVIEW PANEL -->')

# 5. Add CTC GEM widget right underneath the Chat Advisor widget inside logged-in student portal view
logged_in_gem_widget = """
          <!-- CTC GEM WIDGET DIRECTLY BELOW AI CHAT ADVISOR -->
          <div style="padding:16px 20px;background:rgba(9,16,26,0.95);border-top:1px solid var(--border-cyan);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
              <div class="ctc-gem-title">CTC GEM</div>
              <button class="btn btn-cyan" onclick="showPanel('ctc-gem')" style="font-size:11px;padding:4px 10px;">Open Full Blueprint ↗</button>
            </div>
            <div style="font-size:11px;color:var(--text-2);line-height:1.5;">
              <strong style="color:var(--cyan-l);">The Canadian Full Leveraging Blueprint:</strong> OSAP Float Rule · Statement Date Arbitrage (<3% Utilization) · ADP Payroll Rotation (T4 Proof of Income) · Dual-Bureau Stacking (Equifax vs TransUnion).
            </div>
          </div>
"""

if '<!-- CTC GEM WIDGET DIRECTLY BELOW AI CHAT ADVISOR -->' not in html:
    html = html.replace('</div>\n        </div>\n      </div>\n\n      <!-- OVERVIEW PANEL -->', logged_in_gem_widget + '</div>\n        </div>\n      </div>\n\n      <!-- OVERVIEW PANEL -->')

# 6. Update titles mapping in showPanel for 'ctc-gem'
old_show_panel_titles = "chat: ['Young Gen AI Advisor', 'Ask anything about credit, OSAP, scholarships, or funding'],"
new_show_panel_titles = "chat: ['Young Gen AI Advisor', 'Ask anything about credit, OSAP, scholarships, or funding'],\n    'ctc-gem': ['CTC GEM Blueprint', 'The Canadian Full Leveraging & Capital System'],"

if "'ctc-gem':" not in html:
    html = html.replace(old_show_panel_titles, new_show_panel_titles)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("CTC GEM blueprint injected into index.html cleanly!")
