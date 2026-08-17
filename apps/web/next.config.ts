import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  transpilePackages: ['three', '@react-three/fiber', '@react-three/drei'],
  turbopack: {},
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
    ],
  },
}

export default nextConfig
