'use client'

const FEATURES = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <circle cx="10" cy="10" r="8"/>
        <path d="M10 6v4l3 3"/>
        <circle cx="10" cy="10" r="2" fill="currentColor" stroke="none"/>
      </svg>
    ),
    title: 'AI Dimension Extraction',
    desc: 'Gemini Vision reads bores, flanges, angles and tolerances directly from the blueprint image with strict JSON schema validation.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <rect x="2" y="2" width="16" height="16" rx="2"/>
        <path d="M6 10h8M10 6v8"/>
        <circle cx="10" cy="10" r="2"/>
      </svg>
    ),
    title: 'Parametric Geometry',
    desc: 'Every dimension is a named parameter. Change a value, regenerate — the entire solid updates while maintaining all geometric constraints.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <circle cx="10" cy="10" r="7"/>
        <circle cx="10" cy="10" r="3.5"/>
        <path d="M10 2v2M10 16v2M2 10h2M16 10h2"/>
      </svg>
    ),
    title: 'Boolean Solid Modeling',
    desc: 'OpenCascade BRepAlgoAPI_Cut performs real material subtraction — bores and cavities exist in the actual B-Rep topology.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <path d="M10 2L10 18"/>
        <path d="M4 6l6-4 6 4"/>
        <path d="M4 14l6 4 6-4"/>
        <rect x="5" y="7" width="10" height="6" rx="1"/>
      </svg>
    ),
    title: 'Internal Cavity Reconstruction',
    desc: 'Section the model at any axis to reveal stepped bores, side port passages, counterbores — all real geometry, no material faking.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <path d="M4 10l4 4 8-8"/>
        <circle cx="10" cy="10" r="8"/>
      </svg>
    ),
    title: 'Geometric Validation',
    desc: 'BRepCheck_Analyzer confirms every solid is manifold and valid before it reaches the viewer. Failed operations surface immediately.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4">
        <path d="M3 10h14"/>
        <path d="M10 3v14"/>
        <rect x="6" y="6" width="8" height="8" rx="1"/>
      </svg>
    ),
    title: 'Interactive Section Analysis',
    desc: 'A draggable clipping plane slices through the solid in real time — proving internal geometry exists and matches blueprint specifications.',
  },
]

export default function FeaturesGrid() {
  return (
    <section id="features" className="py-24 px-6 bg-[#0a0a0f]">
      <div className="max-w-5xl mx-auto">
        <div className="mb-14 text-center">
          <p className="text-forge-blue text-xs font-medium uppercase tracking-widest mb-3">Engineering Intelligence</p>
          <h2 className="text-3xl md:text-4xl font-bold text-white">Built for Accuracy</h2>
          <p className="text-white/50 mt-3 max-w-xl mx-auto text-sm">
            Every feature is designed around geometric correctness, not visual approximation.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="group rounded-xl p-5 transition-all duration-200"
              style={{
                background: 'rgba(255,255,255,0.025)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255,255,255,0.07)',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.background = 'rgba(68,136,255,0.06)'
                el.style.borderColor = 'rgba(68,136,255,0.2)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.background = 'rgba(255,255,255,0.025)'
                el.style.borderColor = 'rgba(255,255,255,0.07)'
              }}
            >
              <div className="text-forge-blue mb-3">{f.icon}</div>
              <h3 className="text-white text-sm font-semibold mb-2">{f.title}</h3>
              <p className="text-white/50 text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
