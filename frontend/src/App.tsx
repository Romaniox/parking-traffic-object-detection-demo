import { useCallback, useEffect, useState } from 'react'

import { detect, type DetectSuccess } from './api/client'
import { Canvas } from './components/Canvas'
import { MAX_ZOOM, MIN_ZOOM } from './components/ZoomControls'
import { Sidebar } from './components/Sidebar'
import { downloadAnnotated, downloadJSON } from './download'
import { useTheme } from './theme'
import type { AppStatus, CanvasView } from './types'

function App() {
  const [theme, toggleTheme] = useTheme()
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [status, setStatus] = useState<AppStatus>('idle')
  const [result, setResult] = useState<DetectSuccess | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<CanvasView>('annotated')
  const [zoom, setZoom] = useState(1)
  const [conf, setConf] = useState(0.25)

  const activeBoxes = result?.boxes.filter((b) => b.conf >= conf) ?? []

  const resetZoom = useCallback(() => setZoom(1), [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleSelect = useCallback(
    (selected: File) => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setResult(null)
      setError(null)
      setView('annotated')
      setZoom(1)
      setStatus('selected')
    },
    [previewUrl],
  )

  const handleReset = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setFile(null)
    setPreviewUrl(null)
    setResult(null)
    setError(null)
    setView('annotated')
    setZoom(1)
    setConf(0.25)
    setStatus('idle')
  }, [previewUrl])

  const handleProcess = useCallback(async () => {
    if (!file) return
    setStatus('processing')
    setError(null)
    const response = await detect(file)
    if (response.success) {
      setResult(response)
      setView('annotated')
      setStatus('success')
    } else {
      setError(response.error)
      setStatus('error')
    }
  }, [file])

  const handleDownload = useCallback(() => {
    if (!previewUrl || !result) return
    void downloadAnnotated(previewUrl, activeBoxes)
  }, [previewUrl, result, activeBoxes])

  const handleDownloadJson = useCallback(() => {
    if (!result) return
    downloadJSON({ result, filename: file?.name ?? null, activeBoxes, conf })
  }, [result, file, activeBoxes, conf])

  const canProcess = (status === 'selected' || status === 'error') && file !== null

  // Keyboard: zoom +/-/0, Enter to process.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return
      if ((e.key === '+' || e.key === '=') && previewUrl) {
        e.preventDefault()
        setZoom((z) => Math.min(MAX_ZOOM, +(z + 0.25).toFixed(2)))
      } else if (e.key === '-' && previewUrl) {
        e.preventDefault()
        setZoom((z) => Math.max(MIN_ZOOM, +(z - 0.25).toFixed(2)))
      } else if (e.key === '0' && previewUrl) {
        e.preventDefault()
        setZoom(1)
      } else if (e.key === 'Enter' && canProcess) {
        void handleProcess()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [previewUrl, canProcess, handleProcess])

  return (
    <main className="app">
      <section className="app__canvas">
        <Canvas
          imageUrl={previewUrl}
          boxes={activeBoxes}
          view={view}
          status={status}
          zoom={zoom}
          setZoom={setZoom}
          resetZoom={resetZoom}
          onSwitchView={setView}
          onUpload={handleSelect}
          uploadError={null}
        />
      </section>
      <Sidebar
        status={status}
        file={file}
        boxes={activeBoxes}
        errorMessage={error}
        canProcess={canProcess}
        theme={theme}
        conf={conf}
        onConfChange={setConf}
        onToggleTheme={toggleTheme}
        onProcess={handleProcess}
        onDownload={handleDownload}
        onDownloadJson={handleDownloadJson}
        onReset={handleReset}
      />
    </main>
  )
}

export default App
