const PIPELINE = [
  { label: 'Blueprint', sub: 'JPEG / PNG / PDF' },
  { label: 'Gemini Vision', sub: 'AI Extraction' },
  { label: 'Parameters', sub: '28 dimensions' },
  { label: 'CAD Kernel', sub: 'OpenCascade' },
  { label: 'Validation', sub: 'BRepCheck' },
  { label: '3D Solid', sub: 'B-Rep Topology' },
]

const SPECS = [
  { label: 'Target Part',       value: 'Lower Valve Body' },
  { label: 'Material',          value: 'HT150 Cast Iron' },
  { label: 'Overall Height',    value: '118 mm' },
  { label: 'Main Bore Upper',   value: 'Ø 28 mm' },
  { label: 'Side Port Angle',   value: '135°' },
  { label: 'Top Flange Bolts',  value: '4 × Ø 7 mm' },
  { label: 'Bottom Flange Ø',   value: 'Ø 65 mm' },
  { label: 'Fillet Radius',     value: 'R1 mm' },
  { label: 'Boolean Ops',       value: '14 operations' },
  { label: 'Export Formats',    value: 'STEP / STL / OBJ' },
]

export default function TechnicalShowcase() {
  return (
    <section id="showcase" className="py-24 px-6 bg-[#0d0d14]">
      <div className="max-w-5xl mx-auto">
        <div className="mb-14 text-center">
          <p className="text-forge-blue text-xs font-medium uppercase tracking-widest mb-3">Technical Showcase</p>
          <h2 className="text-3xl md:text-4xl font-bold text-white">The Engineering Pipeline</h2>
          <p className="text-white/50 mt-3 max-w-xl mx-auto text-sm">
            Every hole, cavity and internal passage is modeled as actual geometry rather than visual decoration.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* Pipeline flow */}
          <div
            className="rounded-2xl p-6"
            style={{
              background: 'rgba(255,255,255,0.02)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255,255,255,0.07)',
            }}
          >
            <p className="text-white/60 text-xs uppercase tracking-widest mb-5">Engineering Workflow</p>
            <div className="flex flex-col gap-0">
              {PIPELINE.map((step, i) => (
                <div key={step.label} className="flex items-start gap-3">
                  {/* Left rail */}
                  <div className="flex flex-col items-center shrink-0 mt-1">
                    <div
                      className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold font-mono"
                      style={{
                        background: 'rgba(68,136,255,0.12)',
                        border: '1px solid rgba(68,136,255,0.3)',
                        color: '#4488FF',
                      }}
                    >
                      {i + 1}
                    </div>
                    {i < PIPELINE.length - 1 && (
                      <div className="w-px flex-1 my-1" style={{ minHeight: '24px', background: 'rgba(68,136,255,0.15)' }} />
                    )}
                  </div>
                  {/* Content */}
                  <div className="pb-5">
                    <p className="text-white text-sm font-medium leading-none">{step.label}</p>
                    <p className="text-white/40 text-xs mt-0.5">{step.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Spec sheet */}
          <div
            className="rounded-2xl p-6"
            style={{
              background: 'rgba(255,255,255,0.02)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255,255,255,0.07)',
            }}
          >
            <p className="text-white/60 text-xs uppercase tracking-widest mb-5">Reference Specification</p>
            <div className="space-y-2">
              {SPECS.map((spec) => (
                <div
                  key={spec.label}
                  className="flex items-center justify-between py-1.5 border-b"
                  style={{ borderColor: 'rgba(255,255,255,0.05)' }}
                >
                  <span className="text-white/50 text-xs">{spec.label}</span>
                  <span className="text-white text-xs font-mono">{spec.value}</span>
                </div>
              ))}
            </div>

            {/* Geometry accuracy callout */}
            <div
              className="mt-5 rounded-lg p-3"
              style={{
                background: 'rgba(68,136,255,0.07)',
                border: '1px solid rgba(68,136,255,0.18)',
              }}
            >
              <p className="text-forge-blue text-xs font-medium mb-1">Geometry Accuracy</p>
              <p className="text-white/50 text-xs leading-relaxed">
                Section the model at any axis to reveal the complete internal topology —
                stepped bores, counterbores, and side port passages exist as real subtracted material.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
