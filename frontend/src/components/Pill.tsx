import type { AppStatus } from '../types'
import { Icon } from './icons'

const TEXT: Record<AppStatus, string> = {
  idle: 'Ready',
  selected: 'Image selected',
  processing: 'Processing…',
  success: 'Done',
  error: 'Error',
}

export function Pill({ status }: { status: AppStatus }) {
  return (
    <span className={`pill pill--${status}`} aria-live="polite">
      {status === 'processing' ? (
        <span className="pill__spin">
          <Icon name="spinner" size={12} />
        </span>
      ) : (
        <span className="pill__dot" />
      )}
      <span>{TEXT[status]}</span>
    </span>
  )
}
