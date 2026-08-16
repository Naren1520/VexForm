import type { LowerValveBodyParams, ParamFieldState } from '@vexform/types'
import { PARAM_LABELS, PARAM_UNITS } from '@/lib/paramValidation'
import ParamStatusIcon from './ParamStatusIcon'
import { useAppStore } from '@/store'

interface Props {
  paramKey: keyof LowerValveBodyParams
  fieldState: ParamFieldState
}

const STATUS_BORDER: Record<string, string> = {
  ai_match:     'border-[#4488FF]/60',
  ai_deviation: 'border-[#FF4444]/80',
  ai_null:      'border-[#888888]/50',
  user_edited:  'border-white/20',
}

export default function ParamField({ paramKey, fieldState }: Props) {
  const updateParamField = useAppStore((s) => s.updateParamField)
  const label = PARAM_LABELS[paramKey]
  const unit  = PARAM_UNITS[paramKey]
  const isString = paramKey === 'material'
  const isInt = ['top_flange_bolt_hole_count', 'bottom_flange_bolt_hole_count'].includes(paramKey)
  const borderClass = STATUS_BORDER[fieldState.status] ?? 'border-white/20'

  return (
    <div className="flex items-center gap-2 py-1">
      <label className="flex-1 text-forge-muted text-[11px] leading-tight min-w-0 truncate">
        {label}
      </label>
      <div className="flex items-center gap-1.5 shrink-0">
        <div className="relative">
          <input
            type={isString ? 'text' : 'number'}
            step={isInt ? '1' : '0.1'}
            value={fieldState.value as string | number}
            onChange={(e) => {
              const raw = e.target.value
              const val = isString ? raw : isInt ? parseInt(raw) : parseFloat(raw)
              updateParamField(paramKey, val)
            }}
            className={`
              w-[72px] px-2 py-1 rounded text-xs text-forge-text bg-white/[0.05]
              border ${borderClass} outline-none
              focus:border-forge-blue/80 focus:bg-white/[0.08] transition-colors
              font-mono
            `}
          />
        </div>
        {unit && (
          <span className="text-forge-muted text-[10px] w-5 shrink-0">{unit}</span>
        )}
        <span className="w-3 shrink-0 text-center">
          <ParamStatusIcon status={fieldState.status} />
        </span>
      </div>
    </div>
  )
}
