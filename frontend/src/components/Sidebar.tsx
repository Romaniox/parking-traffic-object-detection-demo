import type { DetectionBox } from '../api/client'
import type { Theme } from '../theme'
import type { AppStatus } from '../types'
import { Icon } from './icons'
import { Pill } from './Pill'
import { Stats } from './Stats'
import { ThemeToggle } from './ThemeToggle'

interface SidebarProps {
  status: AppStatus
  file: File | null
  boxes: DetectionBox[]
  errorMessage: string | null
  canProcess: boolean
  theme: Theme
  conf: number
  onConfChange: (v: number) => void
  onToggleTheme: () => void
  onProcess: () => void
  onDownload: () => void
  onDownloadJson: () => void
  onReset: () => void
}

function fmtBytes(n: number): string {
  if (!n) return '0 B'
  const k = 1024
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(n) / Math.log(k))
  return `${(n / k ** i).toFixed(i ? 1 : 0)} ${units[i]}`
}

export function Sidebar({
  status,
  file,
  boxes,
  errorMessage,
  canProcess,
  theme,
  conf,
  onConfChange,
  onToggleTheme,
  onProcess,
  onDownload,
  onDownloadJson,
  onReset,
}: SidebarProps) {
  const busy = status === 'processing'
  const showResults = status === 'success'

  return (
    <aside className="sidebar">
      <div className="side__head">
        <div className="brand">
          <div className="brand__mark" aria-hidden="true" />
          <div>
            <div className="brand__name">Detect</div>
            <div className="brand__sub">Object Detection</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Pill status={status} />
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </div>
      </div>

      {file && (
        <div className="file">
          <div className="file__icon">
            <Icon name="file" size={16} />
          </div>
          <div className="file__meta">
            <div className="file__name" title={file.name}>
              {file.name}
            </div>
            <div className="file__sub">
              {fmtBytes(file.size)} · {(file.type || 'image').replace('image/', '').toUpperCase()}
            </div>
          </div>
          <button className="icon-btn" onClick={onReset} aria-label="Remove and upload another">
            <Icon name="close" size={14} />
          </button>
        </div>
      )}

      <div className="cta">
        <button
          className="btn btn--primary btn--full btn--lg"
          onClick={onProcess}
          disabled={!canProcess || busy}
        >
          {busy ? (
            <>
              <span className="spinner spinner--sm">
                <Icon name="spinner" size={14} />
              </span>{' '}
              Processing…
            </>
          ) : (
            <>
              <Icon name="play" size={14} /> Detect objects
            </>
          )}
        </button>
        {status === 'error' && (
          <div className="cta__err">
            <Icon name="alert" size={13} />
            <span>{errorMessage || 'Something went wrong. Please try again.'}</span>
          </div>
        )}
      </div>

      <div className="divider" />

      <Stats status={status} boxes={boxes} />

      {showResults && (
        <>
          <div className="conf">
            <div className="conf__head">
              <span className="label">Confidence</span>
              <span className="conf__val">{conf.toFixed(2)}</span>
            </div>
            <input
              type="range"
              className="conf__slider"
              min="0.05"
              max="0.95"
              step="0.05"
              value={conf}
              aria-label="Confidence threshold"
              onChange={(e) => onConfChange(Number(e.target.value))}
            />
          </div>

          <div className="actions">
            <button className="btn btn--ghost btn--full" onClick={onDownload}>
              <Icon name="download" size={14} /> Download result
            </button>
            <button className="btn btn--ghost btn--full" onClick={onDownloadJson}>
              <Icon name="download" size={14} /> Download JSON
            </button>
            <button className="btn btn--ghost btn--sm btn--full" onClick={onReset}>
              <Icon name="refresh" size={14} /> New image
            </button>
          </div>
        </>
      )}
    </aside>
  )
}
