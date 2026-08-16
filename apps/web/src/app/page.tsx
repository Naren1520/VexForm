'use client'
import HeroSection from '@/components/landing/HeroSection'
import HowItWorks from '@/components/landing/HowItWorks'
import FeaturesGrid from '@/components/landing/FeaturesGrid'
import TechnicalShowcase from '@/components/landing/TechnicalShowcase'
import CTASection from '@/components/landing/CTASection'
import LandingNav from '@/components/landing/LandingNav'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      <LandingNav />
      <HeroSection />
      <HowItWorks />
      <FeaturesGrid />
      <TechnicalShowcase />
      <CTASection />
    </main>
  )
}
