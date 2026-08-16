import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CAD Studio -VexForm',
  description: 'Blueprint to 3D solid modeling workstation',
}

export default function StudioLayout({ children }: { children: React.ReactNode }) {
  return children
}
