import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { parse } from '@vue/compiler-sfc'

const cardPath = path.resolve('app/components/CardPerItems.vue')
const source = fs.readFileSync(cardPath, 'utf8')
const parsed = parse(source)
const template = parsed.descriptor.template?.content ?? ''

// Validate interactive actions exist with accessible test hooks
assert.match(template, /data-action="wishlist"/, 'Wishlist button must have distinct action hook')
assert.match(template, /data-action="compare"/, 'Compare button must have distinct action hook')

// Verify that the product link does not enclose the action container
const nuxtLinkMatch = template.match(/<NuxtLink[\s\S]*?<\/NuxtLink>/)
assert.ok(nuxtLinkMatch, 'NuxtLink must exist')
assert.ok(!nuxtLinkMatch[0].includes('AddButtonWishlist'), 'Wishlist action must be outside NuxtLink')
assert.ok(!nuxtLinkMatch[0].includes('data-action="compare"'), 'Compare action must be outside NuxtLink')

assert.match(template, /data-test="price-main"/, 'Main price must carry explicit test hook')
assert.match(template, /data-test="trust-badges"/, 'Trust badge container must be present for verified signals')
console.log('✅ Component contract passed')
