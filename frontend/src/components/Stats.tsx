import type { DetectSuccess } from '../api/client'
import type { AppStatus } from '../types'

interface StatsProps {
  status: AppStatus
  result: DetectSuccess | null
}

const EMPTY: Record<AppStatus, string> = {
  idle: 'Upload an image to begin.',
  selected: 'Click "Detect objects" to start.',
  processing: 'Analysing image…',
  success: '',
  error: 'Results will appear after a successful detection.',
}

export function Stats({ status, result }: StatsProps) {
  const show = status === 'success' && result !== null

  return (
    <div className="stats">
      <div className="stats__head">
        <span className="label">Results</span>
      </div>

      <div className={`stats__total ${show ? 'is-on' : ''}`}>
        <div className="stats__total-label">Objects detected</div>
        <div className="stats__total-num">{show ? result.count : '—'}</div>
      </div>

      <div className="stats__classes">
        {show ? (
          result.objects.map((o) => (
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
