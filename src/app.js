'use strict';
/* No child accounts, advertising or individual learning-behavior tracking.
   Optional cookieless site-traffic beacon is injected at build time only for the production site;
   portable/offline builds and unconfigured installations remain untracked. */
const curriculum = JSON.parse(document.getElementById('curriculum-data').textContent);
const original = JSON.parse(document.getElementById('games-data').textContent);
const PUB = 'publisher_claim_reviewed';
const TEACHER = 'teacher_verified';
const visibleReview = g => g.review.status === PUB || g.review.status === TEACHER;
const DRAFT_KEY = 'wonderwood-catalogue-v3';
const GRADE_IDS = curriculum.grades.map(g => g.id);
const GRADE_BANDS = [['K','1','2'],['3','4','5'],['6','7','8'],['9','10','11','12']];
const gradeLabel = g => g === 'K' ? 'Kindergarten' : `Grade ${g}`;
const gradeBand = g => GRADE_BANDS.findIndex(b => b.includes(g));
const assetURL = file => typeof PORTABLE_ASSETS !== 'undefined' ? (PORTABLE_ASSETS['assets/'+file] || '') : 'assets/'+file;
const subjectLabel = id => Number(state.grade) >= 6 ? ({ela:'English',hss:'History',health:'Wellbeing',pe:'PE & Fitness',cs:'Computing'}[id] || curriculum.subjects.find(s => s.id === id)?.name) : curriculum.subjects.find(s => s.id === id)?.name;
function gradeSummary(grades) {
 const sorted = GRADE_IDS.filter(x => grades.includes(x));
 if (sorted.length === 1) return gradeLabel(sorted[0]);
 const ranges=[]; let start=0;
 for(let i=1;i<=sorted.length;i++) {
  if(i<sorted.length && GRADE_IDS.indexOf(sorted[i]) === GRADE_IDS.indexOf(sorted[i-1])+1) continue;
  ranges.push(sorted[start]===sorted[i-1]?sorted[start]:sorted[start]+'–'+sorted[i-1]); start=i;
 }
 return 'Grades '+ranges.join(', ');
}

const FAVORITES_KEY = 'wonderwood-favorites-v2';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const store = {
  get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } }
};
const safeURL = s => {
  if (typeof s !== 'string' || s.length > 2048) return null;
  try { const u = new URL(s); return u.protocol === 'https:' && !u.username && !u.password ? u.href : null; } catch { return null; }
};
let dataset = structuredClone(original);
let favorites = store.get(FAVORITES_KEY, []);
if (!Array.isArray(favorites)) favorites = [];
favorites = favorites.filter(id => typeof id === 'string' && /^[a-z0-9-]+$/.test(id)).slice(0, 2000);
let state = {view:'explore', grade:'K', band:0, subject:'all', topic:'all', type:'all', device:'all', q:'', showAll:false,
  tab:'curriculum', parentSubject:'all', editId:null};
const shortText = (s, max, required = false) => typeof s === 'string' && s.length <= max && (!required || s.trim().length > 0);
function validData(v) {
  if (!v || v.schemaVersion !== 1 || !Array.isArray(v.games) || v.games.length > 2000) return false;
  const ids = new Set();
  return v.games.every(g => {
    if (!g || !shortText(g.id, 150, true) || !/^[a-z0-9-]+$/.test(g.id) || ids.has(g.id) ||
        !shortText(g.title, 150, true) || !shortText(g.publisher, 150, true) || !safeURL(g.url) ||
        !shortText(g.description, 500) || !shortText(g.access, 500) || !shortText(g.priceLabel, 180, true) ||
        !shortText(g.kind, 100, true) || !['browser','app'].includes(g.platform) ||
        !Array.isArray(g.grades) || !g.grades.length || g.grades.some(x => !GRADE_IDS.includes(x)) ||
        !Array.isArray(g.subjects) || !g.subjects.length || g.subjects.some(x => !curriculum.subjects.some(s => s.id === x)) ||
        !Array.isArray(g.topicIds) || g.topicIds.some(id => !curriculum.topics.some(t => t.id === id && g.grades.includes(t.grade) && g.subjects.includes(t.subject))) ||
        !Array.isArray(g.sourceIds) || g.sourceIds.some(id => typeof id !== 'string' || !Object.hasOwn(curriculum.sourceRegister, id)) ||
        !g.review || ![PUB, TEACHER,'needs_review'].includes(g.review.status) || typeof g.review.runtimeTested !== 'boolean') return false;
    if (g.devices !== undefined && (!Array.isArray(g.devices) || g.devices.some(x => !['browser','ios','android','amazon','chromeos','desktop','mobile','unknown'].includes(x)))) return false;
    if (g.review.adEvidenceUrl && !safeURL(g.review.adEvidenceUrl)) return false;
    if (g.review.status === PUB && !safeURL(g.review.adEvidenceUrl) && !Object.hasOwn(curriculum.sourceRegister, g.review.adEvidenceSourceId || '')) return false;
    if (g.review.status === TEACHER && g.teacherVerified !== true) return false;
    if (g.thumbnailAsset !== undefined && (!shortText(g.thumbnailAsset,100) || !/^[a-z0-9-]+\.webp$/.test(g.thumbnailAsset))) return false;
    if (g.review.notes !== undefined && !shortText(g.review.notes, 5000)) return false;
    if (g.learningSuggestion !== undefined && !shortText(g.learningSuggestion, 1500)) return false;
    ids.add(g.id); return true;
  });
}
// Seed revision 2 expands 28 V3 catalogue records into curated K–12 entries.
// Preserve prior user edits and intentional removals from the old seed set.
// Append ONLY IDs first introduced in this revision; stamp the draft so that
// later user removal of a newly added game remains intentional.
const SEED_REVISION = 3;
const V3_BASELINE_IDS = new Set(["starfall-abc", "starfall-read", "starfall-an", "starfall-at", "starfall-en", "starfall-vowels", "khan-kids", "tym-numbers-ios", "tym-eating-ios", "tym-read-web", "tym-numbers-web", "tym-eating-web", "tym-reading-fun", "mlc-frames", "mlc-pieces", "mlc-shapes", "mlc-clock", "pbs-scribbles", "pbs-animal-home", "pbs-city", "pbs-pink", "scratchjr", "tuxpaint", "phet-equality-explorer-basics", "phet-area-builder", "phet-number-line-integers", "phet-graphing-lines", "phet-build-an-atom"]);
const V2_BASELINE_IDS = new Set([...V3_BASELINE_IDS].filter(id => !id.startsWith('phet-')));
// Revision 3 imports teacher-reviewed Hub links without resurrecting existing K–12
// resources the local curator deliberately removed in revision 2.
const REV2_BASELINE_IDS = new Set(original.games.filter(g => !g.id.startsWith('hub-')).map(g => g.id));
function adoptNewSeeds(draft, oldIds) {
  const seen = new Set(draft.games.map(g=>g.id));
  const additions = original.games.filter(g=>!oldIds.has(g.id) && !seen.has(g.id));
  return {...draft, seedRevision:SEED_REVISION, games:[...draft.games, ...additions]};
}
const savedDraft = store.get(DRAFT_KEY, null);
if (validData(savedDraft)) {
  dataset = savedDraft.seedRevision >= SEED_REVISION ? savedDraft : adoptNewSeeds(savedDraft, savedDraft.seedRevision >= 2 ? REV2_BASELINE_IDS : V3_BASELINE_IDS);
  if (dataset !== savedDraft) store.set(DRAFT_KEY, dataset);
} else {
  const legacy = store.get('wonderwood-catalogue-v2', null);
  if (validData(legacy)) {
    dataset = adoptNewSeeds(legacy, V2_BASELINE_IDS);
    store.set(DRAFT_KEY, dataset);
  }
}

