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
    // Build LowerValveBodyParams from form state
    const params: Partial<LowerValveBodyParams> = {}
    for (const key of Object.keys(LOWER_VALVE_BODY_REFERENCE) as Array<keyof LowerValveBodyParams>) {
      const field = paramFormState[key]
      if (field) {
        ;(params as any)[key] = field.value
      } else {
        ;(params as any)[key] = LOWER_VALVE_BODY_REFERENCE[key]
      }
    }
    generateModel(params as LowerValveBodyParams)
  }

  if (extractionStatus === 'idle') {
    return (
      <p className="text-forge-muted text-xs px-1 py-4 text-center">
        Upload and analyze a blueprint to see parameters
      </p>
    )
  }

  if (extractionStatus === 'loading') {
    return (
      <div className="flex items-center gap-2 py-4 justify-center">
        <div className="w-4 h-4 border border-forge-blue border-t-transparent rounded-full animate-spin" />
        <span className="text-forge-muted text-xs">Analyzing engineering drawing…</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1 min-h-0">
      {/* Source badge */}
      {extractionSource && (
        <div className="flex items-center justify-between px-1 mb-1">
          <span className="text-[10px] text-forge-muted">
            {extractionSource === 'gemini' ? '✦ AI extracted' : '◎ Reference values'}
          </span>
          <span className="text-[10px] text-forge-muted font-mono">HT150</span>
        </div>
      )}

      {/* Sections */}
      <div className="flex-1 overflow-y-auto space-y-1 pr-1">
        {PARAM_SECTIONS.map((section) => (
          <div key={section.label} className="border border-white/[0.06] rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection(section.label)}
              className="w-full flex items-center justify-between px-3 py-1.5 bg-white/[0.03]
                         hover:bg-white/[0.05] transition-colors text-left"
            >
              <span className="text-forge-text text-xs font-medium uppercase tracking-wider">
                {section.label}
              </span>
              <span className="text-forge-muted text-xs">
                {openSections[section.label] ? '▲' : '▼'}
              </span>
            </button>

            {openSections[section.label] && (
              <div className="px-3 pb-1 pt-0.5 divide-y divide-white/[0.04]">
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

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={generationStatus === 'loading'}
        className="mt-2 w-full py-2.5 px-4 rounded-lg bg-forge-blue text-white text-sm font-medium
                   hover:bg-forge-blueLight transition-colors duration-150
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {generationStatus === 'loading' ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-3.5 h-3.5 border border-white border-t-transparent rounded-full animate-spin" />
            Generating…
          </span>
        ) : (
          'Generate 3D Model'
        )}
      </button>
    </div>
  )
}
