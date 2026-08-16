import type { ThreeElements } from '@react-three/fiber'

// Augment both 'react' and the jsx-runtime modules so Three.js JSX elements
// are recognised under all JSX transform modes (classic + automatic).
declare module 'react' {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}

declare module 'react/jsx-runtime' {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}

declare module 'react/jsx-dev-runtime' {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}
