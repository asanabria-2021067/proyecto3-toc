import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

cytoscape.use(dagre);

// Mismo lenguaje visual que el proyecto 2: tinta oscura, ámbar para lo activo.
const ESTILO = [
  {
    selector: "node",
    style: {
      shape: "ellipse", width: 52, height: 52, "background-color": "#fdfcf8",
      "border-width": 2, "border-color": "#1e1e1e", label: "data(label)",
      "text-valign": "center", "text-halign": "center",
      "font-family": "Architects Daughter, cursive", "font-size": 18, color: "#1e1e1e",
    },
  },
  { selector: "node.final", style: { "border-style": "double", "border-width": 6 } },
  { selector: "node.inicio", style: { width: 1, height: 1, "background-opacity": 0, "border-width": 0, label: "" } },
  { selector: "node.activo", style: { "background-color": "#ffec99", "border-color": "#f08c00", "border-width": 3 } },
  { selector: "node.final.activo", style: { "border-width": 6 } },
  {
    selector: "edge",
    style: {
      "curve-style": "bezier", "control-point-step-size": 110, width: 1.8, "line-color": "#1e1e1e",
      "target-arrow-color": "#1e1e1e", "target-arrow-shape": "triangle", label: "data(label)",
      "font-family": "IBM Plex Mono, monospace", "font-size": 12, color: "#1971c2", "line-height": 1.25,
      "text-wrap": "wrap", "text-background-opacity": 1,
      "text-background-padding": 4, "text-background-color": "#fdfcf8", "text-border-width": 1, "text-border-color": "#dedbd2", "text-border-opacity": 1, "min-zoomed-font-size": 6, "text-background-shape": "roundrectangle",
    },
  },
  { selector: "edge.bucle", style: { "loop-direction": "-90deg", "loop-sweep": "55deg", "control-point-step-size": 80 } },
  { selector: "edge.activa", style: { "line-color": "#f08c00", "target-arrow-color": "#f08c00", width: 3, "z-index": 10 } },
];

const nodo = (q) => `n_${q}`;
const sim = (s) => (s == null ? "B" : s);

const cacheFmt = (c, c2) => (c === c2 ? `[${sim(c)}]` : `[${sim(c)}→${sim(c2)}]`);

/** Una arista por par (origen, destino). Cada línea: "[cache] leído / escrito,mov".
 *  Si no se cambia el símbolo se escribe "=", y los símbolos con el mismo efecto se agrupan. */
function aElementos(m) {
  const els = [{ data: { id: "inicio" }, classes: "inicio" }];
  const finales = new Set(m.finals);
  for (const q of m.states) els.push({ data: { id: nodo(q), label: q }, classes: finales.has(q) ? "final" : "" });
  els.push({ data: { id: "e_inicio", source: "inicio", target: nodo(m.initial) } });
  const grupos = new Map();
  for (const t of m.delta) {
    const [q, c, a] = t.from;
    const [p, c2, w, mov] = t.to;
    const k = `${q}|${p}`;
    if (!grupos.has(k)) grupos.set(k, { q, p, lineas: new Map() });
    const lineas = grupos.get(k).lineas;
    const igual = (w ?? null) === (a ?? null);
    const clave = igual ? `=|${cacheFmt(c, c2)}|${mov}` : `${a}|${cacheFmt(c, c2)}|${w}|${mov}`;
    if (!lineas.has(clave)) lineas.set(clave, { cache: cacheFmt(c, c2), leidos: [], escr: igual ? "=" : sim(w), mov });
    lineas.get(clave).leidos.push(sim(a));
  }
  for (const { q, p, lineas } of grupos.values()) {
    const texto = [...lineas.values()].map((l) => `${l.cache} ${l.leidos.join(",")} / ${l.escr},${l.mov}`).join("\n");
    els.push({
      data: { id: `e_${q}_${p}`, source: nodo(q), target: nodo(p), label: texto, q, p },
      classes: q === p ? "bucle" : "",
    });
  }
  return els;
}

/**
 * @param {object} machine          machine del contrato.
 * @param {string} estado           estado actual (nodo ámbar).
 * @param {object|null} transicion  transición aplicada (arista ámbar).
 */
export default function Diagrama({ machine, estado, transicion }) {
  const cont = useRef(null);
  const cy = useRef(null);

  useEffect(() => {
    if (!cont.current) return;
    cy.current = cytoscape({
      container: cont.current,
      elements: aElementos(machine),
      style: ESTILO,
      layout: { name: "dagre", rankDir: "LR", nodeSep: 150, rankSep: 280, edgeSep: 40, padding: 24, ranker: "network-simplex" },
      wheelSensitivity: 0.2,
      boxSelectionEnabled: false,
      autoungrabify: true,
    });
    // Cada bucle se dibuja hacia el lado contrario a las demás aristas del nodo,
    // con su etiqueta fuera del bucle.
    cy.current.edges(".bucle").forEach((e) => {
      const n = e.source();
      const angulos = [];
      n.connectedEdges().not(e).forEach((o) => {
        const otro = o.source().id() === n.id() ? o.target() : o.source();
        angulos.push((Math.atan2(otro.position("y") - n.position("y"), otro.position("x") - n.position("x")) * 180) / Math.PI);
      });
      // Candidatos cada 30°: el que quede más lejos de cualquier otra arista del nodo.
      const dif = (x, y) => Math.abs(((x - y + 540) % 360) - 180);
      let ang = -90;
      let mejor = -1;
      for (let c = -180; c < 180; c += 30) {
        const sep = Math.min(180, ...angulos.map((x) => dif(c, x)));
        if (sep > mejor + 1e-6) {
          mejor = sep;
          ang = c;
        }
      }
      const dy = Math.sin((ang * Math.PI) / 180);
      e.style({ "loop-direction": `${ang + 90}deg`, "text-margin-y": dy * 26 });
    });
    cy.current.fit(undefined, 50);
    return () => {
      cy.current?.destroy();
      cy.current = null;
    };
  }, [machine]);

  useEffect(() => {
    const g = cy.current;
    if (!g) return;
    g.nodes().forEach((n) => n.toggleClass("activo", n.data("label") === estado));
    const q = transicion?.from?.[0];
    const p = transicion?.to?.[0];
    g.edges().forEach((e) => e.toggleClass("activa", transicion != null && e.data("q") === q && e.data("p") === p));
  }, [estado, transicion, machine]);

  return <div ref={cont} className="diagrama" />;
}
