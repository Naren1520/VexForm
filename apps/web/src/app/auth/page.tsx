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
    <main
      className="min-h-screen relative flex items-center justify-center overflow-hidden"
      style={{ background: '#0c0c0c' }}
    >
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/images/img1.jpg')" }}
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(135deg, rgba(12,12,12,0.97) 0%, rgba(12,12,12,0.85) 50%, rgba(12,12,12,0.75) 100%)',
        }}
      />

      <div className="absolute left-[55%] top-1/2 -translate-y-1/2 hidden lg:block pointer-events-none opacity-30">
        <OrbitLoader />
      </div>

      <div className="relative z-10 w-full max-w-sm mx-auto px-6">
        <Link
          href="/"
          className="flex items-center gap-3 mb-16 group w-fit"
        >
          <div
            className="relative overflow-hidden rounded-full shrink-0"
            style={{ width: 30, height: 30, outline: '1px solid #c8b89a', outlineOffset: '2px' }}
          >
            <Image
              src="/images/logo/logo.png"
              alt="VexForm"
              fill
              sizes="30px"
              className="object-cover rounded-full"
            />
          </div>
          <span
            className="text-xs font-semibold tracking-widest uppercase transition-colors duration-200"
            style={{ color: '#f5f0eb' }}
          >
            VEXFORM
          </span>
        </Link>

        <p
          className="text-xs uppercase tracking-widest mb-4"
          style={{ color: '#c8b89a', letterSpacing: '0.18em' }}
        >
          Access Studio
        </p>

        <h1
          className="font-light leading-tight mb-3"
          style={{ fontSize: '2.5rem', color: '#f5f0eb', letterSpacing: '-0.02em' }}
        >
          Sign in to
          <br />
          <span style={{ color: '#c8b89a' }}>continue.</span>
        </h1>

        <p
          className="font-light leading-relaxed mb-12 text-sm"
          style={{ color: '#555' }}
        >
          Your engineering studio is one click away.
          No password needed.
        </p>

        {error && (
          <div
            className="mb-6 px-4 py-3 text-xs"
            style={{ border: '1px solid #ff444433', background: '#ff44440a', color: '#ff8888' }}
          >
            Authentication failed. Please try again.
          </div>
        )}

        <button
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="w-full flex items-center justify-center gap-4 py-4 px-6
                     transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: loading ? '#1a1a1a' : '#f5f0eb',
            color: '#0c0c0c',
            border: '1px solid transparent',
          }}
          onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
          onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
        >
          {loading ? (
            <span
              className="w-4 h-4 rounded-full border border-white/20 border-t-transparent animate-spin"
            />
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
          )}
          <span className="text-xs font-medium uppercase tracking-widest">
            {loading ? 'Signing in…' : 'Continue with Google'}
          </span>
        </button>

        <div
          className="mt-8 pt-8 flex items-start gap-3"
          style={{ borderTop: '1px solid #1a1a1a' }}
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="shrink-0 mt-0.5">
            <rect x="3" y="7" width="10" height="8" rx="1" stroke="#333" strokeWidth="1"/>
            <path d="M5 7V5a3 3 0 016 0v2" stroke="#333" strokeWidth="1"/>
          </svg>
          <p className="text-xs font-light leading-relaxed" style={{ color: '#333' }}>
            We only store your name, email, and profile picture from Google.
            Your engineering data stays in your session only.
          </p>
        </div>

        <p className="mt-8 text-center text-xs" style={{ color: '#2a2a2a' }}>
          By continuing, you agree to our{' '}
          <span style={{ color: '#3a3a3a' }}>Terms of Service</span>
          {' '}and{' '}
          <span style={{ color: '#3a3a3a' }}>Privacy Policy</span>
        </p>
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
