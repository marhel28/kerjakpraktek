import assert from 'node:assert/strict'
import { parse } from '@vue/compiler-sfc'
import fs from 'node:fs'
import path from 'node:path'

const filePath = path.resolve('app/pages/(public)/category/[...slug].vue')
const source = fs.readFileSync(filePath, 'utf8')
const parsed = parse(source)
const script = parsed.descriptor.scriptSetup?.content ?? ''
const template = parsed.descriptor.template?.content ?? ''

assert.ok(script.includes('popularProducts'), 'Must track popular products fallback')
assert.ok(template.includes('popularProducts'), 'Template must bind popular products')
console.log('✅ category [...slug].vue contract verified')
