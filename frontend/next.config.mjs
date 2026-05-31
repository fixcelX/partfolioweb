import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: { ignoreDuringBuilds: true },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "picsum.photos" },
      { protocol: "http", hostname: "localhost" },
      { protocol: "http", hostname: "127.0.0.1" },
      // Prod backend (Render) media rasmlari uchun
      { protocol: "https", hostname: "*.onrender.com" },
      { protocol: "https", hostname: "*.railway.app" },
    ],
  },
};

export default withNextIntl(nextConfig);
