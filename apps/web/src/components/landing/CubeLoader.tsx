'use client'

export default function CubeLoader() {
  return (
    <>
      <style>{`
        .cube-loader {
          --size: 80px;
          width: var(--size);
          height: var(--size);
          position: relative;
          transform-origin: 50% 100%;
          transform-style: preserve-3d;
          perspective: 5000px;
          animation: cube-rotar 10s linear infinite alternate both;
        }
        .cube-side {
          width: var(--size);
          height: var(--size);
          position: absolute;
          background:
            repeating-linear-gradient(to right, transparent 1% 9%, #c8b89a44 9% 10%),
            repeating-linear-gradient(to top,   transparent 1% 9%, #c8b89a44 9% 10%);
          background-color: rgba(200, 184, 154, 0.06);
          border: 1px solid rgba(200, 184, 154, 0.15);
        }
        .cube-behind {
          transform: translateZ(calc(-1 * var(--size)));
        }
        .cube-right {
          transform-origin: 100% 50%;
          transform: rotateY(-90deg);
        }
        .cube-left {
          transform-origin: 0% 50%;
          transform: rotateY(90deg);
        }
        .cube-top {
          transform-origin: 50% 0;
          transform: rotateX(-90deg);
        }
        .cube-bottom {
          transform-origin: 50% 100%;
          transform: rotateX(90deg);
        }
        @keyframes cube-rotar {
          0%   { transform: rotateX(0deg)   rotateY(0deg); }
          100% { transform: rotateX(360deg) rotateY(360deg); }
        }
      `}</style>

      <div className="cube-loader">
        <div className="cube-side" />
        <div className="cube-side cube-behind" />
        <div className="cube-side cube-right" />
        <div className="cube-side cube-left" />
        <div className="cube-side cube-top" />
        <div className="cube-side cube-bottom" />
      </div>
    </>
  )
}
