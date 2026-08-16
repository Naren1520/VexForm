'use client'
import LandingNav from '@/components/landing/LandingNav'
import HeroSection from '@/components/landing/HeroSection'
import HowItWorks from '@/components/landing/HowItWorks'
import TechnicalShowcase from '@/components/landing/TechnicalShowcase'
import FeaturesGrid from '@/components/landing/FeaturesGrid'
import CTASection from '@/components/landing/CTASection'

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-x-hidden" style={{ background: '#0c0c0c', color: '#f5f0eb' }}>
      <LandingNav />
      <HeroSection />
      <HowItWorks />
      <TechnicalShowcase />
      <FeaturesGrid />
      <CTASection />
    </main>
  )
}
