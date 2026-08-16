'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

const CAPABILITIES = [
  {
    index: '01',
    title: 'Reads Any Engineering Drawing',
    detail: 'Upload a scanned blueprint, a photograph of a hand drawing, or a digital PDF. The AI reads every annotated dimension — diameters, depths, bolt circles, port angles, tolerances, and surface notes.',
  },
  {
    index: '02',
    title: 'Every Dimension is Editable',
    detail: 'All extracted values are presented for your review before anything is built. Change a bore diameter, adjust a flange thickness, correct a bolt count — the model reflects exactly what you approve.',
  },
  {
    index: '03',
    title: 'True Solid, Not a Shell',
    detail: 'Internal bores, side passages, stepped cavities, and counterbores are cut through the full solid mass. Section the model at any point and the internal geometry is exactly what the drawing specifies.',
  },
  {
    index: '04',
    title: 'Geometry Verified Before Delivery',
    detail: 'Every model is checked for physical validity — wall thicknesses, bore clearances, bolt circle geometry, and angular consistency are all verified before the 3D model is shown to you.',
  },
  {
    index: '05',
    title: 'Interactive Inspection Tools',
    detail: 'Drag a section plane through the solid to reveal any internal feature. Click two points to measure a distance. Rotate and zoom freely. Every feature from the drawing is individually selectable.',
  },
  {
    index: '06',
    title: 'Export for Any Downstream Use',
    detail: 'Download as STEP to open in SolidWorks, Fusion 360, or FreeCAD for further machining work. Export as STL for 3D printing or FEA simulation. OBJ format for rendering and visualisation.',
  },
]

export default function FeaturesGrid() {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const imgY = useTransform(scrollYProgress, [0, 1], ['-8%', '8%'])

  return (
    <section id="capabilities" ref={ref} className="relative overflow-hidden" style={{ background: '#0c0c0c' }}>
      <div className="relative overflow-hidden" style={{ height: '400px', borderBottom: '1px solid #1a1a1a' }}>
        <motion.div className="absolute inset-0" style={{ y: imgY }}>
          <div
            className="absolute inset-[-10%] bg-cover bg-center"
            style={{ backgroundImage: "url('/images/img4.jpg')" }}
          />
          <div
            className="absolute inset-0"
            style={{ background: 'rgba(12,12,12,0.72)' }}
          />
        </motion.div>

        <div className="relative z-10 h-full flex items-end px-8 md:px-16 pb-16 max-w-7xl mx-auto">
          <div>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-xs tracking-widest uppercase mb-5"
              style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
            >
              Capabilities
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
              className="font-light leading-tight"
              style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)', color: '#f5f0eb', letterSpacing: '-0.02em' }}
            >
              Built for
              <br />
              engineering accuracy.
            </motion.h2>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 md:px-16 py-0">
        {CAPABILITIES.map((cap, i) => (
          <motion.div
            key={cap.index}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.55, delay: 0, ease: [0.25, 0.1, 0.25, 1] }}
            className="group grid grid-cols-1 md:grid-cols-12 gap-6 py-10 transition-all duration-300"
            style={{ borderBottom: '1px solid #1a1a1a' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#0f0f0f' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent' }}
          >
            <div className="md:col-span-1">
              <span
                className="font-light"
                style={{ color: '#585858', fontSize: '0.7rem', fontFamily: 'var(--font-mono)' }}
              >
                {cap.index}
              </span>
            </div>
            <div className="md:col-span-4">
              <h3
                className="font-normal transition-colors duration-300 group-hover:text-[#f5f0eb]"
                style={{ color: '#b8b8b8', fontSize: '0.95rem', letterSpacing: '0.01em' }}
              >
                {cap.title}
              </h3>
            </div>
            <div className="md:col-span-7">
              <p className="font-light leading-relaxed" style={{ color: '#808080', fontSize: '0.875rem' }}>
                {cap.detail}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="max-w-7xl mx-auto px-8 md:px-16 py-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-0" style={{ border: '1px solid #1a1a1a' }}>
          {[
            { value: '28', label: 'Dimensions extracted' },
            { value: 'STEP', label: 'Manufacturing-ready format' },
            { value: '<5s', label: 'Model generation time' },
            { value: '100%', label: 'True solid geometry' },
          ].map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="px-8 py-10"
              style={{ borderRight: i < 3 ? '1px solid #1a1a1a' : 'none' }}
            >
              <div
                className="font-light mb-2"
                style={{ color: '#f5f0eb', fontSize: '1.6rem', letterSpacing: '-0.02em' }}
              >
                {item.value}
              </div>
              <div className="text-xs uppercase tracking-widest" style={{ color: '#686868', letterSpacing: '0.12em' }}>
                {item.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
