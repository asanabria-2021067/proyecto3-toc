import { useEffect, useRef, useState } from "react";
import { ejecutar } from "./api.js";
import Reproductor from "./components/Reproductor.jsx";
import { blank } from "./components/Cinta.jsx";
import reconocedora from "../../machines/reconocedora.yaml?raw";
import alteradora from "../../machines/alteradora.yaml?raw";
import catedratico from "../../machines/ejemplo_catedratico.yaml?raw";

const EJEMPLOS = {
  reconocedora: { nombre: "Reconocedora aⁿbⁿcⁿ", yaml: reconocedora },
  alteradora: { nombre: "Alteradora w → w#w", yaml: alteradora },
  catedratico: { nombre: "Ejemplo del catedrático", yaml: catedratico },
};

/** Página completa: editor YAML, parámetros, lista de cadenas y reproductor. */
export default function App() {
  const [yaml, setYaml] = useState(EJEMPLOS.reconocedora.yaml);
  const [maxSteps, setMaxSteps] = useState(1000);
  const [cargando, setCargando] = useState(false);
  const [errores, setErrores] = useState([]);
  const [datos, setDatos] = useState(null); // {machine, warnings, results}
  const [sel, setSel] = useState(0);
  const archivo = useRef(null);

  async function correr(texto = yaml) {
    setCargando(true);
    setErrores([]);
    try {
      setDatos(await ejecutar(texto, Number(maxSteps)));
      setSel(0);
    } catch (e) {
      setErrores(e.mensajes ?? [e.message]);
      setDatos(null);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    correr();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function cargarEjemplo(id) {
    const y = EJEMPLOS[id].yaml;
    setYaml(y);
    correr(y);
  }

  async function subir(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    const texto = await f.text();
    setYaml(texto);
    correr(texto);
    e.target.value = "";
  }

  const maxOk = Number.isInteger(Number(maxSteps)) && maxSteps >= 1 && maxSteps <= 100000;
  const res = datos?.results[sel];

  return (
    <div className="app">
      <header className="cabecera">
        <div className="titulo">
          <h1>Simulador de Máquinas de Turing</h1>
          <p>Teoría de la Computación · Proyecto No. 3 · MT de una cinta con memoria en el estado</p>
        </div>

        <div className="formulario">
          <label>
            <span>Definición de la MT (YAML)</span>
            <textarea value={yaml} onChange={(e) => setYaml(e.target.value)} spellCheck={false} autoComplete="off" />
          </label>
          <div className="lateral">
            <label>
              <span>max_steps (1 – 100000)</span>
              <input
                type="number"
                min={1}
                max={100000}
                value={maxSteps}
                onChange={(e) => setMaxSteps(e.target.value)}
              />
            </label>
            <button type="button" className="primario" onClick={() => correr()} disabled={cargando || !yaml.trim() || !maxOk}>
              {cargando ? "Simulando…" : "Simular"}
            </button>
            <select
              value=""
              onChange={(e) => e.target.value && cargarEjemplo(e.target.value)}
              aria-label="Cargar ejemplo"
            >
              <option value="">Cargar ejemplo…</option>
              {Object.entries(EJEMPLOS).map(([id, ej]) => (
                <option key={id} value={id}>{ej.nombre}</option>
              ))}
            </select>
            <button type="button" onClick={() => archivo.current?.click()}>Abrir archivo .yaml</button>
            <input ref={archivo} type="file" accept=".yaml,.yml" hidden onChange={subir} />
          </div>
        </div>

        {errores.length > 0 && (
          <ul className="error lista">
            {errores.map((m, k) => <li key={k}>{m}</li>)}
          </ul>
        )}
        {datos?.warnings?.length > 0 && (
          <ul className="advertencias">
            {datos.warnings.map((a) => <li key={a}>{a}</li>)}
          </ul>
        )}
      </header>

      {datos && (
        <main className="principal">
          <aside className="cadenas">
            <h2>Cadenas</h2>
            <ul>
              {datos.results.map((r, k) => (
                <li key={k}>
                  <button type="button" className={k === sel ? "activa" : ""} onClick={() => setSel(k)}>
                    <code>{r.input === "" ? "ε" : r.input}</code>
                    <span className={"veredicto " + (r.accepted ? "si" : "no")}>{r.accepted ? "SÍ" : "NO"}</span>
                  </button>
                </li>
              ))}
            </ul>
          </aside>

          <section className="detalle">
            {res ? (
              <>
                <h2>
                  <code>{res.input === "" ? "ε" : res.input}</code>{" "}
                  <span className={"veredicto " + (res.accepted ? "si" : "no")}>{res.accepted ? "ACEPTADA" : "RECHAZADA"}</span>
                </h2>
                <p className="motivo-resumen">{res.reason}</p>
                <Reproductor machine={datos.machine} res={res} />
              </>
            ) : (
              <p className="inicio-vacio">Esta MT no define cadenas de simulación.</p>
            )}
          </section>
        </main>
      )}

      {datos && (
        <section className="tabla-delta">
          <h2>Función de transición δ</h2>
          <p className="ayuda">
            Estados: {datos.machine.states.join(", ")} · inicial <code>{datos.machine.initial}</code> · finales{" "}
            <code>{datos.machine.finals.join(", ")}</code> · blank = <code>B</code>
          </p>
          <table>
            <thead>
              <tr><th>estado</th><th>cache</th><th>lee</th><th></th><th>estado'</th><th>cache'</th><th>escribe</th><th>mov</th></tr>
            </thead>
            <tbody>
              {datos.machine.delta.map((t, k) => (
                <tr key={k}>
                  <td>{t.from[0]}</td><td>{blank(t.from[1])}</td><td>{blank(t.from[2])}</td><td>→</td>
                  <td>{t.to[0]}</td><td>{blank(t.to[1])}</td><td>{blank(t.to[2])}</td><td>{t.to[3]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
