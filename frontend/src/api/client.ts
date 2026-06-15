// Base URL of the backend API. Empty by default => same origin (local dev with
// the Vite proxy, or an all-in-one server deploy). When the frontend is hosted
// separately (e.g. Cloudflare), set VITE_API_BASE at build time to the backend's
// public HTTPS URL, e.g. https://api.example.com
const API_BASE = (import.meta.env.VITE_API_BASE ?? '').replace(/\/+$/, '')

/** Build an absolute API URL from a backend-relative path. */
export function apiUrl(path: string): string {
  return `${API_BASE}${path}`
}

export interface DetectionObject {
  class: string
  count: number
}

export interface DetectionBox {
  class: string
  conf: number
  x: number
  y: number
  w: number
  h: number
}

export interface DetectSuccess {
  success: true
  count: number
  objects: DetectionObject[]
  boxes: DetectionBox[]
  image_url: string
}

export interface DetectError {
  success: false
  error: string
}

export type DetectResponse = DetectSuccess | DetectError

/** POST an image to the backend /detect endpoint and return the parsed result. */
export async function detect(file: File): Promise<DetectResponse> {
  const form = new FormData()
  form.append('image', file)

  let resp: Response
  try {
    resp = await fetch(apiUrl('/detect'), { method: 'POST', body: form })
  } catch {
    return { success: false, error: 'Не удалось связаться с сервером' }
  }

  let data: DetectResponse
  try {
    data = (await resp.json()) as DetectResponse
  } catch {
    return { success: false, error: 'Некорректный ответ сервера' }
  }

  // image_url comes back backend-relative (/detections/{id}/image); make it
  // absolute so it resolves against the backend, not the frontend origin.
  if (data.success) {
    return { ...data, image_url: apiUrl(data.image_url) }
  }
  return data
}