const icons = {
  play:'<path d="m8 4 13 8-13 8Z"/>',
  coin:'<circle cx="12" cy="12" r="9"/><path d="M15 8h-4a2 2 0 0 0 0 4h2a2 2 0 0 1 0 4H9m3-10v12"/>',
  cap:'<path d="m2 9 10-6 10 6-10 6ZM6 12v6q6 5 12 0v-6m4-3v9"/>',
  info:'<circle cx="12" cy="12" r="10"/><path d="M12 11v6m0-10v.1"/>',
  arrow:'<path d="M5 12h14m-5-5 5 5-5 5"/>',
  'arrow-left':'<path d="M19 12H5m5-5-5 5 5 5"/>',
  chevron:'<path d="m9 5 7 7-7 7"/>',
  book:'<path d="M12 6C8 3 4 4 2 5v14c3-2 6-2 10 0 4-2 7-2 10 0V5c-3-1-6-2-10 1Z"/><path d="M12 6v13"/>',
  blocks:'<rect x="2" y="11" width="9" height="10" rx="2"/><rect x="13" y="11" width="9" height="10" rx="2"/><rect x="7" y="1" width="10" height="9" rx="2"/>',
  sprout:'<path d="M12 22V11C5 13 2 8 3 3c7 0 10 4 9 8ZM12 16c7 1 10-3 9-8-6 0-9 3-9 8Z"/>',
  globe:'<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2c6 5 6 15 0 20-6-5-6-15 0-20Z"/>',
  palette:'<path d="M12 2a10 10 0 1 0 0 20h1c2 0 3-2 1-4-1-1 0-3 2-3h3c5 0 4-13-7-13Z"/><circle cx="7" cy="8" r="1"/><circle cx="12" cy="6" r="1"/><circle cx="17" cy="8" r="1"/>',
  heart:'<path d="m12 21-8-8C-3 6 7-2 12 6c5-8 15 0 8 7Z"/>',
  ball:'<circle cx="12" cy="12" r="10"/><path d="M3 7c6 4 8 9 6 15M15 2c-2 6 0 11 6 14M3 17 19 5"/>',
  code:'<path d="m7 7-5 5 5 5m10-10 5 5-5 5M14 3l-4 18"/>',
  grownup:'<circle cx="8" cy="6" r="3"/><circle cx="17" cy="10" r="2.5"/><path d="M2 20v-3a6 6 0 0 1 12 0v3m0 0v-2a4 4 0 0 1 8 0v2"/>',
  search:'<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
  close:'<path d="m6 6 12 12M6 18 18 6"/>',
  external:'<path d="M14 3h7v7m0-7L10 14M10 4H4v17h17v-7"/>',
  check:'<path d="m5 12 4 4L19 6"/>',
  star:'<path d="m12 2 3.1 6.3 7 1-5.1 4.9 1.2 6.9-6.2-3.3-6.2 3.3 1.2-6.9-5.1-4.9 7-1Z"/>',
  phone:'<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M10 5h4M11 19h2"/>',
  tablet:'<rect x="3" y="2" width="18" height="20" rx="2.5"/><path d="M11 19h2"/>',
  desktop:'<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M12 17v4M7 21h10"/>',
  devices:'<rect x="2" y="3" width="15" height="12" rx="2"/><path d="M9 15v4M5 19h8"/><rect x="15" y="9" width="7" height="12" rx="1.5"/>',
  shield:'<path d="m12 2 8 3v7c0 5-8 10-8 10S4 17 4 12V5Z"/><path d="m8 12 3 3 5-6"/>'
};
function icon(name, cl = 'icon') { return `<svg class="${cl}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.book}</svg>`; }
function hydrateIcons(root = document) { root.querySelectorAll('[data-icon]').forEach(n => { n.innerHTML = icon(n.dataset.icon); }); }
function notify(msg) { $('#toast').textContent = msg; $('#toast').hidden = false; clearTimeout(notify.timer); notify.timer = setTimeout(() => { $('#toast').hidden = true; }, 5000); }
function srcLinks(ids) {
  return [...new Set(ids)].filter(k => Object.hasOwn(curriculum.sourceRegister, k)).map(k => {
    const s = curriculum.sourceRegister[k];
    return safeURL(s.url) ? `<a class="mini-source" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a>` : '';
  }).join('');
}
function approved() { return dataset.games.filter(visibleReview); }
const SUBJECT_STYLE = {
  ela:['reading','#ffab55','#ff8734','#e77424','#43230b','📖'],
  math:['math','#7bcfff','#3dacf2','#2792d6','#103b62','🔢'],
  science:['science','#acdf70','#73ba47','#60a83e','#183c15','🌱'],
  hss:['world','#ffe979','#ffda43','#e6bd24','#58400b','🌍'],
  arts:['arts','#ffb0de','#ed7bc4','#d563af','#632450','🎨'],
  health:['health','#69ddd7','#2dc2bd','#24aaa7','#083f45','💗'],
  pe:['move','#ff828a','#fb545e','#d84048','#521922','⚽'],
  cs:['coding','#ba91ff','#8d5ee9','#7245ce','#2c1658','💻']
};
const PRETTY = {
  'khan-kids':['Khan Academy Kids','Stories, reading & math','game-friends.webp'],
  'starfall-abc':['Starfall ABCs','Meet letters & sounds','game-star.webp'],
  'tym-numbers-ios':['Number Skills','Count. Play. Discover.','game-monster.webp'],
  'starfall-read':['Learn to Read','Little words. Big adventures.',null],
  'tym-eating-ios':['Adventurous Eating','Explore a world of food',null],
  'starfall-an':['Make a Word: -an','Build a word family',null],
  'starfall-at':['Make a Word: -at','Build a word family',null],
  'starfall-en':['Make a Word: -en','Short-e word play',null],
  'starfall-vowels':['Vowel Teams','Find the matching sounds',null]
};
function platformInfo(g) {
  const devices = g.devices || [];
  if (g.platform === 'browser') return {label:'Browser', tooltip:'Opens a browser game. Device controls still need hands-on checking.', icons:['globe'], cls:'browser'};
  if (devices.includes('desktop')) return {label:'Desktop app', tooltip:'Desktop installation required; not an in-browser game.', icons:['desktop'], cls:'desktop'};
  if (g.id.endsWith('-ios') || devices.length === 1 && devices[0] === 'ios') return {label:'iPhone / iPad', tooltip:'This link is for the iPhone / iPad app, not browser play.', icons:['phone','tablet'], cls:'mobile'};
  if (devices.some(x => ['ios','android','amazon','mobile'].includes(x)) || g.id === 'khan-kids') return {label:'Mobile app', tooltip:'Phone / tablet app, not a browser game. Check the app details for other supported devices.', icons:['phone','tablet'], cls:'mobile'};
  return {label:'App to install', tooltip:'Installation required. Check supported devices with a grown-up.', icons:['devices'], cls:'mobile'};
}
function priceInfo(g) {
  if (/trial/i.test(g.priceLabel)) return ['Trial · paid', 'paid'];
  if (/purchase|paid|unlock|subscription/i.test(g.priceLabel)) return ['In-app purchases', 'paid'];
  if (/free/i.test(g.priceLabel)) return ['Free','free'];
  return ['Check price','paid'];
}
function renderSubjects() {
  $('#subjects').innerHTML = curriculum.subjects.map(s => {
    const [asset, light, tone, base, ink] = SUBJECT_STYLE[s.id];
    const label = Number(state.grade) >= 6 ? esc(subjectLabel(s.id)) : ({ela:'Reading &<br>Writing',hss:'Our World',arts:'Art & Music',pe:'Move & Play',health:'Healthy Me'}[s.id] || esc(s.short));
    return `<button class="subject ${state.subject === s.id ? 'active' : ''}" style="--light:${light};--tone:${tone};--base:${base};--subject-ink:${ink}" data-subject="${s.id}" aria-pressed="${state.subject === s.id}" aria-label="${esc(s.name)}"><span class="subject-glyph" aria-hidden="true"><img src="assets/subject-${asset}.webp" width="70" height="58" alt=""></span><span>${label}</span></button>`;
  }).join('');
}
function filtered() {
  const q = state.q.trim().toLowerCase();
  return approved().filter(g => g.grades.includes(state.grade) &&
    (state.subject === 'all' || g.subjects.includes(state.subject)) &&
    (state.view !== 'favorites' || favorites.includes(g.id)) &&
    (state.topic === 'all' || g.topicIds.includes(state.topic)) &&
    (state.device === 'all' || state.device === 'browser' && g.platform === 'browser' || state.device === 'app' && g.platform === 'app' || state.device === 'desktop' && g.devices?.includes('desktop')) &&
    (state.type === 'all' || state.type === 'mini' && g.kind === 'Mini-game' || state.type === 'adventure' && ['Game adventure','Learning app'].includes(g.kind) || state.type === 'explore' && ['Interactive simulation','Creative tool','Creative app','Activity collection','Reading resource','Research resource','Video'].includes(g.kind)) &&
    (!q || [g.title, g.description, g.publisher, ...g.subjects.map(s => curriculum.subjects.find(x => x.id === s)?.name || ''), ...g.topicIds.map(t => curriculum.topics.find(x => x.id === t)?.title || '')].join(' ').toLowerCase().includes(q))
  ).sort((a,b) => {
    if (a.hubOrder && b.hubOrder) return a.hubOrder - b.hubOrder;
    const order = ['khan-kids','starfall-abc','tym-numbers-ios','starfall-read','tym-eating-ios'];
    return (order.includes(a.id) ? order.indexOf(a.id) : 99) - (order.includes(b.id) ? order.indexOf(b.id) : 99);
  });
}
/* Illustrations are decorations taken from the approved concept, not game screenshots. */
function gameArt(g) {
  const asset = g.thumbnailAsset || PRETTY[g.id]?.[2];
  if (g.review.status === TEACHER && g.thumbnailAsset) return `<img class="source-thumbnail" src="${assetURL(asset)}" width="250" height="137" alt="${esc(g.title)} thumbnail from the Learning Hub" loading="lazy">`;
  if (g.thumbnailAsset) return `<img class="thematic-thumbnail" src="${assetURL(asset)}" width="250" height="137" alt="" loading="lazy">`;
  if (asset) return `<img src="${assetURL(asset)}" width="250" height="137" alt="" loading="lazy">`;
  const which = g.id === 'tym-eating-ios' ? 'food' : g.id === 'starfall-read' ? 'book' : 'letters';
  let scene = '';
  if (which === 'book') {
    scene = '<circle cx="76" cy="38" r="4" fill="#ffd546"/><path d="m227 18 3 8 8 3-8 3-3 8-3-8-8-3 8-3Z" fill="#ffd546"/><path d="M155 58Q117 27 67 46L76 121Q119 103 155 127Q190 104 236 119L241 46Q194 31 155 58" fill="#0b8e9c"/><path d="M155 53Q113 27 74 41L80 112Q120 99 155 119Q194 99 231 110L234 41Q193 28 155 53" fill="#fffbee"/><path d="M155 55v62" stroke="#dbc99e" stroke-width="2"/><path d="m90 61 47 11m-45 4 45 10m-44 5 43 8m38-28 42-10m-42 25 40-9m-40 23 38-8" stroke="#8bc6cc" stroke-width="5" stroke-linecap="round"/>';
  } else if (which === 'food') {
    scene = '<circle cx="156" cy="84" r="50" fill="#fff9df"/><ellipse cx="153" cy="129" rx="79" ry="7" fill="#73b36244"/><path d="M129 57c-37-25-64 27-37 56 17 19 23 6 39 8 35 8 46-67-2-64" fill="#f65d6c"/><path d="M129 57v-18m0 8q18-21 32-7-9 19-32 7" stroke="#458932" stroke-width="5" fill="#62b34b"/><path d="m190 62 29 55-63-5Z" fill="#ffad38"/><path d="m187 63-8-21m13 20 8-25m-5 26 20-17" stroke="#458c41" stroke-width="7" stroke-linecap="round"/><circle cx="114" cy="82" r="3" fill="#6d2946"/><circle cx="139" cy="83" r="3" fill="#6d2946"/><path d="M119 97q9 9 15 0" stroke="#6d2946" stroke-width="3" fill="none" stroke-linecap="round"/>';
  } else {
    const word = g.id === 'starfall-at' ? ['c','a','t'] : g.id === 'starfall-en' ? ['h','e','n'] : g.id === 'starfall-an' ? ['f','a','n'] : ['a','i','e'];
    const fills = ['#ffb742','#7bcd5b','#ba95f0'];
    const shadows = ['#cd841d','#4c923b','#805dc5'];
    scene = word.map((letter,i) => `<g transform="translate(${54+i*71} ${43+(i===1?-10:4)}) rotate(${i%2?6:-7} 30 30)"><rect y="5" width="63" height="65" rx="13" fill="${shadows[i]}"/><rect width="63" height="63" rx="13" fill="${fills[i]}"/><text x="31" y="47" text-anchor="middle" font-family="Trebuchet MS,sans-serif" font-size="46" font-weight="900" fill="#fffdf5">${letter}</text></g>`).join('');
  }
  const bg = which === 'book' ? '#c0ecf8' : which === 'food' ? '#d9f2c5' : '#fff0c6';
  return `<svg viewBox="0 0 310 155" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="310" height="155" fill="${bg}"/><circle cx="26" cy="40" r="18" fill="#ffffff66"/><circle cx="287" cy="119" r="24" fill="#ffffff66"/>${scene}</svg>`;
}
function card(g) {
  const saved = favorites.includes(g.id), p = platformInfo(g), [cost, costClass] = priceInfo(g);
  const base = original.games.find(x => x.id === g.id);
  const [title, desc] = PRETTY[g.id] && base?.title === g.title && base?.description === g.description ? PRETTY[g.id] : [g.title, g.description];
  const grade = gradeSummary(g.grades);
  return `<article class="game-card" data-game="${g.id}">
    <button class="card-hit" data-open="${g.id}" aria-label="${esc(g.title)}. ${esc(p.tooltip)} ${esc(g.priceLabel)}. View details.">
      <span class="card-image">${gameArt(g)}</span>
      <span class="platform-badge ${p.cls}" title="${esc(p.tooltip)}">${p.icons.map(x => icon(x)).join('')}<span>${p.label}</span></span>
      <span class="card-copy"><span class="card-title-line"><span class="card-title">${esc(title)}</span><span class="card-arrow">${icon('chevron')}</span></span><span class="card-desc">${esc(desc)}</span><span class="card-tags"><span class="tag">${grade}</span><span class="tag ${costClass}">${esc(cost)}</span>${g.review.status===TEACHER?`<span class="tag teacher-tag" title="Teacher-verified selection; advertising not independently checked">${icon('shield')} Teacher</span>`:''}</span></span>
    </button>
    <button class="save ${saved ? 'saved' : ''}" data-save="${g.id}" aria-label="${saved ? 'Remove from' : 'Add to'} favorites: ${esc(g.title)}" aria-pressed="${saved}">${icon('star')}</button>
  </article>`;
}
function hasFilters() { return state.subject !== 'all' || state.topic !== 'all' || state.type !== 'all' || state.device !== 'all' || state.q.trim(); }
function renderGames() {
  const sub = curriculum.subjects.find(x => x.id === state.subject);
  const list = filtered(), limited = !hasFilters() && state.view !== 'favorites' && !state.showAll;
  const featuredLimit = innerWidth <= 960 ? 6 : 5;
  const shown = limited ? list.slice(0,featuredLimit) : list;
  $('#browse-title').textContent = state.view === 'favorites' ? 'Favorites' : state.q.trim() ? 'Search results' : sub ? subjectLabel(sub.id) : state.showAll || hasFilters() ? 'All games' : 'Featured games';
  $('#browse-emoji').textContent = state.view === 'favorites' ? '💛' : sub ? SUBJECT_STYLE[sub.id][5] : '⭐';
  $('#results-count').textContent = `${gradeLabel(state.grade)} · ${shown.length} ${shown.length === 1 ? 'activity' : 'activities'}`;
  $('#games').innerHTML = shown.length ? shown.map(card).join('') : `<div class="empty"><div class="emptyicon" aria-hidden="true">${state.view === 'favorites' ? '⭐' : '🌱'}</div><h3>${state.view === 'favorites' ? 'Save a favorite' : hasFilters() ? 'More coming soon' : 'More coming soon'}</h3><p>${state.view === 'favorites' ? 'Tap a star to save a game here.' : state.q.trim() ? 'Try another search or filter.' : 'No reviewed match yet. Explore another subject.'}</p><div class="empty-actions"><button class="outline" id="empty-reset">All games</button><button class="textbutton" data-nav="parent">Learning goals ${icon('arrow')}</button></div></div>`;
  $('#view-all').hidden = state.view === 'favorites' || !limited || list.length <= featuredLimit;
  $('#reset-filters').hidden = !hasFilters();
  $('#clear-search').hidden = !state.q;
  $('#device-filter').value = state.device;
  $('#footer-grade').textContent = gradeLabel(state.grade);
  $('#footer-subject').textContent = sub ? subjectLabel(sub.id) : 'All subjects';
  $('#year-section').hidden = state.view === 'favorites';
  const savedCount = favorites.filter(id => approved().some(g => g.id === id)).length;
  $('#fav-count').textContent = savedCount; $('#fav-count').hidden = !savedCount;
  $$('[data-type]').forEach(b => { b.classList.toggle('active', b.dataset.type === state.type); b.setAttribute('aria-pressed', b.dataset.type === state.type); });
}
function renderTopics() {
  const topics = state.subject === 'all' ? [] : curriculum.topics.filter(t => t.grade === state.grade && t.subject === state.subject);
  $('#topics').hidden = !topics.length;
  $('#topics').innerHTML = topics.length ? `<button class="chip ${state.topic === 'all' ? 'active' : ''}" data-topic="all" aria-pressed="${state.topic === 'all'}">All topics</button>` + topics.map(t => `<button class="chip ${state.topic === t.id ? 'active' : ''}" data-topic="${t.id}" aria-pressed="${state.topic === t.id}">${esc(t.title)}</button>`).join('') : '';
}
function renderChild() {
  state.band=gradeBand(state.grade); renderGradePicker(); renderSubjects(); renderTopics(); renderGames(); renderYears();
  $$('[data-grade]').forEach(b => { b.classList.toggle('active', b.dataset.grade === state.grade); b.setAttribute('aria-pressed', b.dataset.grade === state.grade); });
}
function renderGradePicker() {
 const labels=['K–2','3–5','6–8','9–12'];
 const bandNames=['Early years','Elementary','Middle school','High school'];
 $('#grade-bands').innerHTML=GRADE_BANDS.map((band,i)=>`<button class="band-chip ${state.band===i?'active':''}" data-band="${i}" aria-pressed="${state.band===i}" aria-label="${bandNames[i]}, grades ${labels[i]}">${labels[i]}</button>`).join('');
 $('#grade-buttons').innerHTML=GRADE_BANDS[state.band].map((g,i)=>`<button class="grade-button grade-tone-${i} ${state.grade===g?'active':''}" data-grade="${g}" aria-pressed="${state.grade===g}">${g==='K'?'<span class="grade-emoji" aria-hidden="true">🌈</span>':g==='1'?'<span class="grade-emoji" aria-hidden="true">☀️</span>':''}<span>${gradeLabel(g)}</span><span class="grade-check">${icon('check')}</span></button>`).join('');
 document.body.classList.toggle('older-grades',Number(state.grade)>=6);
}
function renderYears() {
 const idx=GRADE_IDS.indexOf(state.grade);
 const pair=[state.grade,GRADE_IDS[idx+1] || GRADE_IDS[idx-1]];
 $('#year-panels').innerHTML=pair.map((grade,j)=> {
  const ts=['math','ela','science','hss','arts'].map(sub=>curriculum.topics.find(t=>t.grade===grade&&t.subject===sub)).filter(Boolean);
  return `<article class="year-panel ${j?'grade-one':''}"><img class="year-mascot" src="${assetURL(j?'bunny.webp':'fox.webp')}" alt="" width="140" height="160" loading="lazy"><div class="year-body"><div class="year-title"><h3>${gradeLabel(grade)}</h3><button class="round-button" data-year="${grade}" aria-label="Explore ${gradeLabel(grade)}">${icon('arrow')}</button></div><div class="quick-topics">${ts.map(t=>`<button class="quick-topic" data-quick="${t.id}"><span aria-hidden="true">${SUBJECT_STYLE[t.subject][5]}</span><span>${esc(grade==='K'?({math:'Counting',ela:'Letters',science:'Forces',hss:'Community',arts:'Art'}[t.subject]):grade==='1'?({math:'Add & subtract',ela:'Reading',science:'Sound',hss:'Our world',arts:'Art'}[t.subject]):t.title)}</span></button>`).join('')}</div></div></article>`;
 }).join('');
}
function switchView(v, scroll = true) {
  const subjects = v === 'subjects';
  state.view = subjects ? 'explore' : v;
  $('#child-view').hidden = state.view === 'parent'; $('#parent-view').hidden = state.view !== 'parent';
  $$('.navlink').forEach(b => { const current = b.dataset.nav === v; b.classList.toggle('selected', current); if (current) b.setAttribute('aria-current','page'); else b.removeAttribute('aria-current'); });
  if (state.view === 'parent') renderParent(); else renderChild();
  if (scroll) { if (subjects) scrollToElement('#subject-section'); else window.scrollTo({top:0,behavior:'instant'}); }
}
function scrollToElement(selector) { $(selector)?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'start'}); }
function resetFilters() { state.subject='all'; state.topic='all'; state.type='all'; state.device='all'; state.q=''; state.showAll=true; $('#search').value=''; }
function standardIds(g) { return [...new Set(g.topicIds.flatMap(id => curriculum.topics.find(t => t.id === id)?.standardIds || []))]; }
function evidenceLink(g) { return safeURL(g.review.adEvidenceUrl) || safeURL(curriculum.sourceRegister[g.review.adEvidenceSourceId]?.url); }
function openDetails(id) {
 const g=dataset.games.find(g=>g.id===id); if(!g)return;
 const isPub=g.review.status===PUB, isTeacher=g.review.status===TEACHER, p=platformInfo(g), [cost,costClass]=priceInfo(g), evidence=evidenceLink(g);
 const title=PRETTY[g.id]?.[0] || g.title;
 const desc=PRETTY[g.id]?.[1] || g.description;
 const grade=gradeSummary(g.grades);
 const dialog=$('#details'); dialog.classList.add('game-dialog');
 $('#detail-content').innerHTML=`
 <div class="popup-art">${gameArt(g)}<span class="popup-kicker">${icon('grownup')} Quick check</span><button class="close popup-close" id="close-details" aria-label="Close game details" autofocus>${icon('close')}</button></div>
 <div class="popup-main">
  <p class="popup-publisher">${esc(g.publisher)}</p><h2 id="detail-title">${esc(title)}</h2><p class="popup-description">${esc(desc)}</p>
  <div class="popup-meta">
   <div class="meta-item meta-device">${icon(p.icons[0])}<strong>${esc(p.label)}</strong><small>${g.platform==='app'?'Install needed':'No installation'}</small></div>
   <div class="meta-item meta-cost ${costClass}">${icon('coin')}<strong>${esc(cost)}</strong><small>${g.platform==='app'?'Check app pricing':'Publisher version'}</small></div>
   <div class="meta-item meta-grade">${icon('cap')}<strong>${esc(grade)}</strong><small>Suggested level</small></div>
  </div>
  <div class="popup-review ${isTeacher?'popup-review-teacher':''}">${icon(isPub||isTeacher?'shield':'info')}<span><strong>${isPub?'No ads · publisher claim':isTeacher?'Teacher verified':'Review pending'}</strong><small>${isTeacher?'Ads not independently checked':g.review.runtimeTested?'Local play-check recorded':'Not play-tested'}</small></span></div>
  <details class="popup-notes"><summary>${icon('info')} Grown-up notes <span class="notes-chevron">${icon('chevron')}</span></summary>
   <div class="popup-notes-body"><p><b>Device.</b> ${esc(g.access)}</p><p><b>Cost.</b> ${esc(g.priceLabel)}</p><p><b>Review.</b> ${esc(g.review.notes||'Review needed.')} A publisher claim is not a safety certification.</p><p><b>Learning.</b> ${esc(g.learningSuggestion||'Explore with a grown-up.')} ${esc(g.alignmentStatus||'Suggested practice only.')}</p><p class="codes">${esc(standardIds(g).join(' · '))||'Exact standard mapping pending.'}</p><p><b>Evidence scope.</b> ${esc(g.review.evidenceScope||'Pending')}<br>Reviewed: ${esc(g.review.reviewedOn||'Not yet')}. Links and terms may change.</p><p>${isTeacher?'Thumbnail supplied with the Learning Hub.': 'The thumbnail is a decorative illustration, not a game screenshot.'}</p>${evidence?`<a class="mini-source" href="${esc(evidence)}" target="_blank" rel="noopener noreferrer">Advertising policy ${icon('external')}</a>`:''}${srcLinks(g.sourceIds)}</div>
  </details>
 </div>
 <div class="popup-footer">
  ${state.view==='parent'&&!isPub&&!isTeacher?`<button class="outline" data-review="${g.id}">Review record</button>`:''}
  <a class="primary popup-launch" href="${esc(g.url)}" target="_blank" rel="noopener noreferrer">${icon(g.platform==='app'?'phone':'play')}${g.platform==='app'?'App page':(isPub||isTeacher)?(g.kind==='Video'?'Watch video':g.kind==='Interactive simulation'?'Explore':g.kind==='Mini-game'?'Play game':'Open resource'):'Review link'}${icon('external')}</a>
  <small class="external-caption">${esc(new URL(g.url).hostname)} · New tab</small>
 </div>`;
 if(!dialog.open)dialog.showModal();
 dialog.scrollTop=0;document.body.classList.add('modal-open');
}
function parentMap(){let a=approved(),q=dataset.games.filter(g=>g.review.status==='needs_review'),teach=dataset.games.filter(g=>g.review.status===TEACHER);return `<div class="notice"><b>This is an editorial catalogue map, not the full California standards text.</b> K/1 selected mappings are retained. Grades 2–12 have starter topic shelves; exact codes and full coverage need review. High-school course shelves are not fixed grade requirements.</div><div class="stats"><div class="stat"><strong>${curriculum.topics.length}</strong>topic shelves · K–12</div><div class="stat"><strong>${dataset.games.filter(g=>g.review.status===PUB).length}</strong>publisher no-ad claims</div><div class="stat"><strong>${teach.length}</strong>teacher picks · ad check pending</div><div class="stat"><strong>${q.length}</strong>hidden candidates</div></div><div class="parent-tools"><label class="sr-only" for="parent-grade">Curriculum grade</label><select id="parent-grade">${GRADE_IDS.map(g=>`<option value="${g}" ${state.grade===g?'selected':''}>${gradeLabel(g)}</option>`).join('')}</select><label class="sr-only" for="parent-subject">Curriculum subject</label><select id="parent-subject"><option value="all">All subjects</option>${curriculum.subjects.map(s=>`<option value="${s.id}" ${state.parentSubject===s.id?'selected':''}>${s.name}</option>`).join('')}</select><button class="outline" id="export-curriculum">Export map</button></div>`+curriculum.subjects.filter(s=>state.parentSubject==='all'||s.id===state.parentSubject).map(s=>`<section class="topic-group"><h2>${icon(s.icon)}${s.name}<span>${esc(s.framework)}</span></h2>${curriculum.topics.filter(t=>t.subject===s.id&&t.grade===state.grade).map(t=>{let apps=a.filter(g=>g.topicIds.includes(t.id)),pending=q.filter(g=>g.topicIds.includes(t.id));return `<div class="topic-row"><div><h3>${esc(t.title)}</h3><p>${esc(t.goal)}</p><div class="codes">${t.standardIds.length?esc(t.standardIds.join(' · ')):esc(t.mappingLevel)}</div><details><summary style="font-size:11px;min-height:29px">Activity & sources</summary><p>${esc(t.offscreenFollowup)}</p>${srcLinks(t.sourceIds)}</details></div><div class="coverage"><span class="tag ${apps.length?'':'wait'}">${apps.length?apps.length+' activities':'No reviewed link'}</span>${apps.map(g=>`<br><button class="textbutton" style="min-height:31px;font-size:11px;text-align:left" data-open="${g.id}">${esc(g.title)} ↗</button>`).join('')}${pending.length?`<p>${pending.length} candidate${pending.length===1?'':'s'} in the review queue</p>`:''}</div></div>`}).join('')}</section>`).join('')+`<section class="topic-group"><h2>Across the learning day</h2>${curriculum.supportTracks.map(t=>`<div class="topic-row"><div><h3>${esc(t.title)}</h3><p>${esc(t.note)}</p>${srcLinks(t.sourceIds)}</div></div>`).join('')}<div class="topic-row"><div><h3>Mathematical practices</h3><p>${curriculum.mathPractices.map((p,i)=>`${i+1}. ${esc(p)}`).join('; ')}.</p></div></div></section>`}
function reviewList(){
 const pending=dataset.games.filter(g=>g.review.status==='needs_review');
 const teacher=dataset.games.filter(g=>g.review.status===TEACHER);
 return `<div class="notice"><b>Separate checks.</b> Hidden candidates await an adult's review. Hub selections are visible because the owner reports teacher verification, but their advertising, logins and external destinations have not been independently checked. Teacher verification does not mean ad-free.</div>`+
 `<h2 class="review-heading">Hidden candidates · ${pending.length}</h2>`+
 pending.map(g=>`<div class="review-row"><div><h3>${esc(g.title)}</h3><p>${esc(g.publisher)} · ${esc(g.kind)} · ${esc(g.priceLabel)}</p><p style="margin-top:7px">${esc(g.review.notes)}</p></div><button class="textbutton" data-open="${g.id}">Review ${icon('arrow')}</button></div>`).join('')+
 `<h2 class="review-heading">Teacher picks · ${teacher.length} (ad check pending)</h2>`+
 teacher.map(g=>`<div class="review-row"><div><h3>${esc(g.title)}</h3><p>${esc(g.hubSection||'Learning Hub')} · ${esc(g.gradeEvidence||'Editorial grade suggestion')}</p></div><button class="textbutton" data-open="${g.id}">Details ${icon('arrow')}</button></div>`).join('');
}
function manage() {
  const e = dataset.games.find(g => g.id === state.editId);
  return `<p class="manage-intro"><b>Your local catalogue draft.</b> Add or update a game, then export <code>games.json</code>. Edits stay in this browser; they do not publish to GitHub. New and edited links return to the review queue.</p>
    <div class="parent-tools"><button class="outline" id="export-games">Export games</button><button class="outline" id="import-games">Import games</button><input type="file" accept=".json,application/json" id="import-file" hidden><button class="textbutton" id="reset-draft">Restore original</button></div>
    <form class="editor" id="game-form"><h2>${e ? 'Edit game' : 'Add game'}</h2><div class="form-grid">
    <label class="field">Activity title<input name="title" required maxlength="100" value="${esc(e?.title || '')}" placeholder="Bunny’s Picnic Boat"></label>
    <label class="field">Publisher / creator<input name="publisher" required maxlength="100" value="${esc(e?.publisher || '')}" placeholder="Who made this game?"></label>
    <label class="field full">Official game link (HTTPS)<input name="url" type="url" required maxlength="2048" value="${esc(e?.url || '')}" placeholder="https://…"></label>
    <fieldset class="field"><legend>Subjects</legend><div class="checkrow">${curriculum.subjects.map(s => `<label><input type="checkbox" name="subjects" value="${s.id}" ${e ? e.subjects.includes(s.id) ? 'checked' : '' : s.id === 'ela' ? 'checked' : ''}>${esc(s.short)}</label>`).join('')}</div></fieldset>
    <fieldset class="field"><legend>Grade</legend><div class="checkrow">${GRADE_IDS.map(x => `<label><input type="checkbox" name="grades" value="${x}" ${e ? e.grades.includes(x) ? 'checked' : '' : x === 'K' ? 'checked' : ''}>${gradeLabel(x)}</label>`).join('')}</div></fieldset>
    <label class="field">Activity type<select name="kind">${['Mini-game','Game adventure','Activity collection','Learning app','Creative tool','Creative app','Interactive simulation'].map(k => `<option ${e?.kind === k ? 'selected' : ''}>${k}</option>`).join('')}</select></label>
    <label class="field">Where it plays<select name="playMode"><option value="browser" ${e?.platform === 'browser' ? 'selected' : ''}>Browser game</option><option value="mobile" ${e?.platform === 'app' && !e.devices?.includes('desktop') && !e.id.endsWith('-ios') ? 'selected' : ''}>Mobile app — phone / tablet</option><option value="ios" ${e?.id.endsWith('-ios') ? 'selected' : ''}>iPhone / iPad app</option><option value="desktop" ${e?.devices?.includes('desktop') ? 'selected' : ''}>Desktop app — install</option><option value="unknown">App — device support needs checking</option></select><small>Keep app and browser versions as separate records when their prices or advertising policies differ.</small></label>
    <label class="field">Price / purchases<input name="priceLabel" required maxlength="120" value="${esc(e?.priceLabel || '')}" placeholder="Free / free trial · paid unlock"></label>
    <label class="field">Setup / supported devices<input name="access" required maxlength="160" value="${esc(e?.access || '')}" placeholder="Browser · no account / iPhone & iPad"></label>
    <label class="field full">Short child-facing description<input name="description" required maxlength="120" value="${esc(e?.description || '')}" placeholder="Count carrots with a bunny."></label>
    <label class="field full">Curriculum topics (optional; multiple selection)<select name="topicIds" id="editor-topics" multiple>${topicOptions(e?.topicIds || [], e?.grades || ['K'], e?.subjects || ['ela'])}</select><small>Only topics matching the selected grades and subjects are offered. Ctrl/Cmd-click to select more than one.</small></label>
    <label class="field full">Curator notes<textarea name="notes" maxlength="1500">${esc(e?.review.notes || 'Check advertising, purchases, device support and learning fit before approval.')}</textarea></label>
    </div><div class="form-actions"><button class="primary" type="submit">${e ? 'Save for review' : 'Save for review'}</button>${e ? '<button class="textbutton" id="cancel-edit" type="button">Cancel editing</button>' : ''}</div><p class="local-message">The grown-up area is not password-protected. Local editing is not an authenticated publishing system.</p></form>
    <h2 style="margin:28px 0 14px;font-size:23px">Your catalogue · ${dataset.games.length} entries</h2>
    ${dataset.games.map(g => `<div class="review-row"><div><h3>${esc(g.title)}</h3><p>${esc(g.publisher)} · ${g.review.status === PUB ? 'Publisher no-ad claim recorded' : g.review.status === TEACHER ? 'Teacher verified · ad status unchecked' : 'Review pending'} · ${platformInfo(g).label}</p></div><div class="row-actions"><button class="textbutton" data-open="${g.id}">Details</button><button class="outline" data-edit="${g.id}">Edit</button>${g.review.status !== PUB && g.review.status !== TEACHER ? `<button class="outline" data-review="${g.id}">Review</button>` : ''}<button class="textbutton danger-button" data-delete="${g.id}" aria-label="Remove ${esc(g.title)} from local catalogue">Remove</button></div></div>`).join('')}`;
}
function topicOptions(selected, grades, subjects) {
  return curriculum.topics.filter(t => grades.includes(t.grade) && subjects.includes(t.subject)).map(t => `<option value="${t.id}" ${selected.includes(t.id) ? 'selected' : ''}>${t.grade === 'K' ? 'KG' : 'G'+t.grade} · ${esc(t.title)}</option>`).join('');
}
function sourcePage() {
  return `<div class="notice"><b>This is a working catalogue, not a safety certification or complete course.</b> Some activities have publisher no-ad evidence. Imported Learning Hub links have user-reported teacher verification, with advertising and live destination checks still pending. External activities have not been independently play-tested.</div><section class="editor"><h2>About this little library</h2>
    <div class="source-block"><h3>The curriculum</h3><p class="manage-intro">The supplied map has ${curriculum.topics.length} editorial topic clusters across California Kindergarten through Grade 12, not a complete verbatim standards database or state-approved course. Standards references and off-screen follow-ups are retained from the original research. California Grade 1 is not the same level as UK Year 1. Arts, PE and some support areas need more detailed mapping. Games support practice; they do not establish mastery.</p></div>
    <div class="source-block"><h3>What device icons mean</h3><p class="manage-intro">A globe means the linked resource opens in a browser. Phone and tablet icons mean an app installation, not browser play. The iPhone / iPad badge applies only to that specific app record. App compatibility may include additional supported devices; the official listing has the final requirements. An advertising policy for an app is not automatically evidence for its browser version.</p></div>
    <div class="source-block"><h3>Evidence, not badges of certainty</h3><p class="manage-intro">The child cards never use blanket “safe” or “ad-free” badges for teacher-selected links. Publisher no-ad statements and teacher-verified selections are labeled separately, with their source, date and scope. No-ad does not mean no purchases, analytics, accounts, sponsor messages, or external links. Recheck the exact destination before a child uses it. The local review form records a curator’s check, not an independent audit.</p></div>
    <div class="source-block"><h3>Privacy & editing</h3><p class="manage-intro">Wonderwood loads no advertisements, remote fonts, or third-party game embeds. An optional cookie-free Cloudflare Web Analytics beacon counts aggregate site visits and performance only after the publisher connects it for the live website; it is disabled for local/portable copies. No child names, individual game clicks, grade selections or search terms are sent to analytics. Favorites and editable drafts use this browser’s local storage. Export JSON before clearing site data or changing devices. The Parent/Teacher area is not authentication. Edits and approval are local only; there is no GitHub sync or deployment.</p></div>
    <div class="source-block"><h3>Artwork & accessibility</h3><p class="manage-intro">Woodland artwork comes from the approved design concept. Wonderwood originals use decorative game illustrations. Imported Hub activities display their supplied source thumbnails; these are not endorsements or independently verified screenshots. All core controls are real HTML buttons. There are keyboard focus indicators, native dialogs, reduced-motion support and no autoplay sound. Real screen-reader and touch-device review remains necessary.</p></div>
    <div class="source-block"><h3>Source register</h3>${Object.values(curriculum.sourceRegister).map(s => `<div class="source-item"><strong>${esc(s.title)}</strong>${safeURL(s.url) ? `<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.url)}</a>` : ''}</div>`).join('')}</div></section>`;
}
function analyticsPage() {
  const configured = document.querySelector('meta[name="wonderwood-analytics"]')?.content === 'configured';
  const live = configured && location.protocol === 'https:' && location.hostname === 'sabersara.github.io' && location.pathname.startsWith('/website-games-catalogue/');
  const status = live ? 'Beacon enabled' : configured ? 'Preview · tracking off here' : 'Setup needed';
  const message = live
    ? 'Wonderwood is configured to send aggregate site traffic to Cloudflare Web Analytics. Confirm actual counts in your private dashboard.'
    : configured ? 'This preview is not tracked. The beacon runs only on the published Wonderwood GitHub Pages URL.'
      : 'Add your free Cloudflare Web Analytics token to GitHub to start counting visits. No tracker runs until then.';
  const metrics = [
    ['👀','Visits','How many visits the website receives'],
    ['📈','Page views','How many pages have been opened'],
    ['🔗','Traffic sources','Where visits come from'],
    ['📱','Devices','Mobile, tablet or desktop'],
    ['🌍','Countries','Broad country-level breakdown'],
    ['⚡','Page speed','Loading and Core Web Vitals']
  ];
  return `<section class="analytics-board" aria-labelledby="analytics-title">
    <div class="analytics-head"><div><span class="eyebrow">Grown-ups · Visitor insights</span><h2 id="analytics-title">📊 Website analytics</h2><p>${message}</p></div><span class="analytics-status ${live?'analytics-connected':''}">${live?'● ':''}${status}</span></div>
    <div class="analytics-grid">${metrics.map(([emoji,title,info])=>`<a class="analytics-card" href="https://dash.cloudflare.com/" target="_blank" rel="noopener noreferrer" aria-label="${title} — open Cloudflare dashboard"><span class="analytics-card-icon" aria-hidden="true">${emoji}</span><strong>${title}</strong><small>${info}</small><span class="analytics-card-foot">View dashboard ↗</span></a>`).join('')}</div>
    <div class="analytics-actions"><a class="primary" href="https://dash.cloudflare.com/" target="_blank" rel="noopener noreferrer">Open live dashboard ${icon('external')}</a><a class="outline" href="https://github.com/SaberSara/website-games-catalogue/blob/main/docs/ANALYTICS.md" target="_blank" rel="noopener noreferrer">Setup guide ${icon('external')}</a></div>
    <p class="analytics-honesty"><strong>No made-up visitor numbers.</strong> Cloudflare owns the real counts and keeps them in your account. Wonderwood cannot retrieve those private totals directly from this static page. Reports start only after setup.</p>
    <details class="analytics-privacy"><summary>🔒 Privacy for children</summary><p>Site-wide traffic only. No child names, accounts, cookies, persistent analytics IDs, game-click events, grade choices, search terms, or individual learning history are sent by Wonderwood's analytics integration. Cloudflare may measure aggregated visits, referral hosts, approximate countries, device categories and loading performance. The browser's existing favorites and local editor stay on the device. Review the site's privacy disclosures and legal obligations before use with children.</p></details>
  </section>`;
}
function renderParent() {
  $$('[data-tab]').forEach(b => { const active = b.dataset.tab === state.tab; b.classList.toggle('active', active); if (active) b.setAttribute('aria-current','page'); else b.removeAttribute('aria-current'); });
  $('#parent-content').innerHTML = state.tab === 'curriculum' ? parentMap() : state.tab === 'review' ? reviewList() : state.tab === 'manage' ? manage() : state.tab === 'analytics' ? analyticsPage() : sourcePage();
}
function downloadJSON(data, name) {
  const blob = new Blob([JSON.stringify(data, null, 2) + '\n'], {type:'application/json'});
  const url = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = url; a.download = name; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}
