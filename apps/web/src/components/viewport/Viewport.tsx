'use client'
import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, GizmoHelper, GizmoViewport, ContactShadows } from '@react-three/drei'
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
  const { meshPayload, sectionViewActive, measurementActive, generationStatus } = useAppStore()

  return (
    <div className="relative w-full h-full" style={{ background: '#090909' }}>
      <Canvas
        camera={{ position: [80, 60, 160], fov: 45, near: 0.1, far: 10000 }}
        gl={{ localClippingEnabled: true, antialias: true, alpha: false }}
        dpr={[1, 2]}
        shadows
        style={{ background: '#090909' }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[100, 200, 100]} intensity={1.4} castShadow shadow-mapSize={[2048, 2048]} />
        <directionalLight position={[-80, -40, -80]} intensity={0.3} />
        <pointLight position={[0, 150, 0]} intensity={0.2} color="#c8b89a" />

        <Suspense fallback={<EmptyState />}>
          {meshPayload ? <ModelMesh /> : <EmptyState />}
          {sectionViewActive && meshPayload && <SectionViewPlane />}
          <MeasurementTool />
        </Suspense>

        {meshPayload && (
          <ContactShadows
            opacity={0.25}
            scale={200}
            blur={2}
            far={80}
            resolution={512}
            color="#000000"
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
            axisColors={['#cc4455', '#66aa66', '#c8b89a']}
            labelColor="#888888"
          />
        </GizmoHelper>
      </Canvas>

      {meshPayload && <ScaleBar />}

      {generationStatus === 'loading' && (
        <div
          className="absolute inset-0 flex flex-col items-center justify-center"
          style={{ background: 'rgba(0,0,0,0.75)' }}
        >
          <HandLoader />
          <p className="text-sm font-light mt-10 tracking-wide" style={{ color: 'rgba(255,255,255,0.7)' }}>
            Building solid geometry
          </p>
          <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.3)' }}>
            Applying Boolean operations — this takes a few seconds
          </p>
        </div>
      )}

      {!meshPayload && generationStatus !== 'loading' && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="w-14 h-14 mx-auto mb-5" style={{ opacity: 0.12 }}>
              <svg viewBox="0 0 64 64" fill="none" stroke="#c8b89a" strokeWidth="1">
                <circle cx="32" cy="32" r="28" />
                <circle cx="32" cy="32" r="14" />
                <circle cx="32" cy="32" r="5" />
                <line x1="32" y1="4"  x2="32" y2="18" />
                <line x1="32" y1="46" x2="32" y2="60" />
                <line x1="4"  y1="32" x2="18" y2="32" />
                <line x1="46" y1="32" x2="60" y2="32" />
              </svg>
            </div>
            <p className="text-xs uppercase tracking-widest" style={{ color: '#333' }}>
              Upload a blueprint and generate the 3D model
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
