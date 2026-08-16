import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center text-white">
      <div className="text-center">
        <p className="text-forge-muted text-6xl font-mono mb-4">404</p>
        <p className="text-white/60 mb-6">Page not found</p>
        <Link href="/" className="text-forge-blue text-sm hover:underline">
          ← Back to VexForm
        </Link>
      </div>
    </div>
  )
}
