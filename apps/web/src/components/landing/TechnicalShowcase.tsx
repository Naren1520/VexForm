'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

const GEOMETRY_FEATURES = [
  { step: '01', label: 'Main Body', detail: 'Outer cylindrical shell with precise diameter and height from the drawing' },
  { step: '02', label: 'Top Flange', detail: 'Full annular flange built to specified outer diameter and thickness' },
  { step: '03', label: 'Bottom Flange', detail: 'Matching bottom flange with independent diameter and depth control' },
  { step: '04', label: 'Side Port Boss', detail: 'Radial boss projected at the exact angle specified in the drawing' },
  { step: '05', label: 'Upper Bore', detail: 'Primary through-bore cut from the top to the correct depth and diameter' },
  { step: '06', label: 'Lower Bore', detail: 'Stepped inner bore with independent diameter — creates the internal shoulder' },
  { step: '07', label: 'Side Port Bore', detail: 'Lateral bore through the boss and body at the specified angle' },
  { step: '08', label: 'Top Bolt Pattern', detail: 'Bolt holes and counterbores on the top flange, evenly distributed' },
  { step: '09', label: 'Bottom Bolt Pattern', detail: 'Bolt holes and counterbores on the bottom flange at the bolt circle diameter' },
  { step: '10', label: 'Side Port Bolts', detail: 'Fastener holes on the side port flange face' },
  { step: '11', label: 'Edge Fillets', detail: 'Radius blends applied to all transition edges per drawing notes' },
  { step: '12', label: 'Chamfers', detail: 'Lead-in chamfers on bore entries and flange edges as specified' },
]

export default function TechnicalShowcase() {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const imgY = useTransform(scrollYProgress, [0, 1], ['-6%', '6%'])

  return (
    <section id="technology" ref={ref} className="relative overflow-hidden" style={{ background: '#080808' }}>
      <div className="relative min-h-screen grid grid-cols-1 lg:grid-cols-2">
        <div className="relative hidden lg:block overflow-hidden">
          <motion.div className="absolute inset-0" style={{ y: imgY }}>
            <div
              className="absolute inset-[-10%] bg-cover bg-center"
              style={{ backgroundImage: "url('/images/img3.jpg')" }}
            />
            <div
              className="absolute inset-0"
              style={{ background: 'rgba(8,8,8,0.65)' }}
            />
          </motion.div>

          <div className="relative z-10 h-full flex flex-col justify-between p-12 pt-32">
            <div>
              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="text-xs tracking-widest uppercase mb-4"
                style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
              >
                Solid Geometry
              </motion.p>
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
                className="font-light leading-tight"
                style={{ fontSize: 'clamp(2rem, 3.5vw, 3rem)', color: '#f5f0eb', letterSpacing: '-0.02em' }}
              >
                Real geometry.
                <br />
                Not visualization.
              </motion.h2>
            </div>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="font-light leading-relaxed max-w-sm"
              style={{ color: '#909090', fontSize: '0.9rem' }}
            >
              Every feature in the model is a true physical solid — bores cut through
              the full depth, flanges fused to the body, chamfers blended at every
              edge. Section it anywhere and the internal geometry is exactly what the
              drawing specifies.
            </motion.p>
          </div>
        </div>

        <div className="py-24 px-8 lg:px-16 flex flex-col justify-center" style={{ borderLeft: '1px solid #1a1a1a' }}>
          <div className="lg:hidden mb-12">
            <p className="text-xs tracking-widest uppercase mb-4" style={{ color: '#c8b89a', letterSpacing: '0.18em' }}>Solid Geometry</p>
            <h2 className="font-light leading-tight" style={{ fontSize: '2.5rem', color: '#f5f0eb', letterSpacing: '-0.02em' }}>
              Real geometry.
            </h2>
          </div>

          <p
            className="text-xs tracking-widest uppercase mb-8"
            style={{ color: '#686868', letterSpacing: '0.18em' }}
          >
            Model Features — Built from Your Drawing
          </p>

          <div className="space-y-0">
            {GEOMETRY_FEATURES.map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, x: 16 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.4, delay: i * 0.04, ease: [0.25, 0.1, 0.25, 1] }}
                className="group flex items-start gap-6 py-4 transition-all duration-200"
                style={{ borderBottom: '1px solid #161616' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#111' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent' }}
              >
                <span
                  className="shrink-0 w-6 font-light"
                  style={{ color: '#585858', fontSize: '0.65rem', fontFamily: 'var(--font-mono)', paddingTop: '2px' }}
                >
                  {item.step}
                </span>
                <span
                  className="shrink-0 w-36 font-normal"
                  style={{ color: '#c0c0c0', fontSize: '0.8rem' }}
                >
                  {item.label}
                </span>
                <span className="flex-1 font-light" style={{ color: '#686868', fontSize: '0.78rem', lineHeight: '1.5' }}>
                  {item.detail}
                </span>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="mt-10 pt-8 flex items-center gap-4"
            style={{ borderTop: '1px solid #1a1a1a' }}
          >
            <div className="w-1.5 h-1.5 rounded-full" style={{ background: '#c8b89a' }} />
            <span className="text-xs font-light" style={{ color: '#787878' }}>
              Every solid is validated for geometric integrity before it reaches the viewer
            </span>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
