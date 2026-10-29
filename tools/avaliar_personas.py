"""Diagnóstico rápido: roda todas as personas e imprime ranking, alertas e plano.

Uso:
    python tools/avaliar_personas.py            # todas as personas
    python tools/avaliar_personas.py gustavo    # uma persona específica
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from consultor_pro import MotorInferencia, analisar, carregar  # noqa: E402
from tests.personas import PERSONAS  # noqa: E402


def imprimir_resultado(motor: MotorInferencia, persona, verbose: bool = True) -> None:
    resultado = motor.avaliar(persona.respostas)
    plano = analisar(motor.base, resultado)
    destaque = resultado.destaque
    status = "OK " if destaque.trilha in persona.esperado else "!! "

    print(f"\n{status}{persona.nome}  ({persona.chave})")
    print(f"   esperado: {', '.join(persona.esperado)}")
    print(
        f"   top3: "
        + " | ".join(
            f"{motor.base.trilhas[item.trilha].nome} {item.percentual:.1f}%"
            for item in resultado.top3
        )
    )
    print(
        f"   regras ativadas: {len(resultado.regras_disparadas)} | "
        f"cobertura júnior: {plano.cobertura:.0f}% | "
        f"lacunas: {len(plano.lacunas)} | prazo: {plano.semanas_estimadas} semanas"
    )
    if verbose:
        for alerta in resultado.alertas:
            print(f"   alerta: {alerta}")
        print(f"   próximos passos: {'; '.join(plano.proximos_passos(3))}")


def main() -> int:
    base = carregar()
    motor = MotorInferencia(base)
    filtro = sys.argv[1] if len(sys.argv) > 1 else None
    personas = [p for p in PERSONAS if filtro is None or p.chave == filtro]
    if not personas:
        print(f"persona '{filtro}' não encontrada")
        return 1

    falhas = 0
    for persona in personas:
        resultado = motor.avaliar(persona.respostas)
        if resultado.destaque.trilha not in persona.esperado:
            falhas += 1
        imprimir_resultado(motor, persona)

    print(f"\n{len(personas) - falhas}/{len(personas)} personas com 1º lugar esperado.")
    return 0 if falhas == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
