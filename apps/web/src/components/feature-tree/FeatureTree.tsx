'use client'
import { Component, ReactNode } from 'react'
import type { FeatureNode } from '@vexform/types'
import { FEATURE_TREE_ORDER, FEATURE_TREE_LABELS } from '@vexform/types'
import { useAppStore } from '@/store'
import FeatureTreeNode from './FeatureTreeNode'

// Error boundary
class FeatureTreeErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  render() {
    if (this.state.hasError) {
      return (
        <p className="text-forge-muted text-xs px-3 py-4 text-center">
          Feature tree unavailable
        </p>
      )
    }
    return this.props.children
  }
}

export default function FeatureTree() {
  const { featureTree, generationStatus } = useAppStore()

  // Merge backend results with the canonical order
  const nodes: FeatureNode[] = FEATURE_TREE_ORDER.map((id) => {
    const found = featureTree.find((n) => n.id === id)
    return found ?? {
      id,
      label: FEATURE_TREE_LABELS[id] ?? id,
      status: generationStatus === 'success' ? 'pending' : 'pending',
    }
  })

  if (generationStatus !== 'success' && featureTree.length === 0) {
    return (
      <p className="text-forge-muted text-xs px-3 py-6 text-center">
        Generate a model to see the feature tree
      </p>
    )
  }

  const successCount = nodes.filter((n) => n.status === 'success').length
  const failCount    = nodes.filter((n) => n.status === 'failed').length

  return (
    <FeatureTreeErrorBoundary>
      <div className="flex flex-col h-full">
        {/* Header stats */}
        <div className="flex items-center gap-3 px-3 py-2 border-b border-white/[0.06] mb-1">
          <span className="text-green-400 text-xs">{successCount} ✓</span>
          {failCount > 0 && (
            <span className="text-forge-red text-xs">{failCount} ✗</span>
          )}
          <span className="text-forge-muted text-xs ml-auto">{nodes.length} ops</span>
        </div>

        {/* Tree nodes */}
        <div className="flex-1 overflow-y-auto space-y-0.5 pb-2">
          <div className="px-1">
            <p className="text-forge-muted text-[10px] uppercase tracking-widest px-3 py-1">
              Lower Valve Body
            </p>
            {nodes.map((node, i) => (
              <FeatureTreeNode key={node.id} node={node} index={i} />
            ))}
          </div>
        </div>
      </div>
    </FeatureTreeErrorBoundary>
  )
}
