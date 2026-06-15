import type { Theme } from '../theme'
import { Icon } from './icons'

interface ThemeToggleProps {
  theme: Theme
  onToggle: () => void
}

export function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button className="icon-btn" onClick={onToggle} aria-label="Сменить тему" title="Сменить тему">
      <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={16} />
    </button>
  )
}
