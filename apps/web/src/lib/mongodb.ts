import mongoose from 'mongoose'

declare global {
  var _mongooseCache: { conn: typeof mongoose | null; promise: Promise<typeof mongoose> | null }
}

let cached = global._mongooseCache

if (!cached) {
  cached = global._mongooseCache = { conn: null, promise: null }
}

export async function connectDB(): Promise<typeof mongoose> {
  const uri = process.env.MONGODB_URI

  if (!uri) {
    throw new Error('MONGODB_URI environment variable is not set')
  }

  if (cached.conn) return cached.conn

  if (!cached.promise) {
    cached.promise = mongoose.connect(uri, { bufferCommands: false })
  }

  cached.conn = await cached.promise
  return cached.conn
}
