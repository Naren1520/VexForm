import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'VexForm -Blueprint to 3D',
  description:
    'Transform complex engineering blueprints into validated, parametric 3D CAD geometry using AI-assisted dimension extraction and deterministic solid modeling.',
  keywords: ['CAD', '3D modeling', 'engineering', 'AI', 'blueprint', 'OpenCascade'],
  icons: {
    icon: '/images/logo/logo.png',
    apple: '/images/logo/logo.png',
    shortcut: '/images/logo/logo.png',
  },
  openGraph: {
    title: 'VexForm -Blueprint to 3D',
    description:
      'Transform complex engineering blueprints into validated, parametric 3D CAD geometry using AI-assisted dimension extraction and deterministic solid modeling.',
    images: [{ url: '/images/logo/logo.png', width: 512, height: 512, alt: 'VexForm' }],
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'VexForm -Blueprint to 3D',
    description: 'Blueprint to validated 3D CAD geometry using AI + OpenCascade.',
    images: ['/images/logo/logo.png'],
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
