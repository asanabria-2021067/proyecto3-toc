# Proyecto 3 - Simulador de Maquinas de Turing (UVG, Teoria de la Computacion)

Monorepo: `engine/` (motor, CLI, API en Python), `frontend/` (React, Javier), `machines/` (YAML).

## Uso
```
cd engine
pip install -r requirements.txt
python -m pytest
python main.py ../machines/reconocedora.yaml [--max-steps N] [--cadena "aabbcc"]
uvicorn api:app --reload        # http://localhost:8000/docs
```

## Modelo
MT de una cinta con memoria en el estado: el estado real es el par `[q, cache]`. Una transicion
hace match con `(estado, cache, simbolo leido)` y produce `(nuevo estado, nuevo cache, simbolo escrito, movimiento L|R|S)`.
Valores vacios/null son blank literal (no comodin); el cache inicial es blank. En `tape_alphabet`, `"-"` es blank.
`alphabet` se une a `tape_alphabet` (advertencia). Se acepta al entrar a un estado final; se rechaza si no hay
transicion, si se pasa de `max_steps` (default 1000) o si la cinta termina toda en blanks.

## API (sin estado, CORS abierto para localhost)
- `POST /validate` `{yaml}` -> `{ok, machine, warnings, errors}` (siempre 200; `machine` es `null` si hay errores)
- `POST /run` `{yaml, max_steps?}` -> `{machine, warnings, results}`; si el YAML es invalido: HTTP 400 `{ok: false, errors}`

`machine`: `{states, initial, finals, alphabet, tape_alphabet, delta, strings}` donde `delta` es una lista de
`{"from": [q, cache, leido], "to": [q, cache, escrito, mov]}` y blank es `null`.

## Contrato JSON de cada resultado (`results[i]`)
```
{ "input": str, "accepted": bool, "reason": str, "final_tape": str,
  "steps": [ { "i": int, "state": str, "cache": str|null,
               "tape": [str|null, ...], "head": int, "offset": int, "id": str,
               "transition": null | { "from": [q, c, leido], "to": [q, c, escrito, mov] } } ] }
```
- `null` = blank. `steps[0]` es la configuracion inicial (`transition: null`).
- `tape` es la porcion visible de la cinta (no-blanks mas la celda del cabezal); `head` es el **indice dentro de `tape`**;
  `offset` es la posicion absoluta de `tape[0]` (la cadena de entrada empieza en 0, puede ser negativo).
- `transition` en el paso `i` es la transicion aplicada para llegar a ese paso.
- `id`: notacion clasica `u [q,c] v` (blank = `B`, sin blanks sobrantes en los extremos, la celda del cabezal es la primera de `v`).
- `final_tape`: cinta final sin blanks en los extremos.
- Cadena con simbolos fuera del alfabeto de cinta: `accepted: false`, `reason` empieza con `error:` y `steps: []`; las demas cadenas se simulan normal.
- Ejemplo completo: `engine/sample_run.json`.

