import Snoowrap from 'snoowrap';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const LEADS_FILE = path.join(process.cwd(), 'data', 'reddit-leads.json');

const TARGET_SUBS = [
  'Brampton', 'mississauga', 'Hamilton', 'waterloo', 'kitchener',
  'askTO', 'toronto', 'PersonalFinanceCanada', 'canadasmallbusiness',
  'EntrepreneurRideAlong', 'smallbusiness', 'Entrepreneur',
  'webdev', 'web_design', 'startups'
];

const LEAD_KEYWORDS = [
  'need a website', 'need website', 'looking for developer', 'looking for a developer',
  'build me a website', 'build an app', 'need an app', 'app idea',
  'website recommendation', 'someone to build', 'web developer recommendation',
  'automate my business', 'need online presence', 'booking system',
  'my website is', 'hate my website', 'outdated website', 'need help with website',
  'small business website', 'starting a business', 'just started my business',
  'need a logo', 'need branding', 'ordering system', 'online store',
  'shopify help', 'wordpress help', 'wix help', 'squarespace help',
  'restaurant website', 'booking app', 'scheduling app'
];

const ONTARIO_SIGNALS = [
  'brampton', 'mississauga', 'toronto', 'gta', 'hamilton', 'waterloo',
  'guelph', 'london ontario', 'niagara', 'oakville', 'burlington',
  'markham', 'vaughan', 'richmond hill', 'peel region', 'ontario',
  'york region', 'halton', 'durham'
];

console.log(`\n📡 CoreTrust Lead Hunting — Reddit Monitor`);
console.log(`   Scanning ${TARGET_SUBS.length} subs for ${LEAD_KEYWORDS.length} keywords`);
console.log(`${'─'.repeat(60)}\n`);

function loadExisting() {
  try {
    if (fs.existsSync(LEADS_FILE)) return JSON.parse(fs.readFileSync(LEADS_FILE, 'utf-8'));
  } catch (e) { /* fresh */ }
  return [];
}

function save(data) {
  fs.mkdirSync(path.dirname(LEADS_FILE), { recursive: true });
  fs.writeFileSync(LEADS_FILE, JSON.stringify(data, null, 2));
}

function scorePost(title, body) {
  const text = `${title} ${body}`.toLowerCase();
  let score = 0;
  const matched = [];

  for (const kw of LEAD_KEYWORDS) {
    if (text.includes(kw.toLowerCase())) {
      score += 3;
      matched.push(kw);
    }
  }

  let isOntario = false;
  for (const signal of ONTARIO_SIGNALS) {
    if (text.includes(signal)) {
      score += 2;
      isOntario = true;
      break;
    }
  }

  // Bonus for high-value signals
  if (text.includes('budget') || text.includes('willing to pay') || text.includes('how much')) score += 2;
  if (text.includes('asap') || text.includes('urgent') || text.includes('need it fast')) score += 2;
  if (text.includes('restaurant') || text.includes('ordering')) score += 3; // high-ticket niche

  return { score, matched, isOntario };
}

async function monitor() {
  const { REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD } = process.env;

  if (!REDDIT_CLIENT_ID) {
    console.log('⚠️  Reddit API not configured. Set credentials in .env\n');
    console.log('Manual monitoring guide:\n');
    console.log('1. Open Reddit and search these subs daily:');
    TARGET_SUBS.forEach(s => console.log(`   reddit.com/r/${s}`));
    console.log('\n2. Search for these phrases:');
    LEAD_KEYWORDS.slice(0, 10).forEach(k => console.log(`   "${k}"`));
    console.log('\n3. When you find a match:');
    console.log('   - Write a genuine helpful comment (audit their site, point out issues)');
    console.log('   - Never pitch in the comment');
    console.log('   - Let DMs come to you');
    console.log('   - Target: 2 helpful comments per day\n');
    return;
  }

  const reddit = new Snoowrap({
    userAgent: 'CoreTrust Lead Hunter v1.0 by /u/' + REDDIT_USERNAME,
    clientId: REDDIT_CLIENT_ID,
    clientSecret: REDDIT_CLIENT_SECRET,
    username: REDDIT_USERNAME,
    password: REDDIT_PASSWORD
  });

  const existing = loadExisting();
  const seenIds = new Set(existing.map(l => l.id));
  let newLeads = 0;

  for (const sub of TARGET_SUBS) {
    console.log(`🔍 r/${sub}...`);

    try {
      const posts = await reddit.getSubreddit(sub).getNew({ limit: 100 });

      for (const post of posts) {
        if (seenIds.has(post.id)) continue;

        const { score, matched, isOntario } = scorePost(post.title, post.selftext || '');

        if (score >= 3) {
          const lead = {
            id: post.id,
            subreddit: sub,
            title: post.title,
            url: `https://reddit.com${post.permalink}`,
            author: post.author?.name || '[deleted]',
            upvotes: post.score,
            created: new Date(post.created_utc * 1000).toISOString(),
            matchedKeywords: matched,
            relevanceScore: score,
            isOntario: isOntario,
            snippet: (post.selftext || '').substring(0, 400),
            dateFound: new Date().toISOString(),
            responded: false,
            responseDate: '',
            outcome: '',
            notes: ''
          };

          existing.push(lead);
          seenIds.add(post.id);
          newLeads++;

          const emoji = score >= 8 ? '🔥' : score >= 5 ? '✅' : '📝';
          const geo = isOntario ? ' 📍ON' : '';
          console.log(`  ${emoji} [${score}]${geo} ${post.title.substring(0, 75)}`);
          console.log(`     r/${sub} | ${matched.join(', ')}`);
          console.log(`     ${lead.url}`);
        }
      }
    } catch (e) {
      console.log(`  ❌ ${e.message}`);
    }

    await new Promise(r => setTimeout(r, 2000));
  }

  existing.sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));
  save(existing);

  console.log(`\n${'─'.repeat(60)}`);
  console.log(`📊 Scan Complete`);
  console.log(`   New leads: ${newLeads}`);
  console.log(`   Ontario-specific: ${existing.filter(l => l.isOntario).length}`);
  console.log(`   Total in database: ${existing.length}`);
  console.log(`   High-value (score 8+): ${existing.filter(l => l.relevanceScore >= 8).length}`);
  console.log(`${'─'.repeat(60)}\n`);
}

monitor().catch(console.error);
