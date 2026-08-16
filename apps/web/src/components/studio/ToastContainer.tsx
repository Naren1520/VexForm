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
          className={`
            toast-enter pointer-events-auto
            flex items-start gap-3 px-4 py-3 rounded-lg max-w-sm
            glass border
            ${toast.level === 'error'
              ? 'border-forge-red/30 bg-forge-red/5'
              : 'border-forge-blue/20 bg-forge-blue/5'
            }
          `}
        >
          <span className={`text-base leading-none mt-0.5 ${toast.level === 'error' ? 'text-forge-red' : 'text-forge-blue'}`}>
            {toast.level === 'error' ? '✗' : 'ℹ'}
          </span>
          <p className="text-forge-text text-sm flex-1 leading-snug">{toast.message}</p>
          <button
            onClick={() => dismissToast(toast.id)}
            className="text-forge-muted hover:text-forge-text text-base leading-none shrink-0"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
