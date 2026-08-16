import { StateCreator } from 'zustand'
import type { ExtractedParams, LowerValveBodyParams, ParamFieldState, ParamFormState, ParamFieldStatus } from '@vexform/types'
import { LOWER_VALVE_BODY_REFERENCE, computeFieldStatus } from '@/lib/paramValidation'
import { UiSlice } from './uiSlice'

export type ExtractionStatus = 'idle' | 'loading' | 'success' | 'error'

export interface ExtractionSlice {
  extractionStatus: ExtractionStatus
  extractedParams: ExtractedParams | null
  paramFormState: ParamFormState | null
  extractionSource: 'gemini' | 'fallback' | null
  extractionError: string | null
  startExtraction: (file: File) => Promise<void>
  updateParamField: (key: keyof LowerValveBodyParams, value: number | string) => void
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

  startExtraction: async (file: File) => {
    set({ extractionStatus: 'loading', extractionError: null })

    try {
      const formData = new FormData()
      formData.append('blueprint', file)

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'
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
      const extracted: ExtractedParams = data.params
      const source: 'gemini' | 'fallback' = data.source

      const formState: Partial<ParamFormState> = {}
      const refKeys = Object.keys(LOWER_VALVE_BODY_REFERENCE) as Array<keyof LowerValveBodyParams>

      for (const key of refKeys) {
        const extractedVal = extracted[key]
        const refVal = LOWER_VALVE_BODY_REFERENCE[key]

        let fieldState: ParamFieldState
        if (extractedVal === null || extractedVal === undefined) {
          fieldState = { value: refVal as number | string, status: 'ai_null' }
        } else {
          const status = typeof refVal === 'number' && typeof extractedVal === 'number'
            ? computeFieldStatus(extractedVal, refVal)
            : 'ai_match'
          fieldState = { value: extractedVal as number | string, status }
        }
        formState[key] = fieldState as ParamFieldState
      }

      set({
        extractionStatus: 'success',
        extractedParams: extracted,
        paramFormState: formState as ParamFormState,
        extractionSource: source,
        extractionError: null,
      })
    } catch (err: any) {
      const msg = err?.message ?? 'Extraction failed'
      ;(get() as any).addToast(msg, 'error')
      set({ extractionStatus: 'error', extractionError: msg })
    }
  },

  updateParamField: (key: keyof LowerValveBodyParams, value: number | string) => {
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
    })
  },
})
