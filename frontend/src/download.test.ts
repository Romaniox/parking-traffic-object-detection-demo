import { afterEach, describe, expect, it, vi } from 'vitest'

import { dominantClass, downloadJSON } from './download'
import type { DetectionBox, DetectSuccess } from './api/client'

function box(cls: string): DetectionBox {
  return { class: cls, conf: 0.9, x: 0, y: 0, w: 0.1, h: 0.1 }
}

const BASE_RESULT: DetectSuccess = {
  success: true,
  count: 2,
  objects: [{ class: 'car', count: 1 }, { class: 'person', count: 1 }],
  boxes: [
    { class: 'car', conf: 0.9, x: 0.1, y: 0.1, w: 0.2, h: 0.2 },
    { class: 'person', conf: 0.5, x: 0.3, y: 0.3, w: 0.2, h: 0.2 },
  ],
  image_url: '/detections/test/image',
  image_width: 640,
  image_height: 480,
  model_name: 'stub',
}

describe('downloadJSON', () => {
  afterEach(() => vi.restoreAllMocks())

  it('creates a blob with only the active boxes and correct metadata', async () => {
    const blobs: Blob[] = []
    vi.spyOn(URL, 'createObjectURL').mockImplementation((b) => { blobs.push(b as Blob); return 'blob:fake' })
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    vi.spyOn(document.body, 'appendChild').mockReturnValue(document.body as unknown as Node)
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    const activeBoxes = BASE_RESULT.boxes.filter((b) => b.conf >= 0.8) // only car (0.9)
    downloadJSON({ result: BASE_RESULT, filename: 'test.jpg', activeBoxes, conf: 0.8 })

    expect(blobs).toHaveLength(1)
    const text = await blobs[0].text()
    const json = JSON.parse(text)
    expect(json.conf_threshold).toBe(0.8)
    expect(json.count).toBe(1)
    expect(json.boxes).toHaveLength(1)
    expect(json.boxes[0].class).toBe('car')
    expect(json.objects).toEqual([{ class: 'car', count: 1 }])
    expect(json.filename).toBe('test.jpg')
    expect(json.image_width).toBe(640)
    expect(json.image_height).toBe(480)
    expect(json.model).toBe('stub')
  })
})

describe('dominantClass', () => {
  it('returns the only class when all boxes are the same', () => {
    expect(dominantClass([box('car'), box('car'), box('car')])).toBe('car')
  })

  it('returns the most frequent class', () => {
    const boxes = [box('car'), box('person'), box('car'), box('car'), box('person')]
    expect(dominantClass(boxes)).toBe('car')
  })

  it('returns the first class alphabetically when counts tie', () => {
    // 'apple' and 'zebra' appear once each; alphabetically 'apple' < 'zebra'
    expect(dominantClass([box('zebra'), box('apple')])).toBe('apple')
  })

  it('handles a single box', () => {
    expect(dominantClass([box('bus')])).toBe('bus')
  })
})