function saveDraft(message) {
  const ok = store.set(DRAFT_KEY, dataset);
  notify(ok ? message || 'Saved in this browser. Export the JSON to keep or publish your changes.' : 'Browser storage is unavailable. Export your JSON before closing this page.');
}
function openReview(id) {
  const g = dataset.games.find(g => g.id === id); if (!g || state.view !== 'parent') return;
  $('#details').classList.remove('game-dialog');
  $('#detail-content').innerHTML = `<div class="modal-head"><div><p class="eyebrow">Local curator review</p><h2 id="detail-title">${esc(g.title)}</h2></div><button class="close" id="close-details" aria-label="Close review">${icon('close')}</button></div><div class="modal-body"><p>Approve only after you have checked this exact game and recorded the publisher’s no-ad evidence. This changes only your local draft.</p><p style="margin:12px 0"><a href="${esc(g.url)}" target="_blank" rel="noopener noreferrer">Open official game for review ↗</a></p><form id="review-form" data-id="${g.id}"><div class="form-grid"><label class="field full">Publisher advertising-policy URL<input name="adEvidenceUrl" type="url" required maxlength="2048" value="${esc(evidenceLink(g) || '')}" placeholder="https://publisher.example/privacy"></label><label class="field full">Exact scope of the evidence<input name="evidenceScope" required maxlength="250" placeholder="e.g. iPhone / iPad app only" value="${esc(g.review.evidenceScope || '')}"></label><label class="field full">Review notes<textarea name="notes" required maxlength="1500">${esc(g.review.notes || '')}</textarea></label><label class="checkrow field full"><span><input type="checkbox" name="claim" required> I found an explicit publisher no-ad statement for this version.</span></label><label class="checkrow field full"><span><input type="checkbox" name="tested" required> I checked the exact game, purchases, controls, platform and learning fit.</span></label></div><div class="form-actions"><button class="primary" type="submit">Approve in local draft</button></div></form></div>`;
  if (!$('#details').open) $('#details').showModal(); document.body.classList.add('modal-open');
}
function pop(node, name = 'press-pop') {
  if (!node || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  node.classList.remove(name); void node.offsetWidth; node.classList.add(name);
  setTimeout(() => node.classList.remove(name), 550);
}
function toggleFavorite(id) {
  favorites = favorites.includes(id) ? favorites.filter(x => x !== id) : [...favorites,id];
  const ok = store.set(FAVORITES_KEY, favorites), saved = favorites.includes(id);
  if (state.view === 'favorites') {
    renderGames(); const focus = $(`[data-save="${id}"]`) || $('.save') || $('#empty-reset'); focus?.focus({preventScroll:true});
  } else {
    const button = $(`[data-save="${id}"]`), g = dataset.games.find(x => x.id === id);
    if (button) { button.classList.toggle('saved',saved); button.setAttribute('aria-pressed',saved); button.setAttribute('aria-label',`${saved ? 'Remove from' : 'Add to'} favorites: ${g?.title || id}`); pop(button,'favorite-pop'); }
    const count = favorites.filter(id => approved().some(g => g.id === id)).length;
    $('#fav-count').textContent = count; $('#fav-count').hidden = !count;
  }
  notify(ok ? saved ? 'A new favorite! ⭐' : 'Removed from your favorites.' : 'Favorites saved for this session only.');
}
function restoreActionFocus(attribute, value) {
  const n = document.querySelector(`[${attribute}="${value}"]`); n?.focus({preventScroll:true}); pop(n);
}
document.addEventListener('click', e => {
  const n = e.target.closest('button'); if (!n || n.disabled) return;
  pop(n);
  if (n.dataset.nav) {
    if (n.dataset.parentTab) state.tab = n.dataset.parentTab;
    if (n.dataset.nav === 'explore') { resetFilters(); state.showAll = false; }
    if (n.dataset.nav === 'favorites') { resetFilters(); }
    switchView(n.dataset.nav); return;
  }
  if (n.dataset.band !== undefined) { state.band=Number(n.dataset.band); state.grade=GRADE_BANDS[state.band][0]; state.topic='all'; renderChild(); restoreActionFocus('data-band',String(state.band)); return; }
  if (n.dataset.grade) { const grade=n.dataset.grade; state.grade=grade; state.topic='all'; renderChild(); restoreActionFocus('data-grade',grade); return; }
  if (n.dataset.subject) { state.subject=state.subject===n.dataset.subject?'all':n.dataset.subject; state.topic='all'; state.showAll=true; renderChild(); restoreActionFocus('data-subject',n.dataset.subject); return; }
  if (n.dataset.topic) { state.topic=n.dataset.topic; renderTopics(); renderGames(); restoreActionFocus('data-topic',n.dataset.topic); return; }
  if (n.dataset.type) { state.type=n.dataset.type; state.showAll=true; renderGames(); return; }
  if (n.dataset.save) { toggleFavorite(n.dataset.save); return; }
  if (n.dataset.open) { openDetails(n.dataset.open); return; }
  if (n.dataset.quick) {
    const t=curriculum.topics.find(x=>x.id===n.dataset.quick); if(!t)return;
    resetFilters(); state.grade=t.grade; state.subject=t.subject; state.topic=t.id; switchView('explore',false); scrollToElement('#browse'); return;
  }
  if (n.dataset.year) { resetFilters(); state.grade=n.dataset.year; switchView('explore',false); scrollToElement('#browse'); return; }
  if (n.dataset.tab) { state.tab=n.dataset.tab; state.editId=null; renderParent(); return; }
  if (n.dataset.edit) { state.tab='manage'; state.editId=n.dataset.edit; renderParent(); scrollToElement('#game-form'); $('#game-form [name="title"]').focus({preventScroll:true}); return; }
  if (n.dataset.review) { openReview(n.dataset.review); return; }
  if (n.dataset.delete) {
    const g=dataset.games.find(x=>x.id===n.dataset.delete);
    if(g && confirm(`Remove “${g.title}” from this local draft? Export first to keep a backup.`)) { dataset.games=dataset.games.filter(x=>x.id!==g.id); state.editId=null; saveDraft('Removed from your local draft. Export to keep the updated catalogue.'); renderParent(); } return;
  }
  if (n.id==='view-all') { state.showAll=true; renderGames(); return; }
  if (n.id==='all-subjects') { state.subject='all'; state.topic='all'; renderChild(); return; }
  if (['reset-filters','empty-reset'].includes(n.id)) { resetFilters(); state.view='explore'; switchView('explore',false); scrollToElement('#browse'); return; }
  if (n.id==='clear-search') { state.q=''; $('#search').value=''; renderGames(); $('#search').focus(); return; }
  if (n.id==='close-details') { $('#details').close(); return; }
  if (n.id==='export-games') { downloadJSON(dataset,'games.json'); return; }
  if (n.id==='export-curriculum') { downloadJSON(curriculum,'curriculum.json'); return; }
  if (n.id==='import-games') { $('#import-file').click(); return; }
  if (n.id==='cancel-edit') { state.editId=null; renderParent(); return; }
  if (n.id==='reset-draft' && confirm('Discard local edits and restore the supplied catalogue? Export first to keep your changes.')) { dataset=structuredClone(original); state.editId=null; saveDraft('Supplied catalogue restored in this browser.'); renderParent(); }
});
$('#search').addEventListener('input', e => {
  state.q=e.target.value; state.showAll=true;
  if(state.view==='parent') switchView('explore',false); else renderGames();
});
$('#search-form').addEventListener('submit',e=>{e.preventDefault();if(state.view==='parent')switchView('explore',false);scrollToElement('#browse');});
document.addEventListener('change', async e => {
  if (e.target.id==='device-filter') { state.device=e.target.value; state.showAll=true; renderGames(); }
  if (e.target.id==='parent-grade') { state.grade=e.target.value; renderParent(); }
  if (e.target.id==='parent-subject') { state.parentSubject=e.target.value; renderParent(); }
  if (e.target.closest('#game-form') && ['grades','subjects'].includes(e.target.name)) {
    const form=$('#game-form'), fd=new FormData(form); const selected=[...$('#editor-topics').selectedOptions].map(x=>x.value);
    $('#editor-topics').innerHTML=topicOptions(selected,fd.getAll('grades'),fd.getAll('subjects'));
  }
  if (e.target.id==='import-file') {
    const file=e.target.files[0]; if(!file)return;
    try {
      if(file.size>3_000_000)throw Error('The file is too large. Use a catalogue smaller than 3 MB.');
      const v=JSON.parse(await file.text());
      if(!validData(v))throw Error('Invalid catalogue. Check HTTPS links, unique IDs, supported grades/subjects, topic matches and review evidence.');
      if(confirm('Replace this browser’s local catalogue draft with the imported file?')) { dataset=structuredClone(v); state.editId=null; saveDraft('Catalogue imported into this browser.'); renderParent(); }
    } catch(err) { notify(err.message || 'Could not import the file. Your catalogue was not changed.'); }
    finally { if($('#import-file'))$('#import-file').value=''; }
  }
});
document.addEventListener('submit',e=>{
  if(e.target.id==='game-form') {
    e.preventDefault(); const fd=new FormData(e.target), data=Object.fromEntries(fd.entries());
    const subjects=fd.getAll('subjects'), grades=fd.getAll('grades'), topicIds=fd.getAll('topicIds'), url=safeURL(data.url);
    if(!url || !subjects.length || !grades.length) { notify('Use an HTTPS link, at least one subject and at least one grade.'); return; }
    const existing=dataset.games.find(x=>x.id===state.editId), mode=data.playMode;
    const slug=data.title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'game';
    const id=existing?.id || `${slug}-${Date.now().toString(36)}`;
    const samePlatform=existing && (mode==='browser' ? existing.platform==='browser' : existing.platform==='app');
    const devices=mode==='browser'?['browser']:mode==='ios'?['ios']:mode==='desktop'?['desktop']:mode==='unknown'?['unknown']:samePlatform&&existing.devices?.length?existing.devices:['mobile'];
    const g={...(existing||{}),id,title:data.title.trim(),publisher:data.publisher.trim(),url,subjects,grades,topicIds,kind:data.kind,platform:mode==='browser'?'browser':'app',devices,
      priceLabel:data.priceLabel.trim(),access:data.access.trim(),description:data.description.trim(),sourceIds:existing?.sourceIds||[],featured:existing?.featured||false,
      art:existing?.art||'letters',alignmentStatus:'Editorial practice mapping; updated record needs review.',learningSuggestion:existing?.learningSuggestion||'',
      review:{status:'needs_review',reviewedOn:null,method:'Locally edited draft',runtimeTested:false,adEvidenceSourceId:null,evidenceScope:'',notes:data.notes}};
    const next={...dataset,games:existing?dataset.games.map(x=>x.id===id?g:x):[...dataset.games,g]};
    if(!validData(next)){notify('Please check all fields and topic mappings. The draft has not changed.');return;}
    dataset=next; state.editId=null; saveDraft('Saved to the review queue. Review this record before adding it to the child catalogue.'); renderParent();
  }
  if(e.target.id==='review-form') {
    e.preventDefault(); const fd=new FormData(e.target), g=dataset.games.find(x=>x.id===e.target.dataset.id), evidence=safeURL(fd.get('adEvidenceUrl'));
    if(!g || state.view!=='parent' || !evidence || !fd.has('claim') || !fd.has('tested')) { notify('Complete the evidence and both review checks.'); return; }
    g.review={status:PUB,reviewedOn:new Date().toISOString().slice(0,10),method:'Local curator attestation; not an independent certification',runtimeTested:true,
      adEvidenceSourceId:null,adEvidenceUrl:evidence,evidenceScope:String(fd.get('evidenceScope')).trim(),notes:String(fd.get('notes')).trim()};
    $('#details').close(); saveDraft('Approved in this local draft. Export games to keep your review.'); renderParent();
  }
});
$('#details').addEventListener('close',()=>{document.body.classList.remove('modal-open');$('#details').classList.remove('game-dialog');});
$('#details').addEventListener('click',e=>{if(e.target===$('#details')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
hydrateIcons(); renderChild();

let resizeTimer; window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(state.view!=='parent')renderGames();},150);});
