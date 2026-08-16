import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { createUploadSlice, UploadSlice } from './slices/uploadSlice'
import { createExtractionSlice, ExtractionSlice } from './slices/extractionSlice'
import { createGeometrySlice, GeometrySlice } from './slices/geometrySlice'
import { createViewportSlice, ViewportSlice } from './slices/viewportSlice'
import { createUiSlice, UiSlice } from './slices/uiSlice'

export type AppStore =
  UploadSlice &
  ExtractionSlice &
  GeometrySlice &
  ViewportSlice &
  UiSlice

export const useAppStore = create<AppStore>()(
  devtools(
    (...a) => ({
      ...createUploadSlice(...a),
      ...createExtractionSlice(...a),
      ...createGeometrySlice(...a),
      ...createViewportSlice(...a),
      ...createUiSlice(...a),
    }),
    { name: 'VexFormStore' }
  ) as any
)

export const useUploadStore     = () => useAppStore((s) => s)
export const useGeometryStore   = () => useAppStore((s) => s)
export const useViewportStore   = () => useAppStore((s) => s)
export const useUiStore         = () => useAppStore((s) => s)
export const useExtractionStore = () => useAppStore((s) => s)
