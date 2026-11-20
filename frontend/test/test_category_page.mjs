import assert from 'node:assert/strict'

const url = 'http://localhost:3000/category/security-alarm/sensor-pir'
const res = await fetch(url)
assert.equal(res.status, 200, `Expected 200 OK, got ${res.status}`)

const html = await res.text()
assert.ok(html.includes('SENSOR PIR'), 'Page title or heading must include SENSOR PIR')
assert.ok(!html.includes('__nuxt_error'), 'Page must not render Nuxt error page')
assert.ok(!html.includes('500 Internal Server Error'), 'Page must not have 500 status in body')

console.log('✅ Category page test passed: 200 OK with valid SSR payload')
