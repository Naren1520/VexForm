import { create } from 'zustand'
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

export const useAppStore = create<AppStore>()((set, get, api) => ({
  ...createUploadSlice(
    set as Parameters<typeof createUploadSlice>[0],
    get as Parameters<typeof createUploadSlice>[1],
    api as Parameters<typeof createUploadSlice>[2],
  ),
  ...createExtractionSlice(
    set as Parameters<typeof createExtractionSlice>[0],
    get as Parameters<typeof createExtractionSlice>[1],
    api as Parameters<typeof createExtractionSlice>[2],
  ),
  ...createGeometrySlice(
    set as Parameters<typeof createGeometrySlice>[0],
    get as Parameters<typeof createGeometrySlice>[1],
    api as Parameters<typeof createGeometrySlice>[2],
  ),
  ...createViewportSlice(
    set as Parameters<typeof createViewportSlice>[0],
    get as Parameters<typeof createViewportSlice>[1],
    api as Parameters<typeof createViewportSlice>[2],
  ),
  ...createUiSlice(
    set as Parameters<typeof createUiSlice>[0],
    get as Parameters<typeof createUiSlice>[1],
    api as Parameters<typeof createUiSlice>[2],
  ),
}))

export const useUploadStore     = () => useAppStore((s) => s)
export const useGeometryStore   = () => useAppStore((s) => s)
export const useViewportStore   = () => useAppStore((s) => s)
export const useUiStore         = () => useAppStore((s) => s)
export const useExtractionStore = () => useAppStore((s) => s)
