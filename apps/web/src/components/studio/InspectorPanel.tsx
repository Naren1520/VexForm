'use client'
import { useAppStore } from '@/store'
import FeatureTree from '@/components/feature-tree/FeatureTree'

export default function InspectorPanel() {
  const { generationStatus, meshPayload, featureTree } = useAppStore()

  const successOps = featureTree.filter((n) => n.status === 'success').length
  const totalOps   = featureTree.length

  return (
    <div className="flex flex-col h-full bg-[#0d0d14] border-l border-white/[0.06]">
      <div className="px-3 py-2.5 border-b border-white/[0.06] shrink-0">
        <p className="text-forge-text text-xs font-medium uppercase tracking-wider">Inspector</p>
      </div>

      <div className="px-3 py-2 border-b border-white/[0.04] shrink-0">
        <p className="text-[10px] text-forge-muted uppercase tracking-widest mb-1.5">Geometry</p>
        <div className="space-y-1">
          <StatusRow label="Solid generated" ok={!!meshPayload} />
          <StatusRow label="Boolean ops" ok={successOps > 0} value={`${successOps}/${totalOps}`} />
          <StatusRow label="Valid manifold" ok={generationStatus === 'success'} />
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="px-3 py-2 border-b border-white/[0.04]">
          <p className="text-[10px] text-forge-muted uppercase tracking-widest">Feature Tree</p>
        </div>
        <FeatureTree />
      </div>
    </div>
  )
}

function StatusRow({
  label,
  ok,
  value,
}: {
  label: string
  ok: boolean
  value?: string
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-forge-muted text-[11px]">{label}</span>
      <div className="flex items-center gap-1">
        {value && <span className="text-forge-muted text-[10px] font-mono">{value}</span>}
        <span className={`text-[11px] ${ok ? 'text-green-400' : 'text-forge-muted'}`}>
          {ok ? '✓' : '—'}
        </span>
      </div>
    </div>
  )
}
