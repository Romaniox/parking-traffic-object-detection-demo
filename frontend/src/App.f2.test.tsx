import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import * as client from './api/client'
import * as download from './download'

function makeFile(name = 'photo.png', type = 'image/png') {
  return new File([new Uint8Array([1, 2, 3])], name, { type })
}

const SUCCESS: client.DetectSuccess = {
  success: true,
  count: 1,
  objects: [{ class: 'person', count: 1 }],
  boxes: [{ class: 'person', conf: 0.9, x: 0.1, y: 0.1, w: 0.2, h: 0.4 }],
  image_url: '/detections/abc/image',
}

afterEach(() => {
  vi.restoreAllMocks()
  document.documentElement.removeAttribute('data-theme')
  localStorage.clear()
})

describe('F2 — interactivity', () => {
  it('theme toggle switches data-theme', async () => {
    const user = userEvent.setup()
    render(<App />)
    const before = document.documentElement.dataset.theme
    await user.click(screen.getByRole('button', { name: /Сменить тему/i }))
    expect(document.documentElement.dataset.theme).not.toBe(before)
  })

  it('zoom controls change the level and reset', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())

    expect(screen.getByText('100%')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /Увеличить/i }))
    expect(screen.getByText('125%')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /Сбросить масштаб/i }))
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  it('plain mouse wheel zooms the canvas', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())

    const stage = document.querySelector('.canvas__stage')!
    fireEvent.wheel(stage, { deltaY: -100 })
    await waitFor(() =>
      expect(Number(screen.getByRole('button', { name: /Сбросить масштаб/i }).textContent!.replace('%', ''))).toBeGreaterThan(100),
    )
  })

  it('does not render box labels (chips disabled), but keeps the rects', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue(SUCCESS)
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())
    await user.click(screen.getByRole('button', { name: /Обработать изображение/i }))
    await waitFor(() => expect(document.querySelectorAll('.canvas__overlay rect')).toHaveLength(1))
    expect(document.querySelectorAll('.bbox-label')).toHaveLength(0)
  })

  it('box stroke gets thinner as the canvas zooms in', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue(SUCCESS)
    const user = userEvent.setup()
    render(<App />)
    await user.upload(screen.getByTestId('file-input'), makeFile())
    await user.click(screen.getByRole('button', { name: /Обработать изображение/i }))
    await waitFor(() => expect(document.querySelector('.canvas__overlay rect')).toBeTruthy())

    const before = Number(document.querySelector('.canvas__overlay rect')!.getAttribute('stroke-width'))
    fireEvent.wheel(document.querySelector('.canvas__stage')!, { deltaY: -200 })
    await waitFor(() => {
      const after = Number(document.querySelector('.canvas__overlay rect')!.getAttribute('stroke-width'))
      expect(after).toBeLessThan(before)
    })
  })

  it('download button appears on success and triggers a download', async () => {
    vi.spyOn(client, 'detect').mockResolvedValue(SUCCESS)
    const dl = vi.spyOn(download, 'downloadAnnotated').mockResolvedValue()
    const user = userEvent.setup()
    render(<App />)

    await user.upload(screen.getByTestId('file-input'), makeFile())
    await user.click(screen.getByRole('button', { name: /Обработать изображение/i }))
    const btn = await screen.findByRole('button', { name: /Скачать результат/i })
    await user.click(btn)
    await waitFor(() => expect(dl).toHaveBeenCalled())
  })
})
