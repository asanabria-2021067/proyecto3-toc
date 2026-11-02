# Frontend (Vite + React)

Simulador visual: editor YAML, lista de cadenas con ACEPTADA/RECHAZADA, reproductor paso a paso
(cinta con cabezal, estado/cache, transición aplicada, ID), diagrama de estados y tabla δ.
Atajos del reproductor: flechas ← → , Home, End.

```
cd frontend
npm install
npm run dev        # http://localhost:5173
```
Con Docker (desde la raíz): `docker compose up -d --build` → frontend http://localhost:5175, API http://localhost:8000. Sin Docker: backend con `cd engine && uvicorn api:app --reload`.
Vite redirige `/validate` y `/run` a `BACKEND_URL` (default `http://localhost:8000`).
Los ejemplos se importan directo de `../machines/*.yaml`.
