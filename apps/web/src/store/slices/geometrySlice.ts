import { StateCreator } from 'zustand'
import type { MeshPayload, FeatureNode, ShapeParams } from '@vexform/types'
import { UiSlice } from './uiSlice'

export type GenerationStatus = 'idle' | 'loading' | 'success' | 'error'

export interface GeometrySlice {
  generationStatus: GenerationStatus
  meshPayload: MeshPayload | null
  featureTree: FeatureNode[]
  geometryError: string | null
  selectedFeatureId: string | null
  sessionToken: string
  generateModel: (shapeType: string, params: ShapeParams) => Promise<void>
  selectFeature: (id: string | null) => void
  clearGeometry: () => void
}

export const createGeometrySlice: StateCreator<
  GeometrySlice & UiSlice,
  [],
  [],
  GeometrySlice
> = (set, get) => ({
  generationStatus: 'idle',
  meshPayload: null,
  featureTree: [],
  geometryError: null,
  selectedFeatureId: null,
  sessionToken: typeof crypto !== 'undefined'
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2),

  generateModel: async (shapeType: string, params: ShapeParams) => {
    set({ generationStatus: 'loading', geometryError: null, meshPayload: null, featureTree: [] })

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'
      const sessionToken = get().sessionToken

      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': sessionToken,
        },
        body: JSON.stringify({ shape_type: shapeType, params }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ error: res.statusText }))
        const errMsg =
          errData?.detail?.error ??
          errData?.detail?.errors?.map((e: any) => e.expected_bound).join('; ') ??
          errData?.error ??
          `HTTP ${res.status}`
        ;(get() as any).addToast(errMsg, 'error')
        set({ generationStatus: 'error', geometryError: errMsg })
        return
      }

      const data = await res.json()

      // Normalise bounding box — backend uses snake_case, frontend expects camelCase
      const mesh: MeshPayload = {
        vertices: data.mesh.vertices,
        indices: data.mesh.indices,
        normals: data.mesh.normals,
        boundingBox: {
          min: data.mesh.bounding_box?.min ?? data.mesh.boundingBox?.min ?? [0, 0, 0],
          max: data.mesh.bounding_box?.max ?? data.mesh.boundingBox?.max ?? [100, 100, 100],
        },
      }

      const featureTree: FeatureNode[] = (data.feature_tree ?? data.featureTree ?? []).map(
        (n: any) => ({
          id: n.id,
          label: n.label,
          status: n.status,
          geometryRef: n.geometry_ref ?? n.geometryRef,
          confidence: n.confidence,
          outputType: n.output_type ?? n.outputType,
          topology: n.topology,
          evidence: n.evidence,
        })
      )

      set({ generationStatus: 'success', meshPayload: mesh, featureTree, geometryError: null })
    } catch (err: any) {
      const msg = err?.message ?? 'Generation failed'
      ;(get() as any).addToast(msg, 'error')
      set({ generationStatus: 'error', geometryError: msg })
    }
  },

  selectFeature: (id: string | null) => {
    const current = get().selectedFeatureId
    set({ selectedFeatureId: current === id ? null : id })
  },

  clearGeometry: () => {
    set({
      generationStatus: 'idle',
      meshPayload: null,
      featureTree: [],
      geometryError: null,
      selectedFeatureId: null,
    })
  },
})
