import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Pin Turbopack root so Next does not pick a parent lockfile (e.g. ~/package-lock.json)
  // and traverse protected dirs like ~/Downloads on macOS.
  turbopack: {
    root: __dirname,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  env: {
    // v0 exports often target Vite; we map VITE_API_URL to a Next.js-safe public env var.
    NEXT_PUBLIC_API_URL:
      process.env.VITE_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000",
  },
}

export default nextConfig
