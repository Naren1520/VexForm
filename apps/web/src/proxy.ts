import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export default auth((req) => {
  const isAuthenticated = !!req.auth
  const isStudio = req.nextUrl.pathname.startsWith('/studio')

  if (isStudio && !isAuthenticated) {
    const loginUrl = new URL('/auth', req.url)
    loginUrl.searchParams.set('next', req.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
})

export const config = {
  matcher: ['/studio/:path*'],
}
