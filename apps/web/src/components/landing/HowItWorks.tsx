const STEPS = [
  {
    num: '01',
    title: 'Upload Drawing',
    desc: 'Upload any engineering blueprint as JPEG, PNG, or PDF. The system accepts standard technical drawings up to 20 MB.',
  },
  {
    num: '02',
    title: 'Extract Parameters',
    desc: 'Gemini Vision API analyses the drawing and extracts all 28 dimensional parameters including bores, flanges, angles and tolerances.',
  },
  {
    num: '03',
    title: 'Validate Constraints',
    desc: 'Every parameter is checked against geometric constraints — bore diameters, counterbore ratios, depth limits — before generation.',
  },
  {
    num: '04',
    title: 'Generate Solid',
    desc: 'OpenCascade performs 14 Boolean operations: base cylinder → fused flanges → subtracted bores → bolt holes → fillets and chamfers.',
  },
  {
    num: '05',
    title: 'Inspect in 3D',
    desc: 'Orbit, section, measure and export the validated solid. The clipping plane reveals every internal bore and cavity in real geometry.',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 bg-engineering-grid">
      <div className="max-w-5xl mx-auto">
        <div className="mb-14 text-center">
          <p className="text-forge-blue text-xs font-medium uppercase tracking-widest mb-3">Process</p>
          <h2 className="text-3xl md:text-4xl font-bold text-white">How It Works</h2>
          <p className="text-white/50 mt-3 max-w-xl mx-auto text-sm">
            A deterministic pipeline from 2D drawing to validated 3D solid — every step is traceable.
          </p>
        </div>

        <div className="relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-8 left-0 right-0 h-px bg-white/[0.07]" />

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {STEPS.map((step, i) => (
              <div key={step.num} className="relative">
                {/* Step number bubble */}
                <div className="flex md:justify-center mb-4">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold font-mono relative z-10"
                    style={{
                      background: 'rgba(10,10,15,1)',
                      border: '1px solid rgba(68,136,255,0.35)',
                      color: '#4488FF',
                    }}
                  >
                    {step.num}
                  </div>
                </div>
                {/* Card */}
                <div
                  className="rounded-xl p-4"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(255,255,255,0.07)',
                  }}
                >
                  <h3 className="text-white text-sm font-semibold mb-2">{step.title}</h3>
                  <p className="text-white/50 text-xs leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
