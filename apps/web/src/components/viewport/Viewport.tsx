'use client'
import { Suspense, useEffect, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, GizmoHelper, GizmoViewport, Environment, ContactShadows } from '@react-three/drei'
import { useAppStore } from '@/store'
import ModelMesh from './ModelMesh'
import SectionViewPlane from './SectionViewPlane'
import MeasurementTool from './MeasurementTool'
import ScaleBar from './ScaleBar'
import HandLoader from '@/components/studio/HandLoader'

function EmptyState() {
  return (
    <mesh>
      <boxGeometry args={[0.001, 0.001, 0.001]} />
      <meshBasicMaterial transparent opacity={0} />
    </mesh>
  )
}

export default function Viewport() {
  const {
    meshPayload,
    sectionViewActive,
    measurementActive,
    generationStatus,
  } = useAppStore()

  return (
    <div className="relative w-full h-full bg-[#0d0d14]">
      <Canvas
        camera={{ position: [80, 60, 160], fov: 45, near: 0.1, far: 10000 }}
        gl={{ localClippingEnabled: true, antialias: true, alpha: false }}
        dpr={[1, 2]}
        shadows
        style={{ background: '#0d0d14' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[100, 200, 100]}
          intensity={1.4}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />
        <directionalLight position={[-80, -40, -80]} intensity={0.35} />
        <pointLight position={[0, 150, 0]} intensity={0.3} color="#4488FF" />

        <Suspense fallback={<EmptyState />}>
          {meshPayload ? <ModelMesh /> : <EmptyState />}
          {sectionViewActive && meshPayload && <SectionViewPlane />}
          <MeasurementTool />
        </Suspense>

        {meshPayload && (
          <ContactShadows
            opacity={0.3}
            scale={200}
            blur={2}
            far={80}
            resolution={512}
            color="#000022"
            position={[0, -70, 0]}
          />
        )}

        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.05}
          enabled={!measurementActive}
          minDistance={20}
          maxDistance={600}
        />

        <GizmoHelper alignment="bottom-right" margin={[72, 72]}>
          <GizmoViewport
            axisColors={['#ff4060', '#80ff80', '#4488FF']}
            labelColor="white"
          />
        </GizmoHelper>
      </Canvas>

      {meshPayload && <ScaleBar />}

      {generationStatus === 'loading' && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60">
          <HandLoader />
          <p className="text-white/80 text-sm font-light mt-10 tracking-wide">
            Building solid geometry
          </p>
          <p className="text-white/40 text-xs mt-1">
            Applying Boolean operations — this takes a few seconds
          </p>
        </div>
      )}

      {!meshPayload && generationStatus !== 'loading' && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 opacity-20">
              <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="8" y="8" width="48" height="48" rx="4" />
                <circle cx="32" cy="32" r="14" />
                <circle cx="32" cy="32" r="6" />
                <line x1="32" y1="8" x2="32" y2="18" />
                <line x1="32" y1="46" x2="32" y2="56" />
                <line x1="8" y1="32" x2="18" y2="32" />
                <line x1="46" y1="32" x2="56" y2="32" />
              </svg>
            </div>
            <p className="text-forge-muted text-sm">Upload a blueprint and generate the 3D model</p>
          </div>
        </div>
      )}
    </div>
  )
}
