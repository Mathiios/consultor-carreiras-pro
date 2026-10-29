"""Consultor Avançado de Carreiras em TI — interface Streamlit em etapas."""

from __future__ import annotations

import json
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from consultor_pro.base_conhecimento import ErroBaseConhecimento, carregar
from consultor_pro.motor import MotorInferencia
from consultor_pro.recomendacao import analisar

st.set_page_config(
    page_title="Consultor de Carreiras em TI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

ETAPAS = ["Perfil", "Afinidades", "Objetivos", "Resultado"]
NIVEIS_EXPERIENCIA = [
    "Nenhuma experiência em TI",
    "Estudante com projetos pessoais",
    "Estágio ou trainee",
    "Júnior",
    "Pleno ou acima",
]
FORMACOES = [
    "Ensino médio / técnico",
    "Graduação em exatas (Eng., TI, Matemática)",
    "Graduação em humanas / gestão",
    "Pós-graduação",
    "Autodidata / cursos livres",
]


# ----------------------------------------------------------------------
# Recursos
# ----------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def obter_motor() -> MotorInferencia:
    return MotorInferencia(carregar())


try:
    motor = obter_motor()
except ErroBaseConhecimento as erro:  # base quebrada: falha explícita, sem esconder
    st.error(f"Não foi possível carregar a base de conhecimento.\n\n{erro}")
    st.stop()

base = motor.base
RESPOSTAS_PREFIXO = "resp_"


def inicializar_estado() -> None:
    st.session_state.setdefault("etapa", 0)
    for dimensao in base.dimensoes:
        st.session_state.setdefault(f"resp_{dimensao.id}", 3)
    for categoria in base.categoricas:
        st.session_state.setdefault(f"resp_{categoria.id}", None)
    st.session_state.setdefault("resp_tec_estudadas", [])
    st.session_state.setdefault("resp_tec_dominadas", [])
    st.session_state.setdefault("resp_meta", "Júnior")
    st.session_state.setdefault("perfil_nome", "")
    st.session_state.setdefault("perfil_formacao", FORMACOES[0])
    st.session_state.setdefault("perfil_experiencia", NIVEIS_EXPERIENCIA[0])
    st.session_state.setdefault("perfil_horas", 10)


def reiniciar() -> None:
    for chave in list(st.session_state):
        if chave.startswith(RESPOSTAS_PREFIXO) or chave.startswith("perfil_"):
            del st.session_state[chave]
    st.session_state["etapa"] = 0
    st.rerun()


def coletar_respostas() -> dict:
    respostas: dict = {}
    for dimensao in base.dimensoes:
        respostas[dimensao.id] = st.session_state.get(f"resp_{dimensao.id}", 3)
    for categoria in base.categoricas:
        respostas[categoria.id] = st.session_state.get(f"resp_{categoria.id}")
    respostas.update(
        {
            "tecnologias_estudadas": st.session_state.get("resp_tec_estudadas", []),
            "tecnologias_dominadas": st.session_state.get("resp_tec_dominadas", []),
            "horas_semana": st.session_state.get("perfil_horas", 10),
            "meta_senioridade": st.session_state.get("resp_meta", "Júnior"),
            "nome": (st.session_state.get("perfil_nome") or "").strip(),
            "formacao": st.session_state.get("perfil_formacao"),
            "experiencia": st.session_state.get("perfil_experiencia"),
        }
    )
    return respostas


def rotulo_trilha(codigo: str) -> str:
    trilha = base.trilhas[codigo]
    return f"{trilha.icone} {trilha.nome}"


# ----------------------------------------------------------------------
# Cabeçalho e navegação
# ----------------------------------------------------------------------
inicializar_estado()
etapa: int = st.session_state["etapa"]

st.title("🧭 Consultor Avançado de Carreiras em TI")
st.caption(
    "Sistema especialista com pontuação ponderada: ranking de compatibilidade, "
    "análise de lacunas e plano de estudo personalizado."
)

with st.sidebar:
    st.subheader("Como funciona")
    st.markdown(
        "1. **Entrevista em 3 etapas** — perfil, afinidades (escala 1–5) e objetivos.\n"
        "2. **Motor ponderado** — matriz de afinidade + 38 regras SE–ENTÃO com fator de certeza.\n"
        "3. **Resultado** — Top 3 com %, lacunas de competências, roadmap e portfólio."
    )
    st.divider()
    st.caption(
        f"Base de conhecimento v{base.versao} · "
        f"{len(base.regras)} regras · {len(base.trilhas)} trilhas · "
        f"{len(base.tecnologias)} tecnologias"
    )
    if base.origem:
        st.caption(f"Fonte: `{base.origem.name}`")
    st.divider()
    st.caption(f"Atualizado em {date.today().strftime('%d/%m/%Y')}")

st.progress(min(1.0, (etapa + 1) / 3), text=f"Passo {min(etapa + 1, 3)} de 3 · {ETAPAS[etapa]}")

# ----------------------------------------------------------------------
# Passo 1 — perfil pessoal
# ----------------------------------------------------------------------
if etapa == 0:
    st.subheader("Passo 1 · Perfil pessoal")
    st.write("Esses dados contextualizam o plano de estudo e não entram na pontuação.")

    esquerda, direita = st.columns(2)
    with esquerda:
        st.text_input(
            "Como podemos te chamar?",
            key="perfil_nome",
            placeholder="Opcional",
            help="Usado apenas para personalizar o resultado.",
        )
        st.selectbox("Formação / background", FORMACOES, key="perfil_formacao")
    with direita:
        st.selectbox("Experiência atual em TI", NIVEIS_EXPERIENCIA, key="perfil_experiencia")
        st.slider(
            "Horas de estudo por semana",
            min_value=1,
            max_value=40,
            key="perfil_horas",
            help="O plano de ação converte a carga horária em semanas estimadas.",
        )

    st.info("No próximo passo você vai avaliar suas afinidades de 1 a 5.")

# ----------------------------------------------------------------------
# Passo 2 — afinidades
# ----------------------------------------------------------------------
elif etapa == 1:
    st.subheader("Passo 2 · Afinidades técnicas")
    st.write(
        "Dê uma nota de **1 (nenhuma afinidade)** a **5 (muita afinidade)**. "
        "Não existe resposta certa — o motor calibra o ranking a partir da combinação."
    )

    colunas = st.columns(2)
    for indice, dimensao in enumerate(base.dimensoes):
        with colunas[indice % 2]:
            valor = st.slider(
                dimensao.pergunta,
                min_value=base.escala_min,
                max_value=base.escala_max,
                key=f"resp_{dimensao.id}",
                help=dimensao.ajuda or None,
            )
            st.caption(f"**{dimensao.nome}** · {base.rotulo_likert(valor)}")

    st.divider()
    st.markdown("**Ferramentas e tecnologias**")
    col_a, col_b = st.columns(2)
    with col_a:
        categoria_linguagem = base.categoria("linguagem")
        if categoria_linguagem:
            st.selectbox(
                categoria_linguagem.pergunta,
                options=[o.valor for o in categoria_linguagem.opcoes],
                format_func=lambda v: categoria_linguagem.rotulo_de(v),
                index=None,
                key="resp_linguagem",
                placeholder="Selecione uma opção",
            )
    with col_b:
        st.selectbox(
            "Meta de senioridade",
            ["Júnior", "Pleno"],
            key="resp_meta",
            help="O roadmap é calibrado para o primeiro nível profissional.",
        )

    opcoes_tec = base.tecnologias_conhecidas()
    st.multiselect(
        "Tecnologias que você já estudou (nível iniciante)",
        options=list(opcoes_tec),
        format_func=lambda t: opcoes_tec[t],
        key="resp_tec_estudadas",
        help="Cada tecnologia mapeia para competências usadas na análise de lacunas.",
    )
    st.multiselect(
        "Tecnologias que você domina (já usou em projetos)",
        options=list(opcoes_tec),
        format_func=lambda t: opcoes_tec[t],
        key="resp_tec_dominadas",
    )

# ----------------------------------------------------------------------
# Passo 3 — objetivos
# ----------------------------------------------------------------------
elif etapa == 2:
    st.subheader("Passo 3 · Objetivos de carreira")
    st.write("Agora as perguntas sobre o tipo de valor que você quer entregar.")

    for categoria in base.categoricas:
        if categoria.id == "linguagem":
            continue
        st.radio(
            categoria.pergunta,
            options=[o.valor for o in categoria.opcoes],
            format_func=lambda v, c=categoria: c.rotulo_de(v),
            index=None,
            key=f"resp_{categoria.id}",
        )

    faltando = [
        categoria.nome
        for categoria in base.categoricas
        if categoria.id != "linguagem" and st.session_state.get(f"resp_{categoria.id}") is None
    ]
    if faltando:
        st.warning("Responda também: " + ", ".join(faltando) + ".")

# ----------------------------------------------------------------------
# Passo 4 — resultado
# ----------------------------------------------------------------------
elif etapa == 3:
    respostas = coletar_respostas()
    resultado = motor.avaliar(respostas)
    plano = analisar(base, resultado)
    nome = respostas.get("nome") or "seu perfil"

    st.subheader(f"Resultado para {nome}")
    st.caption(
        "Compatibilidade = aderência ponderada às dimensões (0–100) + ajuste das regras "
        "ativadas (limitado a ±20 pontos percentuais)."
    )

    # Top 3
    colunas = st.columns(3)
    for posicao, item in enumerate(resultado.top3):
        with colunas[posicao]:
            if posicao == 0:
                delta = f"{resultado.margem:+.1f} p.p. vs 2º"
                cor = "normal"
            else:
                delta = f"{item.percentual - resultado.destaque.percentual:+.1f} p.p. vs 1º"
                cor = "off"
            st.metric(label=f"{posicao + 1}º lugar", value=f"{item.percentual:.1f}%", delta=delta, delta_color=cor)
            st.markdown(f"**{rotulo_trilha(item.trilha)}**")
            st.progress(item.percentual / 100)
            st.caption(base.trilhas[item.trilha].resumo)

    for alerta in resultado.alertas:
        st.warning(alerta)

    st.divider()

    # Gráfico de compatibilidade
    st.markdown("### Ranking completo das 10 trilhas")
    dados_ranking = pd.DataFrame(
        [
            {
                "Trilha": rotulo_trilha(item.trilha),
                "Compatibilidade": item.percentual,
                "Base (matriz)": item.base,
                "Ajuste das regras": item.ajuste,
                "Posição": f"{indice + 1}º",
            }
            for indice, item in enumerate(resultado.compatibilidades)
        ]
    )
    grafico = (
        alt.Chart(dados_ranking)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Compatibilidade:Q", scale=alt.Scale(domain=[0, 100]), title="Compatibilidade (%)"),
            y=alt.Y("Trilha:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
            color=alt.Color(
                "Compatibilidade:Q",
                scale=alt.Scale(scheme="tealblues", domain=[0, 100]),
                legend=None,
            ),
            tooltip=[
                "Trilha",
                alt.Tooltip("Compatibilidade:Q", format=".1f"),
                alt.Tooltip("Base (matriz):Q", format=".1f"),
                alt.Tooltip("Ajuste das regras:Q", format="+.1f"),
            ],
        )
        .properties(height=360)
    )
    st.altair_chart(grafico, width="stretch")

    # Radar (comparativo usuário x perfil ideal)
    st.markdown("### Radar de afinidades vs. perfil ideal")
    trilhas_top = [item.trilha for item in resultado.top3]
    escolhida = st.selectbox(
        "Comparar com o perfil ideal de:",
        options=trilhas_top,
        format_func=rotulo_trilha,
        key="comparar_trilha",
    )
    afinidades = resultado.afinidades_usuario()
    ideais = resultado.perfil_ideal(escolhida)
    dados_radar = []
    for dimensao in base.dimensoes:
        dados_radar.append(
            {"Dimensão": dimensao.nome, "Série": "Você", "Nota": afinidades[dimensao.id]}
        )
        dados_radar.append(
            {"Dimensão": dimensao.nome, "Série": "Perfil ideal", "Nota": round(ideais[dimensao.id], 2)}
        )
    grafico_radar = (
        alt.Chart(pd.DataFrame(dados_radar))
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y(
                "Dimensão:N",
                sort=list(reversed([d.nome for d in base.dimensoes])),
                title=None,
                axis=alt.Axis(labelLimit=230),
            ),
            x=alt.X("Nota:Q", scale=alt.Scale(domain=[0, 5]), title="Nota (1–5)"),
            color=alt.Color(
                "Série:N",
                scale=alt.Scale(domain=["Você", "Perfil ideal"], range=["#0ea5e9", "#cbd5e1"]),
                legend=alt.Legend(orient="top"),
            ),
            yOffset="Série:N",
            tooltip=["Dimensão", "Série", alt.Tooltip("Nota:Q", format=".1f")],
        )
        .properties(height=340)
    )
    st.altair_chart(grafico_radar, width="stretch")
    st.caption(
        f"O perfil ideal é derivado dos pesos da matriz de afinidade da trilha "
        f"{rotulo_trilha(escolhida)}."
    )

    st.divider()

    # Lacunas e plano
    st.markdown(f"### Plano de ação para {rotulo_trilha(plano.trilha)}")
    metricas = st.columns(4)
    metricas[0].metric("Cobertura atual", f"{plano.cobertura:.0f}%")
    metricas[1].metric("Lacunas", len(plano.lacunas))
    metricas[2].metric("Carga semanal", f"{plano.horas_semana} h")
    metricas[3].metric(
        "Prazo estimado",
        f"{plano.semanas_estimadas} sem",
        delta=f"~{plano.meses_estimados} meses",
        delta_color="off",
    )

    st.markdown("#### Skill gaps (o que falta para o nível júnior)")
    if plano.lacunas:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Competência": lacuna.nome,
                        "Nível atual": lacuna.atual,
                        "Exigido": lacuna.exigido,
                        "Importância": lacuna.importancia,
                        "Criticidade": lacuna.criticidade,
                        "Horas estimadas": lacuna.horas_estimadas,
                    }
                    for lacuna in plano.lacunas
                ]
            ),
            hide_index=True,
            width="stretch",
        )
    else:
        st.success("Você já cobre todas as competências exigidas para o nível júnior nesta trilha.")

    if plano.forcas:
        st.markdown("#### Pontos fortes já adquiridos")
        st.write(" · ".join(forca.descricao() for forca in plano.forcas))

    st.markdown("#### Roadmap sugerido")
    for fase in plano.fases:
        semanas = fase.semanas(plano.horas_semana)
        rotulo = "🔧 Nivelamento" if fase.tipo == "nivelamento" else "📚 Trilha"
        with st.expander(
            f"Fase {fase.ordem} · {fase.titulo} — {fase.horas} h (~{semanas} sem)", expanded=fase.ordem == 1
        ):
            st.caption(rotulo)
            st.markdown("\n".join(f"- {topico}" for topico in fase.topicos))

    col_cert, col_proj = st.columns(2)
    with col_cert:
        st.markdown("#### Certificações recomendadas")
        st.markdown("\n".join(f"- {cert}" for cert in plano.certificacoes))
        st.markdown("#### Tecnologias da trilha")
        st.write(", ".join(plano.tecnologias))
    with col_proj:
        st.markdown("#### Projetos para o portfólio")
        for projeto in plano.projetos:
            st.markdown(f"**{projeto.titulo}** — {projeto.descricao}")

    st.divider()

    # Transparência
    with st.expander("🔎 Como o motor chegou a esse resultado"):
        destaque = resultado.destaque
        st.markdown(
            f"**{rotulo_trilha(destaque.trilha)}**: aderência da matriz "
            f"**{destaque.base:.1f}%** + ajuste das regras **{destaque.ajuste:+.1f} p.p.** "
            f"= **{destaque.percentual:.1f}%**."
        )
        st.markdown("**Contribuição de cada dimensão (pontos percentuais):**")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Dimensão": base.dimensao(dim).nome if base.dimensao(dim) else dim,
                        "Sua nota": respostas[dim],
                        "Contribuição": valor,
                    }
                    for dim, valor in destaque.contribuicoes.items()
                ]
            ).sort_values("Contribuição", ascending=False),
            hide_index=True,
            width="stretch",
        )

        if destaque.regras:
            st.markdown("**Regras que ajustaram esta trilha:**")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Regra": item.regra.id,
                            "Nome": item.regra.nome,
                            "Tipo": item.regra.tipo,
                            "Certeza": item.regra.certeza,
                            "Efeito": f"{item.efeito_em(destaque.trilha):+.1f} p.p.",
                            "Justificativa": item.regra.explicacao,
                        }
                        for item in destaque.regras
                    ]
                ),
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("Nenhuma regra alterou esta trilha: o resultado veio apenas da matriz.")

        st.markdown(f"**Total de regras ativadas no perfil:** {len(resultado.regras_disparadas)}")
        with st.expander("Ver todas as regras ativadas"):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Regra": item.regra.id,
                            "Nome": item.regra.nome,
                            "Tipo": item.regra.tipo,
                            "Trilhas afetadas": ", ".join(
                                f"{t} ({d:+.1f})" for t, d in item.efeitos_aplicados.items()
                            ),
                        }
                        for item in resultado.regras_disparadas
                    ]
                ),
                hide_index=True,
                width="stretch",
            )

    # Exportação
    exportacao = {
        "gerado_em": date.today().isoformat(),
        "base_versao": base.versao,
        "respostas": respostas,
        "ranking": [
            {"trilha": item.trilha, "compatibilidade": item.percentual} for item in resultado.compatibilidades
        ],
        "plano": {
            "trilha": plano.trilha,
            "cobertura": plano.cobertura,
            "semanas": plano.semanas_estimadas,
            "lacunas": [lacuna.nome for lacuna in plano.lacunas],
            "fases": [fase.titulo for fase in plano.fases],
        },
    }
    st.download_button(
        "⬇️ Baixar meu resultado (JSON)",
        data=json.dumps(exportacao, ensure_ascii=False, indent=2),
        file_name="resultado_consultor_carreiras.json",
        mime="application/json",
    )

# ----------------------------------------------------------------------
# Botões de navegação
# ----------------------------------------------------------------------
st.divider()
voltar, espaco, avancar = st.columns([1, 3, 1])

with voltar:
    if etapa > 0:
        if st.button("← Voltar", width="stretch"):
            st.session_state["etapa"] = etapa - 1
            st.rerun()

with avancar:
    if etapa < 3:
        rotulo = "Ver meu resultado →" if etapa == 2 else "Continuar →"
        if st.button(rotulo, type="primary", width="stretch"):
            if etapa == 2:
                faltando = [
                    categoria.nome
                    for categoria in base.categoricas
                    if categoria.id != "linguagem"
                    and st.session_state.get(f"resp_{categoria.id}") is None
                ]
                if faltando:
                    st.error("Antes de calcular, responda: " + ", ".join(faltando) + ".")
                else:
                    st.session_state["etapa"] = 3
                    st.rerun()
            else:
                st.session_state["etapa"] = etapa + 1
                st.rerun()
    else:
        if st.button("↺ Recomeçar", width="stretch"):
            reiniciar()
