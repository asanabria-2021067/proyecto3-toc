# Proyecto 3 - Simulador de Máquinas de Turing

Proyecto de **Teoría de la Computación** (Universidad del Valle de Guatemala).
Simulador de Máquinas de Turing de una cinta con memoria en el estado (cache): se define la máquina en YAML,
se simulan varias cadenas y se visualiza cada paso (cinta, cabezal, diagrama de estados e IDs) en una interfaz web o por CLI.

## Colaboradores
- Javier Alvarado - 24546 
- Angel Sanabria - 24725

## Contenido
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo correr el programa](#cómo-correr-el-programa)
- [Modelo](#modelo) · [API](#api-sin-estado-cors-abierto-para-localhost) · [Contrato JSON](#contrato-json-de-cada-resultado-resultsi)
- [Máquinas](#máquinas)
- [Guión de presentación](GUION.md)

## Estructura del proyecto
Monorepo con tres partes: el motor en Python, la interfaz web y las máquinas de ejemplo.
```
proyecto3-toc/
├── docker-compose.yml        # levanta backend (8000) y frontend (5175)
├── engine/                   # motor, CLI y API (Python)
│   ├── model.py              # modelo de la MT (estados, delta, to_dict)
│   ├── parser.py             # lee y valida el YAML (errores y advertencias)
│   ├── simulator.py          # simula cada cadena y genera los pasos / IDs
│   ├── main.py               # CLI
│   ├── api.py                # API FastAPI: POST /validate y POST /run
│   ├── sample_run.json       # ejemplo completo del JSON de resultados
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/                # pytest: parser, simulador, CLI y API
├── frontend/                 # interfaz web (Vite + React)
│   ├── index.html
│   ├── vite.config.js        # proxy /validate y /run hacia el backend
│   ├── Dockerfile
│   └── src/
│       ├── main.jsx          # punto de entrada
│       ├── App.jsx           # editor YAML, lista de cadenas, tabla delta
│       ├── api.js            # cliente de la API
│       ├── styles.css
│       └── components/
│           ├── Reproductor.jsx    # control paso a paso, IDs y transición
│           ├── Cinta.jsx          # cinta con el cabezal
│           ├── Diagrama.jsx       # diagrama de estados (Cytoscape)
│           └── ErrorBoundary.jsx
└── machines/                 # MTs en YAML (también son los ejemplos de la web)
    ├── reconocedora.yaml
    ├── alteradora.yaml
    └── ejemplo_catedratico.yaml
```


## Cómo correr el programa

### Opción A: Docker (recomendada)
Requisito: Docker Desktop abierto. Desde la raíz del proyecto:
```
docker compose up -d --build
```
- Interfaz web: http://localhost:5175
- API: http://localhost:8000 (docs interactivas en `/docs`)

Ver logs: `docker compose logs -f`. Apagar: `docker compose down`.
El código está montado como volumen, así que los cambios se recargan solos.
Si el puerto 5175 u 8000 está ocupado, cambia el lado izquierdo de `ports` en `docker-compose.yml`.

### Opción B: sin Docker
Requisitos: Python 3.10+ y Node 18+. Se necesitan **dos terminales**.

Terminal 1 - backend:
```
cd engine
pip install -r requirements.txt
uvicorn api:app --reload
```
Queda en http://localhost:8000.

Terminal 2 - frontend:
```
cd frontend
npm install
npm run dev
```
Abrir http://localhost:5173. Vite redirige `/validate` y `/run` al backend (por defecto `http://localhost:8000`; se cambia con la variable `BACKEND_URL`). Los ejemplos del menú se importan directo de `machines/*.yaml`.

### Usar la interfaz
1. Elige un ejemplo en **Cargar ejemplo...** (o **Abrir archivo .yaml**, o edita el YAML en el cuadro de texto).
2. Ajusta `max_steps` (1 a 100000, default 1000) y presiona **Simular**.
3. A la izquierda aparecen las cadenas de `simulation_strings` con SI/NO; selecciona una.
4. El reproductor muestra la cinta con el cabezal, estado, cache, la transición aplicada y la ID de cada paso. Controles: Reproducir/Pausa, anterior/siguiente, barra de pasos, velocidad y flechas del teclado (izquierda/derecha, Home, End).
5. El diagrama de estados resalta el estado y la transición actuales. Cada línea de una arista es `[cache] leido / escrito,mov` (`=`: no cambia el símbolo; `[a→b]`: el cache cambia; `B`: blank).
6. Debajo del diagrama están las descripciones instantáneas (clic para saltar a un paso) y al final la tabla de la función de transición.

Para probar otra cadena, edita `simulation_strings` en el YAML y vuelve a simular. Los errores de YAML se muestran en un recuadro rojo.

### CLI (sin interfaz)
Desde `engine/`:
```
python main.py ../machines/reconocedora.yaml
python main.py ../machines/alteradora.yaml --cadena "babba"
python main.py ../machines/reconocedora.yaml --max-steps 500
```
Imprime el resumen de la MT y, por cada cadena, las IDs numeradas con la transición aplicada y ACEPTADA / RECHAZADA con el motivo.
`--cadena` simula solo esa cadena. `--max-steps` debe estar entre 1 y 100000 (default 1000); fuera de rango la CLI sale con error.

### Tests
Desde `engine/` (con las dependencias instaladas):
```
python -m pytest
```

### Problemas comunes
- *"No se pudo conectar con el backend"* en la web: el backend no está corriendo (Opción B: terminal 1; Opción A: `docker compose ps`).
- Puerto ocupado: cambia el puerto publicado (Docker) o usa `npm run dev -- --port 5180`.

## Modelo
MT de una cinta con memoria en el estado: el estado real es el par `[q, cache]`. Una transición
hace match con `(estado, cache, símbolo leido)` y produce `(nuevo estado, nuevo cache, símbolo escrito, movimiento L|R|S)`.
Valores vacios/null son blank literal (no comodin); el cache inicial es blank. En `tape_alphabet`, `"-"` es blank.
`alphabet` se une a `tape_alphabet` (advertencia). Se acepta al entrar a un estado final; se rechaza si no hay
transición, si se pasa de `max_steps` (default 1000) o si la cinta termina toda en blanks.

## API (sin estado, CORS abierto para localhost)
- `POST /validate` `{yaml}` -> `{ok, machine, warnings, errors}` (siempre 200; `machine` es `null` si hay errores)
- `POST /run` `{yaml, max_steps?}` -> `{machine, warnings, results}`. `max_steps` va de 1 a 100000 (default 1000). YAML inválido o `max_steps` fuera de rango: HTTP 400 `{ok: false, errors}`

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
- `tape` es la porción visible de la cinta (no-blanks más la celda del cabezal); `head` es el **índice dentro de `tape`**;
  `offset` es la posición absoluta de `tape[0]` (la cadena de entrada empieza en 0, puede ser negativo).
- `transition` en el paso `i` es la transición aplicada para llegar a ese paso.
- `id`: notación clásica `u [q,c] v` (blank = `B`, sin blanks sobrantes en los extremos, la celda del cabezal es la primera de `v`).
- `final_tape`: cinta final sin blanks en los extremos.
- Cadena con símbolos fuera del alfabeto de cinta: `accepted: false`, `reason` empieza con `error:` y `steps: []`; las demás cadenas se simulan normal.
- Ejemplo completo: `engine/sample_run.json`.

## Máquinas

### reconocedora.yaml - a^n b^n c^n (n >= 1)
El cache guarda el símbolo que se busca marcar (`b` o `c`).

| Estado | Qué hace |
|---|---|
| 0 | Inicio de ronda: marca la `a` más a la izquierda con X, pone cache=`b`, va a 1. Si ve `Y`, ya no hay `a`: pasa a 3. |
| 1 | Avanza a la derecha buscando el símbolo del cache. Con cache=`b`: salta `a`,`Y`; al hallar `b` la marca `Y` y cambia cache=`c`. Con cache=`c`: salta `b`,`Z`; al hallar `c` la marca `Z`, limpia cache y pasa a 2. |
| 2 | Regresa a la izquierda hasta la `X` más a la derecha y vuelve a 0. |
| 3 | Verifica que solo queden `Y`/`Z` hasta el blank. |
| 4 | Final (acepta). |

### alteradora.yaml - w -> w#w sobre {a,b}
El cache lleva cada símbolo de w hasta el final de la copia. Marca originales copiados como `X` (a) / `Y` (b).

| Estado | Qué hace |
|---|---|
| 0 | Recorre w a la derecha; al blank escribe `#` y pasa a 3. |
| 3 | Regresa a la izquierda hasta el blank inicial y pasa a 1. |
| 1 | Salta `X`/`Y`; en la primera `a`/`b` sin copiar la marca (`X`/`Y`), la guarda en el cache y pasa a 2. Si ve `#`, ya copio todo: pasa a 4. |
| 2 | Lleva el cache a la derecha hasta el primer blank, escribe ahi el símbolo del cache y vuelve a 3. |
| 4 | Restaura `X`->`a`, `Y`->`b` yendo a la izquierda; al blank inicial va a 5. |
| 5 | Final (acepta). |

`ejemplo_catedratico.yaml` es el ejemplo original del enunciado: está incompleto a propósito (solo tiene transiciones desde el estado 0), así que sus 3 cadenas terminan rechazadas por falta de transición.
