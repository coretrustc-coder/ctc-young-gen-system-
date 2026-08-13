import re

LINK_CATALOG = {
    "neo_secured": {
        "name": "Neo Financial Secured Mastercard",
        "category": "Secured Credit Builder",
        "url": "https://www.neofinancial.com/credit",
        "bonus": "$0 Annual Fee · $50 Min Deposit · Built-in Rent Reporting",
        "tags": ["Equifax + TransUnion", "Fast Approval", "Students 18+"]
    },
    "tangerine_mc": {
        "name": "Tangerine Money-Back Mastercard",
        "category": "No-Fee Cashback Card",
        "url": "https://www.tangerine.ca/en/products/spending/creditcard/money-back-credit-card",
        "bonus": "2% Cashback in 2-3 Categories You Pick",
        "tags": ["No Annual Fee", "Scotiabank Affiliate"]
    },
    "rogers_bank": {
        "name": "Rogers Mastercard",
        "category": "No-FX Cashback Card",
        "url": "https://www.rogersbank.com/en/our_credit_cards/rogers_mastercard",
        "bonus": "3% Cash on USD Spend (FX Neutralizer)",
        "tags": ["$0 Annual Fee", "Great for US/Online Shopping"]
    },
    "scotia_scene": {
        "name": "Scotiabank Scene+ Visa Card",
        "category": "Student Rewards Card",
        "url": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scene-card.html",
        "bonus": "2x Scene+ Points on Groceries, Dining & Movies",
        "tags": ["$0 Annual Fee", "Student Friendly"]
    },
    "pc_financial": {
        "name": "PC Financial Mastercard",
        "category": "Grocery Rewards",
        "url": "https://www.pcfinancial.ca/en/credit-cards/",
        "bonus": "PC Optimum Points at Loblaws, No Frills & Shoppers",
        "tags": ["$0 Annual Fee", "Everyday Rewards"]
    },
    "wealthsimple_cash": {
        "name": "Wealthsimple Cash Account & Credit Card",
        "category": "No-Fee HYSA & Credit",
        "url": "https://www.wealthsimple.com/en-ca/product/cash",
        "bonus": "High Interest · 1% Cashback · NO Foreign FX Fee",
        "tags": ["$0 Fees", "Travel Friendly"]
    },
    "koho_credit": {
        "name": "KOHO Credit Building",
        "category": "Credit Builder",
        "url": "https://www.koho.ca/credit-building/",
        "bonus": "$7/month Autopay Tradeline",
        "tags": ["Reports to Equifax", "Rebuilding Starter"]
    },
    "borrowell_rent": {
        "name": "Borrowell Rent Advantage",
        "category": "Rent Reporting",
        "url": "https://www.borrowell.com/rent-advantage",
        "bonus": "$8/month · Reports Rent to Equifax",
        "tags": ["Equifax Tradeline", "No Landlord Required"]
    },
    "rbc_student": {
        "name": "RBC Student Banking Advantage",
        "category": "Big 6 Student Bank",
        "url": "https://www.rbcroyalbank.com/accounts/student-banking.html",
        "bonus": "$0 Monthly Fee · Free Interac Transfers",
        "tags": ["Big 6 Bank", "Student Package"]
    },
    "td_student": {
        "name": "TD Student Chequing Account",
        "category": "Big 6 Student Bank",
        "url": "https://www.td.com/ca/en/personal-banking/products/bank-accounts/chequing-accounts/student-chequing-account",
        "bonus": "$0 Monthly Fee · Unlimited Transactions",
        "tags": ["Big 6 Bank", "Student Package"]
    },
    "bmo_student": {
        "name": "BMO Student Banking Package",
        "category": "Big 6 Student Bank",
        "url": "https://www.bmo.com/main/personal/bank-accounts/student-banking/",
        "bonus": "$0 Monthly Fee · SPC Discount Card Included",
        "tags": ["Big 6 Bank", "Student Package"]
    },
    "cibc_student": {
        "name": "CIBC Smart for Students",
        "category": "Big 6 Student Bank",
        "url": "https://www.cibc.com/en/personal-banking/bank-accounts/chequing-accounts/smart-for-students.html",
        "bonus": "$0 Monthly Fee · Free SPC+ Membership",
        "tags": ["Big 6 Bank", "Student Package"]
    },
    "scotia_student": {
        "name": "Scotiabank Student Banking",
        "category": "Big 6 Student Bank",
        "url": "https://www.scotiabank.com/ca/en/personal/bank-accounts/students.html",
        "bonus": "$0 Monthly Fee · Earn Scene+ Points on Banking",
        "tags": ["Big 6 Bank", "Student Package"]
    },
    "meridian_cu": {
        "name": "Meridian Credit Union (Ontario)",
        "category": "Ontario Credit Union",
        "url": "https://www.meridiancu.ca/personal/accounts/chequing-accounts/student-chequing-account",
        "bonus": "Student Accounts & Flexible Lines of Credit",
        "tags": ["Ontario's Largest CU", "Flexible Loans"]
    },
    "vancity_cu": {
        "name": "Vancity Credit Union (BC)",
        "category": "BC Credit Union",
        "url": "https://www.vancity.com/Bank/Accounts/ChequingAccounts/",
        "bonus": "Youth & Student Chequing + enviro Visa",
        "tags": ["BC Credit Union", "Community Focused"]
    },
    "duca_cu": {
        "name": "DUCA Financial Credit Union (Ontario)",
        "category": "Ontario Credit Union",
        "url": "https://www.duca.com/personal/accounts/chequing-accounts/",
        "bonus": "High-Interest Savings & Student Loans",
        "tags": ["Fair Banking", "Ontario CU"]
    },
    "firstontario_cu": {
        "name": "FirstOntario Credit Union",
        "category": "Ontario Credit Union",
        "url": "https://www.firstontariocu.com/personal/bank/chequing-accounts",
        "bonus": "No-Fee Student Banking & Personal Lines of Credit",
        "tags": ["Ontario CU", "Member Owned"]
    },
    "desjardins_cu": {
        "name": "Desjardins Student Banking",
        "category": "Ontario & Quebec Credit Union",
        "url": "https://www.desjardins.com/ca/personal/accounts-services/chequing-accounts/students/index.jsp",
        "bonus": "Student Chequing + Cashback Mastercard",
        "tags": ["Desjardins Network", "ON/QC Access"]
    },
    "maxa_financial": {
        "name": "MAXA Financial Digital Credit Union",
        "category": "Digital Credit Union HYSA",
        "url": "https://www.maxafinancial.com/Savings/HighInterestSavings/",
        "bonus": "Top-Tier Canadian High-Yield Savings Rates",
        "tags": ["100% Deposit Guarantee", "Open to All Canadians"]
    },
    "achieva_financial": {
        "name": "Achieva Financial Digital Credit Union",
        "category": "Digital Credit Union HYSA",
        "url": "https://www.achieva.mb.ca/Savings",
        "bonus": "High-Interest Savings & Automated Growth",
        "tags": ["100% Deposit Guarantee", "Open to All Canadians"]
    },
    "eq_bank": {
        "name": "EQ Bank Personal Savings Plus",
        "category": "High-Yield Savings (HYSA)",
        "url": "https://www.eqbank.ca/personal-banking/features-rates",
        "bonus": "High Interest · $0 Fees · Free Interac e-Transfers",
        "tags": ["CDIC Insured", "All Canadian Residents"]
    },
    "osap_estimator": {
        "name": "Official OSAP Aid Estimator Portal",
        "category": "Government Aid Portal",
        "url": "https://www.ontario.ca/page/osap-aid-estimator",
        "bonus": "Calculate OSAP Grants (25%) vs Loans (75%)",
        "tags": ["Official Ontario Portal", "2026 Policy Updated"]
    },
    "nslsc_portal": {
        "name": "NSLSC Student Loan Repayment Portal",
        "category": "Student Loan Repayment",
        "url": "https://www.nslsc.ca/en/home",
        "bonus": "Manage Repayment & Repayment Assistance Plan (RAP)",
        "tags": ["Official Federal Portal", "NSLSC Account"]
    },
    "canada_grant": {
        "name": "Canada Student Grants Portal",
        "category": "Federal Aid",
        "url": "https://www.canada.ca/en/employment-social-development/services/student-financial-aid/student-loan/grants/canada-student-grant.html",
        "bonus": "Non-Repayable Federal Student Grants",
        "tags": ["Federal Government", "Auto via OSAP"]
    },
    "loran_award": {
        "name": "Loran Award ($100,000)",
        "category": "Free Money Stack",
        "url": "https://loranscholar.ca/becoming-a-scholar/",
        "bonus": "$100,000 over 4 Years for Leadership & Academics",
        "tags": ["Scholarship", "High School / Pre-Start"]
    },
    "schulich_leaders": {
        "name": "Schulich Leader Scholarships ($100,000+)",
        "category": "STEM Scholarship",
        "url": "https://schulichleaders.com",
        "bonus": "$100,000 - $120,000 for STEM Undergraduate Degrees",
        "tags": ["STEM Fields", "Top Academics"]
    },
    "td_scholarship": {
        "name": "TD Scholarships for Community Leadership",
        "category": "Community Award",
        "url": "https://www.td.com/ca/en/personal-banking/products/saving-investing/scholarships-bursaries-grants",
        "bonus": "Up to $70,000 in Tuition + Living Support",
        "tags": ["Leadership", "Community Focus"]
    },
    "rbc_future_launch": {
        "name": "RBC Future Launch Scholarships",
        "category": "Youth Scholarship",
        "url": "https://www.rbc.com/dpp/futurelaunch/scholarships.html",
        "bonus": "Flexible Student & Youth Grants",
        "tags": ["RBC Foundation", "Youth Funding"]
    },
    "indspire_awards": {
        "name": "Indspire Building Brighter Futures",
        "category": "Indigenous Funding",
        "url": "https://indspire.ca/programs/students/building-brighter-futures/",
        "bonus": "Bursaries & Scholarships for First Nations, Inuit & Métis",
        "tags": ["Indigenous Students", "Up to $7,000/yr"]
    },
    "yconic_db": {
        "name": "Yconic Canadian Scholarship Finder",
        "category": "Scholarship Database",
        "url": "https://yconic.com",
        "bonus": "Search 1,000+ Verified Canadian Bursaries",
        "tags": ["Free Database", "Apply to 10+ Minimum"]
    },
    "scholartree_db": {
        "name": "ScholarTree Canadian Scholarships",
        "category": "Scholarship Database",
        "url": "https://scholartree.ca",
        "bonus": "Matched Canadian Student Bursaries & Awards",
        "tags": ["Free Database", "Filter by Major"]
    }
}

