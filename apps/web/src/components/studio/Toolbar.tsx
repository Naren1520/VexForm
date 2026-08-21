'use client'
import { useAppStore } from '@/store'
import { downloadBlob } from '@/lib/api'
import Link from 'next/link'
import Image from 'next/image'

export default function Toolbar() {
  const {
    wireframeMode, toggleWireframe,
    sectionViewActive, toggleSectionView, sectionPlaneOffset, setSectionPlaneOffset,
    measurementActive, toggleMeasurement, clearMeasurement,
    meshPayload, sessionToken,
    exportingFormat, setExportingFormat,
    addToast,
  } = useAppStore()

  const hasModel = !!meshPayload

  const handleExport = async (fmt: 'step' | 'stl' | 'obj') => {
    if (!hasModel) return
    setExportingFormat(fmt)
    // Use shape type from store for filename; fall back to 'model'
    const shapeName = (useAppStore.getState() as any).shapeType ?? 'model'
    const filename = `${shapeName}.${fmt}`
    try {
      await downloadBlob(`/export/${fmt}`, filename, sessionToken)
      addToast(`${fmt.toUpperCase()} exported successfully`, 'info')
    } catch (err: any) {
      addToast(err.message ?? `Export ${fmt} failed`, 'error')
    } finally {
      setExportingFormat(null)
    }
  }

  const btnBase = 'px-3 py-1 text-[11px] font-medium tracking-wide uppercase transition-all duration-150 whitespace-nowrap border'
  const btnActive = 'bg-white/10 text-white border-white/20'
  const btnDefault = 'bg-transparent text-white/40 border-white/[0.08] hover:text-white/80 hover:border-white/20'
  const btnDisabled = 'opacity-25 cursor-not-allowed bg-transparent text-white/30 border-white/[0.06]'

  return (
    <div
      className="h-12 flex items-center px-4 gap-3 shrink-0 overflow-x-auto"
      style={{ background: '#0a0a0a', borderBottom: '1px solid #1a1a1a' }}
    >
      <Link href="/" className="flex items-center gap-2.5 mr-3 shrink-0 group">
        <div
          className="relative overflow-hidden rounded-full shrink-0"
          style={{ width: 26, height: 26, outline: '1px solid #c8b89a', outlineOffset: '2px' }}
        >
          <Image src="/images/logo/logo.png" alt="VexForm" fill sizes="26px" className="object-cover rounded-full" />
        </div>
        <span className="text-white/80 text-xs font-semibold tracking-widest uppercase group-hover:text-white transition-colors">
          VexForm
        </span>
      </Link>

      <div className="w-px h-5 shrink-0" style={{ background: '#222' }} />

      <div className="flex items-center gap-1.5">
        <button onClick={toggleWireframe} className={`${btnBase} ${wireframeMode ? btnActive : btnDefault}`} title="Toggle wireframe">
          Wireframe
        </button>
        <button onClick={toggleSectionView} className={`${btnBase} ${sectionViewActive ? btnActive : btnDefault}`} title="Toggle section view">
          Section
        </button>
        {sectionViewActive && (
          <input
            type="range" min="-1" max="1" step="0.01"
            value={sectionPlaneOffset}
            onChange={(e) => setSectionPlaneOffset(parseFloat(e.target.value))}
            className="w-20 shrink-0"
            style={{ accentColor: '#c8b89a' }}
            title="Section plane position"
          />
        )}
        <button
          onClick={() => { if (measurementActive) clearMeasurement(); toggleMeasurement() }}
          className={`${btnBase} ${measurementActive ? btnActive : btnDefault}`}
          title="Measurement tool"
        >
          Measure
        </button>
      </div>

      <div className="flex-1" />

      <div className="flex items-center gap-2 shrink-0">
        <span className="text-[10px] uppercase tracking-widest" style={{ color: '#404040' }}>Export</span>
        {(['step', 'stl', 'obj'] as const).map((fmt) => (
          <button
            key={fmt}
            onClick={() => handleExport(fmt)}
            disabled={!hasModel || exportingFormat !== null}
            title={hasModel ? `Export as ${fmt.toUpperCase()}` : 'Generate a model first'}
            className={`${btnBase} ${!hasModel || exportingFormat !== null ? btnDisabled : btnDefault}`}
          >
            {exportingFormat === fmt ? (
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full border border-white/40 border-t-transparent animate-spin" />
                {fmt.toUpperCase()}
              </span>
            ) : fmt.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  )
}
