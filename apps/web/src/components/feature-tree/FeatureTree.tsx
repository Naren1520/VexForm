'use client'
import { Component, ReactNode } from 'react'
import type { FeatureNode } from '@vexform/types'
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
  const { featureTree, generationStatus, shapeSchema } = useAppStore()

  if (generationStatus !== 'success' && featureTree.length === 0) {
    return (
      <p className="text-[11px] px-3 py-6 text-center" style={{ color: '#333' }}>
        Generate a model to see the feature tree
      </p>
    )
  }

  // Use schema-defined order if available, otherwise use order from API response
  const featureOrder: string[] = shapeSchema?.shape_type === 'programmatic' || shapeSchema?.shape_type === 'cad_ir'
    ? featureTree.map((n) => n.id)
    : (shapeSchema?.feature_tree_order ?? featureTree.map((n) => n.id))

  // Build ordered nodes: fill in pending for any expected ops not yet returned
  const nodeMap = new Map(featureTree.map((n) => [n.id, n]))
  const nodes: FeatureNode[] = featureOrder.map((id) => {
    return nodeMap.get(id) ?? { id, label: id.replace(/_/g, ' '), status: 'pending' as const }
  })
  // Append any nodes from API that weren't in the schema order
  for (const n of featureTree) {
    if (!featureOrder.includes(n.id)) nodes.push(n)
  }

  const KNOWN_UNAVAILABLE = new Set(['chamfers'])
  const successCount = nodes.filter((n) => n.status === 'success').length
  const failCount    = nodes.filter((n) => n.status === 'failed' && !KNOWN_UNAVAILABLE.has(n.id)).length
  const naCount      = nodes.filter((n) => n.status === 'failed' && KNOWN_UNAVAILABLE.has(n.id)).length

  const displayName = shapeSchema?.display_name ?? 'Shape'

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
          {naCount > 0 && (
            <span className="text-[10px] font-mono" style={{ color: '#555' }}>{naCount} n/a</span>
          )}
          <span className="text-[10px] font-mono ml-auto" style={{ color: '#333' }}>{nodes.length} ops</span>
        </div>

        <div className="flex-1 overflow-y-auto pb-2">
          <p className="text-[10px] uppercase tracking-widest px-3 py-2" style={{ color: '#333' }}>
            {displayName}
          </p>
          {nodes.map((node, i) => (
            <FeatureTreeNode key={node.id} node={node} index={i} />
          ))}
        </div>
      </div>
    </FeatureTreeErrorBoundary>
  )
}
