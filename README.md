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
