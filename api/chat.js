// api/chat.js - Master Dual-Engine Bridge (Google Antigravity/Gemini + Anthropic Claude)
// Fully Integrated Master Catalog: Banks, Credit Unions, Schools, OSAP & Scholarships

import { GoogleGenerativeAI } from '@google/generative-ai';
import { Anthropic } from '@anthropic-ai/sdk';
import { createClient } from '@supabase/supabase-js';

// 1. Initialize API Clients
const googleAI = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY 
  ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY)
  : null;

const anthropic = process.env.ANTHROPIC_API_KEY 
  ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  : null;

const supabaseUrl = process.env.SUPABASE_URL || 'https://nhdmnyspqnabpwqiteuc.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZG1ueXNwcW5hYnB3cWl0ZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTI5OTQsImV4cCI6MjA5NDQ2ODk5NH0.-dHaLqHQ31MRyrVIvzxP2DnVbAn6vQ5XN1JrGNPHUYc';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// 2. Comprehensive School Financial Aid & SAG Catalog
const SCHOOL_CATALOG = {
  "utoronto": {
    name: "University of Toronto (U of T)",
    aidUrl: "https://future.utoronto.ca/finances/financial-aid/",
    utapsUrl: "https://registrar.utoronto.ca/finances-and-funding/utaps/",
    sagUrl: "https://future.utoronto.ca/finances/financial-aid/university-of-toronto-financial-aid-utaps/",
    bursariesUrl: "https://registrar.utoronto.ca/finances-and-funding/awards-and-financial-aid/"
  },
  "yorku": {
    name: "York University",
    aidUrl: "https://sfs.yorku.ca/financialaid",
    sagUrl: "https://sfs.yorku.ca/financialaid",
    bursariesUrl: "https://sfs.yorku.ca/scholarships"
  },
  "uwaterloo": {
    name: "University of Waterloo",
    aidUrl: "https://uwaterloo.ca/undergraduate-entrance-awards/",
    bursariesUrl: "https://uwaterloo.ca/future-students/financing/scholarships"
  },
  "mcmaster": {
    name: "McMaster University",
    aidUrl: "https://registrar.mcmaster.ca/financial-aid/",
    bursariesUrl: "https://registrar.mcmaster.ca/award-by-application/"
  },
  "western": {
    name: "Western University",
    aidUrl: "https://www.registrar.uwo.ca/student_finances/index.html",
    bursariesUrl: "https://www.registrar.uwo.ca/student_finances/work_study.html"
  },
  "tmu": {
    name: "Toronto Metropolitan University (Ryerson)",
    aidUrl: "https://www.torontomu.ca/current-students/financial-aid/",
    bursariesUrl: "https://www.torontomu.ca/awards/"
  },
  "queens": {
    name: "Queen's University",
    aidUrl: "https://www.queensu.ca/registrar/financial-aid",
    bursariesUrl: "https://www.queensu.ca/registrar/financial-aid/bursaries"
  },
  "uottawa": {
    name: "University of Ottawa",
    aidUrl: "https://www.uottawa.ca/study/fees-financial-support/bursaries-scholarships"
  },
  "carleton": {
    name: "Carleton University",
    aidUrl: "https://carleton.ca/awards/"
  },
  "guelph": {
    name: "University of Guelph",
    aidUrl: "https://www.uoguelph.ca/registrar/financialservices/"
  },
  "wlu": {
    name: "Wilfrid Laurier University",
    aidUrl: "https://www.wlu.ca/tuition-and-financial-aid/index.html"
  },
  "humber": {
    name: "Humber College",
    aidUrl: "https://humber.ca/admissions/financial-aid.html"
  },
  "seneca": {
    name: "Seneca Polytechnic",
    aidUrl: "https://www.senecapolytechnic.ca/register/financialaid.html"
  },
  "georgebrown": {
    name: "George Brown College",
    aidUrl: "https://www.georgebrown.ca/financial-aid"
  },
  "sheridan": {
    name: "Sheridan College",
    aidUrl: "https://www.sheridancollege.ca/admissions/financial-aid"
  },
  "centennial": {
    name: "Centennial College",
    aidUrl: "https://www.centennialcollege.ca/admissions/financial-aid"
  },
  "algonquin": {
    name: "Algonquin College",
    aidUrl: "https://www.algonquincollege.com/financial-aid/"
  }
};

