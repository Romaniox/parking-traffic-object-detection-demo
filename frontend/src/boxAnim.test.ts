import { describe, expect, it } from 'vitest'

import { BOX_ANIM_MS, BOX_ANIM_TOTAL_MS, boxDelayMs } from './boxAnim'

describe('boxDelayMs', () => {
  it('first box has no delay; single box is immediate', () => {
    expect(boxDelayMs(0, 1)).toBe(0)
    expect(boxDelayMs(0, 10)).toBe(0)
  })

  it('all boxes finish within the 1s budget, regardless of count', () => {
    for (const n of [2, 7, 20, 50, 200]) {
      const last = boxDelayMs(n - 1, n)
      expect(last + BOX_ANIM_MS).toBeLessThanOrEqual(BOX_ANIM_TOTAL_MS)
    }
  })

  it('delays are monotonically increasing across boxes', () => {
    const n = 12
    for (let i = 1; i < n; i++) {
      expect(boxDelayMs(i, n)).toBeGreaterThan(boxDelayMs(i - 1, n))
    }
  })

  it('stays snappy for a few boxes (does not stretch to the full second)', () => {
    // With only 3 boxes the last one should start well before ~700ms.
    expect(boxDelayMs(2, 3)).toBeLessThan(300)
  })
})
