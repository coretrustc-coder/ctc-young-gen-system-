// api/chat.js - Unified Dual-Engine Bridge (Google Antigravity/Gemini + Anthropic Claude)
// Deployed for Vercel / Node.js API endpoints

import { GoogleGenerativeAI } from '@google/generative-ai';
import { Anthropic } from '@anthropic-ai/sdk';
import { createClient } from '@supabase/supabase-js';

// 1. Initialize Clients
const googleAI = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY 
  ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY)
  : null;

const anthropic = process.env.ANTHROPIC_API_KEY 
  ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  : null;

const supabaseUrl = process.env.SUPABASE_URL || 'https://nhdmnyspqnabpwqiteuc.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZG1ueXNwcW5hYnB3cWl0ZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTI5OTQsImV4cCI6MjA5NDQ2ODk5NH0.-dHaLqHQ31MRyrVIvzxP2DnVbAn6vQ5XN1JrGNPHUYc';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// 2. Verified Link & Access Catalog
const LINK_CATALOG = {
  neo_secured: {
    name: "Neo Financial Secured Mastercard",
    category: "Secured Credit Builder",
    url: "https://www.neofinancial.com/products/credit-card",
    bonus: "$0 Annual Fee · $50 Min Deposit · Built-in Rent Reporting",
    tags: ["Equifax + TransUnion", "Fast Approval", "Students 18+"]
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
    url: "https://www.rogersbank.com/en/our_credit_cards",
    bonus: "3% Cash on USD Spend (FX Neutralizer)",
    tags: ["$0 Annual Fee", "Great for US/Online Shopping"]
  },
  eq_bank: {
    name: "EQ Bank Savings Plus Account",
    category: "High-Yield Savings (HYSA)",
    url: "https://www.eqbank.ca/personal-banking/features-rates",
    bonus: "High Interest · $0 Fees · Free Interac e-Transfers",
    tags: ["CDIC Insured", "All Canadian Residents"]
  },
  maxa_financial: {
    name: "MAXA Financial Digital Credit Union",
    category: "Credit Union HYSA",
    url: "https://www.maxafinancial.com",
    bonus: "Top-Tier Canadian Savings Rates",
    tags: ["100% Deposit Guarantee", "Open to All Canadians"]
  },
  meridian_cu: {
    name: "Meridian Credit Union (Ontario)",
    category: "Major Credit Union",
    url: "https://www.meridiancu.ca/personal/credit-cards",
    bonus: "Personal Lines of Credit & Student Banking",
    tags: ["Ontario's Largest CU", "Flexible Underwriting"]
  },
  osap_estimator: {
    name: "Official OSAP Aid Estimator Portal",
    category: "Government Aid Portal",
    url: "https://www.ontario.ca/page/osap-aid-estimator",
    bonus: "Calculate Grants (25%) vs Loans (75%)",
    tags: ["Official Ontario Portal", "2026 Policy Updated"]
  },
  loran_award: {
    name: "Loran Award ($100,000)",
    category: "Free Money Stack",
    url: "https://loranscholar.ca/becoming-a-scholar/",
    bonus: "$100,000 over 4 Years",
    tags: ["Academics + Leadership", "Apply Early"]
  },
  yconic_db: {
    name: "Yconic Scholarship Database",
    category: "Scholarship Finder",
    url: "https://yconic.com",
    bonus: "Search 1,000+ Canadian Student Awards",
    tags: ["Free Student Database", "Apply to 10+ Minimum"]
  }
};

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { messages, fileBase64, mimeType } = req.body;
  const lastUserMsg = messages[messages.length - 1]?.content || '';

  // 3. Supabase Auth & Profile Context Extraction
  let profileSummary = "Guest user (no profile loaded).";
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user } } = await supabase.auth.getUser(token);
    if (user) {
      const { data: prof } = await supabase.from('profiles').select('*').eq('id', user.id).single();
      if (prof) {
        profileSummary = `Student Profile: School=${prof.school || 'N/A'}, Program=${prof.program || 'N/A'}, Year=${prof.study_year || 'N/A'}, Tuition=$${prof.financials?.tuition || 0}, Rent=$${prof.financials?.rentMonthly || 0}, Credit Status=${prof.demographics?.credit || 'none'}.`;
      }
    }
  }

  const systemContext = `You are the CoreTrust Hybrid AI Advisor (Google Antigravity/Gemini + Anthropic Claude).
Context: ${profileSummary}

LINK DELIVERY INSTRUCTIONS:
Whenever recommending credit cards, banks, credit unions, OSAP, or scholarships, format links as markdown using the exact catalog key:
[KEY: Title](URL) (e.g. [neo_secured: Neo Financial Secured Card](https://www.neofinancial.com/products/credit-card)) so the client UI renders a Rich Smart Link Card.

Catalog Keys Available:
${JSON.stringify(LINK_CATALOG, null, 2)}

Provide clear, direct, and actionable advice for 18-25 year old Canadians. Educational guidance only.`;

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
