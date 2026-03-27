/* ============================================================
   Holiday Distance Tracker — app.js
   Logic: each email received while OOO increases the escape
   radius, surfacing holiday destinations further from home.
   ============================================================ */

'use strict';

// ── Constants ────────────────────────────────────────────────
const KM_PER_EMAIL = 150;        // distance added per email
const MAX_SHOWN    = 6;           // cards to display at once
const SIM_INTERVAL = 1200;        // ms between simulated emails

// ── World holiday destinations (lat, lon, emoji, tag) ────────
const DESTINATIONS = [
  { name:'Paris',          country:'France',           lat:48.8566,  lon:2.3522,   emoji:'🗼', tag:'Culture' },
  { name:'Rome',           country:'Italy',            lat:41.9028,  lon:12.4964,  emoji:'🏛️', tag:'History' },
  { name:'Barcelona',      country:'Spain',            lat:41.3851,  lon:2.1734,   emoji:'🎨', tag:'Art & Beach' },
  { name:'Amsterdam',      country:'Netherlands',      lat:52.3676,  lon:4.9041,   emoji:'🚲', tag:'City Break' },
  { name:'Prague',         country:'Czech Republic',   lat:50.0755,  lon:14.4378,  emoji:'🏰', tag:'History' },
  { name:'Vienna',         country:'Austria',          lat:48.2082,  lon:16.3738,  emoji:'🎶', tag:'Music & Art' },
  { name:'Budapest',       country:'Hungary',          lat:47.4979,  lon:19.0402,  emoji:'♨️', tag:'Spa City' },
  { name:'Lisbon',         country:'Portugal',         lat:38.7169,  lon:-9.1395,  emoji:'🌊', tag:'Coast' },
  { name:'Athens',         country:'Greece',           lat:37.9838,  lon:23.7275,  emoji:'🏺', tag:'Ancient' },
  { name:'Istanbul',       country:'Turkey',           lat:41.0082,  lon:28.9784,  emoji:'🕌', tag:'Two Continents' },
  { name:'Cairo',          country:'Egypt',            lat:30.0444,  lon:31.2357,  emoji:'🐫', tag:'Desert' },
  { name:'Marrakech',      country:'Morocco',          lat:31.6295,  lon:-7.9811,  emoji:'🏮', tag:'Souk' },
  { name:'Dubai',          country:'UAE',              lat:25.2048,  lon:55.2708,  emoji:'🏙️', tag:'Luxury' },
  { name:'Zanzibar',       country:'Tanzania',         lat:-6.1630,  lon:39.2026,  emoji:'🌴', tag:'Beach' },
  { name:'Cape Town',      country:'South Africa',     lat:-33.9249, lon:18.4241,  emoji:'🏔️', tag:'Adventure' },
  { name:'Maldives',       country:'Maldives',         lat:3.2028,   lon:73.2207,  emoji:'🐠', tag:'Paradise' },
  { name:'Bangkok',        country:'Thailand',         lat:13.7563,  lon:100.5018, emoji:'🙏', tag:'Street Food' },
  { name:'Bali',           country:'Indonesia',        lat:-8.3405,  lon:115.0920, emoji:'🌺', tag:'Spiritual' },
  { name:'Tokyo',          country:'Japan',            lat:35.6762,  lon:139.6503, emoji:'🗾', tag:'Unique' },
  { name:'Sydney',         country:'Australia',        lat:-33.8688, lon:151.2093, emoji:'🦘', tag:'Harbour' },
  { name:'New York',       country:'USA',              lat:40.7128,  lon:-74.0060, emoji:'🗽', tag:'Iconic' },
  { name:'Havana',         country:'Cuba',             lat:23.1136,  lon:-82.3666, emoji:'💃', tag:'Vintage' },
  { name:'Rio de Janeiro', country:'Brazil',           lat:-22.9068, lon:-43.1729, emoji:'🎭', tag:'Carnival' },
  { name:'Buenos Aires',   country:'Argentina',        lat:-34.6037, lon:-58.3816, emoji:'🥩', tag:'Tango' },
  { name:'Machu Picchu',   country:'Peru',             lat:-13.1631, lon:-72.5450, emoji:'🏔️', tag:'Wonder' },
  { name:'Reykjavik',      country:'Iceland',          lat:64.1466,  lon:-21.9426, emoji:'🌌', tag:'Northern Lights' },
  { name:'Nairobi',        country:'Kenya',            lat:-1.2921,  lon:36.8219,  emoji:'🦁', tag:'Safari' },
  { name:'Petra',          country:'Jordan',           lat:30.3285,  lon:35.4444,  emoji:'🏜️', tag:'Ancient' },
  { name:'Kyoto',          country:'Japan',            lat:35.0116,  lon:135.7681, emoji:'⛩️', tag:'Temples' },
  { name:'Santorini',      country:'Greece',           lat:36.3932,  lon:25.4615,  emoji:'🌅', tag:'Sunset' },
  { name:'Queenstown',     country:'New Zealand',      lat:-45.0312, lon:168.6626, emoji:'🎿', tag:'Adventure' },
  { name:'Vancouver',      country:'Canada',           lat:49.2827,  lon:-123.1207,emoji:'🍁', tag:'Nature' },
  { name:'Phuket',         country:'Thailand',         lat:7.8804,   lon:98.3923,  emoji:'🏄', tag:'Beach' },
  { name:'Serengeti',      country:'Tanzania',         lat:-2.3333,  lon:34.8333,  emoji:'🦒', tag:'Wildlife' },
  { name:'Amalfi Coast',   country:'Italy',            lat:40.6340,  lon:14.6027,  emoji:'🍋', tag:'Scenic' },
  { name:'Banff',          country:'Canada',           lat:51.1784,  lon:-115.5708,emoji:'🏔️', tag:'Mountains' },
  { name:'Cinque Terre',   country:'Italy',            lat:44.1461,  lon:9.6439,   emoji:'🎨', tag:'Villages' },
  { name:'Ha Long Bay',    country:'Vietnam',          lat:20.9101,  lon:107.1839, emoji:'⛵', tag:'Nature' },
  { name:'Patagonia',      country:'Argentina/Chile',  lat:-50.9423, lon:-73.4068, emoji:'🧊', tag:'Wild' },
  { name:'Faroe Islands',  country:'Denmark',          lat:62.0000,  lon:-6.7900,  emoji:'🌫️', tag:'Remote' },
];

