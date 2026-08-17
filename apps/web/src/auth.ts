import NextAuth from 'next-auth'
import Google from 'next-auth/providers/google'
import { connectDB } from '@/lib/mongodb'
import { getUserModel } from '@/models/User'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],

  session: { strategy: 'jwt' },

  callbacks: {
    async signIn({ user, account }) {
      if (account?.provider !== 'google') return false

      try {
        await connectDB()
        const User = await getUserModel()
        const existing = await User.findOne({ email: user.email })

        if (!existing) {
          await User.create({
            name:     user.name,
            email:    user.email,
            image:    user.image,
            googleId: account.providerAccountId,
          })
        }

        return true
      } catch {
        return false
      }
    },

    async jwt({ token, account }) {
      if (account) token.provider = account.provider
      return token
    },

    async session({ session, token }) {
      if (session.user) (session.user as any).provider = token.provider
      return session
    },
  },

  pages: {
    signIn: '/auth',
    error:  '/auth',
  },
})
