import type { ParamFieldState } from '@vexform/types'
import ParamStatusIcon from './ParamStatusIcon'
import { useAppStore } from '@/store'

interface Props {
  paramKey: string
  fieldLabel: string
  fieldUnit: string
  fieldType: 'float' | 'int' | 'string'
  fieldState: ParamFieldState
}

const STATUS_BORDER: Record<string, string> = {
  ai_match:     '#4488FF44',
  ai_deviation: '#FF444466',
  ai_null:      '#33333399',
  user_edited:  '#ffffff22',
}

export default function ParamField({ paramKey, fieldLabel, fieldUnit, fieldType, fieldState }: Props) {
  const updateParamField = useAppStore((s) => s.updateParamField)
  const isString = fieldType === 'string'
  const borderColor = STATUS_BORDER[fieldState.status] ?? '#ffffff22'

  return (
    <div className="flex items-center gap-2 py-1">
      <label className="flex-1 text-[11px] leading-tight min-w-0 truncate" style={{ color: '#555' }}>
        {fieldLabel}
      </label>
      <div className="flex items-center gap-1.5 shrink-0">
        <input
          type={isString ? 'text' : 'number'}
          step={fieldType === 'int' ? '1' : '0.1'}
          value={fieldState.value as string | number}
          onChange={(e) => {
            // Store the raw string value — buildParamsFromFormState will coerce on generate
            updateParamField(paramKey, e.target.value)
          }}
          className="w-[68px] px-2 py-1 text-xs font-mono outline-none transition-colors duration-150"
          style={{
            background: '#0a0a0a',
            border: `1px solid ${borderColor}`,
            color: '#d0d0d0',
          }}
          onFocus={(e) => { (e.currentTarget as HTMLElement).style.borderColor = '#c8b89a88' }}
          onBlur={(e) => { (e.currentTarget as HTMLElement).style.borderColor = borderColor }}
        />
        {fieldUnit && (
          <span className="text-[10px] w-5 shrink-0" style={{ color: '#444' }}>{fieldUnit}</span>
        )}
        <span className="w-3 shrink-0 text-center">
          <ParamStatusIcon status={fieldState.status} />
        </span>
      </div>
    </div>
  )
}
