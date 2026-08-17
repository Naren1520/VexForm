'use client'
import { signIn } from 'next-auth/react'
import { useSearchParams } from 'next/navigation'
import { useState, Suspense } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import OrbitLoader from '@/components/landing/OrbitLoader'

function AuthContent() {
  const searchParams = useSearchParams()
  const next = searchParams.get('next') ?? '/studio'
  const error = searchParams.get('error')
  const [loading, setLoading] = useState(false)

  const handleGoogleSignIn = async () => {
    setLoading(true)
    await signIn('google', { callbackUrl: next })
  }

  return (
    <main className="min-h-screen flex" style={{ background: '#0c0c0c' }}>
      <div
        className="relative flex flex-col justify-between w-full lg:w-[46%] shrink-0 px-12 md:px-20 py-10"
        style={{ borderRight: '1px solid #1a1a1a' }}
      >
        <Link href="/" className="flex items-center gap-3 w-fit group">
          <div
            className="relative overflow-hidden rounded-full shrink-0"
            style={{ width: 30, height: 30, outline: '1px solid #c8b89a', outlineOffset: '2px' }}
          >
            <Image src="/images/logo/logo.png" alt="VexForm" fill sizes="30px" className="object-cover rounded-full" />
          </div>
          <span
            className="text-xs font-semibold tracking-widest uppercase transition-colors duration-200"
            style={{ color: '#f5f0eb' }}
          >
            VEXFORM
          </span>
        </Link>

        <div className="flex flex-col justify-center flex-1 py-16">
          <p
            className="text-xs uppercase tracking-widest mb-6"
            style={{ color: '#c8b89a', letterSpacing: '0.2em' }}
          >
            Access Studio
          </p>

          <h1
            className="font-light leading-none mb-6"
            style={{ fontSize: 'clamp(3rem, 5vw, 4.5rem)', color: '#f5f0eb', letterSpacing: '-0.03em' }}
          >
            Sign in to
            <br />
            <span style={{ color: '#c8b89a' }}>continue.</span>
          </h1>

          <p
            className="font-light leading-relaxed mb-14 max-w-xs"
            style={{ color: '#888888', fontSize: '0.875rem' }}
          >
            Your engineering workspace is one click away.
            No password, no friction.
          </p>

          {error && (
            <div
              className="mb-8 px-4 py-3 text-xs font-light"
              style={{ border: '1px solid #ff444433', background: '#ff44440a', color: '#ff8888' }}
            >
              Authentication failed — please try again.
            </div>
          )}

          <button
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="flex items-center gap-4 py-4 px-6 w-full transition-all duration-300
                       disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: loading ? '#1a1a1a' : '#f5f0eb',
              color: '#0c0c0c',
            }}
            onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
            onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
          >
            {loading ? (
              <span className="w-4 h-4 rounded-full border border-black/20 border-t-transparent animate-spin mx-auto" />
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" className="shrink-0">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                <span className="text-xs font-medium uppercase tracking-widest flex-1 text-center">
                  Continue with Google
                </span>
              </>
            )}
          </button>

          <div
            className="mt-10 pt-8 flex items-start gap-3"
            style={{ borderTop: '1px solid #1a1a1a' }}
          >
            <svg width="13" height="13" viewBox="0 0 16 16" fill="none" className="shrink-0 mt-0.5">
              <rect x="3" y="7" width="10" height="8" rx="1" stroke="#555" strokeWidth="1.2"/>
              <path d="M5 7V5a3 3 0 016 0v2" stroke="#555" strokeWidth="1.2"/>
            </svg>
            <p className="text-xs font-light leading-relaxed" style={{ color: '#707070' }}>
              We only store your name, email, and profile picture.
              Your engineering data stays in your session.
            </p>
          </div>
        </div>

        <p className="text-[10px] text-center" style={{ color: '#4a4a4a' }}>
          By continuing you agree to our{' '}
          <Link href="/legal/terms" className="transition-colors duration-150" style={{ color: '#6a6a6a' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#6a6a6a' }}>
            Terms of Service
          </Link>
          {' '}and{' '}
          <Link href="/legal/privacy" className="transition-colors duration-150" style={{ color: '#6a6a6a' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#6a6a6a' }}>
            Privacy Policy
          </Link>
        </p>
      </div>

      <div className="relative flex-1 hidden lg:flex items-center justify-center overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/images/img6.jpg')" }}
        />
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, rgba(12,12,12,0.85) 0%, rgba(12,12,12,0.4) 60%, rgba(12,12,12,0.7) 100%)',
          }}
        />

        <div className="relative z-10 flex flex-col items-center gap-8 px-16 text-center">
          <div style={{ opacity: 0.9 }}>
            <OrbitLoader />
          </div>

          <div style={{ borderTop: '1px solid #1a1a1a', paddingTop: '2rem', maxWidth: '22rem' }}>
            <p
              className="font-light leading-relaxed text-sm"
              style={{ color: '#aaaaaa' }}
            >
              Upload any engineering drawing.
              Get a fully solid, measurable 3D model in seconds.
            </p>
          </div>

          <div className="flex items-center gap-10">
            {[
              { value: '28', label: 'Dimensions read' },
              { value: '<5s', label: 'Generation' },
              { value: 'STEP', label: 'Export format' },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <div
                  className="font-light mb-1"
                  style={{ color: '#f5f0eb', fontSize: '1.4rem', letterSpacing: '-0.02em', fontFamily: 'var(--font-mono)' }}
                >
                  {s.value}
                </div>
                <div className="text-[10px] uppercase tracking-widest" style={{ color: '#707070', letterSpacing: '0.14em' }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}

export default function AuthPage() {
  return (
    <Suspense>
      <AuthContent />
    </Suspense>
  )
}
