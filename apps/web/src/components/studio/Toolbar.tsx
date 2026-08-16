'use client'
import { useAppStore } from '@/store'
import { downloadBlob } from '@/lib/api'
import Link from 'next/link'

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
    const filenames = { step: 'lower_valve_body.step', stl: 'lower_valve_body.stl', obj: 'lower_valve_body.obj' }
    try {
      await downloadBlob(`/export/${fmt}`, filenames[fmt], sessionToken)
      addToast(`${fmt.toUpperCase()} exported successfully`, 'info')
    } catch (err: any) {
      addToast(err.message ?? `Export ${fmt} failed`, 'error')
    } finally {
      setExportingFormat(null)
    }
  }

  const btnBase = 'px-3 py-1.5 rounded text-xs font-medium transition-colors duration-150 whitespace-nowrap'
  const btnActive = 'bg-forge-blue/20 text-forge-blue border border-forge-blue/40'
  const btnDefault = 'bg-white/[0.04] text-forge-muted border border-white/[0.08] hover:bg-white/[0.07] hover:text-forge-text'
  const btnDisabled = 'opacity-40 cursor-not-allowed bg-white/[0.02] text-forge-muted border border-white/[0.06]'

  return (
    <div className="h-11 bg-[#0d0d14] border-b border-white/[0.08] flex items-center px-4 gap-2 overflow-x-auto shrink-0">
      <Link href="/" className="text-forge-text text-sm font-semibold tracking-tight mr-2 shrink-0 hover:text-forge-blue transition-colors">
        VexForm
      </Link>
      <div className="w-px h-5 bg-white/10 shrink-0" />

      <button
        onClick={toggleWireframe}
        className={`${btnBase} ${wireframeMode ? btnActive : btnDefault}`}
        title="Toggle wireframe"
      >
        Wireframe
      </button>

      <button
        onClick={toggleSectionView}
        className={`${btnBase} ${sectionViewActive ? btnActive : btnDefault}`}
        title="Toggle section view"
      >
        Section
      </button>

      {sectionViewActive && (
        <input
          type="range"
          min="-1"
          max="1"
          step="0.01"
          value={sectionPlaneOffset}
          onChange={(e) => setSectionPlaneOffset(parseFloat(e.target.value))}
          className="w-24 accent-forge-blue shrink-0"
          title="Section plane position"
        />
      )}

      <button
        onClick={() => {
          if (measurementActive) clearMeasurement()
          toggleMeasurement()
        }}
        className={`${btnBase} ${measurementActive ? btnActive : btnDefault}`}
        title="Measurement tool"
      >
        Measure
      </button>

      <div className="flex-1" />

      <span className="text-forge-muted text-[10px] uppercase tracking-wider shrink-0">Export</span>

      {(['step', 'stl', 'obj'] as const).map((fmt) => (
        <button
          key={fmt}
          onClick={() => handleExport(fmt)}
          disabled={!hasModel || exportingFormat !== null}
          title={hasModel ? `Export as ${fmt.toUpperCase()}` : 'Generate a model first'}
          className={`${btnBase} ${
            !hasModel || exportingFormat !== null
              ? btnDisabled
              : btnDefault
          }`}
        >
          {exportingFormat === fmt ? (
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 border border-forge-muted border-t-transparent rounded-full animate-spin" />
              {fmt.toUpperCase()}
            </span>
          ) : (
            fmt.toUpperCase()
          )}
        </button>
      ))}
    </div>
  )
}
