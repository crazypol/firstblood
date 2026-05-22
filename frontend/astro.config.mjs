import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://ai-trend-daily.onrender.com',
  base: '/',
  outDir: 'dist',
  vite: {
    plugins: [tailwindcss()],
  },
});
