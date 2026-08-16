'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useState } from 'react'

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

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
            style={{
              width: 34,
              height: 34,
              outline: '1.5px solid #c8b89a',
              outlineOffset: '2px',
            }}
          >
            <Image
              src="/images/logo/logo.png"
              alt="VexForm"
              fill
              sizes="34px"
              className="object-cover rounded-full"
              priority
            />
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

        <Link
          href="/studio"
          className="text-xs tracking-widest uppercase transition-all duration-200 px-5 py-2.5"
          style={{
            color: '#0c0c0c',
            background: '#f5f0eb',
            letterSpacing: '0.1em',
          }}
          onMouseEnter={(e) => {
            const el = e.currentTarget as HTMLElement
            el.style.background = '#c8b89a'
          }}
          onMouseLeave={(e) => {
            const el = e.currentTarget as HTMLElement
            el.style.background = '#f5f0eb'
          }}
        >
          Open Studio
        </Link>
      </div>
    </nav>
  )
}
