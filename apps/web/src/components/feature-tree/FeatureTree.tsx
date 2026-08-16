'use client'
import { Component, ReactNode } from 'react'
import type { FeatureNode } from '@vexform/types'
import { FEATURE_TREE_ORDER, FEATURE_TREE_LABELS } from '@vexform/types'
import { useAppStore } from '@/store'
import FeatureTreeNode from './FeatureTreeNode'

class FeatureTreeErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() { return { hasError: true } }
  render() {
    if (this.state.hasError) {
      return (
        <p className="text-[11px] px-3 py-4 text-center" style={{ color: '#404040' }}>
          Feature tree unavailable
        </p>
      )
    }
    return this.props.children
  }
}

export default function FeatureTree() {
  const { featureTree, generationStatus } = useAppStore()

  const nodes: FeatureNode[] = FEATURE_TREE_ORDER.map((id) => {
    const found = featureTree.find((n) => n.id === id)
    return found ?? { id, label: FEATURE_TREE_LABELS[id] ?? id, status: 'pending' as any }
  })

  if (generationStatus !== 'success' && featureTree.length === 0) {
    return (
      <p className="text-[11px] px-3 py-6 text-center" style={{ color: '#333' }}>
        Generate a model to see the feature tree
      </p>
    )
  }

  const successCount = nodes.filter((n) => n.status === 'success').length
  const failCount    = nodes.filter((n) => n.status === 'failed').length

  return (
    <FeatureTreeErrorBoundary>
      <div className="flex flex-col h-full">
        <div
          className="flex items-center gap-3 px-3 py-2 shrink-0"
          style={{ borderBottom: '1px solid #1a1a1a' }}
        >
          <span className="text-[10px] font-mono" style={{ color: '#7ab87a' }}>{successCount} ok</span>
          {failCount > 0 && (
            <span className="text-[10px] font-mono" style={{ color: '#ff6666' }}>{failCount} fail</span>
          )}
          <span className="text-[10px] font-mono ml-auto" style={{ color: '#333' }}>{nodes.length} ops</span>
        </div>

        <div className="flex-1 overflow-y-auto pb-2">
          <p className="text-[10px] uppercase tracking-widest px-3 py-2" style={{ color: '#333' }}>
            Lower Valve Body
          </p>
          {nodes.map((node, i) => (
            <FeatureTreeNode key={node.id} node={node} index={i} />
          ))}
        </div>
      </div>
    </FeatureTreeErrorBoundary>
  )
}
