import yaml

from model import BLANK, MOVES, TuringMachine


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(errors))


def norm(v):
    """null/vacio -> BLANK; todo lo demas a str (YAML puede leer 0 como int)."""
    return BLANK if v is None or v == "" else str(v)


def parse_machine(yaml_text):
    """Devuelve (TuringMachine, warnings) o lanza ValidationError con todos los errores."""
    errors, warnings = [], []
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValidationError([f"YAML invalido: {e}"])
    if not isinstance(data, dict):
        raise ValidationError(["el YAML debe ser un mapa con q_states, alphabet, tape_alphabet, delta"])

    for key in ("q_states", "alphabet", "tape_alphabet", "delta"):
        if data.get(key) is None:
            errors.append(f"falta el campo '{key}'")

    qs = data.get("q_states")
    if qs is not None and not isinstance(qs, dict):
        errors.append("'q_states' debe ser un mapa con q_list, initial, final")
        qs = None
    qs = qs or {}
    for key in ("q_list", "initial", "final"):
        if qs.get(key) is None:
            errors.append(f"falta q_states.{key}")

    states = [str(q) for q in qs.get("q_list") or []]
    initial = norm(qs.get("initial"))
    final = qs.get("final")
    finals = {str(f) for f in (final if isinstance(final, list) else [final])} if final is not None else set()

    if qs.get("initial") is not None and initial not in states:
        errors.append(f"el estado inicial '{initial}' no existe en q_list")
    for f in sorted(finals - set(states)):
        errors.append(f"el estado final '{f}' no existe en q_list")

    alphabet = [str(a) for a in data.get("alphabet") or []]
    # "-" en tape_alphabet significa blank
    tape_alpha = [BLANK if x is None or str(x) in ("", "-") else str(x) for x in data.get("tape_alphabet") or []]
    missing = [a for a in alphabet if a not in tape_alpha]
    if missing:
        warnings.append(f"alphabet unido a tape_alphabet (faltaban: {', '.join(missing)})")
        tape_alpha += missing
    if BLANK not in tape_alpha:
        warnings.append("blank agregado a tape_alphabet")
        tape_alpha.append(BLANK)

    delta = {}
    entries = data.get("delta") or []
    if not isinstance(entries, list):
        errors.append("'delta' debe ser una lista")
        entries = []
    for n, t in enumerate(entries, 1):
        where = f"delta[{n}]"
        params = t.get("params") if isinstance(t, dict) else None
        out = t.get("output") if isinstance(t, dict) else None
        if not isinstance(params, dict) or not isinstance(out, dict):
            errors.append(f"{where}: faltan 'params' y/o 'output'")
            continue
        faltan = [f"params.{k}" for k in ("initial_state", "mem_cache_value", "tape_input") if k not in params]
        faltan += [f"output.{k}" for k in ("final_state", "mem_cache_value", "tape_output", "tape_displacement") if k not in out]
        if faltan:
            errors.append(f"{where}: faltan campos {', '.join(faltan)}")
            continue
        q, c, a = norm(params["initial_state"]), norm(params["mem_cache_value"]), norm(params["tape_input"])
        q2, c2, w, mov = norm(out["final_state"]), norm(out["mem_cache_value"]), norm(out["tape_output"]), norm(out["tape_displacement"])
        for s in (q, q2):
            if s not in states:
                errors.append(f"{where}: el estado '{s}' no existe en q_list")
        if mov not in MOVES:
            errors.append(f"{where}: desplazamiento '{mov}' invalido (use L, R o S)")
        for s in (a, w):
            if s not in tape_alpha:
                errors.append(f"{where}: simbolo '{s}' fuera del alfabeto de cinta")
        key = (q, c, a)
        if key in delta:
            errors.append(f"{where}: transicion duplicada para (estado={q}, cache={c}, leido={a})")
        delta[key] = (q2, c2, w, mov)

    strings = [str(s) for s in data.get("simulation_strings") or []]

    if errors:
        raise ValidationError(errors)
    return TuringMachine(states, initial, finals, alphabet, tape_alpha, delta, strings), warnings
