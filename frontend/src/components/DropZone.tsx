import { useRef, useState } from 'react'

import { Icon } from './icons'

const MAX_MB = 10

interface DropZoneProps {
  onFile: (file: File) => void
  error?: string | null
}

// Matches the backend ALLOWED_MIME_TYPES exactly.
// Note: 'image/jpg' is intentionally absent — it is non-standard and the
// backend rejects it too (only 'image/jpeg' is valid per RFC 2045).
function isAllowed(file: File): boolean {
  return ['image/jpeg', 'image/png'].includes(file.type)
}

export function DropZone({ onFile, error }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const cameraRef = useRef<HTMLInputElement>(null)
  const [armed, setArmed] = useState(false)
  const [warn, setWarn] = useState<string | null>(null)

  const handle = (files: FileList | null) => {
    const f = files?.[0]
    if (!f) return
    if (!isAllowed(f)) {
      setWarn('Only JPG, JPEG or PNG')
      return
    }
    setWarn(null)
    onFile(f)
  }

  return (
    <div
      className={`drop ${armed ? 'drop--armed' : ''} ${error || warn ? 'drop--error' : ''}`}
      onDragOver={(e) => {
        e.preventDefault()
        setArmed(true)
      }}
      onDragLeave={() => setArmed(false)}
      onDrop={(e) => {
        e.preventDefault()
        setArmed(false)
        handle(e.dataTransfer.files)
      }}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
      }}
    >
      <input
        ref={inputRef}
        data-testid="file-input"
        type="file"
        accept="image/jpeg,image/jpg,image/png"
        hidden
        onChange={(e) => handle(e.target.files)}
      />
      <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={(e) => handle(e.target.files)}
      />

      <div className="drop__icon">
        <Icon name="image" size={28} />
      </div>
      <div className="drop__title">Drop an image here</div>
      <div className="drop__sub">or click to select a&nbsp;file</div>

      <div className="drop__actions" onClick={(e) => e.stopPropagation()}>
        <button className="btn btn--ghost btn--sm" onClick={() => inputRef.current?.click()}>
          <Icon name="upload" size={14} /> Select file
        </button>
        <button
          className="btn btn--ghost btn--sm drop__camera"
          onClick={() => cameraRef.current?.click()}
        >
          <Icon name="camera" size={14} /> Camera
        </button>
      </div>

      <div className="drop__meta">JPG · JPEG · PNG · up to {MAX_MB} MB</div>

      {(warn || error) && (
        <div className="drop__err">
          <Icon name="alert" size={14} /> {warn || error}
        </div>
      )}
    </div>
  )
}
