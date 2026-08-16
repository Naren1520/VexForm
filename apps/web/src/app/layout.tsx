import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'VexForm — Blueprint to 3D',
  description:
    'Transform complex engineering blueprints into validated, parametric 3D CAD geometry using AI-assisted dimension extraction and deterministic solid modeling.',
  keywords: ['CAD', '3D modeling', 'engineering', 'AI', 'blueprint', 'OpenCascade'],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-scroll-behavior="smooth" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
