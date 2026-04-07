/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const apiDestination = process.env.INTERNAL_API_URL || "http://localhost:8000";

    return [
      {
        source: "/api/:path*",
        destination: `${apiDestination}/api/:path*`
      }
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com"
      },
      {
        protocol: "https",
        hostname: "covers.openlibrary.org"
      }
    ]
  }
};

export default nextConfig;
