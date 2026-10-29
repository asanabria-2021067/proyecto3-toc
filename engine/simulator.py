from model import BLANK, Configuration, Step, Tape, show


def simulate(tm, cadena, max_steps=1000):
    result = {"input": cadena, "accepted": False, "reason": "", "final_tape": "", "steps": []}

    bad = sorted({c for c in cadena if c not in tm.tape_alphabet})
    if bad:
        result["reason"] = f"error: simbolo(s) fuera del alfabeto de cinta: {', '.join(bad)}"
        return result

    tape = Tape.from_string(cadena)
    cfg = Configuration(tm.initial, BLANK, tape)
    steps = [Step(0, cfg).to_dict()]  # to_dict ya: la cinta se muta en sitio
    n = 0
    while True:
        if cfg.state in tm.finals:
            if tape.cells:
                accepted, reason = True, f"estado final '{cfg.state}' alcanzado"
            else:
                accepted, reason = False, "la cinta quedó en blanco"
            break
        if n >= max_steps:
            accepted, reason = False, f"límite de pasos ({max_steps})"
            break
        read = tape.read()
        key = (cfg.state, cfg.cache, read)
        if key not in tm.delta:
            accepted = False
            reason = f"sin transición para (estado={cfg.state}, caché={show(cfg.cache)}, leído={show(read)})"
            break
        q2, c2, w, mov = tm.delta[key]
        tape.write(w)
        tape.move(mov)
        cfg = Configuration(q2, c2, tape)
        n += 1
        steps.append(Step(n, cfg, {"from": list(key), "to": [q2, c2, w, mov]}).to_dict())

    result.update(accepted=accepted, reason=reason, final_tape=tape.content())
    result["steps"] = steps
    return result
