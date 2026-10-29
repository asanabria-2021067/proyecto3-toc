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


