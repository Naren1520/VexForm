'use client'
import { useAppStore } from '@/store'

export default function BlueprintPreview() {
  const { blueprintFile, blueprintPreviewUrl } = useAppStore()

  if (!blueprintPreviewUrl) {
    return (
      <div
        className="w-full h-full flex items-center justify-center"
        style={{ border: '1px solid #1a1a1a', background: '#0a0a0a' }}
      >
        <p className="text-[11px] text-center px-4" style={{ color: '#333' }}>
          Preview appears after upload
        </p>
      </div>
    )
  }

  const isPdf = blueprintFile?.type === 'application/pdf'

  return (
    <div
      className="relative w-full h-full overflow-hidden"
      style={{ border: '1px solid #1a1a1a', background: '#000' }}
    >
      {isPdf ? (
        <iframe
          src={blueprintPreviewUrl}
          className="w-full h-full"
          style={{ minHeight: '196px' }}
          title="Blueprint PDF"
        />
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={blueprintPreviewUrl}
          alt="Engineering blueprint"
          className="w-full h-full object-contain"
          style={{ minHeight: '196px' }}
        />
      )}
      <div
        className="absolute top-2 left-2 px-2 py-0.5 text-[10px] uppercase tracking-widest"
        style={{ background: '#111', border: '1px solid #222', color: '#555' }}
      >
        Blueprint
      </div>
    </div>
  )
}
