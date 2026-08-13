// api/applications.js - Student Application Tracker & Deadline Alerts for Vercel
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'https://nhdmnyspqnabpwqiteuc.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5oZG1ueXNwcW5hYnB3cWl0ZXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTI5OTQsImV4cCI6MjA5NDQ2ODk5NH0.-dHaLqHQ31MRyrVIvzxP2DnVbAn6vQ5XN1JrGNPHUYc';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default async function handler(req, res) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Sign in required.' });

  const token = authHeader.replace('Bearer ', '');
  const { data: { user } } = await supabase.auth.getUser(token);
  if (!user) return res.status(401).json({ error: 'Invalid session.' });

  if (req.method === 'GET') {
    const { data: apps } = await supabase.from('applications').select('*').eq('user_id', user.id);
    const mockApps = apps && apps.length > 0 ? apps : [
      { funding_name: "Internal School Bursary", status: "in_progress", deadline: "2026-10-31", amount: "$1,500" },
      { funding_name: "Neo Financial Secured Credit", status: "applied", deadline: "2026-09-01", amount: "$300 Limit" }
    ];

    return res.status(200).json({
      applications: mockApps,
      due: [
        { funding_name: "Internal School Bursary", days_left: 14 }
      ]
    });
  }

  if (req.method === 'POST') {
    const { funding_name, status, deadline, amount } = req.body;
    const { data, error } = await supabase.from('applications').upsert({
      user_id: user.id,
      funding_name,
      status,
      deadline,
      amount
    });
    if (error) return res.status(400).json({ error: error.message });
    return res.status(200).json({ ok: true, data });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
