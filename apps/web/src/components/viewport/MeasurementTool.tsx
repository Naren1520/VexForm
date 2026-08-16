'use client'
import { useCallback } from 'react'
import { useThree, useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'
import { useAppStore } from '@/store'

const _raycaster = new THREE.Raycaster()
const _mouse     = new THREE.Vector2()

export default function MeasurementTool() {
  const { camera, gl, scene } = useThree()
  const measurementActive  = useAppStore((s) => s.measurementActive)
  const pendingPoint       = useAppStore((s) => s.pendingPoint)
  const measurements       = useAppStore((s) => s.measurements)
  const setMeasurementPoint = useAppStore((s) => s.setMeasurementPoint)

  useFrame(() => {
    gl.domElement.style.cursor = measurementActive ? 'crosshair' : 'grab'
  })

  const handleCanvasClick = useCallback(
    (e: MouseEvent) => {
      if (!measurementActive) return
      const rect = gl.domElement.getBoundingClientRect()
      _mouse.x =  ((e.clientX - rect.left) / rect.width)  * 2 - 1
      _mouse.y = -((e.clientY - rect.top)  / rect.height) * 2 + 1
      _raycaster.setFromCamera(_mouse, camera)

      const meshes: THREE.Object3D[] = []
      scene.traverse((o) => { if ((o as THREE.Mesh).isMesh) meshes.push(o) })

      const hits = _raycaster.intersectObjects(meshes, true)
      if (!hits.length) return

      const p = hits[0].point
      setMeasurementPoint({ x: p.x, y: p.y, z: p.z })
    },
    [measurementActive, camera, gl, scene, setMeasurementPoint]
  )

  useFrame(() => {
    const el = gl.domElement
    if (measurementActive) {
      el.addEventListener('click', handleCanvasClick, { once: false })
    } else {
      el.removeEventListener('click', handleCanvasClick)
    }
  })

  return (
    <>
      {measurementActive && pendingPoint && (
        <mesh position={[pendingPoint.x, pendingPoint.y, pendingPoint.z]}>
          <sphereGeometry args={[0.8, 8, 8]} />
          <meshBasicMaterial color="#FFD700" />
        </mesh>
      )}

      {measurements.map((m) => (
        <group key={m.id}>
          <mesh position={[m.p1.x, m.p1.y, m.p1.z]}>
            <sphereGeometry args={[0.6, 8, 8]} />
            <meshBasicMaterial color="#4488FF" />
          </mesh>
          <mesh position={[m.p2.x, m.p2.y, m.p2.z]}>
            <sphereGeometry args={[0.6, 8, 8]} />
            <meshBasicMaterial color="#4488FF" />
          </mesh>
          <Html
            position={[
              (m.p1.x + m.p2.x) / 2,
              (m.p1.y + m.p2.y) / 2 + 4,
              (m.p1.z + m.p2.z) / 2,
            ]}
            center
          >
            <div
              style={{
                background: 'rgba(0,0,0,0.78)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(68,136,255,0.45)',
                borderRadius: '4px',
                padding: '3px 8px',
                color: '#88bbff',
                fontSize: '11px',
                fontFamily: 'monospace',
                whiteSpace: 'nowrap',
                pointerEvents: 'none',
              }}
            >
              {m.distance}
            </div>
          </Html>
        </group>
      ))}
    </>
  )
}
