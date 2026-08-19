import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { createObjectCsvWriter } from 'csv-writer';
import dotenv from 'dotenv';

dotenv.config();

const niches = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', 'niches.json'), 'utf-8'));
const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const LEADS_FILE = path.join(process.cwd(), 'data', 'leads.csv');
const LEADS_JSON = path.join(process.cwd(), 'data', 'leads.json');

console.log(`\n🎯 CoreTrust Lead Hunting — Google Maps Business Scanner`);
console.log(`   Finding businesses WITHOUT websites in target niches`);
console.log(`${'─'.repeat(60)}\n`);

function loadExistingLeads() {
  try {
    if (fs.existsSync(LEADS_JSON)) {
      return JSON.parse(fs.readFileSync(LEADS_JSON, 'utf-8'));
    }
  } catch (e) { /* fresh */ }
  return [];
}

function saveLeads(leads) {
  fs.mkdirSync(path.dirname(LEADS_JSON), { recursive: true });
  fs.writeFileSync(LEADS_JSON, JSON.stringify(leads, null, 2));
}

function isDuplicate(newLead, existing) {
  return existing.some(l =>
    l.placeId === newLead.placeId ||
    (l.name === newLead.name && l.address === newLead.address)
  );
}

// GTA city coordinates for searching
const CITIES = [
  { name: "Brampton", lat: 43.7315, lng: -79.7624, radius: 15000 },
  { name: "Mississauga", lat: 43.5890, lng: -79.6441, radius: 15000 },
  { name: "Toronto", lat: 43.6532, lng: -79.3832, radius: 20000 },
  { name: "Hamilton", lat: 43.2557, lng: -79.8711, radius: 15000 },
  { name: "Waterloo", lat: 43.4643, lng: -80.5204, radius: 10000 },
  { name: "Guelph", lat: 43.5448, lng: -80.2482, radius: 10000 },
  { name: "London", lat: 42.9849, lng: -81.2453, radius: 15000 },
  { name: "Niagara Falls", lat: 43.0896, lng: -79.0849, radius: 12000 },
  { name: "Markham", lat: 43.8561, lng: -79.3370, radius: 10000 },
  { name: "Vaughan", lat: 43.8361, lng: -79.4983, radius: 10000 },
  { name: "Oakville", lat: 43.4675, lng: -79.6877, radius: 8000 },
  { name: "Richmond Hill", lat: 43.8828, lng: -79.4403, radius: 8000 }
];

async function searchPlaces(query, lat, lng, radius) {
  if (!API_KEY) return [];

  try {
    const response = await axios.get('https://maps.googleapis.com/maps/api/place/textsearch/json', {
      params: { query, location: `${lat},${lng}`, radius, key: API_KEY },
      timeout: 10000
    });

    if (response.data.status === 'OK') return response.data.results;
    if (response.data.status === 'OVER_QUERY_LIMIT') return null;
    return [];
  } catch (e) {
    console.log(`  ❌ API error: ${e.message}`);
    return [];
  }
}

async function getPlaceDetails(placeId) {
  try {
    const response = await axios.get('https://maps.googleapis.com/maps/api/place/details/json', {
      params: {
        place_id: placeId,
        fields: 'name,formatted_phone_number,website,formatted_address,rating,user_ratings_total,types,opening_hours',
        key: API_KEY
      },
      timeout: 10000
    });

    if (response.data.status === 'OK') return response.data.result;
    return null;
  } catch (e) { return null; }
}

