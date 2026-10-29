# Proyecto 3 - Simulador de Maquinas de Turing (UVG, Teoria de la Computacion)

Monorepo: `engine/` (motor, CLI, API en Python), `frontend/` (React, Javier), `machines/` (YAML).

## Uso
Desde `engine/` (Python 3.10+):
```
pip install -r requirements.txt
```

**Tests**
```
python -m pytest
```

**CLI**
```
python main.py ../machines/reconocedora.yaml
python main.py ../machines/alteradora.yaml --cadena "babba"
python main.py ../machines/reconocedora.yaml --max-steps 500
```
Imprime el resumen de la MT y, por cada cadena, las IDs numeradas con la transicion aplicada y ACEPTADA / RECHAZADA con el motivo.
`--cadena` simula solo esa cadena. `--max-steps` debe estar entre 1 y 100000 (default 1000); fuera de rango la CLI sale con error.

**Backend (API)**
```
uvicorn api:app --reload
```
Queda en http://localhost:8000 (docs interactivas en `/docs`).

## Modelo
MT de una cinta con memoria en el estado: el estado real es el par `[q, cache]`. Una transicion
hace match con `(estado, cache, simbolo leido)` y produce `(nuevo estado, nuevo cache, simbolo escrito, movimiento L|R|S)`.
Valores vacios/null son blank literal (no comodin); el cache inicial es blank. En `tape_alphabet`, `"-"` es blank.
`alphabet` se une a `tape_alphabet` (advertencia). Se acepta al entrar a un estado final; se rechaza si no hay
transicion, si se pasa de `max_steps` (default 1000) o si la cinta termina toda en blanks.

## API (sin estado, CORS abierto para localhost)
- `POST /validate` `{yaml}` -> `{ok, machine, warnings, errors}` (siempre 200; `machine` es `null` si hay errores)
- `POST /run` `{yaml, max_steps?}` -> `{machine, warnings, results}`. `max_steps` va de 1 a 100000 (default 1000). YAML invalido o `max_steps` fuera de rango: HTTP 400 `{ok: false, errors}`

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

## Maquinas

### reconocedora.yaml - a^n b^n c^n (n >= 1)
El cache guarda el simbolo que se busca marcar (`b` o `c`).

| Estado | Que hace |
|---|---|
| 0 | Inicio de ronda: marca la `a` mas a la izquierda con X, pone cache=`b`, va a 1. Si ve `Y`, ya no hay `a`: pasa a 3. |
| 1 | Avanza a la derecha buscando el simbolo del cache. Con cache=`b`: salta `a`,`Y`; al hallar `b` la marca `Y` y cambia cache=`c`. Con cache=`c`: salta `b`,`Z`; al hallar `c` la marca `Z`, limpia cache y pasa a 2. |
| 2 | Regresa a la izquierda hasta la `X` mas a la derecha y vuelve a 0. |
| 3 | Verifica que solo queden `Y`/`Z` hasta el blank. |
| 4 | Final (acepta). |

### alteradora.yaml - w -> w#w sobre {a,b}
El cache lleva cada simbolo de w hasta el final de la copia. Marca originales copiados como `X` (a) / `Y` (b).

| Estado | Que hace |
|---|---|
| 0 | Recorre w a la derecha; al blank escribe `#` y pasa a 3. |
| 3 | Regresa a la izquierda hasta el blank inicial y pasa a 1. |
| 1 | Salta `X`/`Y`; en la primera `a`/`b` sin copiar la marca (`X`/`Y`), la guarda en el cache y pasa a 2. Si ve `#`, ya copio todo: pasa a 4. |
| 2 | Lleva el cache a la derecha hasta el primer blank, escribe ahi el simbolo del cache y vuelve a 3. |
| 4 | Restaura `X`->`a`, `Y`->`b` yendo a la izquierda; al blank inicial va a 5. |
| 5 | Final (acepta). |

`ejemplo_catedratico.yaml` es el ejemplo original del enunciado: esta incompleto a proposito (solo tiene transiciones desde el estado 0), asi que sus 3 cadenas terminan rechazadas por falta de transicion.
