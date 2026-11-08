import assert from 'node:assert/strict';
// Run against the frontend server: node tests/landing.http.mjs
const base = process.env.BASE_URL || 'http://127.0.0.1:3000';
const response = await fetch(base);
assert.equal(response.status, 200);
const html = await response.text();
for (const id of ['mission', 'features', 'benefits', 'availability', 'pricing']) {
  assert.ok(html.includes(`id="${id}"`), `Missing destination: ${id}`);
}
assert.equal((html.match(/class="feature-card"/g) || []).length, 3);
assert.equal((html.match(/class="benefit-trigger"/g) || []).length, 3);
assert.equal((html.match(/aria-expanded="true"/g) || []).length, 1);
assert.ok(html.includes('disabled="" aria-describedby="trial-note"'));
assert.ok(html.includes('Historical market proxies; 20% is an unverified savings target.'));
assert.ok(html.includes('AWAITING USER ASSET'));
assert.ok(html.includes('Newsletter signup is not available.'));
assert.ok(!html.includes('<form'));
for (const asset of ['planty_logo.svg', 'golden_harvest_tractor_at_sunset.png']) {
  assert.equal((await fetch(`${base}/assets/images/${asset}`)).status, 200);
}
console.log('PASS landing HTTP: sections, three features, accordion initial state, unavailable trial/newsletter, qualified metrics, asset responses');
