'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState } from 'react'
import Link from 'next/link'

const SECTIONS = [
  {
    id: 'overview',
    title: 'Overview',
    body: `This Privacy Policy explains how VexForm collects, uses, and protects information about you when you use our platform. We are committed to handling your data with transparency and respect. By using VexForm, you agree to the practices described in this policy.`,
  },
  {
    id: 'collected',
    title: 'Information We Collect',
    body: `When you sign in with Google, we receive your name, email address, and profile picture from Google's OAuth service. We store this information in our database to identify your account. We do not collect passwords, payment information, or any data beyond what Google provides during authentication. We also collect basic usage information such as session activity to ensure the service functions correctly.`,
  },
  {
    id: 'engineering',
    title: 'Engineering Drawings and Generated Models',
    body: `Engineering drawings you upload are processed in memory to extract dimensional parameters using AI vision and to generate 3D solid geometry. These files are not stored on our servers beyond your active session. Generated 3D models exist only within your browser session. We do not retain, analyze, or share your engineering content after your session ends.`,
  },
  {
    id: 'usage',
    title: 'How We Use Your Information',
    body: `We use your name and email address to identify your account and associate it with your session. We use your profile picture to display your avatar in the interface. We do not sell, rent, or share your personal information with third parties for marketing purposes. We may use aggregated, anonymized usage data to improve the platform.`,
  },
  {
    id: 'google',
    title: 'Google OAuth',
    body: `VexForm uses Google OAuth 2.0 for authentication. When you sign in, Google shares basic profile information with us under the scopes you approve. We request only the minimum necessary permissions: your name, email, and profile picture. You can revoke VexForm's access to your Google account at any time through your Google Account settings at myaccount.google.com/permissions.`,
  },
  {
    id: 'storage',
    title: 'Data Storage and Security',
    body: `Your account information is stored in MongoDB Atlas, a cloud database hosted on secure infrastructure. We use industry-standard security practices including encrypted connections (TLS/SSL) for all data transmission. Authentication sessions are secured with signed JWT tokens. While we take reasonable measures to protect your data, no system is completely immune to security risks.`,
  },
  {
    id: 'cookies',
    title: 'Cookies and Session Data',
    body: `VexForm uses secure HTTP-only cookies to maintain your authentication session. These cookies contain a signed JWT token used to verify your identity across page loads. We do not use tracking cookies, advertising cookies, or third-party analytics cookies. Session cookies expire when you sign out or after a period of inactivity.`,
  },
  {
    id: 'rights',
    title: 'Your Rights',
    body: `You have the right to access the personal information we hold about you, to request correction of inaccurate data, and to request deletion of your account and associated data. To exercise any of these rights, contact us at narensonu1520@gmail.com. We will respond to all requests within 30 days.`,
  },
  {
    id: 'retention',
    title: 'Data Retention',
    body: `We retain your account information for as long as your account is active. If you request account deletion, we will remove your personal information from our database within 30 days. Engineering drawings and generated models are not retained beyond your session and do not need to be explicitly deleted.`,
  },
  {
    id: 'changes',
    title: 'Changes to This Policy',
    body: `We may update this Privacy Policy from time to time. Changes will be posted to this page with an updated effective date. Your continued use of VexForm after any changes constitutes your acceptance of the updated policy. We recommend reviewing this page periodically.`,
  },
  {
    id: 'contact',
    title: 'Contact Us',
    body: `If you have any questions, concerns, or requests related to this Privacy Policy, please contact us at narensonu1520@gmail.com. We take privacy inquiries seriously and will respond promptly.`,
  },
]

