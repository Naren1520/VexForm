'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import CubeLoader from './CubeLoader'

const STEPS = [
  {
    number: '01',
    title: 'Upload Your Drawing',
    body: 'Drop in any 2D engineering drawing -scanned blueprint, CAD export, or photograph. The system reads dimensions directly from the image, no manual tracing required.',
  },
  {
    number: '02',
    title: 'Automatic Dimension Reading',
    body: 'AI vision scans every annotation on the drawing and pulls out all critical dimensions -diameters, depths, bolt patterns, angles, tolerances, and surface finishes.',
  },
  {
    number: '03',
    title: 'Review Before You Build',
    body: 'Every dimension is laid out for you to verify. Values that differ from standard ranges are flagged. You stay in control -edit anything before the model is generated.',
  },
  {
    number: '04',
    title: 'Solid 3D Model Generated',
    body: 'The geometry engine constructs a true solid model from the parameters -flanges, bores, bolt holes, fillets, and chamfers are all built as real physical features, not textures.',
  },
  {
    number: '05',
    title: 'Inspect, Measure, Export',
    body: 'Section through the model to verify internal geometry. Measure any distance in the viewer. Export as STEP for your CNC workflow, STL for printing, or OBJ for visualisation.',
  },
]

export default function HowItWorks() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const imgY = useTransform(scrollYProgress, [0, 1], ['-8%', '8%'])

  return (
    <section id="process" className="relative overflow-hidden" style={{ background: '#0c0c0c' }}>
      <div
        className="w-full py-2"
        style={{ borderTop: '1px solid #1a1a1a', borderBottom: '1px solid #1a1a1a' }}
      >
        <div className="flex items-center overflow-hidden py-3">
          <motion.div
            animate={{ x: ['0%', '-50%'] }}
            transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
            className="flex items-center gap-12 whitespace-nowrap"
          >
            {Array.from({ length: 8 }).map((_, i) => (
              <span key={i} className="flex items-center gap-12">
                <span className="text-xs uppercase tracking-widest" style={{ color: '#555555', letterSpacing: '0.18em' }}>AI Vision</span>
                <span className="w-1 h-1 rounded-full" style={{ background: '#555555' }} />
                <span className="text-xs uppercase tracking-widest" style={{ color: '#555555', letterSpacing: '0.18em' }}>Parametric Modeling</span>
                <span className="w-1 h-1 rounded-full" style={{ background: '#555555' }} />
                <span className="text-xs uppercase tracking-widest" style={{ color: '#555555', letterSpacing: '0.18em' }}>Solid Geometry</span>
                <span className="w-1 h-1 rounded-full" style={{ background: '#555555' }} />
                <span className="text-xs uppercase tracking-widest" style={{ color: '#555555', letterSpacing: '0.18em' }}>Interactive 3D Viewer</span>
                <span className="w-1 h-1 rounded-full" style={{ background: '#555555' }} />
              </span>
            ))}
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 md:px-16 py-32 grid grid-cols-1 lg:grid-cols-2 gap-24">
        <div>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-xs tracking-widest uppercase mb-6"
            style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
          >
            The Process
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
            className="font-light leading-tight mb-16"
            style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)', color: '#f5f0eb', letterSpacing: '-0.02em' }}
          >
            From flat drawing
            <br />
            to solid geometry.
          </motion.h2>

          <div className="space-y-0">
            {STEPS.map((step, i) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.6, delay: i * 0.08, ease: [0.25, 0.1, 0.25, 1] }}
                className="group flex gap-8 py-8 cursor-default"
                style={{ borderBottom: '1px solid #1a1a1a' }}
              >
                <span
                  className="font-light shrink-0 transition-colors duration-300"
                  style={{ color: '#585858', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.04em', paddingTop: '2px' }}
                  onMouseEnter={(e) => { (e.target as HTMLElement).style.color = '#c8b89a' }}
                  onMouseLeave={(e) => { (e.target as HTMLElement).style.color = '#585858' }}
                >
                  {step.number}
                </span>
                <div>
                  <h3
                    className="font-normal mb-3 transition-colors duration-300"
                    style={{ color: '#c0c0c0', fontSize: '0.9rem', letterSpacing: '0.01em' }}
                  >
                    {step.title}
                  </h3>
                  <p className="font-light leading-relaxed" style={{ color: '#787878', fontSize: '0.85rem' }}>
                    {step.body}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div ref={ref} className="relative hidden lg:block">
          <div className="flex flex-col" style={{ border: '1px solid #1a1a1a' }}>
            <div className="relative overflow-hidden" style={{ height: '520px' }}>
              <div
                className="absolute inset-0 bg-cover bg-center"
                style={{ backgroundImage: "url('/images/img2.jpg')" }}
              />
              <div
                className="absolute inset-0"
                style={{ background: 'rgba(12,12,12,0.5)' }}
              />

              <div className="relative z-10 h-full flex flex-col justify-end p-8">
                <div
                  className="inline-block px-3 py-1 mb-4 text-xs uppercase tracking-widest"
                  style={{ background: '#c8b89a', color: '#0c0c0c', letterSpacing: '0.12em' }}
                >
                  Lower Valve Body
                </div>
                <p className="font-light text-sm" style={{ color: '#b0b0b0' }}>
                  Injector Assembly, Globe Valve type
                  <br />
                  Material: HT150
                </p>
              </div>
            </div>

            <div
              className="flex flex-col items-center justify-center py-16 gap-6"
              style={{ background: '#080808' }}
            >
              <CubeLoader />
              <p
                className="text-xs uppercase tracking-widest text-center"
                style={{ color: '#3a3a3a', letterSpacing: '0.18em' }}
              >
                Solid geometry engine
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
