'use client'
import { useAppStore } from '@/store'

export default function ToastContainer() {
  const { toasts, dismissToast } = useAppStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="pointer-events-auto flex items-start gap-3 px-4 py-3 max-w-sm"
          style={{
            background: '#111',
            border: `1px solid ${toast.level === 'error' ? '#ff444433' : '#c8b89a33'}`,
            animation: 'fadeUp 0.3s ease forwards',
          }}
        >
          <span
            className="text-xs leading-none mt-0.5 shrink-0 font-mono"
            style={{ color: toast.level === 'error' ? '#ff6666' : '#c8b89a' }}
          >
            {toast.level === 'error' ? '✗' : '✓'}
          </span>
          <p className="text-sm flex-1 leading-snug font-light" style={{ color: '#d0d0d0' }}>
            {toast.message}
          </p>
          <button
            onClick={() => dismissToast(toast.id)}
            className="text-base leading-none shrink-0 transition-colors"
            style={{ color: '#444' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = '#aaa' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = '#444' }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
