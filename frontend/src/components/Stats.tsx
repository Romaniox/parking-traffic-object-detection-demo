import type { DetectSuccess } from '../api/client'
import type { AppStatus } from '../types'

interface StatsProps {
  status: AppStatus
  result: DetectSuccess | null
}

const EMPTY: Record<AppStatus, string> = {
  idle: 'Загрузите изображение, чтобы начать.',
  selected: 'Нажмите «Обработать изображение».',
  processing: 'Анализируем изображение…',
  success: '',
  error: 'Результаты появятся после успешной обработки.',
}

export function Stats({ status, result }: StatsProps) {
  const show = status === 'success' && result !== null

  return (
    <div className="stats">
      <div className="stats__head">
        <span className="label">Статистика</span>
      </div>

      <div className={`stats__total ${show ? 'is-on' : ''}`}>
        <div className="stats__total-label">Обнаружено объектов</div>
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
