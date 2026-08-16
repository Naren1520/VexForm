'use client'
import { useAppStore } from '@/store'

export default function BlueprintPreview() {
  const { blueprintFile, blueprintPreviewUrl } = useAppStore()

  if (!blueprintPreviewUrl) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[200px] border border-white/5 rounded-lg bg-white/[0.01]">
        <p className="text-forge-muted text-xs text-center px-4">
          Blueprint preview will appear here after upload
        </p>
      </div>
    )
  }

  const isPdf = blueprintFile?.type === 'application/pdf'

  return (
    <div className="flex-1 relative min-h-[200px] overflow-hidden rounded-lg border border-white/10 bg-black/20">
      {isPdf ? (
        <iframe
          src={blueprintPreviewUrl}
          className="w-full h-full"
          style={{ minHeight: '240px' }}
          title="Blueprint PDF preview"
        />
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={blueprintPreviewUrl}
          alt="Engineering blueprint"
          className="w-full h-full object-contain"
          style={{ minHeight: '240px' }}
        />
      )}
      {/* Overlay label */}
      <div className="absolute top-2 left-2 glass rounded px-2 py-0.5 text-xs text-forge-muted">
        Blueprint
      </div>
    </div>
  )
}
