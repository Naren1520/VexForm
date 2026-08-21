'use client'

import { useState } from 'react'
import { useAppStore } from '@/store'

type StageStatus = 'idle' | 'active' | 'passed' | 'failed' | 'warning'

type Stage = {
  label: string
  detail: string
  status: StageStatus
}

function formatDetail(value: unknown, fallback: string): string {
  if (typeof value === 'string') return value
  if (value && typeof value === 'object') {
    const error = value as { code?: unknown; message?: unknown; feature_id?: unknown }
    const parts = [error.feature_id, error.code, error.message]
      .filter((part): part is string | number => typeof part === 'string' || typeof part === 'number')
    if (parts.length) return parts.join(' — ')
    try { return JSON.stringify(value) } catch { return fallback }
  }
  return fallback
}

function StatusMark({ status }: { status: StageStatus }) {
  if (status === 'active') return <span className="w-2.5 h-2.5 rounded-full border border-[#c8b89a] border-t-transparent animate-spin" />
  if (status === 'passed') return <span style={{ color: '#7ab87a' }}>✓</span>
  if (status === 'failed') return <span style={{ color: '#ff7777' }}>!</span>
  if (status === 'warning') return <span style={{ color: '#d7ad6c' }}>!</span>
  return <span style={{ color: '#444' }}>·</span>
}

export default function DiagnosticsMenu() {
  const {
    blueprintFile, uploadError,
    extractionStatus, extractionError, extractionSource, shapeType,
    generationStatus, geometryError, meshPayload, featureTree,
    exportingFormat,
  } = useAppStore()
  const [open, setOpen] = useState(false)

  const stages: Stage[] = [
    {
      label: 'Blueprint loaded',
      detail: uploadError ?? (blueprintFile ? blueprintFile.name : 'Waiting for a drawing'),
      status: uploadError ? 'failed' : blueprintFile ? 'passed' : 'idle',
    },
    {
      label: 'Gemini 3.6 Flash',
      detail: formatDetail(extractionError, extractionStatus === 'success' ? `Response: ${extractionSource ?? 'unknown'}` : 'Waiting for analysis'),
      status: extractionStatus === 'loading' ? 'active' : extractionStatus === 'error' ? 'failed' : extractionStatus === 'success' && extractionSource === 'fallback' ? 'warning' : extractionStatus === 'success' ? 'passed' : 'idle',
    },
    {
      label: 'CAD-IR review',
      detail: shapeType ? `Pipeline: ${shapeType}` : 'CAD-IR not available',
      status: extractionStatus === 'success' && extractionSource === 'fallback' ? 'warning' : extractionStatus === 'success' ? 'passed' : extractionStatus === 'error' ? 'failed' : 'idle',
    },
    {
      label: 'OCC / B-Rep',
      detail: formatDetail(geometryError, generationStatus === 'success' ? `${featureTree.length} features returned` : 'Waiting for generation'),
      status: generationStatus === 'loading' ? 'active' : generationStatus === 'error' ? 'failed' : generationStatus === 'success' ? 'passed' : 'idle',
    },
    {
      label: 'Mesh output',
      detail: meshPayload ? `${meshPayload.indices.length / 3} triangles` : 'No mesh generated',
      status: meshPayload ? 'passed' : generationStatus === 'error' ? 'failed' : 'idle',
    },
    {
      label: 'Exports',
      detail: exportingFormat ? `Writing ${exportingFormat.toUpperCase()}` : meshPayload ? 'STEP / STL / OBJ ready' : 'Unavailable until a model is generated',
      status: exportingFormat ? 'active' : meshPayload ? 'passed' : 'idle',
    },
  ]

  const failures = stages.filter((stage) => stage.status === 'failed')
  const warnings = stages.filter((stage) => stage.status === 'warning')

  return (
    <div className="relative shrink-0">
      <button
        type="button"
        aria-label="Open diagnostics"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="w-8 h-7 flex items-center justify-center transition-colors cursor-pointer"
        style={{ color: failures.length ? '#ff7777' : warnings.length ? '#d7ad6c' : '#777' }}
        title="Pipeline diagnostics"
      >
        <span className="text-lg leading-none tracking-[3px]">•••</span>
      </button>

      {open && (
        <div className="absolute right-0 bottom-9 z-50 w-[320px] border shadow-2xl" style={{ background: '#101010', borderColor: '#292929' }}>
          <div className="flex items-center justify-between px-3 py-2 border-b" style={{ borderColor: '#242424' }}>
            <div>
              <p className="text-[10px] uppercase tracking-[0.18em]" style={{ color: '#aaa' }}>Pipeline diagnostics</p>
              <p className="text-[10px] mt-1" style={{ color: '#555' }}>{failures.length ? `${failures.length} stage failure` : warnings.length ? 'Review required' : 'System ready'}</p>
            </div>
            <button type="button" onClick={() => setOpen(false)} className="text-xs px-1" style={{ color: '#555' }} aria-label="Close diagnostics">×</button>
          </div>
          <div className="p-2">
            {stages.map((stage) => (
              <div key={stage.label} className="flex items-start gap-2 px-2 py-2" style={{ background: stage.status === 'failed' ? '#281616' : stage.status === 'warning' ? '#211d15' : 'transparent' }}>
                <span className="w-4 shrink-0 text-center text-xs pt-px"><StatusMark status={stage.status} /></span>
                <div className="min-w-0">
                  <p className="text-[11px]" style={{ color: stage.status === 'failed' ? '#ffb0b0' : '#bbb' }}>{stage.label}</p>
                  <p className="text-[10px] truncate mt-0.5" style={{ color: stage.status === 'failed' ? '#d77d7d' : stage.status === 'warning' ? '#c9a96e' : '#555' }} title={stage.detail}>{stage.detail}</p>
                </div>
                <span className="ml-auto text-[9px] uppercase tracking-wider" style={{ color: stage.status === 'passed' ? '#6d9e6d' : stage.status === 'failed' ? '#d36e6e' : stage.status === 'warning' ? '#c9a96e' : '#444' }}>{stage.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
