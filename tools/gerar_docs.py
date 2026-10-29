"""Gera a documentação da base de conhecimento a partir do JSON.

Assim como no projeto anterior, a tabela de regras não é mantida à mão:
ela é derivada do arquivo ``data/regras_carreiras.json`` para nunca ficar
dessincronizada do motor.

Uso:
    python tools/gerar_docs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.stdout.reconfigure(encoding="utf-8")

from consultor_pro import carregar  # noqa: E402

SAIDA = RAIZ / "docs" / "Base_de_Conhecimento.md"

OPERADORES_TEXTO = {">=": "≥", "<=": "≤", ">": ">", "<": "<", "==": "=", "!=": "≠"}


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> str:
    texto = ["| " + " | ".join(cabecalho) + " |", "|" + "|".join(["---"] * len(cabecalho)) + "|"]
    texto += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return "\n".join(texto)


def rotulo_condicao(base, condicao) -> str:
    questao = base.questao(condicao.fonte)
    nome = questao.nome if questao else condicao.fonte
    valor = condicao.valor
    if isinstance(valor, str):
        categoria = base.categoria(condicao.fonte)
        if categoria:
            valor = categoria.rotulo_de(valor)
    return f"{nome} {OPERADORES_TEXTO.get(condicao.op, condicao.op)} {valor}"


def gerar() -> str:
    base = carregar()
    linhas: list[str] = [
        "# Base de Conhecimento — Consultor Avançado de Carreiras em TI",
        "",
        f"> Documento gerado automaticamente a partir de `data/regras_carreiras.json` "
        f"(versão {base.versao}). **Não edite à mão.**",
        "",
        f"- Trilhas: **{len(base.trilhas)}**",
        f"- Dimensões de afinidade: **{len(base.dimensoes)}**",
        f"- Questões categóricas: **{len(base.categoricas)}**",
        f"- Regras ponderadas: **{len(base.regras)}**",
        f"- Competências mapeadas: **{len(base.skills)}**",
        f"- Tecnologias de entrada no portfólio: **{len(base.tecnologias)}**",
        f"- Limite de ajuste das regras: **±{base.ajuste_maximo_regras:.0f} p.p.**",
        "",
        "## 1. Dimensões de afinidade (escala Likert 1–5)",
        "",
        tabela(
            ["ID", "Dimensão", "Pergunta", "Escala"],
            [[d.id, d.nome, d.pergunta, f"{base.escala_min}–{base.escala_max}"] for d in base.dimensoes],
        ),
        "",
        "## 2. Questões categóricas",
        "",
    ]

    for categoria in base.categoricas:
        linhas.append(f"### `{categoria.id}` — {categoria.nome}")
        linhas.append("")
        linhas.append(categoria.pergunta)
        linhas.append("")
        linhas.append(tabela(["Valor", "Rótulo"], [[o.valor, o.rotulo] for o in categoria.opcoes]))
        linhas.append("")

    linhas += ["## 3. Matriz de afinidade (peso de cada dimensão por trilha)", ""]
    cabecalho = ["Dimensão"] + [f"{t.icone} {t.codigo}" for t in base.trilhas.values()]
    corpo = [
        [base.dimensao(dim).nome if base.dimensao(dim) else dim]
        + [str(int(base.matriz[dim][codigo])) for codigo in base.trilhas]
        for dim in base.ids_dimensoes
    ]
    linhas.append(tabela(cabecalho, corpo))
    linhas.append("")
    linhas.append(
        "Peso **0** significa que a dimensão não influencia a trilha; pesos maiores "
        "aumentam a contribuição da resposta para aquela trilha."
    )
    linhas.append("")

    linhas += [
        "## 4. Regras ponderadas",
        "",
        "Cada regra ativada aplica `delta × certeza` pontos percentuais à trilha. "
        f"O ajuste total por trilha é limitado a ±{base.ajuste_maximo_regras:.0f} p.p.",
        "",
    ]

    por_tipo: dict[str, list] = {}
    for regra in base.regras:
        por_tipo.setdefault(regra.tipo, []).append(regra)

    nomes_tipo = {
        "reforco": "4.1 Regras de reforço",
        "desambiguacao": "4.2 Regras de desambiguação",
        "penalidade": "4.3 Regras de penalidade (perfis conflitantes)",
    }
    for tipo in ("reforco", "desambiguacao", "penalidade"):
        regras = por_tipo.get(tipo, [])
        if not regras:
            continue
        linhas += [f"### {nomes_tipo.get(tipo, tipo)}", ""]
        linhas.append(
            tabela(
                ["ID", "Regra", "Certeza", "SE (condições)", "ENTÃO (efeito em p.p.)"],
                [
                    [
                        r.id,
                        r.nome,
                        f"{r.certeza:.2f}",
                        " **E** ".join(rotulo_condicao(base, c) for c in r.condicoes),
                        "<br>".join(
                            f"{e.trilha}: {e.delta:+.0f} ({e.delta * r.certeza:+.1f} com certeza)"
                            for e in r.efeitos
                        ),
                    ]
                    for r in regras
                ],
            )
        )
        linhas.append("")

    linhas += ["## 5. Trilhas, competências e roadmap", ""]
    for trilha in base.trilhas.values():
        linhas += [
            f"### {trilha.icone} {trilha.nome}",
            "",
            trilha.resumo,
            "",
            "**Competências para o nível júnior:**",
            "",
            tabela(
                ["Competência", "Nível exigido", "Importância"],
                [
                    [
                        base.skills[c.skill].nome,
                        f"{c.nivel_junior}/5",
                        f"{c.importancia}/5",
                    ]
                    for c in trilha.competencias
                ],
            ),
            "",
            "**Roadmap:**",
            "",
            tabela(
                ["Fase", "Título", "Horas", "Tópicos"],
                [
                    [i, fase.titulo, f"{fase.horas}h", ", ".join(fase.topicos)]
                    for i, fase in enumerate(trilha.roadmap, start=1)
                ],
            ),
            "",
            f"**Certificações:** {', '.join(trilha.certificacoes)}",
            "",
            "**Projetos de portfólio:**",
            "",
        ]
        for projeto in trilha.projetos:
            linhas.append(f"- **{projeto.titulo}** — {projeto.descricao}")
        linhas.append("")

    linhas += [
        "## 6. Tecnologias e competências que elas comprovam",
        "",
        tabela(
            ["Tecnologia", "Competências (nível relativo)"],
            [
                [
                    tecnologia.nome,
                    ", ".join(
                        f"{base.skills[skill].nome} ({nivel})"
                        for skill, nivel in tecnologia.skills.items()
                    ),
                ]
                for tecnologia in base.tecnologias.values()
            ],
        ),
        "",
    ]

    return "\n".join(linhas)


def main() -> int:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(gerar(), encoding="utf-8")
    print(f"Documentação gerada em {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
