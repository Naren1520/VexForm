'use client'
import { useRef, useMemo, useEffect } from 'react'
import * as THREE from 'three'
import { buildBufferGeometry } from '@/lib/bufferGeometry'
import { useAppStore } from '@/store'

export default function ModelMesh() {
  const meshRef = useRef<THREE.Mesh>(null)
  const wireframeMode = useAppStore((s) => s.wireframeMode)
  const meshPayload   = useAppStore((s) => s.meshPayload)
  const addToast      = useAppStore((s) => s.addToast)

  const geometry = useMemo(() => {
    if (!meshPayload) return null
    try {
      const geo = buildBufferGeometry(meshPayload)
      geo.computeBoundingBox()
      const center = new THREE.Vector3()
      geo.boundingBox!.getCenter(center)
      geo.translate(-center.x, -center.y, -center.z)
      return geo
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Model data could not be loaded'
      addToast(msg, 'error')
      return null
    }
  }, [meshPayload, addToast])

  useEffect(() => () => { geometry?.dispose() }, [geometry])

  if (!geometry) return null

  return (
    <mesh ref={meshRef} geometry={geometry} castShadow receiveShadow>
      {wireframeMode ? (
        <meshBasicMaterial color="#4488FF" wireframe />
      ) : (
        <meshStandardMaterial
          color="#2d4a8a"
          roughness={0.45}
          metalness={0.55}
          side={THREE.DoubleSide}
        />
      )}
    </mesh>
  )
}
