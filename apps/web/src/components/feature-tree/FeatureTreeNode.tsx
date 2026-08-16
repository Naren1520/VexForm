import type { FeatureNode } from '@vexform/types'
import { useAppStore } from '@/store'

interface Props {
  node: FeatureNode
  index: number
}

export default function FeatureTreeNode({ node, index }: Props) {
  const { selectedFeatureId, selectFeature } = useAppStore()
  const isSelected = selectedFeatureId === node.id

  const statusIcon =
    node.status === 'success' ? (
      <span className="text-green-400 text-xs">✓</span>
    ) : node.status === 'failed' ? (
      <span className="text-forge-red text-xs">✗</span>
    ) : (
      <span className="text-forge-muted text-xs">⋯</span>
    )

  return (
    <button
      onClick={() => selectFeature(node.id)}
      className={`
        feature-node w-full flex items-center gap-2 px-3 py-1.5 rounded text-left
        transition-colors duration-100
        ${isSelected ? 'selected' : ''}
      `}
    >
      <span className="text-forge-muted text-[10px] font-mono w-4 shrink-0 text-right">
        {String(index + 1).padStart(2, '0')}
      </span>
      <span className={`text-xs flex-1 ${isSelected ? 'text-forge-blue' : 'text-forge-text'}`}>
        {node.label}
      </span>
      {statusIcon}
    </button>
  )
}
