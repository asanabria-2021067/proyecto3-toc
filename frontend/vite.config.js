import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";

// /validate y /run se redirigen al backend (uvicorn api:app, puerto 8000).
// fs.allow ".." permite importar ../machines/*.yaml como ejemplos (?raw).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    fs: { allow: [".."] },
    proxy: { "/validate": BACKEND, "/run": BACKEND },
  },
});
