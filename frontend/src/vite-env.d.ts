/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API base URL. Empty => same origin. */
  readonly VITE_API_BASE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
