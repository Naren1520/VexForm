'use client'
import dynamic from 'next/dynamic'
import { useCallback } from 'react'
import { useAppStore } from '@/store'
import Toolbar from '@/components/studio/Toolbar'
import PanelDivider from '@/components/studio/PanelDivider'
import InspectorPanel from '@/components/studio/InspectorPanel'
import ToastContainer from '@/components/studio/ToastContainer'
import FileUploadZone from '@/components/upload/FileUploadZone'
import BlueprintPreview from '@/components/upload/BlueprintPreview'
import ParamReviewForm from '@/components/params/ParamReviewForm'
import DotsLoader from '@/components/ui/DotsLoader'

const Viewport = dynamic(() => import('@/components/viewport/Viewport'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center w-full h-full" style={{ background: '#090909' }}>
      <DotsLoader text="Loading…" size={14} />
    </div>
  ),
})

export default function StudioPage() {
  const { leftPanelWidthPct, setLeftPanelWidth } = useAppStore()

  const handleLeftResize = useCallback(
    (deltaX: number) => {
      const deltaPct = (deltaX / window.innerWidth) * 100
      setLeftPanelWidth(leftPanelWidthPct + deltaPct)
    },
    [leftPanelWidthPct, setLeftPanelWidth]
  )

  return (
    <div className="studio-layout" style={{ background: '#090909' }}>
      <Toolbar />
      <div className="flex flex-1 min-h-0">
        <div
          className="flex flex-col min-w-[220px] overflow-hidden shrink-0"
          style={{ width: `${leftPanelWidthPct}%`, background: '#0c0c0c', borderRight: '1px solid #1a1a1a' }}
        >
          <div className="p-3 shrink-0" style={{ borderBottom: '1px solid #1a1a1a' }}>
            <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: '#404040' }}>Blueprint</p>
            <FileUploadZone />
          </div>
          <div className="px-3 pt-2 pb-1 shrink-0" style={{ height: '200px' }}>
            <BlueprintPreview />
          </div>
          <div className="flex flex-col flex-1 min-h-0 p-3 overflow-hidden">
            <p className="text-[10px] uppercase tracking-widest mb-2 shrink-0" style={{ color: '#404040' }}>
              Parameters
            </p>
            <div className="flex-1 overflow-y-auto min-h-0">
              <ParamReviewForm />
            </div>
          </div>
        </div>

        <PanelDivider onResize={handleLeftResize} />

        <div className="flex-1 min-w-[300px] relative overflow-hidden">
          <Viewport />
        </div>

        <div className="w-[260px] shrink-0 overflow-hidden">
          <InspectorPanel />
        </div>
      </div>
      <ToastContainer />
    </div>
  )
}
