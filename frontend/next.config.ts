import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8002/api/:path*',
      },
    ];
  },
  trailingSlash: false,
};

export default nextConfig;
