'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useState, useRef } from 'react'
import { useSession, signOut } from 'next-auth/react'

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { data: session } = useSession()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  const studioHref = session ? '/studio' : '/auth?next=/studio'
  const user = session?.user

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-500"
      style={{
        borderBottom: scrolled ? '1px solid #1e1e1e' : '1px solid transparent',
        background: scrolled ? 'rgba(12,12,12,0.96)' : 'transparent',
        backdropFilter: scrolled ? 'blur(24px)' : 'none',
      }}
    >
      <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div
            className="relative shrink-0 overflow-hidden rounded-full"
            style={{ width: 34, height: 34, outline: '1.5px solid #c8b89a', outlineOffset: '2px' }}
          >
            <Image src="/images/logo/logo.png" alt="VexForm" fill sizes="34px" className="object-cover rounded-full" priority />
          </div>
          <span
            className="font-semibold tracking-tight text-sm transition-colors duration-200"
            style={{ color: '#f5f0eb', letterSpacing: '0.04em' }}
          >
            VEXFORM
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-10">
          {[
            { label: 'Process', href: '#process' },
            { label: 'Technology', href: '#technology' },
            { label: 'Capabilities', href: '#capabilities' },
          ].map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-xs tracking-widest uppercase transition-colors duration-200"
              style={{ color: '#aaaaaa', letterSpacing: '0.1em' }}
              onMouseEnter={(e) => ((e.target as HTMLElement).style.color = '#f5f0eb')}
              onMouseLeave={(e) => ((e.target as HTMLElement).style.color = '#aaaaaa')}
            >
              {item.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <div ref={dropdownRef} className="relative">
              <button
                onClick={() => setDropdownOpen((p) => !p)}
                className="flex items-center gap-3 transition-opacity duration-200 hover:opacity-80"
              >
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-medium leading-tight" style={{ color: '#f5f0eb' }}>
                    {user.name}
                  </p>
                  <p className="text-[10px] leading-tight" style={{ color: '#555' }}>
                    {user.email}
                  </p>
                </div>
                <div
                  className="relative shrink-0 overflow-hidden rounded-full"
                  style={{ width: 32, height: 32, outline: '1px solid #2a2a2a', outlineOffset: '2px' }}
                >
                  {user.image ? (
                    <Image
                      src={user.image}
                      alt={user.name ?? 'User'}
                      fill
                      sizes="32px"
                      className="object-cover rounded-full"
                    />
                  ) : (
                    <div
                      className="w-full h-full flex items-center justify-center text-xs font-medium"
                      style={{ background: '#1a1a1a', color: '#c8b89a' }}
                    >
                      {user.name?.[0]?.toUpperCase() ?? 'U'}
                    </div>
                  )}
                </div>
                <svg
                  width="10" height="6" viewBox="0 0 10 6" fill="none"
                  className="transition-transform duration-200"
                  style={{ transform: dropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <path d="M1 1l4 4 4-4" stroke="#555" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
              </button>

              {dropdownOpen && (
                <div
                  className="absolute right-0 top-full mt-3 w-56 py-1"
                  style={{ background: '#111', border: '1px solid #1e1e1e' }}
                >
                  <div className="px-4 py-3" style={{ borderBottom: '1px solid #1a1a1a' }}>
                    <p className="text-xs font-medium truncate" style={{ color: '#f5f0eb' }}>
                      {user.name}
                    </p>
                    <p className="text-[10px] truncate mt-0.5" style={{ color: '#555' }}>
                      {user.email}
                    </p>
                  </div>

                  <Link
                    href="/studio"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs uppercase tracking-widest transition-colors duration-150"
                    style={{ color: '#888' }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#f5f0eb' }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#888' }}
                  >
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                      <rect x="1" y="1" width="14" height="14" rx="1" stroke="currentColor" strokeWidth="1"/>
                      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1"/>
                    </svg>
                    Open Studio
                  </Link>

                  <button
                    onClick={() => { setDropdownOpen(false); signOut({ callbackUrl: '/' }) }}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-xs uppercase tracking-widest transition-colors duration-150 text-left"
                    style={{ color: '#888' }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#ff8888' }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#888' }}
                  >
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                      <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
                      <path d="M11 11l3-3-3-3M14 8H6" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href={studioHref}
              className="text-xs tracking-widest uppercase transition-all duration-200 px-5 py-2.5"
              style={{ color: '#0c0c0c', background: '#f5f0eb', letterSpacing: '0.1em' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}
