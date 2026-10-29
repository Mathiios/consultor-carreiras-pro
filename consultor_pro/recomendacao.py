"""Análise de lacunas (skill gaps) e geração do plano de ação pessoal.

A lógica aqui é deliberadamente separada do motor de inferência: o motor diz
*qual trilha combina com o perfil*; este módulo responde *o que falta* para
chegar ao nível júnior nessa trilha e *em que ordem estudar*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Any, Iterable

from .base_conhecimento import BaseConhecimento, Competencia, Projeto, Trilha
from .motor import Resultado

#: Horas de estudo estimadas para subir ~1 nível em uma competência.
HORAS_POR_NIVEL = 12


# ----------------------------------------------------------------------
# Estruturas
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Lacuna:
    skill: str
    nome: str
    atual: int
    exigido: int
    importancia: int
    topicos: tuple[str, ...] = ()

    @property
    def deficit(self) -> int:
        return max(0, self.exigido - self.atual)

    @property
    def prioridade(self) -> float:
        return self.deficit * self.importancia

    @property
    def criticidade(self) -> str:
        if self.deficit >= 2 and self.importancia >= 4:
            return "Crítica"
        if self.deficit >= 2 or (self.deficit == 1 and self.importancia >= 4):
            return "Alta"
        if self.deficit == 1 and self.importancia == 3:
            return "Moderada"
        return "Leve"

    @property
    def horas_estimadas(self) -> int:
        return max(1, self.deficit) * HORAS_POR_NIVEL

    def descricao(self) -> str:
        return f"{self.nome}: nível {self.atual}/5 → precisa de {self.exigido}/5"


@dataclass(frozen=True)
class Forca:
    skill: str
    nome: str
    atual: int
    exigido: int

    def descricao(self) -> str:
        return f"{self.nome} (nível {self.atual}/5, exigido {self.exigido}/5)"


@dataclass(frozen=True)
class FasePlano:
    ordem: int
    titulo: str
    tipo: str  # "nivelamento" | "trilha"
    horas: int
    topicos: tuple[str, ...]

    def semanas(self, horas_semana: int) -> int:
        return max(1, ceil(self.horas / max(1, horas_semana)))


@dataclass
class PlanoAcao:
    trilha: str
    nome_trilha: str
    lacunas: list[Lacuna]
    forcas: list[Forca]
    fases: list[FasePlano]
    certificacoes: list[str]
    projetos: list[Projeto]
    tecnologias: list[str]
    cobertura: float
    horas_semana: int
    meta: str = "Júnior"

    @property
    def horas_totais(self) -> int:
        return sum(fase.horas for fase in self.fases)

    @property
    def semanas_estimadas(self) -> int:
        return max(1, ceil(self.horas_totais / max(1, self.horas_semana)))

    @property
    def meses_estimados(self) -> float:
        return round(self.semanas_estimadas / 4.345, 1)

    @property
    def lacunas_criticas(self) -> list[Lacuna]:
        return [lac for lac in self.lacunas if lac.criticidade in {"Crítica", "Alta"}]

    def proximos_passos(self, limite: int = 5) -> list[str]:
        passos = [
            f"Fechar a lacuna de {lac.nome} (nível {lac.atual}/5 → {lac.exigido}/5)"
            for lac in self.lacunas[:limite]
        ]
        if not passos:
            passos = [
                "Você já cobre os pré-requisitos de nível júnior: foque em consolidar "
                "um projeto de portfólio completo."
            ]
        return passos


# ----------------------------------------------------------------------
# Níveis atuais a partir das tecnologias declaradas
# ----------------------------------------------------------------------
def niveis_por_skill(
    base: BaseConhecimento,
    estudadas: Iterable[str] = (),
    dominadas: Iterable[str] = (),
) -> dict[str, int]:
    """Converte as tecnologias que o usuário conhece em níveis por competência."""
    niveis: dict[str, int] = {}

    def aplicar(ids: Iterable[str], rotulo: str) -> None:
        for tech_id in ids:
            tecnologia = base.tecnologias.get(tech_id)
            if not tecnologia:
                continue
            for skill_id, peso in tecnologia.skills.items():
                # "estudei" -> no máximo nível 2; "domino" -> peso + 1 (até 5)
                nivel = min(2, max(1, peso)) if rotulo == "estudada" else min(5, peso + 1)
                niveis[skill_id] = max(niveis.get(skill_id, 0), nivel)

    aplicar(estudadas, "estudada")
    aplicar(dominadas, "dominada")
    return niveis


def _avaliar_competencia(
    competencia: Competencia, niveis: dict[str, int], base: BaseConhecimento
) -> Lacuna | Forca:
    skill = base.skills[competencia.skill]
    atual = min(5, niveis.get(competencia.skill, 0))
    if atual >= competencia.nivel_junior:
        return Forca(
            skill=competencia.skill,
            nome=skill.nome,
            atual=atual,
            exigido=competencia.nivel_junior,
        )
    return Lacuna(
        skill=competencia.skill,
        nome=skill.nome,
        atual=atual,
        exigido=competencia.nivel_junior,
        importancia=competencia.importancia,
        topicos=skill.topicos,
    )


# ----------------------------------------------------------------------
# Plano de ação
# ----------------------------------------------------------------------
def analisar(
    base: BaseConhecimento,
    resultado: Resultado,
    trilha: str | None = None,
    horas_semana: int | None = None,
    meta: str = "Júnior",
) -> PlanoAcao:
    """Cruza a trilha recomendada com o conhecimento atual do usuário."""
    codigo = trilha or resultado.destaque.trilha
    dados: Trilha = base.trilhas[codigo]
    respostas: dict[str, Any] = resultado.respostas

    estudadas = [t for t in respostas.get("tecnologias_estudadas", []) if isinstance(t, str)]
    dominadas = [t for t in respostas.get("tecnologias_dominadas", []) if isinstance(t, str)]
    niveis = niveis_por_skill(base, estudadas, dominadas)

    lacunas: list[Lacuna] = []
    forcas: list[Forca] = []
    for competencia in dados.competencias:
        avaliada = _avaliar_competencia(competencia, niveis, base)
        if isinstance(avaliada, Lacuna):
            lacunas.append(avaliada)
        else:
            forcas.append(avaliada)

    lacunas.sort(key=lambda lac: (-lac.prioridade, -lac.importancia, lac.nome))

    # cobertura ponderada das competências exigidas
    soma_importancia = sum(c.importancia for c in dados.competencias) or 1
    cobertura = 100 * sum(
        min(niveis.get(c.skill, 0) / max(1, c.nivel_junior), 1.0) * c.importancia
        for c in dados.competencias
    ) / soma_importancia

    if horas_semana is not None:
        horas = horas_semana
    else:
        horas = respostas.get("horas_semana")
        if horas is None:
            horas = 10
    horas = max(1, int(horas))
    meta = str(respostas.get("meta_senioridade") or meta)

    fases: list[FasePlano] = []
    if lacunas:
        topicos_nivelamento: list[str] = []
        for lacuna in lacunas[:6]:
            topicos_nivelamento.append(f"{lacuna.nome} — {', '.join(lacuna.topicos[:3])}")
        fases.append(
            FasePlano(
                ordem=1,
                titulo="Nivelamento: fechar lacunas para o nível júnior",
                tipo="nivelamento",
                horas=sum(lac.horas_estimadas for lac in lacunas),
                topicos=tuple(topicos_nivelamento),
            )
        )

    for indice, fase in enumerate(dados.roadmap, start=len(fases) + 1):
        fases.append(
            FasePlano(
                ordem=indice,
                titulo=fase.titulo,
                tipo="trilha",
                horas=fase.horas,
                topicos=fase.topicos,
            )
        )

    return PlanoAcao(
        trilha=codigo,
        nome_trilha=dados.nome,
        lacunas=lacunas,
        forcas=forcas,
        fases=fases,
        certificacoes=list(dados.certificacoes),
        projetos=list(dados.projetos),
        tecnologias=[base.tecnologias[t].nome for t in dados.tecnologias if t in base.tecnologias],
        cobertura=round(cobertura, 1),
        horas_semana=horas,
        meta=meta,
    )
