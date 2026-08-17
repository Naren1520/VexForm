'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'

const SECTIONS = [
  {
    id: 'acceptance',
    title: 'Acceptance of Terms',
    body: `By accessing or using VexForm, you agree to be bound by these Terms of Service. If you do not agree to these terms, you may not access or use the service. These terms apply to all users of VexForm, including visitors, registered users, and anyone who accesses the platform in any capacity.`,
  },
  {
    id: 'description',
    title: 'Description of Service',
    body: `VexForm is an AI-assisted CAD platform that converts 2D engineering drawings into validated 3D solid models. The service uses machine learning for dimension extraction and deterministic geometry engines for model construction. VexForm is provided as a software-as-a-service tool for engineering and design workflows.`,
  },
  {
    id: 'accounts',
    title: 'User Accounts',
    body: `You may sign in to VexForm using your Google account. By doing so, you grant VexForm permission to access your basic profile information including your name, email address, and profile picture. You are responsible for maintaining the security of your account and for all activities that occur under your account. You must notify us immediately of any unauthorized use of your account.`,
  },
  {
    id: 'data',
    title: 'User Data and Engineering Content',
    body: `Engineering drawings you upload to VexForm are processed to extract dimensional parameters and generate 3D geometry. Uploaded files are used solely for the purpose of model generation within your active session. VexForm does not retain, store, or share your engineering drawings or generated geometry beyond the duration of your session unless you explicitly save them. You retain full ownership of all engineering content you upload.`,
  },
  {
    id: 'ip',
    title: 'Intellectual Property',
    body: `All content, software, algorithms, and design elements of VexForm are the property of VexForm and its developers, protected by applicable intellectual property laws. You may not copy, modify, distribute, or create derivative works from any part of the VexForm platform without prior written consent. The 3D models generated from your engineering drawings are owned by you and may be used for any lawful purpose.`,
  },
  {
    id: 'prohibited',
    title: 'Prohibited Uses',
    body: `You may not use VexForm to upload drawings or data that you do not have the right to use, or that contain confidential third-party information without authorization. You may not attempt to reverse-engineer, probe, or exploit the VexForm platform. You may not use the service for any unlawful purpose or in violation of any applicable regulation. Automated or bulk access to the service without prior agreement is not permitted.`,
  },
  {
    id: 'disclaimer',
    title: 'Disclaimer of Warranties',
    body: `VexForm is provided on an "as is" and "as available" basis without warranties of any kind, either express or implied. We do not warrant that the service will be uninterrupted, error-free, or that the generated 3D models will be suitable for any specific engineering or manufacturing application. All generated models should be independently verified by a qualified engineer before use in any physical or safety-critical application.`,
  },
  {
    id: 'liability',
    title: 'Limitation of Liability',
    body: `To the fullest extent permitted by applicable law, VexForm and its developers shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the service. This includes damages resulting from reliance on AI-extracted dimensions, geometry generation errors, or any other output produced by the platform.`,
  },
  {
    id: 'changes',
    title: 'Changes to Terms',
    body: `We reserve the right to modify these Terms of Service at any time. Changes will be posted to this page with an updated effective date. Your continued use of VexForm after any changes constitutes your acceptance of the revised terms. We encourage you to review these terms periodically.`,
  },
  {
    id: 'contact',
    title: 'Contact',
    body: `If you have any questions about these Terms of Service, please contact us at narensonu1520@gmail.com. We will respond to all inquiries within a reasonable timeframe.`,
  },
]

export default function TermsPage() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll()
  const progressWidth = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])
  const [active, setActive] = useState('acceptance')

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
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: "url('/images/img-terms.jpg')" }} />
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
            Terms of Service
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
                href="/legal/privacy"
                className="block text-xs font-light transition-colors duration-200"
                style={{ color: '#444' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#444' }}
              >
                Privacy Policy →
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
          <Link href="/legal/privacy" className="text-xs font-light transition-colors duration-200" style={{ color: '#777' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#c8b89a' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#777' }}>
            Privacy Policy
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
