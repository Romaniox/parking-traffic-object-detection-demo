import type { DetectionBox } from '../api/client'
import type { AppStatus } from '../types'

interface StatsProps {
  status: AppStatus
  boxes: DetectionBox[]
}

const EMPTY: Record<AppStatus, string> = {
  idle: 'Upload an image to begin.',
  selected: 'Click "Detect objects" to start.',
  processing: 'Analysing image…',
  success: '',
  error: 'Results will appear after a successful detection.',
}

export function Stats({ status, boxes }: StatsProps) {
  const show = status === 'success'

  const count = boxes.length
  const objMap = new Map<string, number>()
  for (const b of boxes) objMap.set(b.class, (objMap.get(b.class) ?? 0) + 1)
  const objects = [...objMap.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([cls, cnt]) => ({ class: cls, count: cnt }))

  return (
    <div className="stats">
      <div className="stats__head">
        <span className="label">Results</span>
      </div>

      <div className={`stats__total ${show ? 'is-on' : ''}`}>
        <div className="stats__total-label">Objects detected</div>
        <div className="stats__total-num">{show ? count : '—'}</div>
      </div>

      <div className="stats__classes">
        {show ? (
          objects.map((o) => (
            <div className="stats__row" key={o.class}>
              <span className="stats__swatch" aria-hidden="true" />
              <span className="stats__class">{o.class}</span>
              <span className="stats__count">{o.count}</span>
            </div>
          ))
        ) : (
          <div className="stats__empty">{EMPTY[status]}</div>
        )}
      </div>
    </div>
  )
}
