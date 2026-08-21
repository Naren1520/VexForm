import { StateCreator } from 'zustand'
import type { Toast } from '@vexform/types'

export interface UiSlice {
  toasts: Toast[]
  leftPanelWidthPct: number   // 15–75, default 33
  rightPanelWidthPx: number   // 200–400, default 280
  exportingFormat: 'step' | 'stl' | 'obj' | null
  addToast: (message: string, level?: 'info' | 'error') => void
  dismissToast: (id: string) => void
  setLeftPanelWidth: (pct: number) => void
  setRightPanelWidth: (px: number) => void
  setExportingFormat: (fmt: 'step' | 'stl' | 'obj' | null) => void
}

function formatToastMessage(message: unknown): string {
  if (typeof message === 'string') return message
  if (message && typeof message === 'object') {
    const error = message as { feature_id?: unknown; code?: unknown; message?: unknown }
    const parts = [error.feature_id, error.code, error.message]
      .filter((part): part is string | number => typeof part === 'string' || typeof part === 'number')
    if (parts.length) return parts.join(' — ')
    try { return JSON.stringify(message) } catch { return 'An unexpected error occurred' }
  }
  return String(message ?? 'An unexpected error occurred')
}

export const createUiSlice: StateCreator<UiSlice, [], [], UiSlice> = (set, get) => ({
  toasts: [],
  leftPanelWidthPct: 33,
  rightPanelWidthPx: 280,
  exportingFormat: null,

  addToast: (message: string, level: 'info' | 'error' = 'info') => {
    const id = crypto.randomUUID()
    const toast: Toast = { id, message: formatToastMessage(message), level, createdAt: Date.now() }
    set((s) => ({ toasts: [...s.toasts, toast] }))
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, 5000)
  },

  dismissToast: (id: string) => {
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
  },

  setLeftPanelWidth: (pct: number) => {
    set({ leftPanelWidthPct: Math.min(75, Math.max(15, pct)) })
  },

  setRightPanelWidth: (px: number) => {
    set({ rightPanelWidthPx: Math.min(400, Math.max(200, px)) })
  },

  setExportingFormat: (fmt) => set({ exportingFormat: fmt }),
})
