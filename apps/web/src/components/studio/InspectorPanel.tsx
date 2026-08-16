'use client'
import { useAppStore } from '@/store'
import FeatureTree from '@/components/feature-tree/FeatureTree'

export default function InspectorPanel() {
  const { generationStatus, meshPayload, featureTree } = useAppStore()

  const successOps = featureTree.filter((n) => n.status === 'success').length
  const totalOps   = featureTree.length

  return (
    <div className="flex flex-col h-full" style={{ background: '#0c0c0c', borderLeft: '1px solid #1a1a1a' }}>
      <div className="px-4 py-3 shrink-0" style={{ borderBottom: '1px solid #1a1a1a' }}>
        <p className="text-[10px] uppercase tracking-widest" style={{ color: '#404040' }}>Inspector</p>
      </div>

      <div className="px-4 py-3 shrink-0" style={{ borderBottom: '1px solid #1a1a1a' }}>
        <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: '#404040' }}>Geometry</p>
        <div className="space-y-2">
          <StatusRow label="Solid generated" ok={!!meshPayload} />
          <StatusRow label="Boolean ops" ok={successOps > 0} value={totalOps > 0 ? `${successOps}/${totalOps}` : undefined} />
          <StatusRow label="Valid manifold" ok={generationStatus === 'success'} />
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-4 py-2.5 shrink-0" style={{ borderBottom: '1px solid #1a1a1a' }}>
          <p className="text-[10px] uppercase tracking-widest" style={{ color: '#404040' }}>Feature Tree</p>
        </div>
        <div className="flex-1 overflow-hidden">
          <FeatureTree />
        </div>
      </div>
    </div>
  )
}

function StatusRow({ label, ok, value }: { label: string; ok: boolean; value?: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[11px]" style={{ color: '#555' }}>{label}</span>
      <div className="flex items-center gap-2">
        {value && (
          <span className="text-[10px] font-mono" style={{ color: '#555' }}>{value}</span>
        )}
        <span
          className="text-[10px] font-mono w-4 text-right"
          style={{ color: ok ? '#7ab87a' : '#333' }}
        >
          {ok ? '✓' : '—'}
        </span>
      </div>
    </div>
  )
}
