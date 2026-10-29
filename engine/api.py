from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from parser import ValidationError, parse_machine
from simulator import simulate

app = FastAPI(title="Simulador de Maquinas de Turing")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


class ValidateReq(BaseModel):
    yaml: str


class RunReq(BaseModel):
    yaml: str
    max_steps: int = 1000


def invalid(e):
    return JSONResponse({"ok": False, "errors": e.errors}, status_code=400)


@app.post("/validate")
def validate(req: ValidateReq):
    try:
        tm, warnings = parse_machine(req.yaml)
    except ValidationError as e:
        return {"ok": False, "machine": None, "warnings": [], "errors": e.errors}
    return {"ok": True, "machine": tm.to_dict(), "warnings": warnings, "errors": []}


@app.post("/run")
def run(req: RunReq):
    try:
        tm, warnings = parse_machine(req.yaml)
    except ValidationError as e:
        return invalid(e)
    return {
        "machine": tm.to_dict(),
        "warnings": warnings,
        "results": [simulate(tm, s, req.max_steps) for s in tm.strings],
    }
