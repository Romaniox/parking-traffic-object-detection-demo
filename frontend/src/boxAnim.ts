// Box draw-in animation timing. All boxes finish within BOX_ANIM_TOTAL_MS so the
// reveal stays quick even with many detections, while staying smooth and staggered.
export const BOX_ANIM_MS = 150 // per-box draw duration
export const BOX_ANIM_TOTAL_MS = 500 // every box is fully drawn by this point
const BASE_STAGGER_MS = 30 // snappy gap when there are only a few boxes

/** Animation delay (ms) for the box at `index` given `total` boxes. */
export function boxDelayMs(index: number, total: number): number {
  if (total <= 1) return 0
  const budget = BOX_ANIM_TOTAL_MS - BOX_ANIM_MS
  const stagger = Math.min(BASE_STAGGER_MS, budget / (total - 1))
  return Math.round(index * stagger)
}
