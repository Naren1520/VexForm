'use client'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function HeroSection() {
  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{
        backgroundImage: `
          url('https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=1920&q=80&auto=format&fit=crop'),
          linear-gradient(180deg, #0a0a0f 0%, transparent 40%, #0a0a0f 100%)
        `,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundBlendMode: 'normal',
      }}
    >
      {/* Dark overlay — no glow, just depth */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(180deg, rgba(10,10,15,0.65) 0%, rgba(10,10,15,0.45) 50%, rgba(10,10,15,0.92) 100%)',
        }}
      />

      {/* Engineering grid overlay */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `
            linear-gradient(rgba(68, 136, 255, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(68, 136, 255, 0.06) 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px',
        }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-3xl">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="inline-flex items-center gap-2 mb-6 px-3 py-1 rounded-full text-xs font-medium"
            style={{
              background: 'rgba(68, 136, 255, 0.10)',
              border: '1px solid rgba(68, 136, 255, 0.25)',
              backdropFilter: 'blur(12px)',
              color: '#6aa3ff',
            }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-forge-blue" />
            AI-Assisted CAD Reconstruction · OpenCascade Boolean Solids
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-4xl md:text-6xl font-bold text-white leading-tight tracking-tight mb-4"
          >
            From Engineering
            <br />
            <span className="text-white/90">Drawings to</span>
            <br />
            <span
              style={{
                backgroundImage: 'linear-gradient(90deg, #4488FF, #88bbff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Intelligent 3D Reality
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            className="text-base md:text-lg text-white/60 mb-8 leading-relaxed max-w-xl"
          >
            Transform complex engineering blueprints into validated, parametric 3D CAD geometry
            using AI-assisted dimension extraction and deterministic solid modeling.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.5 }}
            className="flex flex-wrap items-center gap-3"
          >
            <Link
              href="/studio"
              className="px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all duration-150"
              style={{
                background: '#4488FF',
                border: '1px solid rgba(68,136,255,0.6)',
              }}
            >
              Launch CAD Studio →
            </Link>
            <a
              href="#how-it-works"
              className="px-6 py-3 rounded-xl text-sm font-medium transition-all duration-150"
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.12)',
                backdropFilter: 'blur(12px)',
                color: 'rgba(255,255,255,0.75)',
              }}
            >
              View Engineering Demo
            </a>
          </motion.div>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="mt-12 flex flex-wrap gap-8"
          >
            {[
              { label: 'Boolean Operations', value: '14+' },
              { label: 'Blueprint Dimensions', value: '28' },
              { label: 'Export Formats', value: 'STEP/STL/OBJ' },
              { label: 'CAD Kernel', value: 'OpenCascade' },
            ].map((stat) => (
              <div key={stat.label} className="flex flex-col gap-0.5">
                <span className="text-white text-xl font-semibold font-mono">{stat.value}</span>
                <span className="text-white/40 text-xs">{stat.label}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Bottom fade */}
      <div
        className="absolute bottom-0 left-0 right-0 h-24 pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, transparent, #0a0a0f)',
        }}
      />
    </section>
  )
}
