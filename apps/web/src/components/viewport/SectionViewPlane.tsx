'use client'
import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useAppStore } from '@/store'

const SECTION_PLANE = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0)

export default function SectionViewPlane() {
  const { gl } = useThree()
  const sectionPlaneOffset = useAppStore((s) => s.sectionPlaneOffset)

  useEffect(() => {
    SECTION_PLANE.constant = -sectionPlaneOffset * 60
    gl.clippingPlanes = [SECTION_PLANE]
    gl.localClippingEnabled = true

    return () => {
      gl.clippingPlanes = []
      gl.localClippingEnabled = false
    }
  }, [gl, sectionPlaneOffset])

  return null
}
