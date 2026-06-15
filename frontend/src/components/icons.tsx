import type { CSSProperties } from 'react'

export type IconName =
  | 'upload'
  | 'camera'
  | 'image'
  | 'plus'
  | 'minus'
  | 'download'
  | 'close'
  | 'play'
  | 'check'
  | 'alert'
  | 'spinner'
  | 'file'
  | 'refresh'
  | 'sun'
  | 'moon'

const PATHS: Record<IconName, React.ReactNode> = {
  upload: (
    <>
      <path d="M12 3v12" />
      <path d="m7 8 5-5 5 5" />
      <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </>
  ),
  camera: (
    <>
      <path d="M3 8a2 2 0 0 1 2-2h2l1.5-2h7L17 6h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
      <circle cx="12" cy="13" r="3.5" />
    </>
  ),
  image: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <path d="m21 15-5-5L5 21" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </>
  ),
  minus: <path d="M5 12h14" />,
  download: (
    <>
      <path d="M12 3v12" />
      <path d="m7 10 5 5 5-5" />
      <path d="M4 19h16" />
    </>
  ),
  close: (
    <>
      <path d="m6 6 12 12" />
      <path d="M6 18 18 6" />
    </>
  ),
  play: <path d="m6 4 14 8-14 8Z" />,
  check: <path d="m4 12 5 5L20 6" />,
  alert: (
    <>
      <path d="M12 8v5" />
      <path d="M12 17h.01" />
      <circle cx="12" cy="12" r="9" />
    </>
  ),
  spinner: (
    <>
      <circle cx="12" cy="12" r="9" opacity=".25" />
      <path d="M21 12a9 9 0 0 0-9-9" />
    </>
  ),
  file: (
    <>
      <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z" />
      <path d="M14 3v6h6" />
    </>
  ),
  refresh: (
    <>
      <path d="M21 12a9 9 0 1 1-3-6.7" />
      <path d="M21 4v5h-5" />
    </>
  ),
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M19 5l-1.5 1.5M6.5 17.5 5 19" />
    </>
  ),
  moon: <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />,
}

interface IconProps {
  name: IconName
  size?: number
}

export function Icon({ name, size = 18 }: IconProps) {
  const style: CSSProperties = {
    width: size,
    height: size,
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.75,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
  }
  return (
    <svg viewBox="0 0 24 24" style={style} aria-hidden="true">
      {PATHS[name]}
    </svg>
  )
}
