'use client'
import Link from 'next/link'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import StarLoader from './StarLoader'
// import OrbitLoader from './OrbitLoader'

export default function HeroSection() {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] })
  const imgY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '12%'])
  const opacity = useTransform(scrollYProgress, [0, 0.6], [1, 0])

  return (
    <section ref={ref} className="relative h-screen min-h-[700px] overflow-hidden">
      <motion.div className="absolute inset-0" style={{ y: imgY }}>
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/images/img1.jpg')" }}
        />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(to bottom, rgba(12,12,12,0.65) 0%, rgba(12,12,12,0.55) 50%, rgba(12,12,12,0.95) 100%)' }}
        />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(to left, rgba(12,12,12,0.82) 0%, rgba(12,12,12,0.5) 40%, transparent 100%)' }}
        />
      </motion.div>

      <motion.div
        className="absolute inset-0 pointer-events-none flex items-center justify-end pr-[8%]"
        style={{ opacity }}
      >
        <StarLoader />
        {/* <OrbitLoader /> */}
      </motion.div>

      <motion.div
        className="relative z-10 h-full flex flex-col justify-end pb-28 px-8 md:px-16 max-w-7xl mx-auto"
        style={{ y: textY, opacity }}
      >
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
          className="text-xs tracking-widest uppercase mb-8"
          style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
        >
          2D Drawing to 3D Model
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.35, ease: [0.25, 0.1, 0.25, 1] }}
          className="font-light leading-none mb-8"
          style={{
            fontSize: 'clamp(3rem, 8vw, 7rem)',
            color: '#f5f0eb',
            letterSpacing: '-0.02em',
          }}
        >
          Blueprint
          <br />
          <span style={{ color: '#c8b89a' }}>to 3D Reality.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.55, ease: [0.25, 0.1, 0.25, 1] }}
          className="max-w-lg mb-12 font-light leading-relaxed"
          style={{ color: '#c0c0c0', fontSize: '1rem' }}
        >
          Upload any engineering drawing and get a fully parametric, measurable
          3D model in seconds — ready to section, inspect, and export for manufacturing.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
          className="flex items-center gap-6"
        >
          <Link
            href="/studio"
            className="text-xs tracking-widest uppercase px-8 py-4 transition-all duration-300"
            style={{ background: '#f5f0eb', color: '#0c0c0c', letterSpacing: '0.12em' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
          >
            Open CAD Studio
          </Link>
          <a
            href="#process"
            className="text-xs tracking-widest uppercase transition-colors duration-200 flex items-center gap-3"
            style={{ color: '#909090', letterSpacing: '0.12em' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#f5f0eb' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#909090' }}
          >
            See How It Works
            <span className="block w-8 h-px" style={{ background: 'currentColor' }} />
          </a>
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2, delay: 1.4 }}
        className="absolute bottom-10 right-10 z-10 flex flex-col items-center gap-3"
      >
        <span
          className="text-xs uppercase tracking-widest"
          style={{ color: '#585858', letterSpacing: '0.14em', writingMode: 'vertical-rl' }}
        >
          Scroll
        </span>
        <div className="w-px h-12" style={{ background: 'linear-gradient(to bottom, #585858, transparent)' }} />
      </motion.div>
    </section>
  )
}
