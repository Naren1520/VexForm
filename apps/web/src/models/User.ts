import { Schema, model } from 'mongoose'
import { connectDB } from '@/lib/mongodb'

const UserSchema = new Schema(
  {
    name:     { type: String, required: true },
    email:    { type: String, required: true, unique: true, lowercase: true },
    image:    { type: String },
    googleId: { type: String, unique: true, sparse: true },
  },
  { timestamps: true }
)

export async function getUserModel() {
  const mongoose = await connectDB()
  return mongoose.models.User || mongoose.model('User', UserSchema)
}