async function scanForLeads() {
  const existingLeads = loadExistingLeads();
  let totalNew = 0;
  let noWebsiteCount = 0;
  let badWebsiteCount = 0;

  // Filter niches by CLI arg if provided
  const nicheArg = process.argv.find(a => a.startsWith('--niche='))?.split('=')[1];
  const cityArg = process.argv.find(a => a.startsWith('--city='))?.split('=')[1];

  const targetNiches = nicheArg
    ? niches.niches.filter(n => n.name.toLowerCase().includes(nicheArg.toLowerCase()))
    : niches.niches;

  const targetCities = cityArg
    ? CITIES.filter(c => c.name.toLowerCase().includes(cityArg.toLowerCase()))
    : CITIES;

  for (const niche of targetNiches) {
    console.log(`\n📂 Niche: ${niche.name} (Priority: ${niche.priority})`);
    console.log(`   Avg deal: $${niche.avgDealSize} | Retainer: $${niche.retainerPotential}/mo`);

    for (const city of targetCities) {
      // Skip cities not in this niche's target list unless scanning all
      if (!nicheArg && !niche.cities.includes(city.name)) continue;

      for (const term of niche.searchTerms.slice(0, 3)) { // Top 3 terms per niche
        const query = `${term} ${city.name} Ontario`;
        console.log(`\n  🔍 "${query}"`);

        const results = await searchPlaces(query, city.lat, city.lng, city.radius);

        if (results === null) {
          console.log('  ⚠️  API quota exceeded. Saving progress...');
          saveLeads(existingLeads);
          await exportToCsv(existingLeads);
          return;
        }

        for (const place of results) {
          if (isDuplicate({ placeId: place.place_id, name: place.name, address: place.formatted_address }, existingLeads)) continue;

          // Get detailed info
          const details = await getPlaceDetails(place.place_id);
          await new Promise(r => setTimeout(r, 200));

          if (!details) continue;

          const hasWebsite = !!details.website;
          const hasBadWebsite = hasWebsite && (
            details.website.includes('facebook.com') ||
            details.website.includes('instagram.com') ||
            details.website.includes('yelp.com') ||
            details.website.includes('yellowpages')
          );

          // We want businesses WITHOUT websites or with social-media-only "websites"
          const isLead = !hasWebsite || hasBadWebsite;

          const lead = {
            name: details.name,
            niche: niche.name,
            address: details.formatted_address,
            city: city.name,
            phone: details.formatted_phone_number || '',
            website: details.website || 'NONE',
            hasRealWebsite: hasWebsite && !hasBadWebsite,
            rating: details.rating || null,
            reviewCount: details.user_ratings_total || 0,
            placeId: place.place_id,
            isLead: isLead,
            leadType: !hasWebsite ? 'NO_WEBSITE' : hasBadWebsite ? 'SOCIAL_ONLY' : 'HAS_WEBSITE',
            suggestedPackage: niche.pitch,
            estimatedDealSize: niche.avgDealSize,
            retainerPotential: niche.retainerPotential,
            priority: niche.priority,
            dateFound: new Date().toISOString(),
            status: 'NEW',
            contactedDate: '',
            notes: ''
          };

          existingLeads.push(lead);
          totalNew++;

          if (isLead) {
            const tag = hasBadWebsite ? '🟡 SOCIAL ONLY' : '🔴 NO WEBSITE';
            if (!hasWebsite) noWebsiteCount++;
            if (hasBadWebsite) badWebsiteCount++;
            console.log(`    ${tag} ${details.name}`);
            console.log(`       📍 ${details.formatted_address}`);
            console.log(`       📞 ${details.formatted_phone_number || 'No phone'}`);
            console.log(`       ⭐ ${details.rating || '?'} (${details.user_ratings_total || 0} reviews)`);
            console.log(`       💰 Potential: $${niche.avgDealSize} + $${niche.retainerPotential}/mo`);
          } else {
            console.log(`    ⚪ ${details.name} — has website, skipping`);
          }
        }

        // Delay between searches
        await new Promise(r => setTimeout(r, 2000));
      }
    }
  }

  saveLeads(existingLeads);
  await exportToCsv(existingLeads);

  const leadOnly = existingLeads.filter(l => l.isLead);
  const totalPotentialRevenue = leadOnly.reduce((sum, l) => sum + (l.estimatedDealSize || 0), 0);
  const totalPotentialRetainer = leadOnly.reduce((sum, l) => sum + (l.retainerPotential || 0), 0);

  console.log(`\n${'─'.repeat(60)}`);
  console.log(`📊 Scan Complete`);
  console.log(`   Total businesses scanned: ${totalNew}`);
  console.log(`   🔴 No website: ${noWebsiteCount}`);
  console.log(`   🟡 Social media only: ${badWebsiteCount}`);
  console.log(`   Total actionable leads: ${leadOnly.length}`);
  console.log(`   💰 Potential one-time revenue: $${totalPotentialRevenue.toLocaleString()}`);
  console.log(`   💰 Potential monthly retainers: $${totalPotentialRetainer.toLocaleString()}/mo`);
  console.log(`${'─'.repeat(60)}\n`);
}

async function exportToCsv(leads) {
  const leadsOnly = leads.filter(l => l.isLead);
  if (leadsOnly.length === 0) return;

  const csvWriter = createObjectCsvWriter({
    path: LEADS_FILE,
    header: [
      { id: 'dateFound', title: 'Date Found' },
      { id: 'name', title: 'Business Name' },
      { id: 'niche', title: 'Niche' },
      { id: 'city', title: 'City' },
      { id: 'address', title: 'Address' },
      { id: 'phone', title: 'Phone' },
      { id: 'website', title: 'Current Website' },
      { id: 'leadType', title: 'Lead Type' },
      { id: 'rating', title: 'Google Rating' },
      { id: 'reviewCount', title: 'Review Count' },
      { id: 'suggestedPackage', title: 'Suggested Package' },
      { id: 'estimatedDealSize', title: 'Est. Deal Size ($)' },
      { id: 'retainerPotential', title: 'Retainer Potential ($/mo)' },
      { id: 'priority', title: 'Priority' },
      { id: 'status', title: 'Status' },
      { id: 'contactedDate', title: 'Contacted Date' },
      { id: 'notes', title: 'Notes' }
    ]
  });

  const formatted = leadsOnly.map(l => ({
    ...l,
    dateFound: new Date(l.dateFound).toLocaleDateString('en-CA')
  }));

  // Sort: priority first, then by review count (higher = more established = better lead)
  formatted.sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    return (b.reviewCount || 0) - (a.reviewCount || 0);
  });

  await csvWriter.writeRecords(formatted);
  console.log(`\n  📄 Leads exported to: ${LEADS_FILE}`);
}

// No API key fallback
if (!API_KEY) {
  console.log('⚠️  No GOOGLE_PLACES_API_KEY set in .env');
  console.log('');
  console.log('Two options to find leads:\n');
  console.log('OPTION A — Get a free API key:');
  console.log('  1. Go to https://console.cloud.google.com');
  console.log('  2. Create a project → Enable Places API');
  console.log('  3. Create credentials → API key');
  console.log('  4. Add to .env: GOOGLE_PLACES_API_KEY=your_key');
  console.log('  5. Free tier: 28,500 calls/month (plenty)\n');
  console.log('OPTION B — Manual Google Maps method:');
  console.log('  1. Open Google Maps in browser');
  console.log('  2. Search: "barber Brampton" or "restaurant Mississauga"');
  console.log('  3. Click each listing');
  console.log('  4. No website link = LEAD');
  console.log('  5. Website goes to Facebook/Instagram = LEAD');
  console.log('  6. Note: name, phone, address → add to data/leads.csv\n');
  console.log('Target niches to search:');
  niches.niches.forEach(n => {
    console.log(`  ${n.priority === 1 ? '🔥' : '📌'} ${n.name}: "${n.searchTerms[0]} [city]"`);
  });
  console.log('');
  process.exit(0);
}

scanForLeads().catch(console.error);
