import { useEffect, useRef, useState } from 'react'

import type { DetectionBox } from '../api/client'
import { BOX_ANIM_MS, boxDelayMs } from '../boxAnim'
import type { AppStatus, CanvasView } from '../types'
import { usePinchZoom } from '../usePinchZoom'
import { DropZone } from './DropZone'
import { Icon } from './icons'
import { MAX_ZOOM, MIN_ZOOM, ZoomControls } from './ZoomControls'

// Per-box labels (class · confidence) are disabled for now. Set to true to
// bring them back — the rendering logic below is kept intact.
const SHOW_BOX_LABELS = false

// On-screen box stroke width (px) at zoom 1; scaled down as we zoom in so it
// stays crisp and doesn't hide detail.
const BASE_STROKE = 2.5
const MIN_STROKE = 0.6

interface CanvasProps {
  imageUrl: string | null
  boxes: DetectionBox[]
  view: CanvasView
  status: AppStatus
  zoom: number
  setZoom: (updater: (z: number) => number) => void
  resetZoom: () => void
  onSwitchView: (v: CanvasView) => void
  onUpload: (file: File) => void
  uploadError?: string | null
}

export function Canvas({
  imageUrl,
  boxes,
  view,
  status,
  zoom,
  setZoom,
  resetZoom,
  onSwitchView,
  onUpload,
  uploadError,
}: CanvasProps) {
  const stageRef = useRef<HTMLDivElement>(null)
  const drag = useRef<{ x: number; y: number } | null>(null)
  const [dragging, setDragging] = useState(false)
  const [pan, setPan] = useState({ x: 0, y: 0 })

  const hasResults = status === 'success' && boxes.length > 0
  const showBoxes = view === 'annotated' && status === 'success'

  // Reset pan when zoom returns to 1 or the image changes (intentional sync of
  // local view state to props).
  const atBaseZoom = zoom === 1
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPan({ x: 0, y: 0 })
  }, [imageUrl, atBaseZoom])

  // Pinch-to-zoom + single-finger pan on touch devices.
  // Prevents the browser from zooming the whole page on pinch.
  usePinchZoom({ stageRef, active: !!imageUrl, zoom, setZoom, setPan })

  // Mouse-wheel zoom over the canvas (the stage doesn't scroll, so plain wheel
  // is free to zoom).
  useEffect(() => {
    const el = stageRef.current
    if (!el || !imageUrl) return
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const dz = -e.deltaY * 0.0025
      setZoom((z) => Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, +(z + dz * z).toFixed(2))))
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [imageUrl, setZoom])

  // Mouse-only drag pan — touch pan is handled by usePinchZoom.
  const onPointerDown = (e: React.PointerEvent) => {
    if (e.pointerType === 'touch') return
    if (zoom <= 1 || !imageUrl) return
    drag.current = { x: e.clientX - pan.x, y: e.clientY - pan.y }
    setDragging(true)
    e.currentTarget.setPointerCapture(e.pointerId)
  }
  const onPointerMove = (e: React.PointerEvent) => {
    if (e.pointerType === 'touch') return
    if (!drag.current) return
    setPan({ x: e.clientX - drag.current.x, y: e.clientY - drag.current.y })
  }
  const onPointerUp = (e: React.PointerEvent) => {
    if (e.pointerType === 'touch') return
    drag.current = null
    setDragging(false)
    try {
      e.currentTarget.releasePointerCapture(e.pointerId)
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="canvas">
      {hasResults && (
        <div className="canvas__toolbar canvas__toolbar--tl">
          <div className="seg" role="tablist" aria-label="Просмотр">
            <button
              role="tab"
              aria-selected={view === 'original'}
              className={view === 'original' ? 'is-on' : ''}
              onClick={() => onSwitchView('original')}
            >
              Оригинал
            </button>
            <button
              role="tab"
              aria-selected={view === 'annotated'}
              className={view === 'annotated' ? 'is-on' : ''}
              onClick={() => onSwitchView('annotated')}
            >
              Аннотировано
            </button>
          </div>
        </div>
      )}

      {imageUrl && (
        <div className="canvas__toolbar canvas__toolbar--br">
          <ZoomControls zoom={zoom} setZoom={setZoom} reset={resetZoom} />
        </div>
      )}

      <div
        ref={stageRef}
        className={`canvas__stage ${status === 'processing' ? 'is-processing' : ''}`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        style={{
          cursor: zoom > 1 ? (dragging ? 'grabbing' : 'grab') : 'default',
          touchAction: 'none',
        }}
      >
        {!imageUrl && (
          <div className="canvas__empty">
            <DropZone onFile={onUpload} error={uploadError} />
          </div>
        )}

        {imageUrl && (
          <div
            className="canvas__pan"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transition: dragging ? 'none' : 'transform .18s cubic-bezier(.2,.7,.2,1)',
            }}
          >
            <img src={imageUrl} alt="" className="canvas__img" draggable={false} />

            {showBoxes && (
              <svg className="canvas__overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
                {boxes.map((b, i) => (
                  <rect
                    key={i}
                    x={b.x * 100}
                    y={b.y * 100}
                    width={b.w * 100}
                    height={b.h * 100}
                    fill="none"
                    stroke="var(--accent)"
                    strokeWidth={Math.max(MIN_STROKE, BASE_STROKE / zoom)}
                    vectorEffect="non-scaling-stroke"
                    style={{
                      animation: `boxIn ${BOX_ANIM_MS}ms ${boxDelayMs(i, boxes.length)}ms both`,
                    }}
                  />
                ))}
              </svg>
            )}

            {showBoxes && SHOW_BOX_LABELS && (
              <div className="canvas__labels" aria-hidden="true">
                {boxes.map((b, i) => (
                  <span
                    key={i}
                    className="bbox-label-wrap"
                    style={{
                      left: `${b.x * 100}%`,
                      top: `${b.y * 100}%`,
                      transform: `translateY(-100%) scale(${1 / zoom})`,
                      transformOrigin: 'left bottom',
                    }}
                  >
                    <span
                      className="bbox-label"
                      style={{ animation: `boxIn ${BOX_ANIM_MS}ms ${boxDelayMs(i, boxes.length)}ms both` }}
                    >
                      {b.class} · {(b.conf * 100).toFixed(0)}%
                    </span>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {status === 'processing' && (
          <div className="canvas__veil" role="status" aria-live="polite">
            <div className="scanline" />
            <div className="canvas__veil-content">
              <div className="spinner">
                <Icon name="spinner" size={20} />
              </div>
              <div className="canvas__veil-txt">Обнаружение объектов</div>
              <div className="canvas__veil-sub">Обычно 3–8 секунд</div>
            </div>
          </div>
        )}

        {status === 'error' && imageUrl && (
          <div className="canvas__error">
            <Icon name="alert" size={18} />
            <span>Не удалось обработать изображение</span>
          </div>
        )}
      </div>
    </div>
  )
}
