import { useEffect, useState } from "react";
import Cinta, { blank } from "./Cinta.jsx";
import Diagrama from "./Diagrama.jsx";

const fmtTrans = (t) => {
  if (!t) return "Configuración inicial";
  const [q, c, a] = t.from;
  const [p, c2, w, mov] = t.to;
  return `δ([${q}, ${blank(c)}], ${blank(a)}) = ([${p}, ${blank(c2)}], ${blank(w)}, ${mov})`;
};

/**
 * Reproduce paso a paso la simulación de una cadena.
 * @param {object} machine  machine del contrato.
 * @param {object} res      results[i] del contrato.
 */
export default function Reproductor({ machine, res }) {
  const [i, setI] = useState(0);
  const [auto, setAuto] = useState(false);
  const [velocidad, setVelocidad] = useState(500);
  const pasos = res.steps;
  const ultimo = pasos.length - 1;

  useEffect(() => {
    setI(0);
    setAuto(false);
  }, [res]);

  useEffect(() => {
    if (!auto) return;
    if (i >= ultimo) {
      setAuto(false);
      return;
    }
    const t = setTimeout(() => setI((x) => Math.min(x + 1, ultimo)), velocidad);
    return () => clearTimeout(t);
  }, [auto, i, ultimo, velocidad]);

  if (pasos.length === 0) {
    return <p className="error">{res.reason}</p>;
  }

  const paso = pasos[i];
  const alFinal = i === ultimo;

  function teclas(e) {
    if (e.key === "ArrowRight") setI((x) => Math.min(x + 1, ultimo));
    else if (e.key === "ArrowLeft") setI((x) => Math.max(x - 1, 0));
    else if (e.key === "Home") setI(0);
    else if (e.key === "End") setI(ultimo);
    else return;
    e.preventDefault();
  }

  return (
    <div className="reproductor" tabIndex={0} onKeyDown={teclas} aria-label="Reproductor de pasos (flechas ← →)">
      <div className="estado-fila">
        <span className="chip">estado <b>{paso.state}</b></span>
        <span className="chip">cache <b>{blank(paso.cache)}</b></span>
        <span className="chip">paso <b>{paso.i}</b> / {pasos[ultimo].i}</span>
        {alFinal && (
          <span className={"veredicto " + (res.accepted ? "si" : "no")}>
            {res.accepted ? "ACEPTADA" : "RECHAZADA"}
          </span>
        )}
      </div>

      <Cinta paso={paso} pasos={pasos} />

      <p className="transicion">{fmtTrans(paso.transition)}</p>
      <p className="id-actual">
        ID: <code>{paso.id}</code>
      </p>

      <div className="controles">
        <button type="button" onClick={() => setI(0)} disabled={i === 0} aria-label="Inicio">⏮</button>
        <button type="button" onClick={() => setI(i - 1)} disabled={i === 0} aria-label="Anterior">◀</button>
        <button
          type="button"
          className="primario"
          onClick={() => {
            if (alFinal) setI(0);
            setAuto(!auto);
          }}
        >
          {auto ? "⏸ Pausa" : alFinal ? "↺ Repetir" : "▶ Reproducir"}
        </button>
        <button type="button" onClick={() => setI(i + 1)} disabled={alFinal} aria-label="Siguiente">▶</button>
        <button type="button" onClick={() => setI(ultimo)} disabled={alFinal} aria-label="Final">⏭</button>
        <input
          type="range"
          min={0}
          max={ultimo}
          value={i}
          onChange={(e) => {
            setAuto(false);
            setI(Number(e.target.value));
          }}
          aria-label="Paso"
        />
        <label className="velocidad">
          <span>velocidad</span>
          <input
            type="range"
            min={50}
            max={1500}
            step={50}
            value={1550 - velocidad}
            onChange={(e) => setVelocidad(1550 - Number(e.target.value))}
          />
        </label>
      </div>

      {alFinal && (
        <p className={"motivo " + (res.accepted ? "si" : "no")}>
          {res.reason} · cinta final: <code>{res.final_tape || "(vacía)"}</code>
        </p>
      )}

      <div className="dos-col">
        <section>
          <h3>Diagrama de estados</h3>
          <p className="ayuda">Cada línea: <code>[cache] leído / escrito,mov</code> · <code>[a→b]</code> el cache cambia · <code>=</code> no cambia el símbolo · B = blank</p>
          <Diagrama machine={machine} estado={paso.state} transicion={paso.transition} />
        </section>
        <section>
          <h3>Descripciones instantáneas</h3>
          <ol className="ids" start={0}>
            {pasos.map((p, k) => (
              <li key={k} className={k === i ? "activa" : ""}>
                <button type="button" onClick={() => { setAuto(false); setI(k); }}>
                  <span className="n">{p.i}</span>
                  <code>{p.id}</code>
                </button>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}
