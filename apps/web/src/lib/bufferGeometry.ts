import * as THREE from 'three'
import type { MeshPayload } from '@vexform/types'

export function buildBufferGeometry(payload: MeshPayload): THREE.BufferGeometry {
  if (!payload.vertices?.length || !payload.indices?.length) {
    throw new Error('invalid mesh data: vertices or indices are empty')
  }

  const positions = new Float32Array(payload.vertices)
  const indices   = new Uint32Array(payload.indices)

  for (let i = 0; i < positions.length; i++) {
    if (!isFinite(positions[i])) {
      throw new Error(`invalid mesh data: non-finite value at vertex position ${i}`)
    }
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setIndex(new THREE.BufferAttribute(indices, 1))

  if (payload.normals?.length === payload.vertices.length) {
    const normals = new Float32Array(payload.normals)
    geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3))
  } else {
    geometry.computeVertexNormals()
  }

  geometry.computeBoundingBox()
  geometry.computeBoundingSphere()

  return geometry
}
