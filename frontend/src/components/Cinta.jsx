import { useEffect, useMemo, useRef } from "react";

export const blank = (s) => (s == null || s === "" ? "B" : s);

/**
 * Cinta con ventana fija: abarca todas las celdas que la cinta llega a mostrar
 * durante la simulación, así no "salta" entre pasos. El cabezal se resalta en ámbar.
 * @param {object} paso   steps[i] del contrato.
 * @param {Array}  pasos  todos los steps (para calcular la ventana).
 */
export default function Cinta({ paso, pasos }) {
  const ventana = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;
    for (const p of pasos) {
      min = Math.min(min, p.offset);
      max = Math.max(max, p.offset + p.tape.length - 1);
    }
    return { min: min - 1, max: max + 1 };
  }, [pasos]);

  const celdas = [];
  for (let pos = ventana.min; pos <= ventana.max; pos++) {
    const idx = pos - paso.offset;
    const sim = idx >= 0 && idx < paso.tape.length ? paso.tape[idx] : null;
    celdas.push({ pos, sim, cabezal: idx === paso.head });
  }

  const activa = useRef(null);
  useEffect(() => {
    activa.current?.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
  }, [paso]);

  return (
    <div className="cinta" role="img" aria-label={`Cinta: ${paso.id}`}>
      {celdas.map((c) => (
        <div key={c.pos} className={"celda" + (c.cabezal ? " cabezal" : "")} ref={c.cabezal ? activa : null}>
          <span className={"simbolo" + (c.sim == null ? " vacio" : "")}>{blank(c.sim)}</span>
          <span className="pos">{c.pos}</span>
          {c.cabezal && <span className="flecha">▲</span>}
        </div>
      ))}
    </div>
  );
}
