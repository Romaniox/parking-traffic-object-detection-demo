import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { DropZone } from './DropZone'

function makeFile(type: string) {
  return new File([new Uint8Array([1, 2, 3])], 'photo.img', { type })
}

describe('DropZone — file type filtering', () => {
  it('accepts image/jpeg', async () => {
    const onFile = vi.fn()
    render(<DropZone onFile={onFile} />)
    await userEvent.upload(screen.getByTestId('file-input'), makeFile('image/jpeg'))
    expect(onFile).toHaveBeenCalled()
    expect(screen.queryByText(/Только JPG/i)).not.toBeInTheDocument()
  })

  it('accepts image/png', async () => {
    const onFile = vi.fn()
    render(<DropZone onFile={onFile} />)
    await userEvent.upload(screen.getByTestId('file-input'), makeFile('image/png'))
    expect(onFile).toHaveBeenCalled()
  })

  it('rejects image/jpg (non-standard MIME) — backend only accepts image/jpeg', async () => {
    const onFile = vi.fn()
    render(<DropZone onFile={onFile} />)
    await userEvent.upload(screen.getByTestId('file-input'), makeFile('image/jpg'))
    expect(onFile).not.toHaveBeenCalled()
    expect(screen.getByText(/Только JPG/i)).toBeInTheDocument()
  })

  it('rejects unsupported types (e.g. text/plain) — onChange does not fire', async () => {
    // jsdom respects the <input accept="..."> attribute and does not fire onChange
    // for files that don't match, so onFile is never called. In a real browser the
    // file dialog filter prevents selection; a user forcing a mismatch would still
    // hit the isAllowed() guard and see a warning.
    const onFile = vi.fn()
    render(<DropZone onFile={onFile} />)
    await userEvent.upload(screen.getByTestId('file-input'), makeFile('text/plain'))
    expect(onFile).not.toHaveBeenCalled()
  })
})
