import { resolve } from 'path'
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  root: resolve('./templates/static/src'),
  base: '/static/',
  plugins: [svelte()],
  build: {
    manifest: true,
    outDir: resolve('./dist/vite'),
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      input: {
        main: resolve('./templates/static/src/main.js'),
	    // explore: resolve('./theme/static/src/explore/main.js'),

      }
    }
  }
})
