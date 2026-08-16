import Link from 'next/link'

export default function LandingNav() {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center justify-between px-8"
      style={{
        background: 'rgba(10, 10, 15, 0.75)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-7 h-7 rounded-md bg-forge-blue/20 border border-forge-blue/30 flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="1" y="1" width="12" height="12" rx="1.5" stroke="#4488FF" strokeWidth="1.2"/>
            <circle cx="7" cy="7" r="3.5" stroke="#4488FF" strokeWidth="1.2"/>
            <line x1="7" y1="1" x2="7" y2="4" stroke="#4488FF" strokeWidth="1.2"/>
            <line x1="7" y1="10" x2="7" y2="13" stroke="#4488FF" strokeWidth="1.2"/>
          </svg>
        </div>
        <span className="text-white font-semibold text-sm tracking-tight">VexForm</span>
      </div>

      {/* Links */}
      <div className="hidden md:flex items-center gap-6">
        <a href="#how-it-works" className="text-forge-muted text-sm hover:text-white transition-colors">
          How It Works
        </a>
        <a href="#features" className="text-forge-muted text-sm hover:text-white transition-colors">
          Features
        </a>
        <a href="#showcase" className="text-forge-muted text-sm hover:text-white transition-colors">
          Showcase
        </a>
      </div>

      {/* CTA */}
      <Link
        href="/studio"
        className="px-4 py-1.5 rounded-lg text-sm font-medium text-white transition-colors duration-150"
        style={{
          background: 'rgba(68, 136, 255, 0.15)',
          border: '1px solid rgba(68, 136, 255, 0.35)',
          backdropFilter: 'blur(12px)',
        }}
      >
        Launch Studio
      </Link>
    </nav>
  )
}
