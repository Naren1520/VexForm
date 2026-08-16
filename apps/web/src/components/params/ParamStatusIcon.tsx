import type { ParamFieldStatus } from '@vexform/types'

interface Props {
  status: ParamFieldStatus
}

export default function ParamStatusIcon({ status }: Props) {
  if (status === 'ai_match') {
    return (
      <span title="AI extracted -within reference range" className="text-[10px] opacity-70">✦</span>
    )
  }
  if (status === 'ai_deviation') {
    return (
      <span title="AI extracted -deviates >20% from reference" className="text-[10px]">⚠</span>
    )
  }
  if (status === 'ai_null') {
    return (
      <span title="Not extracted -using reference value" className="text-[10px] opacity-50">◎</span>
    )
  }
  if (status === 'user_edited') {
    return (
      <span title="User edited" className="text-[10px] opacity-60">✏</span>
    )
  }
  return null
}
