"""Carregamento e validação da base de conhecimento (JSON).

Todo o conhecimento do sistema (dimensões, pesos, regras, trilhas, competências)
vive em ``data/regras_carreiras.json``. Este módulo transforma o JSON em
estruturas tipadas e **valida a consistência** antes de o motor rodar.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_PADRAO = RAIZ_PROJETO / "data" / "regras_carreiras.json"

OPERADORES = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


class ErroBaseConhecimento(ValueError):
    """Base de conhecimento inválida ou inconsistente."""


# ----------------------------------------------------------------------
# Estruturas tipadas
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Dimensao:
    id: str
    nome: str
    pergunta: str
    ajuda: str
    etapa: int


@dataclass(frozen=True)
class Opcao:
    valor: str
    rotulo: str


@dataclass(frozen=True)
class Categoria:
    id: str
    nome: str
    pergunta: str
    etapa: int
    opcoes: tuple[Opcao, ...]

    def rotulo_de(self, valor: str | None) -> str:
        for opcao in self.opcoes:
            if opcao.valor == valor:
                return opcao.rotulo
        return "—" if valor is None else str(valor)


@dataclass(frozen=True)
class Condicao:
    fonte: str
    op: str
    valor: Any

    def descricao(self) -> str:
        return f"{self.fonte} {self.op} {self.valor}"


@dataclass(frozen=True)
class Efeito:
    trilha: str
    delta: float


@dataclass(frozen=True)
class Regra:
    id: str
    nome: str
    tipo: str
    certeza: float
    condicoes: tuple[Condicao, ...]
    efeitos: tuple[Efeito, ...]
    explicacao: str

    @property
    def peso_maximo(self) -> float:
        return max((abs(e.delta) for e in self.efeitos), default=0.0)


@dataclass(frozen=True)
class Competencia:
    skill: str
    nivel_junior: int
    importancia: int


@dataclass(frozen=True)
class FaseRoadmap:
    titulo: str
    horas: int
    topicos: tuple[str, ...]


@dataclass(frozen=True)
class Projeto:
    titulo: str
    descricao: str


@dataclass(frozen=True)
class Skill:
    id: str
    nome: str
    topicos: tuple[str, ...]


@dataclass(frozen=True)
class Tecnologia:
    id: str
    nome: str
    skills: dict[str, int]


@dataclass(frozen=True)
class Trilha:
    codigo: str
    nome: str
    icone: str
    resumo: str
    atividades: tuple[str, ...]
    tecnologias: tuple[str, ...]
    competencias: tuple[Competencia, ...]
    roadmap: tuple[FaseRoadmap, ...]
    certificacoes: tuple[str, ...]
    projetos: tuple[Projeto, ...]


@dataclass(frozen=True)
class BaseConhecimento:
    versao: str
    escala_min: int
    escala_max: int
    rotulos_escala: dict[str, str]
    dimensoes: tuple[Dimensao, ...]
    categoricas: tuple[Categoria, ...]
    matriz: dict[str, dict[str, float]]
    regras: tuple[Regra, ...]
    skills: dict[str, Skill]
    tecnologias: dict[str, Tecnologia]
    trilhas: dict[str, Trilha]
    ajuste_maximo_regras: float
    origem: Path | None = field(default=None, compare=False)

    # -- consultas auxiliares -----------------------------------------
    @property
    def ids_trilhas(self) -> list[str]:
        return list(self.trilhas)

    @property
    def ids_dimensoes(self) -> list[str]:
        return [d.id for d in self.dimensoes]

    @property
    def rotulos_likert(self) -> dict[int, str]:
        return {int(k): v for k, v in self.rotulos_escala.items()}

    def dimensao(self, dim_id: str) -> Dimensao | None:
        return next((d for d in self.dimensoes if d.id == dim_id), None)

    def categoria(self, cat_id: str) -> Categoria | None:
        return next((c for c in self.categoricas if c.id == cat_id), None)

    def questao(self, fonte: str) -> Dimensao | Categoria | None:
        return self.dimensao(fonte) or self.categoria(fonte)

    def tecnologias_conhecidas(self) -> dict[str, str]:
        return {t.id: t.nome for t in self.tecnologias.values()}

    def rotulo_likert(self, valor: int) -> str:
        return self.rotulos_escala.get(str(valor), str(valor))


# ----------------------------------------------------------------------
# Validação
# ----------------------------------------------------------------------
def _validar(base: BaseConhecimento) -> None:
    problemas: list[str] = []
    dims = {d.id for d in base.dimensoes}
    cats = {c.id for c in base.categoricas}
    trilhas = set(base.trilhas)

    if not base.dimensoes:
        problemas.append("nenhuma dimensão definida")
    if not base.trilhas:
        problemas.append("nenhuma trilha definida")
    if len(base.categoricas) == 0:
        problemas.append("nenhuma questão categórica definida")

    # matriz completa e coerente
    for dim in dims:
        if dim not in base.matriz:
            problemas.append(f"matriz sem a dimensão '{dim}'")
            continue
        for trilha in trilhas:
            if trilha not in base.matriz[dim]:
                problemas.append(f"matriz sem o peso {dim}×{trilha}")
            else:
                peso = base.matriz[dim][trilha]
                if not isinstance(peso, (int, float)) or peso < 0:
                    problemas.append(f"peso inválido em {dim}×{trilha}: {peso!r}")
    for dim in base.matriz:
        if dim not in dims:
            problemas.append(f"matriz possui dimensão desconhecida '{dim}'")
        else:
            for trilha_extra in base.matriz[dim]:
                if trilha_extra not in trilhas:
                    problemas.append(f"matriz possui trilha desconhecida '{trilha_extra}' em '{dim}'")

    # regras
    for regra in base.regras:
        for condicao in regra.condicoes:
            if condicao.fonte not in dims | cats:
                problemas.append(f"regra {regra.id}: fonte desconhecida '{condicao.fonte}'")
            if condicao.op not in OPERADORES:
                problemas.append(f"regra {regra.id}: operador inválido '{condicao.op}'")
            if condicao.fonte in cats and condicao.op in {"==", "!="}:
                cat = next(c for c in base.categoricas if c.id == condicao.fonte)
                validos = {o.valor for o in cat.opcoes}
                if condicao.valor not in validos:
                    problemas.append(
                        f"regra {regra.id}: valor '{condicao.valor}' inexistente em '{condicao.fonte}'"
                    )
        for efeito in regra.efeitos:
            if efeito.trilha not in trilhas:
                problemas.append(f"regra {regra.id}: trilha desconhecida '{efeito.trilha}'")
        if not 0 < regra.certeza <= 1:
            problemas.append(f"regra {regra.id}: certeza deve estar em (0, 1]")

    # competências e tecnologias
    for codigo, trilha in base.trilhas.items():
        if not trilha.competencias:
            problemas.append(f"trilha '{codigo}' sem competências")
        for competencia in trilha.competencias:
            if competencia.skill not in base.skills:
                problemas.append(f"trilha '{codigo}': competência desconhecida '{competencia.skill}'")
        for tecnologia in trilha.tecnologias:
            if tecnologia not in base.tecnologias:
                problemas.append(f"trilha '{codigo}': tecnologia desconhecida '{tecnologia}'")
    for tecnologia in base.tecnologias.values():
        for skill_id in tecnologia.skills:
            if skill_id not in base.skills:
                problemas.append(f"tecnologia '{tecnologia.id}': skill desconhecida '{skill_id}'")

    # ids duplicados
    if len(dims) != len(base.dimensoes):
        problemas.append("dimensões com id duplicado")
    if len({r.id for r in base.regras}) != len(base.regras):
        problemas.append("regras com id duplicado")

    if problemas:
        raise ErroBaseConhecimento(
            "Base de conhecimento inconsistente:\n - " + "\n - ".join(problemas)
        )


# ----------------------------------------------------------------------
# Carregamento
# ----------------------------------------------------------------------
def carregar(caminho: str | Path | None = None) -> BaseConhecimento:
    """Lê o JSON, converte para objetos tipados e valida a consistência."""
    caminho = Path(caminho) if caminho else CAMINHO_PADRAO

    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroBaseConhecimento(f"arquivo não encontrado: {caminho}") from erro
    except json.JSONDecodeError as erro:
        raise ErroBaseConhecimento(f"JSON inválido em {caminho}: {erro}") from erro

    try:
        dimensoes = tuple(
            Dimensao(
                id=d["id"],
                nome=d["nome"],
                pergunta=d["pergunta"],
                ajuda=d.get("ajuda", ""),
                etapa=int(d.get("etapa", 2)),
            )
            for d in bruto["dimensoes"]
        )
        categoricas = tuple(
            Categoria(
                id=c["id"],
                nome=c["nome"],
                pergunta=c["pergunta"],
                etapa=int(c.get("etapa", 3)),
                opcoes=tuple(Opcao(valor=o["valor"], rotulo=o["rotulo"]) for o in c["opcoes"]),
            )
            for c in bruto["categoricas"]
        )
        regras = tuple(
            Regra(
                id=r["id"],
                nome=r["nome"],
                tipo=r.get("tipo", "reforco"),
                certeza=float(r.get("certeza", 1.0)),
                condicoes=tuple(
                    Condicao(fonte=c["fonte"], op=c["op"], valor=c["valor"]) for c in r["condicoes"]
                ),
                efeitos=tuple(Efeito(trilha=e["trilha"], delta=float(e["delta"])) for e in r["efeitos"]),
                explicacao=r.get("explicacao", ""),
            )
            for r in bruto["regras"]
        )
        skills = {
            sid: Skill(id=sid, nome=s["nome"], topicos=tuple(s.get("topicos", [])))
            for sid, s in bruto["competencias"].items()
        }
        tecnologias = {
            tid: Tecnologia(
                id=tid,
                nome=t["nome"],
                skills={k: int(v) for k, v in t.get("skills", {}).items()},
            )
            for tid, t in bruto["tecnologias"].items()
        }
        trilhas = {
            codigo: Trilha(
                codigo=codigo,
                nome=t["nome"],
                icone=t.get("icone", "•"),
                resumo=t.get("resumo", ""),
                atividades=tuple(t.get("atividades", [])),
                tecnologias=tuple(t.get("tecnologias", [])),
                competencias=tuple(
                    Competencia(
                        skill=c["skill"],
                        nivel_junior=int(c["nivel_junior"]),
                        importancia=int(c["importancia"]),
                    )
                    for c in t.get("competencias", [])
                ),
                roadmap=tuple(
                    FaseRoadmap(
                        titulo=f["titulo"],
                        horas=int(f["horas"]),
                        topicos=tuple(f.get("topicos", [])),
                    )
                    for f in t.get("roadmap", [])
                ),
                certificacoes=tuple(t.get("certificacoes", [])),
                projetos=tuple(
                    Projeto(titulo=p["titulo"], descricao=p.get("descricao", ""))
                    for p in t.get("projetos", [])
                ),
            )
            for codigo, t in bruto["trilhas"].items()
        }
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroBaseConhecimento(f"estrutura inválida no JSON: {erro}") from erro

    escala = bruto.get("escala_likert", {})
    base = BaseConhecimento(
        versao=bruto.get("versao", "?"),
        escala_min=int(escala.get("min", 1)),
        escala_max=int(escala.get("max", 5)),
        rotulos_escala={str(k): v for k, v in escala.get("rotulos", {}).items()},
        dimensoes=dimensoes,
        categoricas=categoricas,
        matriz={dim: {t: float(w) for t, w in linha.items()} for dim, linha in bruto["matriz_afinidade"].items()},
        regras=regras,
        skills=skills,
        tecnologias=tecnologias,
        trilhas=trilhas,
        ajuste_maximo_regras=float(bruto.get("ajuste_maximo_regras", 20)),
        origem=caminho,
    )

    _validar(base)
    return base
