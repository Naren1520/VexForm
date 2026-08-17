import type { FeatureNode } from '@vexform/types'
import { useAppStore } from '@/store'

interface Props {
  node: FeatureNode
  index: number
}

// Chamfers are known to be unavailable in pythonocc-core 7.9 (confirmed OCC bug)
const KNOWN_UNAVAILABLE = new Set(['chamfers'])

export default function FeatureTreeNode({ node, index }: Props) {
  const { selectedFeatureId, selectFeature } = useAppStore()
  const isSelected = selectedFeatureId === node.id

  const isUnavailable = node.status === 'failed' && KNOWN_UNAVAILABLE.has(node.id)

  const statusColor =
    node.status === 'success' ? '#7ab87a' :
    isUnavailable             ? '#555' :
    node.status === 'failed'  ? '#ff6666' : '#333'

  const statusIcon =
    node.status === 'success' ? '✓' :
    isUnavailable             ? '—' :
    node.status === 'failed'  ? '✗' : '⋯'

  const statusTitle =
    isUnavailable ? 'Not available in pythonocc-core 7.9' : undefined

  return (
    <button
      onClick={() => selectFeature(node.id)}
      className="w-full flex items-center gap-2 px-3 py-1.5 text-left transition-all duration-100"
      style={{
        background: isSelected ? '#1a1a1a' : 'transparent',
        borderLeft: isSelected ? '2px solid #c8b89a' : '2px solid transparent',
      }}
      onMouseEnter={(e) => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = '#111' }}
      onMouseLeave={(e) => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = 'transparent' }}
    >
      <span className="text-[10px] font-mono w-4 shrink-0 text-right" style={{ color: '#333' }}>
        {String(index + 1).padStart(2, '0')}
      </span>
      <span className="text-[11px] flex-1 truncate" style={{ color: isSelected ? '#f5f0eb' : '#888' }}>
        {node.label}
      </span>
      <span
        className="text-[10px] font-mono shrink-0"
        style={{ color: statusColor }}
        title={statusTitle}
      >
        {statusIcon}
      </span>
    </button>
  )
}
