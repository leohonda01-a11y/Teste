"""
Módulo de formatação de mensagens para o bot Telegram.
Formata resumos, transações e relatórios em texto bonito.
"""

from categorias import obter_emoji_categoria


def formatar_valor(valor: float) -> str:
    """Formata um valor monetário no padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_transacao_registrada(descricao: str, valor: float, categoria: str, tipo: str, transacao_id: int) -> str:
    """Formata a mensagem de confirmação de uma transação registrada."""
    emoji = obter_emoji_categoria(categoria)
    tipo_emoji = "🔴" if tipo == "gasto" else "🟢"
    tipo_texto = "Gasto" if tipo == "gasto" else "Receita"

    return (
        f"{tipo_emoji} *{tipo_texto} registrado!*\n\n"
        f"📝 *Descrição:* {descricao}\n"
        f"💰 *Valor:* {formatar_valor(valor)}\n"
        f"{emoji} *Categoria:* {categoria}\n"
        f"🔖 *ID:* #{transacao_id}\n\n"
        f"_Para remover, envie:_ `/remover {transacao_id}`"
    )


def formatar_resumo_mes(resumo: dict) -> str:
    """Formata o resumo mensal em uma mensagem bonita."""
    meses_pt = {
        "01": "Janeiro", "02": "Fevereiro", "03": "Março",
        "04": "Abril", "05": "Maio", "06": "Junho",
        "07": "Julho", "08": "Agosto", "09": "Setembro",
        "10": "Outubro", "11": "Novembro", "12": "Dezembro",
    }
    mes_num = resumo["mes"].split("-")[1]
    ano = resumo["mes"].split("-")[0]
    mes_nome = meses_pt.get(mes_num, resumo["mes"])

    saldo_emoji = "🟢" if resumo["saldo"] >= 0 else "🔴"

    texto = (
        f"📊 *Resumo de {mes_nome}/{ano}*\n"
        f"{'━' * 28}\n\n"
        f"🟢 Receitas: {formatar_valor(resumo['total_receitas'])}\n"
        f"🔴 Gastos: {formatar_valor(resumo['total_gastos'])}\n"
        f"{saldo_emoji} Saldo: {formatar_valor(resumo['saldo'])}\n"
        f"📋 Transações: {resumo['qtd_transacoes']}\n\n"
    )

    if resumo["gastos_por_categoria"]:
        texto += f"*Gastos por Categoria:*\n{'─' * 28}\n"
        for g in resumo["gastos_por_categoria"]:
            emoji = obter_emoji_categoria(g["categoria"])
            percentual = (
                (g["total"] / resumo["total_gastos"] * 100)
                if resumo["total_gastos"] > 0
                else 0
            )
            barra = "█" * int(percentual / 5) + "░" * (20 - int(percentual / 5))
            texto += (
                f"\n{emoji} *{g['categoria']}*\n"
                f"   {formatar_valor(g['total'])} ({percentual:.1f}%)\n"
                f"   {barra}\n"
            )

    return texto


def formatar_resumo_semana(resumo: dict) -> str:
    """Formata o resumo semanal."""
    saldo_emoji = "🟢" if resumo["saldo"] >= 0 else "🔴"

    texto = (
        f"📅 *Resumo da Semana*\n"
        f"{'━' * 28}\n"
        f"📆 {resumo['inicio']} a {resumo['fim']}\n\n"
        f"🟢 Receitas: {formatar_valor(resumo['total_receitas'])}\n"
        f"🔴 Gastos: {formatar_valor(resumo['total_gastos'])}\n"
        f"{saldo_emoji} Saldo: {formatar_valor(resumo['saldo'])}\n\n"
    )

    if resumo["gastos_por_categoria"]:
        texto += f"*Gastos por Categoria:*\n{'─' * 28}\n"
        for g in resumo["gastos_por_categoria"]:
            emoji = obter_emoji_categoria(g["categoria"])
            texto += f"{emoji} {g['categoria']}: {formatar_valor(g['total'])}\n"

    return texto


def formatar_resumo_hoje(resumo: dict) -> str:
    """Formata o resumo do dia."""
    texto = (
        f"📅 *Resumo de Hoje* ({resumo['data']})\n"
        f"{'━' * 28}\n\n"
        f"🔴 Total gasto: {formatar_valor(resumo['total_gastos'])}\n\n"
    )

    if resumo["transacoes"]:
        texto += f"*Transações:*\n{'─' * 28}\n"
        for t in resumo["transacoes"]:
            emoji = obter_emoji_categoria(t["categoria"])
            texto += f"{emoji} {t['descricao']} — {formatar_valor(t['valor'])} (#{t['id']})\n"
    else:
        texto += "_Nenhum gasto registrado hoje._\n"

    return texto


def formatar_ultimas_transacoes(transacoes: list) -> str:
    """Formata a lista de últimas transações."""
    if not transacoes:
        return "📋 _Nenhuma transação encontrada._"

    texto = f"📋 *Últimas Transações*\n{'━' * 28}\n\n"

    for t in transacoes:
        tipo_emoji = "🔴" if t["tipo"] == "gasto" else "🟢"
        cat_emoji = obter_emoji_categoria(t.get("categoria", "Outros"))
        texto += (
            f"{tipo_emoji} *{t['descricao']}*\n"
            f"   {formatar_valor(t['valor'])} | {cat_emoji} {t.get('categoria', 'Outros')} | {t['data']} | #{t['id']}\n\n"
        )

    return texto


def formatar_orcamento(orcamentos: list) -> str:
    """Formata a lista de orçamentos."""
    if not orcamentos:
        return (
            "💰 _Nenhum orçamento definido._\n\n"
            "Para definir, use:\n"
            "`/orcamento Alimentação 500`"
        )

    texto = f"💰 *Orçamentos do Mês*\n{'━' * 28}\n\n"

    for o in orcamentos:
        emoji = obter_emoji_categoria(o["categoria"])
        percentual = o["percentual"]

        if percentual >= 100:
            status = "🚨 ESTOURADO"
            barra_cor = "🟥"
        elif percentual >= 80:
            status = "⚠️ ATENÇÃO"
            barra_cor = "🟨"
        else:
            status = "✅ OK"
            barra_cor = "🟩"

        blocos = int(percentual / 5)
        if blocos > 20:
            blocos = 20
        barra = "█" * blocos + "░" * (20 - blocos)

        texto += (
            f"{emoji} *{o['categoria']}* {status}\n"
            f"   Gasto: {formatar_valor(o['gasto'])} / {formatar_valor(o['limite'])}\n"
            f"   Restante: {formatar_valor(o['restante'])}\n"
            f"   {barra} {percentual:.0f}%\n\n"
        )

    return texto


def formatar_ajuda() -> str:
    """Retorna a mensagem de ajuda com todos os comandos disponíveis."""
    return (
        "🤖 *Assistente Financeiro — Ajuda*\n"
        f"{'━' * 28}\n\n"
        "*Registrar Gastos:*\n"
        "Basta enviar uma mensagem no formato:\n"
        "`Descrição Valor`\n"
        "Exemplos:\n"
        "• `Almoço 35`\n"
        "• `Uber 18.50`\n"
        "• `Mercado 250`\n\n"
        "*Registrar Receitas:*\n"
        "`/receita Salário 5000`\n"
        "`/receita Freelance 800`\n\n"
        "*Consultas:*\n"
        "📊 /resumo — Resumo do mês atual\n"
        "📅 /semana — Resumo da semana\n"
        "📅 /hoje — Resumo de hoje\n"
        "📋 /historico — Últimas transações\n"
        "📈 /grafico — Gráfico de gastos por categoria\n\n"
        "*Orçamento:*\n"
        "💰 /orcamento — Ver orçamentos\n"
        "💰 `/orcamento Alimentação 500` — Definir limite\n\n"
        "*Outros:*\n"
        "🗑 `/remover 123` — Remover transação\n"
        "📂 /categorias — Ver categorias\n"
        "📤 /exportar — Exportar CSV do mês\n"
        "❓ /ajuda — Esta mensagem\n"
    )
