export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8001'

export async function apiGet(path: string, sessionToken?: string) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: sessionToken ? { 'X-Session-Token': sessionToken } : {},
  })
  return res
}

export async function downloadBlob(
  path: string,
  filename: string,
  sessionToken?: string
): Promise<void> {
  const res = await apiGet(path, sessionToken)
  if (!res.ok) {
    const data = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(data?.detail?.error ?? data?.error ?? `Export failed: HTTP ${res.status}`)
  }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
