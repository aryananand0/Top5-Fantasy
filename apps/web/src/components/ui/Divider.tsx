import { cn } from '@/lib/cn'

type DividerStyle = 'wavy' | 'dashed' | 'solid'
type DividerSpacing = 'sm' | 'md' | 'lg'

interface DividerProps {
  style?: DividerStyle
  spacing?: DividerSpacing
  className?: string
}

const spacingStyles: Record<DividerSpacing, string> = {
  sm: 'my-4',
  md: 'my-6',
  lg: 'my-8',
}

// Wavy SVG path — hand-drawn pencil-line feel
function WavyLine({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 10"
      preserveAspectRatio="none"
      className={cn('w-full h-[10px]', className)}
      aria-hidden="true"
    >
      <path
        d="M0,5 Q25,1 50,5 Q75,9 100,5 Q125,1 150,5 Q175,9 200,5 Q225,1 250,5 Q275,9 300,5 Q325,1 350,5 Q375,9 400,5"
        stroke="var(--color-ink-faint)"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function Divider({ style = 'wavy', spacing = 'md', className }: DividerProps) {
  return (
    <div
      role="separator"
      className={cn('w-full', spacingStyles[spacing], className)}
    >
      {style === 'wavy' && <WavyLine />}
      {style === 'dashed' && (
        <div className="border-t-2 border-dashed border-ink-faint" />
      )}
      {style === 'solid' && (
        <div className="border-t-2 border-ink-faint" />
      )}
    </div>
  )
}
