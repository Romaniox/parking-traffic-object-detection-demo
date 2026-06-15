import { useEffect, useRef } from 'react'

import { MAX_ZOOM, MIN_ZOOM } from './components/ZoomControls'

// ─── Pure helpers (exported for unit tests) ──────────────────────────────────

/** Euclidean distance between two touch contact points. */
export function touchDistance(
  t1: { clientX: number; clientY: number },
  t2: { clientX: number; clientY: number },
): number {
  const dx = t2.clientX - t1.clientX
  const dy = t2.clientY - t1.clientY
  return Math.sqrt(dx * dx + dy * dy)
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

interface UsePinchZoomOptions {
  /** The scrollable / zoomable stage element. */
  stageRef: React.RefObject<HTMLElement | null>
  /** Whether there is content to interact with (disables listeners when null). */
  active: boolean
  /** Current zoom value — must be kept in sync via a ref so the handler reads fresh. */
  zoom: number
  setZoom: (updater: (z: number) => number) => void
  setPan: React.Dispatch<React.SetStateAction<{ x: number; y: number }>>
}

/**
 * Adds pinch-to-zoom and single-finger pan to a stage element.
 *
 * - 2 fingers  → pinch zoom (clamped to [MIN_ZOOM, MAX_ZOOM])
 * - 1 finger   → pan (only when zoomed in)
 *
 * Touch events call preventDefault() so the browser does NOT zoom the page.
 * Pair with `touch-action: none` on the stage element for full coverage.
 */
export function usePinchZoom({ stageRef, active, zoom, setZoom, setPan }: UsePinchZoomOptions) {
  // Keep a ref so event-handler closures always read the latest zoom.
  const zoomRef = useRef(zoom)
  useEffect(() => {
    zoomRef.current = zoom
  }, [zoom])

  useEffect(() => {
    const el = stageRef.current
    if (!el || !active) return

    // Gesture state
    let pinchInitialDist = 0
    let pinchInitialZoom = 1
    let panStart: { x: number; y: number; px: number; py: number } | null = null

    const onTouchStart = (e: TouchEvent) => {
      e.preventDefault() // block browser page-zoom / scroll

      if (e.touches.length === 2) {
        // Begin pinch
        pinchInitialDist = touchDistance(e.touches[0], e.touches[1])
        pinchInitialZoom = zoomRef.current
        panStart = null // cancel any in-progress pan
      } else if (e.touches.length === 1 && zoomRef.current > 1) {
        // Begin single-finger pan (only when zoomed in)
        const t = e.touches[0]
        panStart = { x: t.clientX, y: t.clientY, px: 0, py: 0 }
        // We'll capture the current pan position on the first move
      }
    }

    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault()

      if (e.touches.length === 2 && pinchInitialDist > 0) {
        // Pinch zoom
        const dist = touchDistance(e.touches[0], e.touches[1])
        const scale = dist / pinchInitialDist
        const next = +(pinchInitialZoom * scale).toFixed(2)
        setZoom(() => Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, next)))
      } else if (e.touches.length === 1 && panStart) {
        // Single-finger pan
        const t = e.touches[0]
        const dx = t.clientX - panStart.x
        const dy = t.clientY - panStart.y
        setPan((p) => ({ x: p.x + dx, y: p.y + dy }))
        panStart = { x: t.clientX, y: t.clientY, px: 0, py: 0 }
      }
    }

    const onTouchEnd = (e: TouchEvent) => {
      e.preventDefault()
      if (e.touches.length < 2) {
        pinchInitialDist = 0
      }
      if (e.touches.length === 0) {
        panStart = null
      }
    }

    el.addEventListener('touchstart', onTouchStart, { passive: false })
    el.addEventListener('touchmove', onTouchMove, { passive: false })
    el.addEventListener('touchend', onTouchEnd, { passive: false })
    el.addEventListener('touchcancel', onTouchEnd, { passive: false })

    return () => {
      el.removeEventListener('touchstart', onTouchStart)
      el.removeEventListener('touchmove', onTouchMove)
      el.removeEventListener('touchend', onTouchEnd)
      el.removeEventListener('touchcancel', onTouchEnd)
    }
  }, [active, stageRef, setZoom, setPan])
}
