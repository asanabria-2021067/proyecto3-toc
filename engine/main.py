import argparse
import sys

from model import show
from parser import ValidationError, parse_machine
from simulator import check_max_steps, simulate


def summary(tm, warnings):
    print("=" * 60)
    print("MAQUINA DE TURING")
    print(f"  Estados:       {', '.join(tm.states)}")
    print(f"  Inicial:       {tm.initial}")
    print(f"  Finales:       {', '.join(sorted(tm.finals))}")
    print(f"  Alfabeto:      {', '.join(tm.alphabet)}")
    print(f"  Alfabeto cinta: {', '.join(show(s) for s in tm.tape_alphabet)}")
    print(f"  Transiciones:  {len(tm.delta)}")
    for w in warnings:
        print(f"  ADVERTENCIA: {w}")
    print("=" * 60)


def fmt(t):
    (q, c, a), (q2, c2, w, m) = t["from"], t["to"]
    return f"d({q},{show(c)},{show(a)}) = ({q2},{show(c2)},{show(w)},{m})"


def max_steps_arg(text):
    try:
        return check_max_steps(int(text))
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Simulador de Maquinas de Turing")
    ap.add_argument("archivo")
    ap.add_argument("--max-steps", type=max_steps_arg, default=1000)
    ap.add_argument("--cadena", help="simular solo esta cadena")
    args = ap.parse_args()

    try:
        with open(args.archivo, encoding="utf-8") as f:
            tm, warnings = parse_machine(f.read())
    except ValidationError as e:
        print("MAQUINA INVALIDA:")
        for err in e.errors:
            print(f"  - {err}")
        sys.exit(1)

    summary(tm, warnings)
    for cadena in [args.cadena] if args.cadena is not None else tm.strings:
        r = simulate(tm, cadena, args.max_steps)
        print(f"\nCadena: '{cadena}'")
        for s in r["steps"]:
            tr = f"   {fmt(s['transition'])}" if s["transition"] else ""
            print(f"  {s['i']:>3}. {s['id']}{tr}")
        print(f"  -> {'ACEPTADA' if r['accepted'] else 'RECHAZADA'}: {r['reason']}")
        if r["steps"]:
            print(f"     cinta final: '{r['final_tape']}'")


if __name__ == "__main__":
    main()