// ── State ────────────────────────────────────────────────────
let homeCoords  = null;   // { lat, lon, name }
let isOOO       = false;
let emailCount  = 0;
let simTimer    = null;
let map         = null;
let homeMarker  = null;
let destMarkers = [];
let circleLayer = null;

// ── DOM refs ─────────────────────────────────────────────────
const homeInput      = document.getElementById('homeInput');
const setHomeBtn     = document.getElementById('setHomeBtn');
const homeStatus     = document.getElementById('homeStatus');
const oooToggle      = document.getElementById('oooToggle');
const oooIcon        = document.getElementById('oooIcon');
const oooText        = document.getElementById('oooText');
const emailPanel     = document.getElementById('emailPanel');
const mapPanel       = document.getElementById('mapPanel');
const cardsPanel     = document.getElementById('cardsPanel');
const emailCountEl   = document.getElementById('emailCount');
const emailPlusBtn   = document.getElementById('emailPlusBtn');
const emailMinusBtn  = document.getElementById('emailMinusBtn');
const simulateBtn    = document.getElementById('simulateBtn');
const stopSimBtn     = document.getElementById('stopSimBtn');
const distanceValue  = document.getElementById('distanceValue');
const destinationCards = document.getElementById('destinationCards');

// ── Haversine distance (km) ──────────────────────────────────
function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)**2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon/2)**2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function toRad(deg) { return deg * Math.PI / 180; }

