/**
 * Cliente de la API del motor. En desarrollo Vite redirige /validate y /run a localhost:8000.
 * Los errores de YAML llegan como {ok:false, errors:[...]} (HTTP 400 en /run).
 */
export class ErrorApi extends Error {
  constructor(mensajes) {
    super(mensajes.join("\n"));
    this.mensajes = mensajes;
  }
}

async function post(ruta, cuerpo) {
  let res;
  try {
    res = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
  } catch {
    throw new ErrorApi(["No se pudo conectar con el backend. ¿Está corriendo `uvicorn api:app` en el puerto 8000?"]);
  }
  let datos = null;
  try {
    datos = await res.json();
  } catch {
    /* sin cuerpo JSON */
  }
  if (!res.ok) {
    if (Array.isArray(datos?.errors)) throw new ErrorApi(datos.errors.map(String));
    if (Array.isArray(datos?.detail)) throw new ErrorApi(datos.detail.map((d) => d.msg || JSON.stringify(d)));
    throw new ErrorApi([datos?.detail || `El backend respondió ${res.status}`]);
  }
  return datos;
}

/** -> {ok, machine, warnings, errors} (siempre 200). */
export const validar = (yaml) => post("/validate", { yaml });

/** -> {machine, warnings, results}. Lanza ErrorApi si el YAML es inválido. */
export const ejecutar = (yaml, maxSteps) => post("/run", { yaml, max_steps: maxSteps });
