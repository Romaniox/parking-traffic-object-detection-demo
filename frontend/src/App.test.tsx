import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import * as client from './api/client'

function makeFile(name = 'photo.png', type = 'image/png') {
  return new File([new Uint8Array([1, 2, 3])], name, { type })
}

const SUCCESS: client.DetectSuccess = {
  success: true,
  count: 3,
  objects: [
    { class: 'person', count: 2 },
    { class: 'car', count: 1 },
  ],
  boxes: [
    { class: 'person', conf: 0.94, x: 0.05, y: 0.1, w: 0.2, h: 0.6 },
    { class: 'person', conf: 0.9, x: 0.3, y: 0.1, w: 0.2, h: 0.6 },
    { class: 'car', conf: 0.88, x: 0.6, y: 0.4, w: 0.3, h: 0.3 },
  ],
  image_url: '/detections/abc/image',
}

afterEach(() => vi.restoreAllMocks())

describe('App detection flow (redesign)', () => {
  it('disables the process button until an image is selected', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /Обработать изображение/i })).toBeDisabled()
  })

  it('runs the full path: count, per-class stats, and one rect per box', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue(SUCCESS)
    const user = userEvent.setup()
    render(<App />)

    await user.upload(screen.getByTestId('file-input'), makeFile())
    const button = screen.getByRole('button', { name: /Обработать изображение/i })
    expect(button).toBeEnabled()
    await user.click(button)

    expect(await screen.findByText('3')).toBeInTheDocument() // total count
    expect(screen.getByText('person')).toBeInTheDocument()
    expect(screen.getByText('car')).toBeInTheDocument()
    // one <rect> overlay per box
    await waitFor(() => expect(document.querySelectorAll('.canvas__overlay rect')).toHaveLength(3))
  })

  it('disables the button while processing', async () => {
    let resolve!: (v: client.DetectResponse) => void
    vi.spyOn(client, 'detect').mockReturnValue(
      new Promise<client.DetectResponse>((r) => {
        resolve = r
      }),
    )
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())
    const button = screen.getByRole('button', { name: /Обработать изображение/i })
    await user.click(button)
    expect(button).toBeDisabled()
    resolve(SUCCESS)
    await waitFor(() => expect(screen.getByText('3')).toBeInTheDocument())
  })

  it('toggling to "Оригинал" hides the box overlay', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue(SUCCESS)
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())
    await user.click(screen.getByRole('button', { name: /Обработать изображение/i }))
    await waitFor(() => expect(document.querySelectorAll('.canvas__overlay rect')).toHaveLength(3))

    await user.click(screen.getByRole('tab', { name: /Оригинал/i }))
    expect(document.querySelectorAll('.canvas__overlay rect')).toHaveLength(0)
  })

  it('shows an error message when the API returns an error', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue({ success: false, error: 'Inference failed' })
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())
    await user.click(screen.getByRole('button', { name: /Обработать изображение/i }))
    expect(await screen.findByText(/Inference failed/i)).toBeInTheDocument()
  })
})