// 3. Master Verified Financial Institution & Portal Catalog
const LINK_CATALOG = {
  // Secud & Starter Credit Cards
  neo_secured: {
    name: "Neo Financial Secured Mastercard",
    category: "Secured Credit Builder",
    url: "https://www.neofinancial.com/credit",
    bonus: "$0 Annual Fee · $50 Min Deposit · Built-in Rent Reporting",
    tags: ["Equifax + TransUnion", "Fast Approval", "Students 18+"]
  },
  tangerine_mc: {
    name: "Tangerine Money-Back Mastercard",
    category: "No-Fee Cashback Card",
    url: "https://www.tangerine.ca/en/products/spending/creditcard/money-back-credit-card",
    bonus: "2% Cashback in 2-3 Categories You Pick",
    tags: ["No Annual Fee", "Scotiabank Affiliate"]
  },
  rogers_bank: {
    name: "Rogers Mastercard",
    category: "No-FX Cashback Card",
    url: "https://www.rogersbank.com/en/our_credit_cards/rogers_mastercard",
    bonus: "3% Cash on USD Spend (FX Neutralizer)",
    tags: ["$0 Annual Fee", "Great for US/Online Shopping"]
  },
  scotia_scene: {
    name: "Scotiabank Scene+ Visa Card",
    category: "Student Rewards Card",
    url: "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scene-card.html",
    bonus: "2x Scene+ Points on Groceries, Dining & Movies",
    tags: ["$0 Annual Fee", "Student Friendly"]
  },
  pc_financial: {
    name: "PC Financial Mastercard",
    category: "Grocery Rewards",
    url: "https://www.pcfinancial.ca/en/credit-cards/",
    bonus: "PC Optimum Points at Loblaws, No Frills & Shoppers",
    tags: ["$0 Annual Fee", "Everyday Rewards"]
  },
  wealthsimple_cash: {
    name: "Wealthsimple Cash Account & Credit Card",
    category: "No-Fee HYSA & Credit",
    url: "https://www.wealthsimple.com/en-ca/product/cash",
    bonus: "High Interest · 1% Cashback · NO Foreign FX Fee",
    tags: ["$0 Fees", "Travel Friendly"]
  },
  koho_credit: {
    name: "KOHO Credit Building",
    category: "Credit Builder",
    url: "https://www.koho.ca/credit-building/",
    bonus: "$7/month Autopay Tradeline",
    tags: ["Reports to Equifax", "Rebuilding Starter"]
  },
  borrowell_rent: {
    name: "Borrowell Rent Advantage",
    category: "Rent Reporting",
    url: "https://www.borrowell.com/rent-advantage",
    bonus: "$8/month · Reports Rent to Equifax",
    tags: ["Equifax Tradeline", "No Landlord Required"]
  },

  // Big 6 Canadian Banks (Student Portals & Accounts)
  rbc_student: {
    name: "RBC Student Banking Advantage",
    category: "Big 6 Student Bank",
    url: "https://www.rbcroyalbank.com/accounts/student-banking.html",
    bonus: "$0 Monthly Fee · Free Interac Transfers",
    tags: ["Big 6 Bank", "Student Package"]
  },
  td_student: {
    name: "TD Student Chequing Account",
    category: "Big 6 Student Bank",
    url: "https://www.td.com/ca/en/personal-banking/products/bank-accounts/chequing-accounts/student-chequing-account",
    bonus: "$0 Monthly Fee · Unlimited Transactions",
    tags: ["Big 6 Bank", "Student Package"]
  },
  bmo_student: {
    name: "BMO Student Banking Package",
    category: "Big 6 Student Bank",
    url: "https://www.bmo.com/main/personal/bank-accounts/student-banking/",
    bonus: "$0 Monthly Fee · SPC Discount Card Included",
    tags: ["Big 6 Bank", "Student Package"]
  },
  cibc_student: {
    name: "CIBC Smart for Students",
    category: "Big 6 Student Bank",
    url: "https://www.cibc.com/en/personal-banking/bank-accounts/chequing-accounts/smart-for-students.html",
    bonus: "$0 Monthly Fee · Free SPC+ Membership",
    tags: ["Big 6 Bank", "Student Package"]
  },
  scotia_student: {
    name: "Scotiabank Student Banking",
    category: "Big 6 Student Bank",
    url: "https://www.scotiabank.com/ca/en/personal/bank-accounts/students.html",
    bonus: "$0 Monthly Fee · Earn Scene+ Points on Banking",
    tags: ["Big 6 Bank", "Student Package"]
  },

  // Credit Unions (Ontario, BC & National Digital)
  meridian_cu: {
    name: "Meridian Credit Union (Ontario)",
    category: "Ontario Credit Union",
    url: "https://www.meridiancu.ca/personal/accounts/chequing-accounts/student-chequing-account",
    bonus: "Student Accounts & Flexible Lines of Credit",
    tags: ["Ontario's Largest CU", "Flexible Loans"]
  },
  vancity_cu: {
    name: "Vancity Credit Union (BC)",
    category: "BC Credit Union",
    url: "https://www.vancity.com/Bank/Accounts/ChequingAccounts/",
    bonus: "Youth & Student Chequing + enviro Visa",
    tags: ["BC Credit Union", "Community Focused"]
  },
  duca_cu: {
    name: "DUCA Financial Credit Union (Ontario)",
    category: "Ontario Credit Union",
    url: "https://www.duca.com/personal/accounts/chequing-accounts/",
    bonus: "High-Interest Savings & Student Loans",
    tags: ["Fair Banking", "Ontario CU"]
  },
  firstontario_cu: {
    name: "FirstOntario Credit Union",
    category: "Ontario Credit Union",
    url: "https://www.firstontariocu.com/personal/bank/chequing-accounts",
    bonus: "No-Fee Student Banking & Personal Lines of Credit",
    tags: ["Ontario CU", "Member Owned"]
  },
  desjardins_cu: {
    name: "Desjardins Student Banking",
    category: "Ontario & Quebec Credit Union",
    url: "https://www.desjardins.com/ca/personal/accounts-services/chequing-accounts/students/index.jsp",
    bonus: "Student Chequing + Cashback Mastercard",
    tags: ["Desjardins Network", "ON/QC Access"]
  },
  maxa_financial: {
    name: "MAXA Financial Digital Credit Union",
    category: "Digital Credit Union HYSA",
    url: "https://www.maxafinancial.com/Savings/HighInterestSavings/",
    bonus: "Top-Tier Canadian High-Yield Savings Rates",
    tags: ["100% Deposit Guarantee", "Open to All Canadians"]
  },
  achieva_financial: {
    name: "Achieva Financial Digital Credit Union",
    category: "Digital Credit Union HYSA",
    url: "https://www.achieva.mb.ca/Savings",
    bonus: "High-Interest Savings & Automated Growth",
    tags: ["100% Deposit Guarantee", "Open to All Canadians"]
  },
  eq_bank: {
    name: "EQ Bank Personal Savings Plus",
    category: "High-Yield Savings (HYSA)",
    url: "https://www.eqbank.ca/personal-banking/features-rates",
    bonus: "High Interest · $0 Fees · Free Interac e-Transfers",
    tags: ["CDIC Insured", "All Canadian Residents"]
  },

  // Government & Financial Aid Portals
  osap_estimator: {
    name: "Official OSAP Aid Estimator Portal",
    category: "Government Aid Portal",
    url: "https://www.ontario.ca/page/osap-aid-estimator",
    bonus: "Calculate OSAP Grants (25%) vs Loans (75%)",
    tags: ["Official Ontario Portal", "2026 Policy Updated"]
  },
  nslsc_portal: {
    name: "NSLSC Student Loan Repayment Portal",
    category: "Student Loan Repayment",
    url: "https://www.nslsc.ca/en/home",
    bonus: "Manage Repayment & Repayment Assistance Plan (RAP)",
    tags: ["Official Federal Portal", "NSLSC Account"]
  },
  canada_grant: {
    name: "Canada Student Grants Portal",
    category: "Federal Aid",
    url: "https://www.canada.ca/en/employment-social-development/services/student-financial-aid/student-loan/grants/canada-student-grant.html",
    bonus: "Non-Repayable Federal Student Grants",
    tags: ["Federal Government", "Auto via OSAP"]
  },

  // Free Money Stack (Scholarships & Bursaries)
  loran_award: {
    name: "Loran Award ($100,000)",
    category: "Free Money Stack",
    url: "https://loranscholar.ca/becoming-a-scholar/",
    bonus: "$100,000 over 4 Years for Leadership & Academics",
    tags: ["Scholarship", "High School / Pre-Start"]
  },
  schulich_leaders: {
    name: "Schulich Leader Scholarships ($100,000+)",
    category: "STEM Scholarship",
    url: "https://schulichleaders.com",
    bonus: "$100,000 - $120,000 for STEM Undergraduate Degrees",
    tags: ["STEM Fields", "Top Academics"]
  },
  td_scholarship: {
    name: "TD Scholarships for Community Leadership",
    category: "Community Award",
    url: "https://www.td.com/ca/en/personal-banking/products/saving-investing/scholarships-bursaries-grants",
    bonus: "Up to $70,000 in Tuition + Living Support",
    tags: ["Leadership", "Community Focus"]
  },
  rbc_future_launch: {
    name: "RBC Future Launch Scholarships",
    category: "Youth Scholarship",
    url: "https://www.rbc.com/dpp/futurelaunch/scholarships.html",
    bonus: "Flexible Student & Youth Grants",
    tags: ["RBC Foundation", "Youth Funding"]
  },
  indspire_awards: {
    name: "Indspire Building Brighter Futures",
    category: "Indigenous Funding",
    url: "https://indspire.ca/programs/students/building-brighter-futures/",
    bonus: "Bursaries & Scholarships for First Nations, Inuit & Métis",
    tags: ["Indigenous Students", "Up to $7,000/yr"]
  },
  yconic_db: {
    name: "Yconic Canadian Scholarship Finder",
    category: "Scholarship Database",
    url: "https://yconic.com",
    bonus: "Search 1,000+ Verified Canadian Bursaries",
    tags: ["Free Database", "Apply to 10+ Minimum"]
  },
  scholartree_db: {
    name: "ScholarTree Canadian Scholarships",
    category: "Scholarship Database",
    url: "https://scholartree.ca",
    bonus: "Matched Canadian Student Bursaries & Awards",
    tags: ["Free Database", "Filter by Major"]
  }
};

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { messages, fileBase64, mimeType } = req.body;
  const lastUserMsg = messages[messages.length - 1]?.content || '';

  // 4. Extract Supabase User Profile Context
  let profileSummary = "Guest user (no profile saved).";
  let matchedSchoolObj = null;
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user } } = await supabase.auth.getUser(token);
    if (user) {
      const { data: prof } = await supabase.from('profiles').select('*').eq('id', user.id).single();
      if (prof) {
        profileSummary = `Student Profile: School=${prof.school || 'N/A'}, Program=${prof.program || 'N/A'}, Year=${prof.study_year || 'N/A'}, Tuition=$${prof.financials?.tuition || 0}, Rent=$${prof.financials?.rentMonthly || 0}, Credit Status=${prof.demographics?.credit || 'none'}.`;
        
        // Match school key in SCHOOL_CATALOG
        const schoolLower = (prof.school || '').toLowerCase();
        for (const [sKey, sObj] of Object.entries(SCHOOL_CATALOG)) {
          if (schoolLower.includes(sKey) || schoolLower.includes(sObj.name.toLowerCase())) {
            matchedSchoolObj = sObj;
            break;
          }
        }
      }
    }
  }

  let schoolContextString = "";
  if (matchedSchoolObj) {
    schoolContextString = `\nSTUDENT'S MATCHED SCHOOL PORTALS:
- Official Financial Aid: ${matchedSchoolObj.aidUrl}
- Bursaries & Scholarships: ${matchedSchoolObj.bursariesUrl || matchedSchoolObj.aidUrl}
${matchedSchoolObj.sagUrl ? `- Student Access Guarantee (SAG): ${matchedSchoolObj.sagUrl}` : ''}`;
  }

  const systemContext = `You are the CoreTrust Hybrid AI Advisor (Google Antigravity/Gemini + Anthropic Claude).
Context: ${profileSummary}${schoolContextString}

LINK DELIVERY DIRECTIVE:
Whenever recommending credit cards, Big 6 banks, credit unions, OSAP, or scholarships, format links using catalog keys in markdown:
[KEY: Title](URL) (e.g. [neo_secured: Neo Financial Secured Card](https://www.neofinancial.com/credit) or [rbc_student: RBC Student Banking](https://www.rbcroyalbank.com/accounts/student-banking.html)).

AVAILABLE CATALOG KEYS:
${JSON.stringify(LINK_CATALOG, null, 2)}

Always give clear, direct, actionable advice for 18-25 year old Canadians. Educational guidance only.`;

  // -------------------------------------------------------------
  // TASK ROUTER
  // -------------------------------------------------------------

  // Route A: Document OCR / Multimodal Image -> Google Gemini
  if (fileBase64 && mimeType && googleAI) {
    try {
      const model = googleAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
      const result = await model.generateContent([
        "Parse this financial document (OSAP notice, tuition statement, or bill). Extract total tuition, grants, loans, and due dates.",
        { inlineData: { data: fileBase64, mimeType } }
      ]);
      return res.status(200).json({ engine: 'Google-Gemini-Vision', reply: result.response.text() });
    } catch (e) {
      console.error('Gemini Vision error:', e);
    }
  }

  // Route B: Legal Disputes / Compliance -> Anthropic Claude
  const isLegal = /dispute|letter|equifax|transunion|consumer reporting act|compliance/i.test(lastUserMsg);

  if (isLegal && anthropic) {
    try {
      const resp = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1500,
        system: systemContext,
        messages: messages.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
      });
      return res.status(200).json({ engine: 'Anthropic-Claude-Legal', reply: resp.content[0].text });
    } catch (e) {
      console.error('Claude API error:', e);
    }
  }

  // Route C: General Chat & Fast Advisor -> Google Gemini (with Fallback to Claude)
  if (googleAI) {
    try {
      const model = googleAI.getGenerativeModel({ model: 'gemini-1.5-flash', systemInstruction: systemContext });
      const chat = model.startChat({});
      const result = await chat.sendMessage(lastUserMsg);
      return res.status(200).json({ engine: 'Google-Gemini-Flash', reply: result.response.text() });
    } catch (e) {
      console.error('Gemini Chat error:', e);
    }
  }

  if (anthropic) {
    try {
      const resp = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1200,
        system: systemContext,
        messages: messages.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
      });
      return res.status(200).json({ engine: 'Anthropic-Claude', reply: resp.content[0].text });
    } catch (e) {
      console.error('Claude API error:', e);
    }
  }

  // Fallback if no API key is present:
  return res.status(200).json({
    engine: 'CoreTrust-Fallback-Engine',
    reply: `Here are the verified financial and aid portals for Canadian students:\n` +
      Object.values(LINK_CATALOG).map(item => `• [${item.name}](${item.url}) — ${item.bonus}`).join('\n')
  });
}
