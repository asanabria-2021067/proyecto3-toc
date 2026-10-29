from model import BLANK
from parser import parse_machine
from simulator import simulate


def machine(delta, final="f", strings=""):
    """delta: lista de (q, c, leido, q2, c2, escrito, mov); '' = blank."""
    rows = "".join(
        f"  - params: {{initial_state: {q}, mem_cache_value: '{c}', tape_input: '{a}'}}\n"
        f"    output: {{final_state: {q2}, mem_cache_value: '{c2}', tape_output: '{w}', tape_displacement: {m}}}\n"
        for q, c, a, q2, c2, w, m in delta
    )
    text = f"q_states: {{q_list: [s, t, f], initial: s, final: {final}}}\nalphabet: [a, b]\ntape_alphabet: [a, b, '-']\ndelta:\n{rows}"
    return parse_machine(text)[0]


def test_mueve_r_l_s_y_cache():
    tm = machine([
        ("s", "", "a", "t", "a", "b", "R"),   # escribe b, guarda a en cache
        ("t", "a", "a", "t", "a", "a", "L"),  # lee a (2da celda), vuelve
        ("t", "a", "b", "f", "", "b", "S"),
    ])
    r = simulate(tm, "aa")
    assert [s["state"] for s in r["steps"]] == ["s", "t", "t", "f"]
    assert r["steps"][1]["tape"] == ["b", "a"] and r["steps"][1]["head"] == 1
    assert r["steps"][2]["head"] == 0 and r["steps"][3]["head"] == 0  # L luego S
    assert r["accepted"] and r["final_tape"] == "ba"


def test_crece_a_la_izquierda():
    tm = machine([("s", "", "a", "f", "", "b", "L")])
    r = simulate(tm, "a")
    last = r["steps"][-1]
    assert last["tape"] == [None, "b"] and last["head"] == 0 and last["offset"] == -1
    assert last["id"] == " [f,B] Bb"
    assert r["final_tape"] == "b"


def test_id_clasica():
    tm = machine([("s", "", "a", "t", "a", "a", "R"), ("t", "a", "b", "t", "a", "b", "R")])
    r = simulate(tm, "ab", max_steps=1)
    assert r["steps"][0]["id"] == " [s,B] ab"
    assert r["steps"][1]["id"] == "a [t,a] b"


def test_transicion_en_pasos():
    tm = machine([("s", "", "a", "f", "", "a", "S")])
    r = simulate(tm, "a")
    assert r["steps"][0]["transition"] is None
    assert r["steps"][1]["transition"] == {"from": ["s", None, "a"], "to": ["f", None, "a", "S"]}


def test_rechazo_sin_transicion():
    tm = machine([("s", "", "a", "f", "", "a", "S")])
    r = simulate(tm, "b")
    assert not r["accepted"] and "sin transición" in r["reason"]


def test_limite_de_pasos():
    tm = machine([("s", "", "a", "s", "", "a", "S")])
    r = simulate(tm, "a", max_steps=5)
    assert not r["accepted"] and "límite de pasos" in r["reason"]
    assert len(r["steps"]) == 6


def test_cinta_toda_blank_se_rechaza():
    tm = machine([("s", "", "a", "f", "", "", "S")])
    r = simulate(tm, "a")
    assert not r["accepted"] and "blanco" in r["reason"] and r["final_tape"] == ""


def test_simbolo_invalido_no_tumba_las_demas():
    tm = machine([("s", "", "a", "f", "", "a", "S")])
    bad = simulate(tm, "az")
    assert not bad["accepted"] and bad["reason"].startswith("error") and bad["steps"] == []
    assert simulate(tm, "a")["accepted"]


def test_pasos_no_comparten_cinta():
    tm = machine([("s", "", "a", "t", "", "b", "R"), ("t", "", "a", "f", "", "b", "S")])
    r = simulate(tm, "aa")
    assert r["steps"][0]["tape"] == ["a", "a"] and r["steps"][2]["tape"] == ["b", "b"]


