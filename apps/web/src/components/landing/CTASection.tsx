import Link from 'next/link'

export default function CTASection() {
  return (
    <section
      className="relative py-28 px-6 overflow-hidden"
      style={{
        backgroundImage: `
          url('https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=1920&q=80&auto=format&fit=crop')
        `,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Overlay */}
      <div
        className="absolute inset-0"
        style={{ background: 'rgba(10,10,15,0.82)' }}
      />

      {/* Grid */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(68,136,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(68,136,255,0.06) 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px',
        }}
      />

      <div className="relative z-10 max-w-3xl mx-auto text-center">
        <p className="text-forge-blue text-xs font-medium uppercase tracking-widest mb-4">
          Ready to start
        </p>
        <h2 className="text-3xl md:text-5xl font-bold text-white mb-5 leading-tight">
          Turn the next engineering<br />drawing into a 3D model.
        </h2>
        <p className="text-white/50 text-sm md:text-base max-w-lg mx-auto mb-8 leading-relaxed">
          Upload a blueprint, let AI extract the dimensions, and generate a validated
          Boolean solid in seconds. Export as STEP for manufacturing.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/studio"
            className="px-8 py-3 rounded-xl text-sm font-semibold text-white transition-all duration-150"
            style={{
              background: '#4488FF',
              border: '1px solid rgba(68,136,255,0.6)',
            }}
          >
            Open CAD Studio →
          </Link>
          <a
            href="#how-it-works"
            className="px-8 py-3 rounded-xl text-sm font-medium transition-all duration-150"
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.12)',
              backdropFilter: 'blur(12px)',
              color: 'rgba(255,255,255,0.7)',
            }}
          >
            Learn more
          </a>
        </div>
      </div>
    </section>
  )
}
