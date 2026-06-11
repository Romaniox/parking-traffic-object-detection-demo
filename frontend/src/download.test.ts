import { describe, expect, it } from 'vitest'

import { dominantClass } from './download'
import type { DetectionBox } from './api/client'

function box(cls: string): DetectionBox {
  return { class: cls, conf: 0.9, x: 0, y: 0, w: 0.1, h: 0.1 }
}

describe('dominantClass', () => {
  it('returns the only class when all boxes are the same', () => {
    expect(dominantClass([box('car'), box('car'), box('car')])).toBe('car')
  })

  it('returns the most frequent class', () => {
    const boxes = [box('car'), box('person'), box('car'), box('car'), box('person')]
    expect(dominantClass(boxes)).toBe('car')
  })

  it('returns the first class alphabetically when counts tie', () => {
    // 'apple' and 'zebra' appear once each; alphabetically 'apple' < 'zebra'
    expect(dominantClass([box('zebra'), box('apple')])).toBe('apple')
  })

  it('handles a single box', () => {
    expect(dominantClass([box('bus')])).toBe('bus')
  })
})
