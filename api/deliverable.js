// api/deliverable.js - Generates branded PDF Funding Plan content for Vercel
import { Anthropic } from '@anthropic-ai/sdk';
import { createClient } from '@supabase/supabase-js';

const anthropic = process.env.ANTHROPIC_API_KEY ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }) : null;
const supabaseUrl = process.env.SUPABASE_URL || 'https://nhdmnyspqnabpwqiteuc.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZG1ueXNwcW5hYnB3cWl0ZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTI5OTQsImV4cCI6MjA5NDQ2ODk5NH0.-dHaLqHQ31MRyrVIvzxP2DnVbAn6vQ5XN1JrGNPHUYc';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Sign in required to generate a funding plan.' });

  const token = authHeader.replace('Bearer ', '');
  const { data: { user } } = await supabase.auth.getUser(token);
  if (!user) return res.status(401).json({ error: 'Invalid session.' });

  const { data: profile } = await supabase.from('profiles').select('*').eq('id', user.id).single();
  const profStr = JSON.stringify(profile || {});

  const prompt = `Generate a professional, structured Canadian Student Funding Plan for this student:
${profStr}

Include:
1. EXECUTIVE SUMMARY & FUNDING RATIO (2026 OSAP 25% grant / 75% loan split)
2. TAILORED BURSARY & SCHOLARSHIP STACK (with deadlines & eligibility)
3. 4-YEAR CREDIT BUILDING ROADMAP (Neo Secured -> Tangerine/Scotia -> Credit Union LOC)
4. HUSTLE REVENUE & T2125 TAX PROOF STRATEGY
5. 60-DAY IMMEDIATE ACTION CHECKLIST

Format clearly with headings and plain language.`;

  if (anthropic) {
    try {
      const resp = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1500,
        messages: [{ role: 'user', content: prompt }]
      });
      return res.status(200).json({ content: resp.content[0].text });
    } catch (e) {
      console.error('Claude deliverable error:', e);
    }
  }

  // Fallback if API key not set
  return res.status(200).json({
    content: `CORETRUST STUDENT FUNDING PLAN\nGenerated: ${new Date().toLocaleDateString('en-CA')}\n\n1. OSAP & AID STACK:\n- Apply for Ontario Student Assistance Program (25% Grant / 75% Loan Split)\n- Check school Financial Aid Office for internal bursaries (Oct/Nov deadline)\n\n2. CREDIT FOUNDATION:\n- Open Neo Financial Secured Card ($50 deposit)\n- Activate KOHO Credit Building ($7/mo)\n- Statement Date Trick: Pay balance 3 days before statement close for <10% utilization\n\n3. SCHOLARSHIP STACK:\n- Apply to minimum 10 awards on Yconic.com & ScholarTree.ca\n- Loran Award & Schulich Leaders for high school / pre-start students.`
  });
}
