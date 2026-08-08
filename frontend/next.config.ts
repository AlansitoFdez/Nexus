import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits a self-contained .next/standalone server (only the files the
  // build actually needs to run, node_modules included) instead of
  // requiring the full project + all devDependencies at runtime — the
  // Docker image copies that folder instead of shipping the whole repo.
  output: "standalone",
};

export default nextConfig;
