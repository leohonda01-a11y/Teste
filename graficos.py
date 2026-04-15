"""
Módulo de geração de gráficos para relatórios visuais.
Gera gráficos de pizza e barras para análise de gastos.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

# Configuração visual
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "text.color": "#e0e0e0",
    "axes.labelcolor": "#e0e0e0",
    "xtick.color": "#e0e0e0",
    "ytick.color": "#e0e0e0",
})

CORES = [
    "#e94560", "#0f3460", "#533483", "#e94560",
    "#16c79a", "#f5a623", "#7b68ee", "#ff6b6b",
    "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7",
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficos_temp")


def _garantir_diretorio():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def grafico_pizza_categorias(gastos_por_categoria: list, mes: str, user_id: int) -> str:
    """
    Gera um gráfico de pizza com a distribuição de gastos por categoria.
    Retorna o caminho do arquivo de imagem.
    """
    _garantir_diretorio()

    if not gastos_por_categoria:
        return ""

    categorias = [g["categoria"] for g in gastos_por_categoria]
    valores = [g["total"] for g in gastos_por_categoria]
    total = sum(valores)

    fig, ax = plt.subplots(figsize=(10, 8))

    wedges, texts, autotexts = ax.pie(
        valores,
        labels=None,
        autopct=lambda pct: f"R$ {pct * total / 100:.0f}\n({pct:.1f}%)" if pct > 5 else "",
        colors=CORES[: len(categorias)],
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor="#1a1a2e", linewidth=2),
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color("#ffffff")

    # Legenda
    legend_labels = [
        f"{cat} — R$ {val:.2f}" for cat, val in zip(categorias, valores)
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Categorias",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10,
        title_fontsize=12,
        facecolor="#16213e",
        edgecolor="#0f3460",
        labelcolor="#e0e0e0",
    )

    meses_pt = {
        "01": "Janeiro", "02": "Fevereiro", "03": "Março",
        "04": "Abril", "05": "Maio", "06": "Junho",
        "07": "Julho", "08": "Agosto", "09": "Setembro",
        "10": "Outubro", "11": "Novembro", "12": "Dezembro",
    }
    mes_nome = meses_pt.get(mes.split("-")[1], mes)
    ano = mes.split("-")[0]

    ax.set_title(
        f"Gastos por Categoria — {mes_nome}/{ano}\nTotal: R$ {total:.2f}",
        fontsize=16,
        fontweight="bold",
        color="#e0e0e0",
        pad=20,
    )

    filepath = os.path.join(OUTPUT_DIR, f"pizza_{user_id}_{mes}.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()

    return filepath


def grafico_barras_diario(transacoes_diarias: list, mes: str, user_id: int) -> str:
    """
    Gera um gráfico de barras com gastos diários.
    transacoes_diarias: lista de dicts com 'dia' e 'total'.
    Retorna o caminho do arquivo de imagem.
    """
    _garantir_diretorio()

    if not transacoes_diarias:
        return ""

    dias = [t["dia"] for t in transacoes_diarias]
    valores = [t["total"] for t in transacoes_diarias]

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(dias, valores, color="#e94560", edgecolor="#0f3460", linewidth=0.5, width=0.7)

    # Destacar o dia com maior gasto
    max_idx = valores.index(max(valores))
    bars[max_idx].set_color("#f5a623")

    ax.set_xlabel("Dia do Mês", fontsize=12)
    ax.set_ylabel("Valor (R$)", fontsize=12)

    meses_pt = {
        "01": "Janeiro", "02": "Fevereiro", "03": "Março",
        "04": "Abril", "05": "Maio", "06": "Junho",
        "07": "Julho", "08": "Agosto", "09": "Setembro",
        "10": "Outubro", "11": "Novembro", "12": "Dezembro",
    }
    mes_nome = meses_pt.get(mes.split("-")[1], mes)
    ano = mes.split("-")[0]

    ax.set_title(
        f"Gastos Diários — {mes_nome}/{ano}",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"R$ {x:.0f}"))
    ax.grid(axis="y", alpha=0.3, color="#e0e0e0")
    ax.set_axisbelow(True)

    filepath = os.path.join(OUTPUT_DIR, f"barras_{user_id}_{mes}.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()

    return filepath


def grafico_evolucao_mensal(dados_mensais: list, user_id: int) -> str:
    """
    Gera um gráfico de linha com a evolução de gastos e receitas ao longo dos meses.
    dados_mensais: lista de dicts com 'mes', 'gastos', 'receitas'.
    """
    _garantir_diretorio()

    if not dados_mensais:
        return ""

    meses = [d["mes"] for d in dados_mensais]
    gastos = [d["gastos"] for d in dados_mensais]
    receitas = [d["receitas"] for d in dados_mensais]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(meses, gastos, "o-", color="#e94560", linewidth=2, markersize=8, label="Gastos")
    ax.plot(meses, receitas, "o-", color="#16c79a", linewidth=2, markersize=8, label="Receitas")

    ax.fill_between(meses, gastos, alpha=0.1, color="#e94560")
    ax.fill_between(meses, receitas, alpha=0.1, color="#16c79a")

    ax.set_xlabel("Mês", fontsize=12)
    ax.set_ylabel("Valor (R$)", fontsize=12)
    ax.set_title("Evolução Financeira Mensal", fontsize=16, fontweight="bold", pad=15)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"R$ {x:.0f}"))
    ax.legend(fontsize=12, facecolor="#16213e", edgecolor="#0f3460", labelcolor="#e0e0e0")
    ax.grid(alpha=0.3, color="#e0e0e0")
    ax.set_axisbelow(True)

    plt.xticks(rotation=45)

    filepath = os.path.join(OUTPUT_DIR, f"evolucao_{user_id}.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()

    return filepath
