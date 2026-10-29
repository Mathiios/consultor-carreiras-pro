"""Motor de inferência com pontuação ponderada e tratamento de incerteza.

Modelo de cálculo (documentado no README):

1. **Aderência base (matriz)**::

       base(t) = 100 * Σ_d [ peso(d,t) * n_d ] / Σ_d peso(d,t)
       n_d     = (resposta_d - 1) / (escala_max - 1)      # normaliza para 0..1

2. **Ajuste das regras ponderadas** (fator de certeza)::

       ajuste(t) = clamp( Σ_regras (delta * certeza), -limite, +limite )

3. **Compatibilidade final**::

       compat(t) = clamp(0, 100, base(t) + ajuste(t))

O limite do ajuste (padrão ±20 p.p., definido no JSON) impede que as regras
sozinhas invertam um perfil muito desalinhado — a matriz de afinidade continua
sendo o sinal dominante.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base_conhecimento import (
    OPERADORES,
    BaseConhecimento,
    Regra,
    carregar,
)


# ----------------------------------------------------------------------
# Estruturas de saída
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RegraDisparada:
    """Regra ativada e o efeito efetivo (delta × certeza) por trilha."""

    regra: Regra
    efeitos_aplicados: dict[str, float]

    @property
    def impacto(self) -> float:
        return sum(abs(v) for v in self.efeitos_aplicados.values())

    def efeito_em(self, trilha: str) -> float:
        return self.efeitos_aplicados.get(trilha, 0.0)


@dataclass
class Compatibilidade:
    """Resultado de compatibilidade de uma trilha."""

    trilha: str
    base: float
    ajuste: float
    percentual: float
    contribuicoes: dict[str, float]
    regras: list[RegraDisparada] = field(default_factory=list)

    @property
    def ajuste_aplicado(self) -> bool:
        return abs(self.ajuste) > 0.01


@dataclass
class Resultado:
    """Diagnóstico completo do perfil."""

    respostas: dict[str, Any]
    compatibilidades: list[Compatibilidade]
    regras_disparadas: list[RegraDisparada]
    alertas: list[str] = field(default_factory=list)
    base_origem: BaseConhecimento | None = field(default=None, repr=False)

    # -- atalhos -------------------------------------------------------
    @property
    def ranking(self) -> list[Compatibilidade]:
        return self.compatibilidades

    @property
    def destaque(self) -> Compatibilidade:
        return self.compatibilidades[0]

    @property
    def top3(self) -> list[Compatibilidade]:
        return self.compatibilidades[:3]

    @property
    def vice(self) -> Compatibilidade:
        return self.compatibilidades[1]

    @property
    def margem(self) -> float:
        return self.destaque.percentual - self.vice.percentual

    def por_trilha(self, codigo: str) -> Compatibilidade:
        for item in self.compatibilidades:
            if item.trilha == codigo:
                return item
        raise KeyError(codigo)

    def nome(self, codigo: str) -> str:
        return self.base_origem.trilhas[codigo].nome if self.base_origem else codigo

    def icone(self, codigo: str) -> str:
        return self.base_origem.trilhas[codigo].icone if self.base_origem else "•"

    # -- visualizações --------------------------------------------------
    def afinidades_usuario(self) -> dict[str, float]:
        """Respostas Likert do usuário (1..5) por dimensão."""
        if not self.base_origem:
            return {}
        return {d.id: float(self.respostas.get(d.id, 3)) for d in self.base_origem.dimensoes}

    def perfil_ideal(self, codigo: str) -> dict[str, float]:
        """Perfil ideal da trilha na mesma escala 1..5 (derivado dos pesos)."""
        if not self.base_origem:
            return {}
        base = self.base_origem
        pesos = {d.id: base.matriz[d.id][codigo] for d in base.dimensoes}
        maior = max(pesos.values()) or 1.0
        return {dim: 1 + 4 * (peso / maior) for dim, peso in pesos.items()}

    def resumo(self) -> str:
        primeiro = self.destaque
        return (
            f"{self.icone(primeiro.trilha)} {self.nome(primeiro.trilha)} — "
            f"{primeiro.percentual:.1f}% de compatibilidade"
        )


# ----------------------------------------------------------------------
# Motor
# ----------------------------------------------------------------------
class MotorInferencia:
    """Avalia um perfil e devolve o ranking de compatibilidade."""

    def __init__(self, base: BaseConhecimento | None = None) -> None:
        self.base = base or carregar()

    # -- utilidades -----------------------------------------------------
    def _normalizar_respostas(self, respostas: dict[str, Any]) -> dict[str, Any]:
        # campos extras (nome, horas de estudo, tecnologias) são preservados:
        # o módulo de recomendação precisa deles para montar o plano de ação.
        normalizadas: dict[str, Any] = dict(respostas)
        padrao = (self.base.escala_min + self.base.escala_max) / 2

        for dimensao in self.base.dimensoes:
            bruto = respostas.get(dimensao.id, padrao)
            try:
                valor = float(bruto)
            except (TypeError, ValueError):
                valor = float(padrao)
            valor = max(self.base.escala_min, min(self.base.escala_max, valor))
            normalizadas[dimensao.id] = int(round(valor))

        for categoria in self.base.categoricas:
            valor = respostas.get(categoria.id)
            validos = [o.valor for o in categoria.opcoes]
            normalizadas[categoria.id] = valor if valor in validos else None

        return normalizadas

    def _condicao_satisfeita(self, condicao, respostas: dict[str, Any]) -> bool:
        valor = respostas.get(condicao.fonte)
        if valor is None:
            return False
        comparador = OPERADORES[condicao.op]
        try:
            if isinstance(valor, (int, float)) and isinstance(condicao.valor, (int, float)):
                return comparador(valor, condicao.valor)
            if condicao.op not in {"==", "!="}:
                return False
            return comparador(valor, condicao.valor)
        except TypeError:
            return False

    def _regra_disparada(self, regra: Regra, respostas: dict[str, Any]) -> bool:
        return all(self._condicao_satisfeita(c, respostas) for c in regra.condicoes)

    # -- avaliação ------------------------------------------------------
    def avaliar(self, respostas: dict[str, Any]) -> Resultado:
        respostas = self._normalizar_respostas(respostas)
        escala = self.base.escala_max - self.base.escala_min or 1

        # 1) aderência base (matriz de afinidade)
        compatibilidades: dict[str, Compatibilidade] = {}
        for codigo in self.base.ids_trilhas:
            contribuicoes: dict[str, float] = {}
            soma_pesos = 0.0
            for dimensao in self.base.dimensoes:
                peso = self.base.matriz[dimensao.id][codigo]
                soma_pesos += peso
                normalizado = (respostas[dimensao.id] - self.base.escala_min) / escala
                contribuicoes[dimensao.id] = 100 * peso * normalizado
            base_pct = sum(contribuicoes.values()) / soma_pesos if soma_pesos else 0.0
            compatibilidades[codigo] = Compatibilidade(
                trilha=codigo,
                base=round(base_pct, 2),
                ajuste=0.0,
                percentual=round(base_pct, 2),
                contribuicoes={
                    dim: round(valor / soma_pesos if soma_pesos else 0.0, 2)
                    for dim, valor in contribuicoes.items()
                },
            )

        # 2) regras ponderadas (com fator de certeza)
        disparadas: list[RegraDisparada] = []
        ajustes = {codigo: 0.0 for codigo in self.base.ids_trilhas}
        for regra in self.base.regras:
            if not self._regra_disparada(regra, respostas):
                continue
            aplicados = {
                efeito.trilha: efeito.delta * regra.certeza for efeito in regra.efeitos
            }
            disparadas.append(RegraDisparada(regra=regra, efeitos_aplicados=aplicados))
            for trilha, delta in aplicados.items():
                ajustes[trilha] += delta

        limite = self.base.ajuste_maximo_regras

        # 3) compatibilidade final
        for codigo, item in compatibilidades.items():
            ajuste = max(-limite, min(limite, ajustes[codigo]))
            item.ajuste = round(ajuste, 2)
            item.percentual = round(max(0.0, min(100.0, item.base + ajuste)), 1)
            item.regras = [r for r in disparadas if r.efeito_em(codigo) != 0]

        ordenadas = sorted(
            compatibilidades.values(),
            key=lambda c: (-c.percentual, -c.base, self.base.ids_trilhas.index(c.trilha)),
        )

        alertas = self._gerar_alertas(ordenadas, respostas, disparadas)

        return Resultado(
            respostas=respostas,
            compatibilidades=ordenadas,
            regras_disparadas=disparadas,
            alertas=alertas,
            base_origem=self.base,
        )

    # -- alertas / tratamento de incerteza ------------------------------
    def _gerar_alertas(
        self,
        ranking: list[Compatibilidade],
        respostas: dict[str, Any],
        disparadas: list[RegraDisparada],
    ) -> list[str]:
        alertas: list[str] = []
        primeira, segunda = ranking[0], ranking[1]
        margem = primeira.percentual - segunda.percentual

        if margem < 3:
            alertas.append(
                f"Empate técnico: {self.base.trilhas[primeira.trilha].nome} e "
                f"{self.base.trilhas[segunda.trilha].nome} estão a {margem:.1f} p.p. "
                "de distância. Considere experimentar as duas trilhas antes de decidir."
            )
        if primeira.percentual < 45:
            alertas.append(
                "Perfil pouco definido: nenhuma trilha passou de 45% de compatibilidade. "
                "Vale revisar suas respostas ou explorar mais as áreas antes de escolher."
            )
        valores = [respostas[d.id] for d in self.base.dimensoes]
        if len(set(valores)) == 1:
            alertas.append(
                "Respostas uniformes: todas as afinidades receberam a mesma nota, o que "
                "reduz o poder de discriminação do motor. Tente diferenciar o que mais te atrai."
            )
        if len(disparadas) == 0:
            alertas.append(
                "Nenhuma regra foi ativada: o resultado veio apenas da matriz de afinidade."
            )
        elif len(disparadas) >= 15:
            alertas.append(
                f"Perfil multifacetado: {len(disparadas)} regras foram ativadas. É normal ter "
                "afinidade com mais de uma área — use o Top 3 para comparar."
            )
        if primeira.percentual >= 90:
            alertas.append(
                "Compatibilidade muito alta: revise também as lacunas de competências antes "
                "de assumir que a trilha é confortável."
            )
        return alertas


# ----------------------------------------------------------------------
# Conveniência
# ----------------------------------------------------------------------
_MOTOR_PADRAO: MotorInferencia | None = None


def motor_padrao() -> MotorInferencia:
    """Instância única do motor (evita reler o JSON a cada avaliação)."""
    global _MOTOR_PADRAO
    if _MOTOR_PADRAO is None:
        _MOTOR_PADRAO = MotorInferencia(carregar())
    return _MOTOR_PADRAO


def avaliar(respostas: dict[str, Any]) -> Resultado:
    """Atalho: avalia um perfil usando a base de conhecimento padrão."""
    return motor_padrao().avaliar(respostas)
