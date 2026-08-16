'use client'
import Link from 'next/link'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

export default function CTASection() {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const imgY = useTransform(scrollYProgress, [0, 1], ['-8%', '8%'])

  return (
    <section ref={ref} className="relative overflow-hidden" style={{ minHeight: '80vh' }}>
      <motion.div className="absolute inset-0" style={{ y: imgY }}>
        <div
          className="absolute inset-[-10%] bg-cover bg-center"
          style={{ backgroundImage: "url('/images/img5.jpg')" }}
        />
        <div
          className="absolute inset-0"
          style={{ background: 'rgba(12,12,12,0.78)' }}
        />
      </motion.div>

      <div className="relative z-10 h-full min-h-[80vh] flex flex-col justify-between px-8 md:px-16 max-w-7xl mx-auto py-28">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
        >
          <p
            className="text-xs tracking-widest uppercase mb-8"
            style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
          >
            Get Started
          </p>
          <h2
            className="font-light leading-none"
            style={{ fontSize: 'clamp(2.5rem, 6vw, 5.5rem)', color: '#f5f0eb', letterSpacing: '-0.02em', maxWidth: '14ch' }}
          >
            Turn the next
            <br />
            drawing into
            <br />
            a 3D model.
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 mt-20">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.25, 0.1, 0.25, 1] }}
          >
            <p className="font-light leading-relaxed mb-10" style={{ color: '#909090', fontSize: '0.9rem' }}>
              Upload your drawing, confirm the dimensions the AI reads, and get
              a fully solid 3D model in seconds. Section it, measure it, then
              export directly into your manufacturing workflow -no manual CAD
              modelling required.
            </p>
            <div className="flex items-center gap-6">
              <Link
                href="/studio"
                className="text-xs tracking-widest uppercase px-8 py-4 transition-all duration-300"
                style={{
                  background: '#f5f0eb',
                  color: '#0c0c0c',
                  letterSpacing: '0.12em',
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
              >
                Open CAD Studio
              </Link>
              <a
                href="#process"
                className="text-xs tracking-widest uppercase transition-colors duration-200"
                style={{ color: '#707070', letterSpacing: '0.12em' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#f5f0eb' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#707070' }}
              >
                Review the process
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.28, ease: [0.25, 0.1, 0.25, 1] }}
            className="flex flex-col justify-end"
          >
            <div className="space-y-0">
              {[
                { label: 'Upload', detail: 'Any 2D engineering drawing' },
                { label: 'Read', detail: 'AI reads all dimensions automatically' },
                { label: 'Generate', detail: 'Full solid 3D model in seconds' },
                { label: 'Export', detail: 'STEP, STL, or OBJ -ready for production' },
              ].map((item, i) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: 12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.3 + i * 0.07 }}
                  className="flex items-center justify-between py-4"
                  style={{ borderBottom: '1px solid #1a1a1a' }}
                >
                  <span className="text-xs uppercase tracking-widest" style={{ color: '#707070', letterSpacing: '0.12em' }}>
                    {item.label}
                  </span>
                  <span className="text-xs font-light" style={{ color: '#909090' }}>
                    {item.detail}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      <div
        className="relative z-10 px-8 md:px-16 max-w-7xl mx-auto pb-12 flex items-center justify-between"
        style={{ borderTop: '1px solid #1a1a1a' }}
      >
        <span className="text-xs font-light" style={{ color: '#505050' }}>
          VexForm -2D Drawing to 3D Model
        </span>
        <span className="text-xs font-light" style={{ color: '#505050' }}>
          Built by Naren S J
        </span>
      </div>
    </section>
  )
}
