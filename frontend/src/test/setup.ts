import '@testing-library/jest-dom'

// jsdom doesn't implement object URLs; stub them for preview rendering.
if (!URL.createObjectURL) {
  URL.createObjectURL = () => 'blob:preview'
}
if (!URL.revokeObjectURL) {
  URL.revokeObjectURL = () => {}
}
