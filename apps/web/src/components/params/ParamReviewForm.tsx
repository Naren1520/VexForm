'use client'
import { useState } from 'react'
import type { LowerValveBodyParams } from '@vexform/types'
import { PARAM_SECTIONS, LOWER_VALVE_BODY_REFERENCE } from '@/lib/paramValidation'
import { useAppStore } from '@/store'
import ParamField from './ParamField'

export default function ParamReviewForm() {
  const {
    paramFormState,
    extractionStatus,
    extractionSource,
    generateModel,
    generationStatus,
  } = useAppStore()

  const [openSections, setOpenSections] = useState<Record<string, boolean>>(
    Object.fromEntries(PARAM_SECTIONS.map((s) => [s.label, true]))
  )

  const toggleSection = (label: string) =>
    setOpenSections((p) => ({ ...p, [label]: !p[label] }))

  const handleGenerate = () => {
    if (!paramFormState) return
    const params: Partial<LowerValveBodyParams> = {}
    for (const key of Object.keys(LOWER_VALVE_BODY_REFERENCE) as Array<keyof LowerValveBodyParams>) {
      const field = paramFormState[key]
      ;(params as any)[key] = field ? field.value : LOWER_VALVE_BODY_REFERENCE[key]
    }
    generateModel(params as LowerValveBodyParams)
  }

  if (extractionStatus === 'idle') {
    return (
      <p className="text-[11px] px-1 py-4 text-center" style={{ color: '#404040' }}>
        Upload and analyze a blueprint to see parameters
      </p>
    )
  }

  if (extractionStatus === 'loading') {
    return (
      <div className="flex items-center gap-2 py-4 justify-center">
        <span className="w-3.5 h-3.5 rounded-full border border-white/20 border-t-transparent animate-spin" />
        <span className="text-[11px]" style={{ color: '#555' }}>Analyzing drawing…</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1 min-h-0">
      {extractionSource && (
        <div className="flex items-center justify-between px-1 mb-1">
          <span className="text-[10px]" style={{ color: '#555' }}>
            {extractionSource === 'gemini' ? '✦ AI extracted' : '◎ Reference values'}
          </span>
          <span className="text-[10px] font-mono" style={{ color: '#444' }}>HT150</span>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-1 pr-0.5">
        {PARAM_SECTIONS.map((section) => (
          <div key={section.label} style={{ border: '1px solid #1a1a1a', overflow: 'hidden' }}>
            <button
              onClick={() => toggleSection(section.label)}
              className="w-full flex items-center justify-between px-3 py-2 text-left transition-colors duration-150"
              style={{ background: '#111' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#161616' }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = '#111' }}
            >
              <span className="text-[10px] font-medium uppercase tracking-widest" style={{ color: '#888' }}>
                {section.label}
              </span>
              <span className="text-[10px]" style={{ color: '#444' }}>
                {openSections[section.label] ? '▲' : '▼'}
              </span>
            </button>

            {openSections[section.label] && (
              <div className="px-3 pb-1 pt-0.5" style={{ borderTop: '1px solid #1a1a1a' }}>
                {section.keys.map((key) => {
                  const field = paramFormState?.[key]
                  if (!field) return null
                  return <ParamField key={key} paramKey={key} fieldState={field} />
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleGenerate}
        disabled={generationStatus === 'loading'}
        className="mt-2 w-full py-2.5 px-4 text-xs font-medium uppercase tracking-widest
                   transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
        style={{ background: '#f5f0eb', color: '#0c0c0c' }}
        onMouseEnter={(e) => { if (generationStatus !== 'loading') (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
        onMouseLeave={(e) => { if (generationStatus !== 'loading') (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
      >
        {generationStatus === 'loading' ? (
          <>
            <span className="w-3 h-3 rounded-full border border-black/30 border-t-transparent animate-spin shrink-0" />
            Generating…
          </>
        ) : 'Generate 3D Model'}
      </button>
    </div>
  )
}
