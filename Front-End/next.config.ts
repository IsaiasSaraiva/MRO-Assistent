import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,  // ignora erros de TypeScript no build
  },
  eslint: {
    ignoreDuringBuilds: true,  // ignora erros de ESLint no build
  },
  images: {
    remotePatterns: [
      {
        hostname: "avatar.vercel.sh",
      },
    ],
  },
};

export default nextConfig;