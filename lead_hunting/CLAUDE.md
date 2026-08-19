# CoreTrust Lead Hunting — Web/App Dev Client Acquisition

## Project Purpose
Automated and semi-automated lead generation system for CoreTrust Consulting's AI agent/app development and website building services. Target market: GTA, Peel Region, York Region, Waterloo, Guelph, London, Hamilton, Niagara.

## Operator Context
- Trevon runs CoreTrust Consulting out of Brampton, Ontario
- Services: websites, apps, AI automation (n8n, Telegram bots), booking systems, direct ordering platforms
- Tech stack for client deliverables: Lovable AI, Claude Code, n8n, Telegram Bot API
- Communication style: direct, no fluff, compliance-first
- Pricing tiers: Digital Storefront ($500-800), Full Business Site ($1,500-3,000), Restaurant Direct Order ($2,000 + $200/mo retainer), AI Automation ($1,500-5,000), App MVP ($5,000-15,000), Monthly Retainer ($300-1,000/mo)

## Architecture
```
coretrust-lead-hunting/
├── CLAUDE.md              # This file
├── scrapers/
│   ├── google-maps.js     # Find businesses without websites by niche + city
│   ├── reddit-monitor.js  # Keyword alerts on target subreddits
│   └── facebook-scan.js   # Group monitoring notes and templates
├── outreach/
│   ├── templates/         # Cold call scripts, DM templates, email sequences
│   └── audit-checklist.md # Free website audit framework for warm leads
├── data/
│   ├── leads.csv          # Master lead tracker
│   └── niches.json        # Target niches by city with priority scores
└── docs/
    ├── playbook.md        # Full hunting playbook (Section 1 + 2)
    └── pricing.md         # Service packages and scoping guide
```

## Target Niches (Priority Order)
1. Barbershops/salons — highest volume, weakest digital presence in GTA
2. Independent restaurants — bleeding 30% on delivery app commissions
3. Trades contractors — plumbing, electrical, HVAC, landscaping
4. Cleaning services — residential and commercial
5. Auto detailing / mobile car wash
6. Immigration consultants — massive in Brampton/Mississauga
7. Driving schools
8. Tutoring services
9. Pet grooming / dog walking
10. Event planners / DJs

## Target Regions
- Tier 1 (home base): Brampton, Mississauga, Toronto
- Tier 2 (expansion): Hamilton, Waterloo, Guelph
- Tier 3 (reach): London, Niagara, York Region (Markham, Vaughan, Richmond Hill)

## Key Search Queries for Reddit/Social Monitoring
- "need a website" + [city]
- "looking for developer" + [city]
- "build an app" + Ontario/GTA
- "booking system" + small business
- "automate my business"
- "my website is trash"
- "need online presence"

## Target Subreddits
r/Brampton, r/mississauga, r/Hamilton, r/waterloo, r/kitchener, r/askTO, r/toronto, r/PersonalFinanceCanada, r/canadasmallbusiness, r/EntrepreneurRideAlong

## Rules
- Never spam. 90% value / 10% promotion ratio on all platforms.
- Never fabricate testimonials or reviews.
- All outreach must be genuine, helpful, and compliant with CASL (Canadian Anti-Spam Legislation).
- Free audits are the conversion tool — never hard-pitch cold.
- Track all leads in data/leads.csv with source, date, status, and follow-up date.

## Commands
- `npm run scrape:maps` — Run Google Maps business scraper
- `npm run monitor:reddit` — Start Reddit keyword monitoring
- `npm run export:leads` — Export leads to CSV
