'use client'
import { useAppStore } from '@/store'

export default function ScaleBar() {
  const meshPayload = useAppStore((s) => s.meshPayload)
  if (!meshPayload) return null

  const bb = meshPayload.boundingBox
  const height = Math.abs(bb.max[2] - bb.min[2])
  const displayVal = Math.round(height)

  return (
    <div className="absolute bottom-4 left-4 flex items-center gap-2 pointer-events-none">
      <div
        className="h-[2px] bg-forge-muted"
        style={{ width: '60px' }}
      />
      <span className="text-forge-muted text-xs font-mono">{displayVal} mm</span>
    </div>
  )
}
