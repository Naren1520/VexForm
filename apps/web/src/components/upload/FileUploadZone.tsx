'use client'
import { useRef, useCallback, useState } from 'react'
import { useAppStore } from '@/store'

export default function FileUploadZone() {
  const { setBlueprint, uploadError, blueprintFile, startExtraction, extractionStatus } = useAppStore()
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const isAnalyzing = extractionStatus === 'loading'

  const handleFile = useCallback((file: File) => { setBlueprint(file) }, [setBlueprint])

  const onDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true) }
  const onDragLeave = () => setIsDragging(false)
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }
  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }
  const handleAnalyze = () => { if (blueprintFile && !isAnalyzing) startExtraction(blueprintFile) }

  return (
    <div className="space-y-2">
      <div
        className="relative p-3 text-center cursor-pointer transition-all duration-200"
        style={{
          border: `1px solid ${isDragging ? '#c8b89a66' : '#222'}`,
          background: isDragging ? '#c8b89a0a' : '#0a0a0a',
        }}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        onMouseEnter={(e) => { if (!isDragging) (e.currentTarget as HTMLElement).style.borderColor = '#333' }}
        onMouseLeave={(e) => { if (!isDragging) (e.currentTarget as HTMLElement).style.borderColor = '#222' }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
          className="hidden"
          onChange={onInputChange}
        />
        <div className="flex flex-col items-center gap-2 py-1">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#444" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          {blueprintFile ? (
            <div>
              <p className="text-xs font-medium truncate max-w-[170px]" style={{ color: '#d0d0d0' }}>
                {blueprintFile.name}
              </p>
              <p className="text-[10px] mt-0.5" style={{ color: '#444' }}>Click to replace</p>
            </div>
          ) : (
            <div>
              <p className="text-xs" style={{ color: '#888' }}>Drop blueprint here</p>
              <p className="text-[10px] mt-0.5" style={{ color: '#444' }}>JPEG · PNG · PDF · max 20 MB</p>
            </div>
          )}
        </div>
      </div>

      {uploadError && (
        <p className="text-[11px] px-1" style={{ color: '#ff6666' }}>{uploadError}</p>
      )}

      {blueprintFile && (
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="w-full py-2 px-3 text-xs font-medium uppercase tracking-widest
                     transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed
                     flex items-center justify-center gap-2"
          style={{
            background: isAnalyzing ? '#1a1a1a' : '#f5f0eb',
            color: isAnalyzing ? '#666' : '#0c0c0c',
            border: '1px solid transparent',
          }}
          onMouseEnter={(e) => { if (!isAnalyzing) (e.currentTarget as HTMLElement).style.background = '#c8b89a' }}
          onMouseLeave={(e) => { if (!isAnalyzing) (e.currentTarget as HTMLElement).style.background = '#f5f0eb' }}
        >
          {isAnalyzing ? (
            <>
              <span className="w-3 h-3 rounded-full border border-white/30 border-t-transparent animate-spin shrink-0" />
              Analyzing…
            </>
          ) : 'Analyze Blueprint'}
        </button>
      )}
    </div>
  )
}
