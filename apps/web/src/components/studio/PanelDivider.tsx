'use client'
import { useRef, useCallback } from 'react'
import { useAppStore } from '@/store'

interface Props {
  onResize: (deltaX: number) => void
}

export default function PanelDivider({ onResize }: Props) {
  const dragging = useRef(false)
  const lastX = useRef(0)

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    dragging.current = true
    lastX.current = e.clientX
    e.currentTarget.setPointerCapture(e.pointerId)
  }, [])

  const onPointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragging.current) return
    const delta = e.clientX - lastX.current
    lastX.current = e.clientX
    onResize(delta)
  }, [onResize])

  const onPointerUp = useCallback(() => {
    dragging.current = false
  }, [])

  return (
    <div
      className="w-1 shrink-0 bg-white/[0.06] hover:bg-forge-blue/40 cursor-col-resize
                 transition-colors duration-150 relative group"
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
    >
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                      flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {[0,1,2].map((i) => (
          <div key={i} className="w-0.5 h-1 bg-forge-blue rounded-full" />
        ))}
      </div>
    </div>
  )
}
