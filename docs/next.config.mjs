import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  output: 'export',
  reactStrictMode: true,
  // Every route becomes `path/index.html`, which GitHub Pages serves without
  // relying on its extensionless-URL fallback.
  trailingSlash: true,
};

export default withMDX(config);