SCHOOL_CATALOG = {
    "utoronto": { "name": "University of Toronto (U of T)", "aidUrl": "https://future.utoronto.ca/finances/financial-aid/", "bursariesUrl": "https://registrar.utoronto.ca/finances-and-funding/awards-and-financial-aid/", "sagUrl": "https://future.utoronto.ca/finances/financial-aid/university-of-toronto-financial-aid-utaps/" },
    "york": { "name": "York University", "aidUrl": "https://sfs.yorku.ca/financialaid", "bursariesUrl": "https://sfs.yorku.ca/scholarships", "sagUrl": "https://sfs.yorku.ca/financialaid" },
    "waterloo": { "name": "University of Waterloo", "aidUrl": "https://uwaterloo.ca/undergraduate-entrance-awards/", "bursariesUrl": "https://uwaterloo.ca/future-students/financing/scholarships" },
    "mcmaster": { "name": "McMaster University", "aidUrl": "https://registrar.mcmaster.ca/financial-aid/", "bursariesUrl": "https://registrar.mcmaster.ca/award-by-application/" },
    "western": { "name": "Western University", "aidUrl": "https://www.registrar.uwo.ca/student_finances/index.html", "bursariesUrl": "https://www.registrar.uwo.ca/student_finances/work_study.html" },
    "tmu": { "name": "Toronto Metropolitan University (Ryerson)", "aidUrl": "https://www.torontomu.ca/current-students/financial-aid/", "bursariesUrl": "https://www.torontomu.ca/awards/" },
    "queens": { "name": "Queen's University", "aidUrl": "https://www.queensu.ca/registrar/financial-aid", "bursariesUrl": "https://www.queensu.ca/registrar/financial-aid/bursaries" },
    "uottawa": { "name": "University of Ottawa", "aidUrl": "https://www.uottawa.ca/study/fees-financial-support/bursaries-scholarships" },
    "carleton": { "name": "Carleton University", "aidUrl": "https://carleton.ca/awards/" },
    "guelph": { "name": "University of Guelph", "aidUrl": "https://www.uoguelph.ca/registrar/financialservices/" },
    "laurier": { "name": "Wilfrid Laurier University", "aidUrl": "https://www.wlu.ca/tuition-and-financial-aid/index.html" },
    "humber": { "name": "Humber College", "aidUrl": "https://humber.ca/admissions/financial-aid.html" },
    "seneca": { "name": "Seneca Polytechnic", "aidUrl": "https://www.senecapolytechnic.ca/register/financialaid.html" },
    "george brown": { "name": "George Brown College", "aidUrl": "https://www.georgebrown.ca/financial-aid" },
    "sheridan": { "name": "Sheridan College", "aidUrl": "https://www.sheridancollege.ca/admissions/financial-aid" },
    "centennial": { "name": "Centennial College", "aidUrl": "https://www.centennialcollege.ca/admissions/financial-aid" },
    "algonquin": { "name": "Algonquin College", "aidUrl": "https://www.algonquincollege.com/financial-aid/" }
}

with open('ctc_advisor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith('LINK_CATALOG ='):
        skip = True
        new_lines.append(f"LINK_CATALOG = {repr(LINK_CATALOG)}\n\nSCHOOL_CATALOG = {repr(SCHOOL_CATALOG)}\n\n")
    elif line.startswith('# Persistent Advisor Memory') or line.startswith('# ---'):
        skip = False
    if not skip:
        new_lines.append(line)

with open('ctc_advisor.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("ctc_advisor.py cleanly updated with Python dictionary syntax!")
