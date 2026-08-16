import { StateCreator } from 'zustand'
import { validateBlueprint } from '@/lib/paramValidation'

export interface UploadSlice {
  blueprintFile: File | null
  blueprintPreviewUrl: string | null
  uploadError: string | null
  setBlueprint: (file: File) => void
  clearBlueprint: () => void
}

export const createUploadSlice: StateCreator<UploadSlice, [], [], UploadSlice> = (set, get) => ({
  blueprintFile: null,
  blueprintPreviewUrl: null,
  uploadError: null,

  setBlueprint: (file: File) => {
    const validation = validateBlueprint(file.type, file.size)
    if (!validation.valid) {
      set({ uploadError: validation.error ?? 'Invalid file', blueprintFile: null, blueprintPreviewUrl: null })
      return
    }
    const prev = get().blueprintPreviewUrl
    if (prev) URL.revokeObjectURL(prev)

    const previewUrl = URL.createObjectURL(file)
    set({ blueprintFile: file, blueprintPreviewUrl: previewUrl, uploadError: null })
  },

  clearBlueprint: () => {
    const prev = get().blueprintPreviewUrl
    if (prev) URL.revokeObjectURL(prev)
    set({ blueprintFile: null, blueprintPreviewUrl: null, uploadError: null })
  },
})
