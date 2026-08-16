'use client'
import { useRef, useCallback } from 'react'

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
      className="w-px shrink-0 cursor-col-resize relative group transition-colors duration-150"
      style={{ background: '#1a1a1a' }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#c8b89a44' }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = '#1a1a1a' }}
    />
  )
}