export default function PrivacyPage() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll()
  const progressWidth = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])
  const [active, setActive] = useState('overview')

  return (
    <div className="min-h-screen" style={{ background: '#0c0c0c', color: '#f5f0eb' }}>
      <motion.div
        className="fixed top-0 left-0 h-px z-50"
        style={{ width: progressWidth, background: '#c8b89a' }}
      />

      <div
        className="relative h-[40vh] min-h-[300px] flex flex-col justify-end overflow-hidden"
        style={{ borderBottom: '1px solid #1a1a1a' }}
      >
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: "url('/images/img-privacy.jpg')" }} />
        <div className="absolute inset-0" style={{ background: 'rgba(12,12,12,0.82)' }} />

        <div className="relative z-10 max-w-6xl mx-auto w-full px-8 md:px-16 pb-12">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-[10px] uppercase tracking-widest mb-8 transition-colors duration-200"
            style={{ color: '#3a3a3a' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#3a3a3a' }}
          >
            <span>←</span> VexForm
          </Link>
          <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: '#c8b89a', letterSpacing: '0.2em' }}>
            Legal
          </p>
          <h1 className="font-light" style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)', letterSpacing: '-0.02em', color: '#f5f0eb' }}>
            Privacy Policy
          </h1>
          <p className="text-xs mt-3 font-light" style={{ color: '#555' }}>
            Effective date: August 2026
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 md:px-16 py-16 flex flex-col lg:flex-row gap-16">
        <nav className="hidden lg:block w-56 shrink-0">
          <div className="sticky top-8 space-y-0">
            <p className="text-[10px] uppercase tracking-widest mb-4" style={{ color: '#555', letterSpacing: '0.16em' }}>
              Contents
            </p>
            {SECTIONS.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                onClick={() => setActive(s.id)}
                className="block py-2 text-xs transition-all duration-200 font-light"
                style={{
                  color: active === s.id ? '#f5f0eb' : '#777',
                  borderLeft: `2px solid ${active === s.id ? '#c8b89a' : 'transparent'}`,
                  paddingLeft: '12px',
                }}
                onMouseEnter={(e) => { if (active !== s.id) (e.currentTarget as HTMLElement).style.color = '#ccc' }}
                onMouseLeave={(e) => { if (active !== s.id) (e.currentTarget as HTMLElement).style.color = '#777' }}
              >
                {s.title}
              </a>
            ))}

            <div className="pt-8 mt-8" style={{ borderTop: '1px solid #1a1a1a' }}>
              <Link
                href="/legal/terms"
                className="block text-xs font-light transition-colors duration-200"
                style={{ color: '#444' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#444' }}
              >
                Terms of Service →
              </Link>
            </div>
          </div>
        </nav>

        <div ref={ref} className="flex-1 min-w-0 space-y-0">
          {SECTIONS.map((section, i) => (
            <motion.div
              key={section.id}
              id={section.id}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
              onViewportEnter={() => setActive(section.id)}
              className="py-10"
              style={{ borderBottom: i < SECTIONS.length - 1 ? '1px solid #1a1a1a' : 'none' }}
            >
              <div className="flex items-start gap-6 mb-5">
                <span
                  className="font-light shrink-0 mt-1"
                  style={{ color: '#555', fontSize: '0.7rem', fontFamily: 'var(--font-mono)' }}
                >
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h2
                  className="font-normal"
                  style={{ fontSize: '1.05rem', color: '#e0e0e0', letterSpacing: '0.01em' }}
                >
                  {section.title}
                </h2>
              </div>
              <p
                className="font-light leading-relaxed ml-10"
                style={{ color: '#b0b0b0', fontSize: '0.875rem', lineHeight: '1.8' }}
              >
                {section.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      <div
        className="max-w-6xl mx-auto px-8 md:px-16 py-10 flex flex-col sm:flex-row items-center justify-between gap-4"
        style={{ borderTop: '1px solid #1a1a1a' }}
      >
        <span className="text-xs font-light" style={{ color: '#555' }}>
          VexForm — AI-Assisted CAD Reconstruction
        </span>
        <div className="flex items-center gap-6">
          <Link href="/legal/terms" className="text-xs font-light transition-colors duration-200" style={{ color: '#777' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#777' }}>
            Terms of Service
          </Link>
          <Link href="/" className="text-xs font-light transition-colors duration-200" style={{ color: '#777' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#f5f0eb' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#777' }}>
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
