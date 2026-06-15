import { describe, expect, it } from 'vitest'

import { touchDistance } from './usePinchZoom'

describe('touchDistance', () => {
  it('returns 0 for the same point', () => {
    expect(touchDistance({ clientX: 10, clientY: 20 }, { clientX: 10, clientY: 20 })).toBe(0)
  })

  it('returns correct Euclidean distance (3-4-5 triangle)', () => {
    expect(touchDistance({ clientX: 0, clientY: 0 }, { clientX: 3, clientY: 4 })).toBe(5)
  })

  it('is commutative — order of fingers does not matter', () => {
    const a = { clientX: 100, clientY: 50 }
    const b = { clientX: 200, clientY: 150 }
    expect(touchDistance(a, b)).toBe(touchDistance(b, a))
  })

  it('handles negative coordinates', () => {
    expect(touchDistance({ clientX: -3, clientY: 0 }, { clientX: 0, clientY: -4 })).toBe(5)
  })
})
