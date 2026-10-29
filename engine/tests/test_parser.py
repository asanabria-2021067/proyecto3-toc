from pathlib import Path

import pytest

from model import BLANK
from parser import ValidationError, parse_machine

MACHINES = Path(__file__).resolve().parents[2] / "machines"

BASE = """
q_states: {{q_list: [0, 1], initial: 0, final: {final}}}
alphabet: [a]
tape_alphabet: {tape}
delta:
{delta}
"""


def yml(delta, final="1", tape="[a, '-']"):
    return BASE.format(delta=delta, final=final, tape=tape)


OK = """  - params: {initial_state: 0, mem_cache_value: , tape_input: a}
    output: {final_state: 1, mem_cache_value: , tape_output: a, tape_displacement: R}"""


def errors_of(text):
    with pytest.raises(ValidationError) as e:
        parse_machine(text)
    return " | ".join(e.value.errors)


def test_ejemplo_catedratico():
    tm, warnings = parse_machine((MACHINES / "ejemplo_catedratico.yaml").read_text())
    assert tm.initial == "0" and tm.finals == {"5"}
    assert BLANK in tm.tape_alphabet
    assert any("alphabet unido" in w for w in warnings)  # a y b no estan en tape_alphabet
    assert "aab#aab" in tm.strings


def test_null_es_blank_y_normaliza_a_str():
    tm, _ = parse_machine(yml(OK))
    assert tm.delta[("0", BLANK, "a")] == ("1", BLANK, "a", "R")


def test_final_como_lista():
    tm, _ = parse_machine(yml(OK, final="['1', 0]"))
    assert tm.finals == {"0", "1"}


def test_union_de_alfabetos_y_blank():
    tm, w = parse_machine(yml(OK, tape="[]"))
    assert "a" in tm.tape_alphabet and BLANK in tm.tape_alphabet
    assert len(w) == 2


def test_dash_es_blank():
    tm, w = parse_machine(yml(OK))
    assert BLANK in tm.tape_alphabet and w == []


def test_estado_inicial_inexistente():
    assert "inicial" in errors_of(yml(OK).replace("initial: 0", "initial: 9"))


def test_estado_final_inexistente():
    assert "final '9'" in errors_of(yml(OK, final="9"))


def test_estado_de_delta_inexistente():
    assert "estado '7'" in errors_of(yml(OK.replace("final_state: 1", "final_state: 7")))


def test_desplazamiento_invalido():
    assert "desplazamiento" in errors_of(yml(OK.replace("R", "X")))


def test_simbolo_fuera_de_cinta():
    assert "fuera del alfabeto" in errors_of(yml(OK.replace("tape_output: a", "tape_output: z")))


def test_duplicada():
    assert "duplicada" in errors_of(yml(OK + "\n" + OK))


def test_campos_faltantes():
    assert "falta el campo 'delta'" in errors_of("q_states: {q_list: [0], initial: 0, final: 0}\nalphabet: [a]\ntape_alphabet: [a]")
    assert "faltan campos" in errors_of(yml("  - params: {initial_state: 0}\n    output: {final_state: 1}"))


def test_reporta_todos_los_errores():
    bad = OK.replace("final_state: 1", "final_state: 7").replace("R", "X")
    with pytest.raises(ValidationError) as e:
        parse_machine(yml(bad, final="9"))
    assert len(e.value.errors) >= 3
