import { Icon } from './icons'

interface ZoomControlsProps {
  zoom: number
  setZoom: (updater: (z: number) => number) => void
  reset: () => void
}

export const MIN_ZOOM = 1
export const MAX_ZOOM = 5

export function ZoomControls({ zoom, setZoom, reset }: ZoomControlsProps) {
  return (
    <div className="zoom">
      <button
        className="zoom__btn"
        onClick={() => setZoom((z) => Math.max(MIN_ZOOM, +(z - 0.25).toFixed(2)))}
        aria-label="Уменьшить"
        disabled={zoom <= MIN_ZOOM}
      >
        <Icon name="minus" size={16} />
      </button>
      <button className="zoom__level" onClick={reset} aria-label="Сбросить масштаб" title="Сбросить">
        {Math.round(zoom * 100)}%
      </button>
      <button
        className="zoom__btn"
        onClick={() => setZoom((z) => Math.min(MAX_ZOOM, +(z + 0.25).toFixed(2)))}
        aria-label="Увеличить"
        disabled={zoom >= MAX_ZOOM}
      >
        <Icon name="plus" size={16} />
      </button>
    </div>
  )
}
