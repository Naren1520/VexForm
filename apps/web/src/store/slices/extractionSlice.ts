import { StateCreator } from 'zustand'
import type { CADModel, ShapeParams, ShapeSchema, ParamFieldState, ParamFormState, ParamFieldStatus } from '@vexform/types'
import { computeFieldStatus } from '@/lib/paramValidation'
import { UiSlice } from './uiSlice'

export type ExtractionStatus = 'idle' | 'loading' | 'success' | 'error'

export interface ExtractionSlice {
  extractionStatus: ExtractionStatus
  extractedParams: ShapeParams | null
  paramFormState: ParamFormState | null
  extractionSource: 'gemini' | 'fallback' | null
  extractionError: string | null
  /** The full schema returned by the backend for the detected/selected shape */
  shapeSchema: ShapeSchema | null
  /** The identified shape type string */
  shapeType: string | null
  cadIr: CADModel | null
  startExtraction: (file: File) => Promise<void>
  updateParamField: (key: string, value: number | string) => void
  clearExtraction: () => void
}

export const createExtractionSlice: StateCreator<
  ExtractionSlice & UiSlice,
  [],
  [],
  ExtractionSlice
> = (set, get) => ({
  extractionStatus: 'idle',
  extractedParams: null,
  paramFormState: null,
  extractionSource: null,
  extractionError: null,
  shapeSchema: null,
  shapeType: null,
  cadIr: null,

  startExtraction: async (file: File) => {
    set({ extractionStatus: 'loading', extractionError: null })

    try {
      const formData = new FormData()
      formData.append('blueprint', file)

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/extract`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ error: res.statusText }))
        const errMsg = errData?.detail?.error ?? errData?.error ?? `HTTP ${res.status}`
        ;(get() as any).addToast(errMsg, 'error')
        set({ extractionStatus: 'error', extractionError: errMsg })
        return
      }

      const data = await res.json()
      const extracted: ShapeParams = data.params
      const schema: ShapeSchema = data.schema
      const shapeType: string = 'programmatic'
      const source: 'gemini' | 'fallback' = data.source
      const referenceValues = schema.reference_values ?? {}

      // For programmatic shapes, store the construction program in params too
      // so the generate call can send it to the backend
      const paramsWithProgram: ShapeParams = { ...extracted }
      if (shapeType === 'programmatic' && data.construction_program) {
        paramsWithProgram['construction_program'] = data.construction_program as any
        paramsWithProgram['part_name'] = data.part_name ?? ''
      }
      if (data.cad_ir) {
        paramsWithProgram['cad_ir'] = data.cad_ir as any
      }

      // Build per-field form state with deviation scoring
      const formState: ParamFormState = {}
      for (const fieldDef of schema.fields) {
        const key = fieldDef.key
        const extractedVal = paramsWithProgram[key]
        const refVal = referenceValues[key]

        let fieldState: ParamFieldState
        if (extractedVal === null || extractedVal === undefined) {
          fieldState = {
            value: (refVal !== null && refVal !== undefined) ? (refVal as number | string) : '',
            status: 'ai_null',
          }
        } else {
          const status: ParamFieldStatus =
            typeof refVal === 'number' && typeof extractedVal === 'number'
              ? computeFieldStatus(extractedVal, refVal)
              : 'ai_match'
          fieldState = { value: extractedVal as number | string, status }
        }
        formState[key] = fieldState
      }

      set({
        extractionStatus: 'success',
        extractedParams: paramsWithProgram,
        paramFormState: formState,
        extractionSource: source,
        extractionError: null,
        shapeSchema: schema,
        shapeType,
        cadIr: data.cad_ir ?? null,
      })
    } catch (err: any) {
      const msg = err?.message ?? 'Extraction failed'
      ;(get() as any).addToast(msg, 'error')
      set({ extractionStatus: 'error', extractionError: msg })
    }
  },

  updateParamField: (key: string, value: number | string) => {
    const current = get().paramFormState
    if (!current) return
    set({
      paramFormState: {
        ...current,
        [key]: { value, status: 'user_edited' as ParamFieldStatus },
      },
    })
  },

  clearExtraction: () => {
    set({
      extractionStatus: 'idle',
      extractedParams: null,
      paramFormState: null,
      extractionSource: null,
      extractionError: null,
      shapeSchema: null,
      shapeType: null,
      cadIr: null,
    })
  },
})
