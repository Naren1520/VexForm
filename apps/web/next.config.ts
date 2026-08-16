import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  // Transpile Three.js ecosystem — required for App Router + Turbopack
  transpilePackages: ['three', '@react-three/fiber', '@react-three/drei'],

  // Turbopack-specific: resolve aliases to ensure single React instance
  turbopack: {
    resolveAlias: {
      react: path.resolve('./node_modules/react'),
      'react-dom': path.resolve('./node_modules/react-dom'),
    },
  },

  // Webpack config (production builds)
  webpack(config) {
    config.resolve = config.resolve ?? {}
    config.resolve.alias = {
      ...(config.resolve.alias as Record<string, string>),
      react: path.resolve('./node_modules/react'),
      'react-dom': path.resolve('./node_modules/react-dom'),
    }
    return config
  },
}

export default nextConfig
