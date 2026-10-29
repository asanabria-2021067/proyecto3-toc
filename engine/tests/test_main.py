import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
MACHINES = ENGINE.parent / "machines"


def cli(*args):
    return subprocess.run(
        [sys.executable, "main.py", *args], cwd=ENGINE, capture_output=True, text=True, encoding="utf-8"
    )


def test_reconocedora_muestra_aceptadas_y_rechazadas():
    p = cli(str(MACHINES / "reconocedora.yaml"))
    assert p.returncode == 0
    assert p.stdout.count("ACEPTADA") == 2 and p.stdout.count("RECHAZADA") == 2
    assert "d(0,B,a) = (1,b,X,R)" in p.stdout  # transicion aplicada junto a la ID


def test_alteradora_acepta_y_cadena_suelta():
    p = cli(str(MACHINES / "alteradora.yaml"))
    assert p.returncode == 0 and p.stdout.count("ACEPTADA") == 4 and "RECHAZADA" not in p.stdout
    p = cli(str(MACHINES / "alteradora.yaml"), "--cadena", "abz")
    assert "RECHAZADA" in p.stdout and "fuera del alfabeto" in p.stdout


def test_max_steps():
    assert "límite de pasos" in cli(str(MACHINES / "reconocedora.yaml"), "--max-steps", "3").stdout
    p = cli(str(MACHINES / "reconocedora.yaml"), "--max-steps", "100001")
    assert p.returncode == 2 and "max_steps debe estar entre 1 y 100000" in p.stderr


def test_yaml_invalido(tmp_path):
    f = tmp_path / "mala.yaml"
    f.write_text("q_states: 1", encoding="utf-8")
    p = cli(str(f))
    assert p.returncode == 1 and "MAQUINA INVALIDA" in p.stdout
