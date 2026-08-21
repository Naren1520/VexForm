'use client'
import type { ShapeSchema } from '@vexform/types'
import { useAppStore } from '@/store'

interface Props {
  onClose: () => void
}

export default function ParamRangesModal({ onClose }: Props) {
  const shapeSchema = useAppStore((s) => s.shapeSchema)

  if (!shapeSchema) return null

  const { fields, display_name } = shapeSchema

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}
      onClick={onClose}
    >
      <div
        className="relative w-[520px] max-h-[80vh] flex flex-col rounded-lg overflow-hidden"
        style={{ background: '#0d0d0d', border: '1px solid #222' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 shrink-0"
          style={{ borderBottom: '1px solid #1a1a1a' }}
        >
          <div>
            <p className="text-xs font-medium uppercase tracking-widest" style={{ color: '#888' }}>
              Parameter Ranges
            </p>
            <p className="text-[10px] mt-0.5" style={{ color: '#444' }}>
              Valid ranges for {display_name}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-base leading-none transition-colors"
            style={{ color: '#444' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#888' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#444' }}
          >
            ×
          </button>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-[11px]" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#111', borderBottom: '1px solid #1a1a1a' }}>
                <th className="text-left px-4 py-2 font-medium uppercase tracking-widest text-[10px]" style={{ color: '#555' }}>
                  Parameter
                </th>
                <th className="text-center px-3 py-2 font-medium uppercase tracking-widest text-[10px] w-24" style={{ color: '#555' }}>
                  Min
                </th>
                <th className="text-center px-3 py-2 font-medium uppercase tracking-widest text-[10px] w-24" style={{ color: '#555' }}>
                  Max
                </th>
              </tr>
            </thead>
            <tbody>
              {fields.map((f, i) => (
                <tr
                  key={f.key}
                  style={{
                    borderBottom: '1px solid #111',
                    background: i % 2 === 0 ? 'transparent' : '#0a0a0a',
                  }}
                  title={f.description}
                >
                  <td className="px-4 py-1.5" style={{ color: '#777' }}>
                    {f.label}
                    {f.description && (
                      <span className="ml-1.5 text-[9px]" style={{ color: '#333' }}>
                        ({f.description})
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-1.5 text-center font-mono" style={{ color: '#4a7c4a' }}>
                    {f.min_val !== null ? `${f.min_val}${f.unit ? ' ' + f.unit : ''}` : '—'}
                  </td>
                  <td className="px-3 py-1.5 text-center font-mono" style={{ color: '#7a4a4a' }}>
                    {f.max_val !== null ? `${f.max_val}${f.unit ? ' ' + f.unit : ''}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div
          className="px-4 py-2 shrink-0"
          style={{ borderTop: '1px solid #1a1a1a', background: '#080808' }}
        >
          <p className="text-[10px]" style={{ color: '#333' }}>
            All dimensions in mm · Hover a row for constraint details · Ranges enforce geometric validity
          </p>
        </div>
      </div>
    </div>
  )
}
