// api/audit.js - "What am I missing?" Funding Audit Endpoint for Vercel
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'https://nhdmnyspqnabpwqiteuc.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZG1ueXNwcW5hYnB3cWl0ZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTI5OTQsImV4cCI6MjA5NDQ2ODk5NH0.-dHaLqHQ31MRyrVIvzxP2DnVbAn6vQ5XN1JrGNPHUYc';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

const SCHOLARSHIP_MASTER_LIST = [
  { name: "Canada Student Grant (Full-Time)", amount: "Up to $3,000/yr", deadline: "Auto via OSAP", tag: "Federal" },
  { name: "OSOG Ontario Student Grant", amount: "Varies", deadline: "Auto via OSAP", tag: "Provincial" },
  { name: "Loran Award", amount: "$100,000 over 4 yrs", deadline: "October 15", tag: "National" },
  { name: "Schulich Leader Scholarships", amount: "$100,000 - $120,000", deadline: "January 30", tag: "STEM" },
  { name: "TD Scholarships for Community Leadership", amount: "Up to $70,000", deadline: "November 15", tag: "Leadership" },
  { name: "RBC Future Launch Scholarship", amount: "$1,500", deadline: "Rolling quarterly", tag: "Youth" },
  { name: "Indspire Building Brighter Futures", amount: "Up to $7,000/yr", deadline: "Feb 1 / Aug 1 / Nov 1", tag: "Indigenous" },
  { name: "Black Excellence Unifor Scholarship", amount: "$2,000", deadline: "June 30", tag: "Diversity" },
  { name: "BSWD Disability Grant", amount: "Up to $2,000/yr", deadline: "School Financial Aid", tag: "Accessibility" }
];

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Sign in required.' });

  const token = authHeader.replace('Bearer ', '');
  const { data: { user } } = await supabase.auth.getUser(token);
  if (!user) return res.status(401).json({ error: 'Invalid session.' });

  const { data: profile } = await supabase.from('profiles').select('*').eq('id', user.id).single();
  const profileComplete = Boolean(profile && profile.school);

  return res.status(200).json({
    missing: SCHOLARSHIP_MASTER_LIST,
    profile_complete: profileComplete
  });
}
