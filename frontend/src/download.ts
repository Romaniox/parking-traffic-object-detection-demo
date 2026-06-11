import type { DetectionBox } from './api/client'

// Set to true to draw class name + confidence labels on downloaded images.
// Mirrors the SHOW_BOX_LABELS flag in Canvas.tsx (on-screen overlay).
const DOWNLOAD_BOX_LABELS = false

// Set to true to draw a large count badge (e.g. "12 car") in the top-right
// corner of the downloaded image.
const DOWNLOAD_COUNT_BADGE = true

// ─── Pure helpers (exported for unit tests) ──────────────────────────────────

/** Returns the most frequent class name among boxes; ties broken alphabetically. */
export function dominantClass(boxes: DetectionBox[]): string {
  const counts = new Map<string, number>()
  for (const b of boxes) counts.set(b.class, (counts.get(b.class) ?? 0) + 1)
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .at(0)![0]
}

// ─── Private helpers ─────────────────────────────────────────────────────────

function accentColor(): string {
  const v = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()
  return v || '#2563eb'
}

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = url
  })
}

// ─── Main export ─────────────────────────────────────────────────────────────

/** Render the original image with detection boxes drawn on it and download as PNG. */
export async function downloadAnnotated(imageUrl: string, boxes: DetectionBox[]): Promise<void> {
  const img = await loadImage(imageUrl)
  const canvas = document.createElement('canvas')
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.drawImage(img, 0, 0)

  const accent = accentColor()
  const stroke = Math.max(2, Math.round(img.naturalWidth / 600))
  const fontSize = Math.max(14, Math.round(img.naturalWidth / 100))
  ctx.lineWidth = stroke
  ctx.strokeStyle = accent
  ctx.font = `${fontSize}px ui-sans-serif, system-ui, sans-serif`

  for (const b of boxes) {
    const x = b.x * img.naturalWidth
    const y = b.y * img.naturalHeight
    const w = b.w * img.naturalWidth
    const h = b.h * img.naturalHeight
    ctx.strokeStyle = accent
    ctx.strokeRect(x, y, w, h)

    if (DOWNLOAD_BOX_LABELS) {
      const label = `${b.class} ${(b.conf * 100).toFixed(0)}%`
      const padX = stroke * 2
      const padY = stroke
      const labelH = fontSize + padY * 2
      const m = ctx.measureText(label)
      ctx.fillStyle = accent
      ctx.fillRect(x - stroke / 2, y - labelH, m.width + padX * 2, labelH)
      ctx.fillStyle = '#fff'
      ctx.fillText(label, x + padX - stroke / 2, y - padY * 1.5)
    }
  }

  // Count badge — large "12 car" label in the top-right corner.
  if (DOWNLOAD_COUNT_BADGE && boxes.length > 0) {
    const badgeText = `${boxes.length} ${dominantClass(boxes)}`
    const badgeFontSize = Math.max(40, Math.round(img.naturalWidth / 18))
    const padX = Math.round(badgeFontSize * 0.55)
    const padY = Math.round(badgeFontSize * 0.35)

    ctx.font = `bold ${badgeFontSize}px ui-sans-serif, system-ui, sans-serif`
    const textW = ctx.measureText(badgeText).width
    const badgeW = textW + padX * 2
    const badgeH = badgeFontSize + padY * 2
    const margin = stroke * 6
    const bx = img.naturalWidth - badgeW - margin
    const by = margin

    ctx.fillStyle = accent
    ctx.fillRect(bx, by, badgeW, badgeH)
    ctx.fillStyle = '#fff'
    // textBaseline default is 'alphabetic'; offset up slightly for visual centering
    ctx.fillText(badgeText, bx + padX, by + padY + badgeFontSize * 0.82)
  }

  const blob = await new Promise<Blob | null>((res) => canvas.toBlob(res, 'image/png'))
  if (!blob) return
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `detect_${Date.now()}.png`
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
