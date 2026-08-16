'use client'
import { useRef, useCallback, useState } from 'react'
import { useAppStore } from '@/store'

export default function FileUploadZone() {
  const { setBlueprint, uploadError, blueprintFile, startExtraction } = useAppStore()
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFile = useCallback(
    (file: File) => {
      setBlueprint(file)
    },
    [setBlueprint]
  )

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const onDragLeave = () => setIsDragging(false)

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const handleAnalyze = () => {
    if (blueprintFile) startExtraction(blueprintFile)
  }

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        className={`
          relative border rounded-lg p-4 text-center cursor-pointer transition-all duration-200
          ${isDragging
            ? 'border-forge-blue bg-forge-blue/10'
            : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]'
          }
        `}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
          className="hidden"
          onChange={onInputChange}
        />
        <div className="flex flex-col items-center gap-2 py-2">
          <svg className="w-7 h-7 text-forge-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          {blueprintFile ? (
            <div>
              <p className="text-forge-text text-sm font-medium truncate max-w-[180px]">{blueprintFile.name}</p>
              <p className="text-forge-muted text-xs">Click to replace</p>
            </div>
          ) : (
            <div>
              <p className="text-forge-text text-sm">Drop blueprint here</p>
              <p className="text-forge-muted text-xs mt-0.5">JPEG, PNG or PDF · max 20 MB</p>
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {uploadError && (
        <p className="text-forge-red text-xs px-1">{uploadError}</p>
      )}

      {/* Analyze button */}
      {blueprintFile && (
        <button
          onClick={handleAnalyze}
          className="w-full py-2 px-4 rounded-lg bg-forge-blue text-white text-sm font-medium
                     hover:bg-forge-blueLight transition-colors duration-150"
        >
          Analyze Blueprint
        </button>
      )}
    </div>
  )
}
