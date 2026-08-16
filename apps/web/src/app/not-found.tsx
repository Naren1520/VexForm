import Link from 'next/link'

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: '#090909', color: '#f5f0eb' }}
    >
      <div className="text-center">
        <p
          className="font-light font-mono mb-4"
          style={{ fontSize: '5rem', color: '#1e1e1e', letterSpacing: '-0.04em' }}
        >
          404
        </p>
        <p className="text-sm font-light mb-8" style={{ color: '#555' }}>
          Page not found
        </p>
        <Link
          href="/"
          className="text-xs uppercase tracking-widest transition-colors duration-200"
          style={{ color: '#c8b89a' }}
          onMouseEnter={(e) => { (e.target as HTMLElement).style.color = '#f5f0eb' }}
          onMouseLeave={(e) => { (e.target as HTMLElement).style.color = '#c8b89a' }}
        >
          ← Back to VexForm
        </Link>
      </div>
    </div>
  )
}
