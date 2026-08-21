'use client'
import { useState } from 'react'
import type { ShapeSchema } from '@vexform/types'
import { buildParamsFromFormState } from '@/lib/paramValidation'
import { useAppStore } from '@/store'
import ParamField from './ParamField'
import ParamRangesModal from './ParamRangesModal'

export default function ParamReviewForm() {
  const {
    paramFormState,
    extractedParams,
    shapeSchema,
    shapeType,
    extractionStatus,
    extractionSource,
    generateModel,
    generationStatus,
  } = useAppStore()

  const [openSections, setOpenSections] = useState<Record<string, boolean>>({})
  const [showRanges, setShowRanges] = useState(false)

  const toggleSection = (label: string) =>
    setOpenSections((p) => ({ ...p, [label]: !(p[label] ?? true) }))

  const handleGenerate = () => {
    if (!paramFormState || !shapeSchema || !shapeType) return
    const params = buildParamsFromFormState(shapeSchema, paramFormState, extractedParams ?? undefined)
    generateModel(shapeType, params)
  }

  // ── Idle / loading states ──────────────────────────────────────────────────
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

  if (!shapeSchema || !paramFormState) return null

  const schema: ShapeSchema = shapeSchema
  const sections = schema.sections

  return (
    <div className="flex flex-col gap-1 min-h-0">
      {/* Header row */}
      <div className="flex items-center justify-between px-1 mb-1">
        <div className="flex items-center gap-2">
          <span className="text-[10px]" style={{ color: '#555' }}>
            {extractionSource === 'gemini' ? '✦ AI extracted' : '◎ Reference values'}
          </span>
          {schema.display_name && (
            <span
              className="text-[10px] font-mono px-1.5 py-0.5 rounded"
              style={{ background: '#111', border: '1px solid #1a1a1a', color: '#666' }}
            >
              {schema.display_name}
            </span>
          )}
        </div>
        {/* Material badge if available */}
        {paramFormState['material'] && (
          <span className="text-[10px] font-mono" style={{ color: '#444' }}>
            {paramFormState['material'].value}
          </span>
        )}
        <button
          onClick={() => setShowRanges(true)}
          className="text-[10px] px-2 py-0.5 rounded transition-colors duration-150"
          style={{ background: '#111', border: '1px solid #1a1a1a', color: '#555' }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.color = '#888'
            ;(e.currentTarget as HTMLElement).style.borderColor = '#333'
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.color = '#555'
            ;(e.currentTarget as HTMLElement).style.borderColor = '#1a1a1a'
          }}
          title="View valid ranges for all parameters"
        >
          View Ranges
        </button>
      </div>

      {showRanges && <ParamRangesModal onClose={() => setShowRanges(false)} />}

      {/* Collapsible param sections */}
      <div className="flex-1 overflow-y-auto space-y-1 pr-0.5">
        {sections.map((section) => {
          const isOpen = openSections[section.label] ?? true
          return (
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
                  {isOpen ? '▲' : '▼'}
                </span>
              </button>

              {isOpen && (
                <div className="px-3 pb-1 pt-0.5" style={{ borderTop: '1px solid #1a1a1a' }}>
                  {section.keys.map((key) => {
                    const fieldDef = schema.fields.find((f) => f.key === key)
                    const fieldState = paramFormState[key]
                    if (!fieldDef || !fieldState) return null
                    return (
                      <ParamField
                        key={key}
                        paramKey={key}
                        fieldLabel={fieldDef.label}
                        fieldUnit={fieldDef.unit}
                        fieldType={fieldDef.field_type}
                        fieldState={fieldState}
                      />
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Generate button */}
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
