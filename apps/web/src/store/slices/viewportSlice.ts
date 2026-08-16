import { StateCreator } from 'zustand'

export interface MeasurementPoint {
  x: number
  y: number
  z: number
}

export interface MeasurementAnnotation {
  id: string
  p1: MeasurementPoint
  p2: MeasurementPoint
  distance: string
}

export interface ViewportSlice {
  wireframeMode: boolean
  sectionViewActive: boolean
  sectionPlaneOffset: number
  measurementActive: boolean
  pendingPoint: MeasurementPoint | null
  measurements: MeasurementAnnotation[]
  toggleWireframe: () => void
  toggleSectionView: () => void
  setSectionPlaneOffset: (val: number) => void
  toggleMeasurement: () => void
  setMeasurementPoint: (point: MeasurementPoint) => void
  clearMeasurement: () => void
}

export const createViewportSlice: StateCreator<ViewportSlice, [], [], ViewportSlice> = (set, get) => ({
  wireframeMode: false,
  sectionViewActive: false,
  sectionPlaneOffset: 0,
  measurementActive: false,
  pendingPoint: null,
  measurements: [],

  toggleWireframe: () => set((s) => ({ wireframeMode: !s.wireframeMode })),

  toggleSectionView: () => set((s) => ({
    sectionViewActive: !s.sectionViewActive,
    sectionPlaneOffset: 0,
  })),

  setSectionPlaneOffset: (val: number) => set({ sectionPlaneOffset: val }),

  toggleMeasurement: () => {
    const active = get().measurementActive
    set({ measurementActive: !active, pendingPoint: null })
  },

  setMeasurementPoint: (point: MeasurementPoint) => {
    const pending = get().pendingPoint
    if (!pending) {
      set({ pendingPoint: point })
    } else {
      const dx = point.x - pending.x
      const dy = point.y - pending.y
      const dz = point.z - pending.z
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)
      const annotation: MeasurementAnnotation = {
        id: crypto.randomUUID(),
        p1: pending,
        p2: point,
        distance: dist.toFixed(2) + ' mm',
      }
      set((s) => ({
        measurements: [...s.measurements, annotation],
        pendingPoint: null,
      }))
    }
  },

  clearMeasurement: () => set({ measurements: [], pendingPoint: null }),
})