// ── Geocoding via Nominatim (free, no key) ───────────────────
async function geocode(query) {
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`;
  const res  = await fetch(url, { headers: { 'Accept-Language': 'en' } });
  const data = await res.json();
  if (!data.length) throw new Error('Location not found');
  return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon), name: data[0].display_name.split(',')[0] };
}

// ── Set home ─────────────────────────────────────────────────
setHomeBtn.addEventListener('click', async () => {
  const q = homeInput.value.trim();
  if (!q) return;

  setHomeBtn.disabled = true;
  setHomeBtn.textContent = 'Locating…';
  homeStatus.className = 'status-msg';
  homeStatus.textContent = '';

  try {
    homeCoords = await geocode(q);
    homeStatus.textContent = `✔ Home set to: ${homeCoords.name}`;
    oooToggle.disabled = false;
    initMap();
  } catch (e) {
    homeStatus.className = 'status-msg error';
    homeStatus.textContent = '✘ Could not find that location. Try "London, UK"';
  } finally {
    setHomeBtn.disabled = false;
    setHomeBtn.textContent = 'Set Home';
  }
});

homeInput.addEventListener('keydown', e => { if (e.key === 'Enter') setHomeBtn.click(); });

// ── OOO toggle ───────────────────────────────────────────────
oooToggle.addEventListener('click', () => {
  isOOO = !isOOO;
  oooToggle.classList.toggle('active', isOOO);
  oooIcon.textContent = isOOO ? '🏖️' : '🖥️';
  oooText.textContent  = isOOO ? 'OOO Active' : 'Enable OOO';

  reveal(emailPanel, isOOO);
  reveal(mapPanel,   isOOO);
  reveal(cardsPanel, isOOO);

  if (!isOOO) {
    stopSimulation();
    resetEmails();
  } else {
    renderAll();
  }
});

// ── Reveal / hide panels ─────────────────────────────────────
function reveal(el, show) {
  el.setAttribute('aria-hidden', String(!show));
}

// ── Map init ─────────────────────────────────────────────────
function initMap() {
  if (!map) {
    map = L.map('map', { zoomControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
  }

  map.setView([homeCoords.lat, homeCoords.lon], 4);

  if (homeMarker) homeMarker.remove();
  homeMarker = L.marker([homeCoords.lat, homeCoords.lon], {
    icon: L.divIcon({ className: '', html: '<div style="font-size:1.8rem">🏠</div>', iconAnchor: [18,18] })
  }).addTo(map).bindPopup(`<b>Home:</b> ${homeCoords.name}`);
}

// ── Email counter ────────────────────────────────────────────
emailPlusBtn.addEventListener('click',  () => changeEmails(1));
emailMinusBtn.addEventListener('click', () => changeEmails(-1));

function changeEmails(delta) {
  emailCount = Math.max(0, emailCount + delta);
  renderAll();
}

function resetEmails() {
  emailCount = 0;
  emailCountEl.textContent = '0';
  distanceValue.textContent = '— km';
  clearMapDestinations();
  destinationCards.innerHTML = '';
}

// ── Simulation ───────────────────────────────────────────────
simulateBtn.addEventListener('click', () => {
  simulateBtn.classList.add('hidden');
  stopSimBtn.classList.remove('hidden');
  simTimer = setInterval(() => changeEmails(1), SIM_INTERVAL);
});

stopSimBtn.addEventListener('click', stopSimulation);

function stopSimulation() {
  if (simTimer) { clearInterval(simTimer); simTimer = null; }
  simulateBtn.classList.remove('hidden');
  stopSimBtn.classList.add('hidden');
}

// ── Core render ──────────────────────────────────────────────
function renderAll() {
  if (!homeCoords || !isOOO) return;

  const radiusKm = emailCount * KM_PER_EMAIL;
  emailCountEl.textContent  = emailCount;
  distanceValue.textContent = emailCount === 0 ? '0 km' : `${radiusKm.toLocaleString()} km`;

  const sorted = sortedDestinations(radiusKm);
  renderCards(sorted);
  renderMapDestinations(sorted, radiusKm);
}

// Sort destinations: those within the radius, closest first; then wrap-around
function sortedDestinations(radiusKm) {
  if (!homeCoords) return [];

  const withDist = DESTINATIONS.map(d => ({
    ...d,
    dist: Math.round(haversine(homeCoords.lat, homeCoords.lon, d.lat, d.lon))
  }));

  if (radiusKm === 0) {
    // show nearest destinations before OOO emails start
    return withDist.sort((a,b) => a.dist - b.dist).slice(0, MAX_SHOWN);
  }

  // pick destinations within a band: [radius * 0.5, radius * 1.3]
  const lower = radiusKm * 0.5;
  const upper = radiusKm * 1.3;
  let band = withDist.filter(d => d.dist >= lower && d.dist <= upper);

  // If too few, expand to nearest above radius
  if (band.length < 3) {
    band = withDist.filter(d => d.dist <= upper).sort((a,b) => Math.abs(a.dist - radiusKm) - Math.abs(b.dist - radiusKm));
  }

  return band.sort((a,b) => Math.abs(a.dist - radiusKm) - Math.abs(b.dist - radiusKm)).slice(0, MAX_SHOWN);
}

// ── Cards ────────────────────────────────────────────────────
let prevCardKeys = new Set();

function renderCards(destinations) {
  const newKeys = new Set(destinations.map(d => d.name));

  destinationCards.innerHTML = destinations.length === 0
    ? '<p class="no-results">No destinations found at this range — keep those emails coming!</p>'
    : destinations.map(d => {
        const isNew = !prevCardKeys.has(d.name);
        return `
          <div class="dest-card${isNew ? ' new' : ''}">
            <div class="card-emoji">${d.emoji}</div>
            <div class="card-body">
              <div class="card-name">${d.name}</div>
              <div class="card-country">${d.country}</div>
              <div class="card-dist">✈ ${d.dist.toLocaleString()} km away</div>
              <span class="card-tag">${d.tag}</span>
            </div>
          </div>`;
      }).join('');

  prevCardKeys = newKeys;
}

// ── Map destinations ─────────────────────────────────────────
function clearMapDestinations() {
  destMarkers.forEach(m => m.remove());
  destMarkers = [];
  if (circleLayer) { circleLayer.remove(); circleLayer = null; }
}

function renderMapDestinations(destinations, radiusKm) {
  if (!map) return;
  clearMapDestinations();

  // Draw radius circle
  if (radiusKm > 0) {
    circleLayer = L.circle([homeCoords.lat, homeCoords.lon], {
      radius: radiusKm * 1000,
      color: '#0ea5e9',
      fillColor: '#bae6fd',
      fillOpacity: 0.12,
      weight: 2,
      dashArray: '6 4',
    }).addTo(map);
  }

  destinations.forEach(d => {
    const marker = L.marker([d.lat, d.lon], {
      icon: L.divIcon({
        className: '',
        html: `<div style="font-size:1.6rem;filter:drop-shadow(0 1px 3px #0008)">${d.emoji}</div>`,
        iconAnchor: [16, 16]
      })
    })
    .addTo(map)
    .bindPopup(`<b>${d.name}</b><br>${d.country}<br><i>${d.dist.toLocaleString()} km away</i>`);
    destMarkers.push(marker);
  });

  // Fit map to show home + all destinations
  if (destinations.length) {
    const bounds = L.latLngBounds(
      [[homeCoords.lat, homeCoords.lon], ...destinations.map(d => [d.lat, d.lon])]
    );
    map.fitBounds(bounds, { padding: [40, 40] });
  }
}
