const nextConfig = {
  async rewrites() {
    const base = process.env.INTERNAL_API_BASE_URL || "http://127.0.0.1:8000";
    return [{ source: "/api/v1/:path*", destination: `${base}/api/v1/:path*` }];
  },
};

export default nextConfig;
