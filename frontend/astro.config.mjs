import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://liuyang.github.io',
  base: '/firstblood',
  outDir: 'dist',
  vite: {
    plugins: [tailwindcss()],
  },
});
