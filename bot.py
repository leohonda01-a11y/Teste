"""
Assistente Financeiro Telegram
Bot para gerenciar finanças pessoais via Telegram.

Uso: python3 bot.py
"""

import os
import re
import logging
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from database import (
    init_db,
    registrar_usuario,
    adicionar_categoria_padrao,
    adicionar_transacao,
    remover_transacao,
    obter_ultimas_transacoes,
    resumo_mes,
    resumo_semana,
    resumo_hoje,
    listar_categorias,
    definir_orcamento,
    verificar_orcamento,
    listar_orcamentos,
    exportar_transacoes_csv,
)
from categorias import categorizar, obter_emoji_categoria, listar_categorias_disponiveis
from formatacao import (
    formatar_transacao_registrada,
    formatar_resumo_mes,
    formatar_resumo_semana,
    formatar_resumo_hoje,
    formatar_ultimas_transacoes,
    formatar_orcamento,
    formatar_ajuda,
    formatar_valor,
)
from graficos import grafico_pizza_categorias

# ─── Configuração ────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Token do bot — defina via variável de ambiente
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not BOT_TOKEN:
    print("=" * 50)
    print("ERRO: Token do bot não configurado!")
    print("")
    print("Configure o token de uma das formas:")
    print("  1. Variável de ambiente:")
    print("     export TELEGRAM_BOT_TOKEN='seu_token_aqui'")
    print("")
    print("  2. Edite este arquivo e coloque o token diretamente:")
    print("     BOT_TOKEN = 'seu_token_aqui'")
    print("=" * 50)
    exit(1)


# ─── Funções auxiliares ──────────────────────────────────────────────────────

def garantir_usuario(user_id: int, nome: str):
    """Garante que o usuário está registrado no banco."""
    registrar_usuario(user_id, nome)
    adicionar_categoria_padrao(user_id)


def parse_valor(texto: str) -> float | None:
    """
    Extrai um valor numérico de uma string.
    Aceita formatos: 35 | 35.50 | 35,50 | 1.500,00 | 1500.00
    """
    # Remove espaços extras
    texto = texto.strip()

    # Tenta formato brasileiro: 1.500,00 ou 35,50
    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{1,2})", texto)
    if match:
        valor_str = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(valor_str)
        except ValueError:
            pass

    # Tenta formato com ponto decimal: 35.50 ou 1500.00
    match = re.search(r"(\d+\.?\d*)", texto)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    return None


def parse_gasto_mensagem(texto: str) -> tuple | None:
    """
    Extrai descrição e valor de uma mensagem de gasto.
    Formatos aceitos:
      - "Almoço 35"
      - "Uber 18.50"
      - "Mercado 250,00"
      - "35 almoço"
    """
    texto = texto.strip()

    # Formato: "Descrição Valor" (valor no final)
    match = re.match(r"^(.+?)\s+([\d.,]+)$", texto)
    if match:
        descricao = match.group(1).strip()
        valor = parse_valor(match.group(2))
        if valor and valor > 0:
            return descricao, valor

    # Formato: "Valor Descrição" (valor no início)
    match = re.match(r"^([\d.,]+)\s+(.+)$", texto)
    if match:
        valor = parse_valor(match.group(1))
        descricao = match.group(2).strip()
        if valor and valor > 0:
            return descricao, valor

    return None


# ─── Handlers de Comandos ────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    await update.message.reply_text(
        f"Olá, *{user.first_name}*! 👋\n\n"
        f"Eu sou seu *Assistente Financeiro*! 💰\n\n"
        f"Comigo, você pode gerenciar seus gastos de forma simples e rápida.\n\n"
        f"*Como usar:*\n"
        f"Basta me enviar uma mensagem com o gasto:\n"
        f"• `Almoço 35`\n"
        f"• `Uber 18.50`\n"
        f"• `Mercado 250`\n\n"
        f"Eu categorizo automaticamente! 🎯\n\n"
        f"Digite /ajuda para ver todos os comandos.",
        parse_mode="Markdown",
    )


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /ajuda."""
    await update.message.reply_text(formatar_ajuda(), parse_mode="Markdown")


async def cmd_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /resumo — resumo do mês."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    # Verifica se foi passado um mês específico
    mes = None
    if context.args:
        try:
            # Aceita formato MM/YYYY ou YYYY-MM
            arg = context.args[0]
            if "/" in arg:
                parts = arg.split("/")
                mes = f"{parts[1]}-{parts[0].zfill(2)}"
            elif "-" in arg:
                mes = arg
        except (IndexError, ValueError):
            pass

    dados = resumo_mes(user.id, mes)
    texto = formatar_resumo_mes(dados)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /semana — resumo da semana."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    dados = resumo_semana(user.id)
    texto = formatar_resumo_semana(dados)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /hoje — resumo do dia."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    dados = resumo_hoje(user.id)
    texto = formatar_resumo_hoje(dados)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /historico — últimas transações."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    limite = 10
    if context.args:
        try:
            limite = min(int(context.args[0]), 50)
        except ValueError:
            pass

    transacoes = obter_ultimas_transacoes(user.id, limite)
    texto = formatar_ultimas_transacoes(transacoes)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_receita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /receita — registrar receita."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Formato incorreto!\n\n"
            "Use: `/receita Descrição Valor`\n"
            "Exemplo: `/receita Salário 5000`",
            parse_mode="Markdown",
        )
        return

    texto_completo = " ".join(context.args)
    resultado = parse_gasto_mensagem(texto_completo)

    if not resultado:
        await update.message.reply_text(
            "❌ Não consegui entender o valor.\n\n"
            "Use: `/receita Salário 5000`",
            parse_mode="Markdown",
        )
        return

    descricao, valor = resultado
    transacao_id = adicionar_transacao(user.id, "receita", descricao, valor, "Receita")

    await update.message.reply_text(
        formatar_transacao_registrada(descricao, valor, "Receita", "receita", transacao_id),
        parse_mode="Markdown",
    )


async def cmd_remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /remover — remover transação."""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ Informe o ID da transação.\n\n"
            "Use: `/remover 123`\n"
            "Veja os IDs com /historico",
            parse_mode="Markdown",
        )
        return

    try:
        transacao_id = int(context.args[0].replace("#", ""))
    except ValueError:
        await update.message.reply_text("❌ ID inválido. Use um número.", parse_mode="Markdown")
        return

    if remover_transacao(user.id, transacao_id):
        await update.message.reply_text(f"✅ Transação #{transacao_id} removida com sucesso!")
    else:
        await update.message.reply_text(f"❌ Transação #{transacao_id} não encontrada.")


async def cmd_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /categorias — listar categorias."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    cats = listar_categorias_disponiveis()
    texto = "📂 *Categorias Disponíveis*\n\n"
    for nome, emoji in cats:
        texto += f"{emoji} {nome}\n"
    texto += "\n_Os gastos são categorizados automaticamente!_"

    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /orcamento — ver ou definir orçamento."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    if not context.args:
        # Mostrar orçamentos
        orcamentos = listar_orcamentos(user.id)
        texto = formatar_orcamento(orcamentos)
        await update.message.reply_text(texto, parse_mode="Markdown")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Formato incorreto!\n\n"
            "Use: `/orcamento Categoria Valor`\n"
            "Exemplo: `/orcamento Alimentação 500`",
            parse_mode="Markdown",
        )
        return

    categoria = context.args[0]
    valor = parse_valor(context.args[1])

    if not valor:
        await update.message.reply_text("❌ Valor inválido.", parse_mode="Markdown")
        return

    # Verifica se a categoria existe
    cats_disponiveis = [c[0].lower() for c in listar_categorias_disponiveis()]
    categoria_encontrada = None
    for cat_nome in [c[0] for c in listar_categorias_disponiveis()]:
        if cat_nome.lower() == categoria.lower():
            categoria_encontrada = cat_nome
            break

    if not categoria_encontrada:
        await update.message.reply_text(
            f"❌ Categoria '{categoria}' não encontrada.\n"
            "Use /categorias para ver as disponíveis.",
            parse_mode="Markdown",
        )
        return

    definir_orcamento(user.id, categoria_encontrada, valor)
    emoji = obter_emoji_categoria(categoria_encontrada)

    await update.message.reply_text(
        f"✅ Orçamento definido!\n\n"
        f"{emoji} *{categoria_encontrada}*: {formatar_valor(valor)}/mês",
        parse_mode="Markdown",
    )


async def cmd_grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /grafico — gerar gráfico de gastos."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    mes = datetime.now().strftime("%Y-%m")
    if context.args:
        try:
            arg = context.args[0]
            if "/" in arg:
                parts = arg.split("/")
                mes = f"{parts[1]}-{parts[0].zfill(2)}"
            elif "-" in arg:
                mes = arg
        except (IndexError, ValueError):
            pass

    dados = resumo_mes(user.id, mes)

    if not dados["gastos_por_categoria"]:
        await update.message.reply_text(
            "📊 _Nenhum gasto registrado neste mês para gerar o gráfico._",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text("📊 Gerando gráfico... aguarde!")

    filepath = grafico_pizza_categorias(dados["gastos_por_categoria"], mes, user.id)

    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"📊 Gastos por categoria — {mes}",
            )
        os.remove(filepath)
    else:
        await update.message.reply_text("❌ Erro ao gerar o gráfico.")


async def cmd_exportar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /exportar — exportar transações em CSV."""
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    mes = None
    if context.args:
        try:
            arg = context.args[0]
            if "/" in arg:
                parts = arg.split("/")
                mes = f"{parts[1]}-{parts[0].zfill(2)}"
            elif "-" in arg:
                mes = arg
        except (IndexError, ValueError):
            pass

    filepath = exportar_transacoes_csv(user.id, mes)

    if os.path.exists(filepath):
        with open(filepath, "rb") as doc:
            await update.message.reply_document(
                document=doc,
                filename=os.path.basename(filepath),
                caption="📤 Aqui está sua exportação em CSV!",
            )
        os.remove(filepath)
    else:
        await update.message.reply_text("❌ Erro ao exportar.")


# ─── Handler de Mensagens de Texto (registro de gastos) ─────────────────────

async def mensagem_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para mensagens de texto livres.
    Tenta interpretar como um registro de gasto.
    """
    user = update.effective_user
    garantir_usuario(user.id, user.first_name)

    texto = update.message.text.strip()

    # Ignora mensagens muito curtas ou que parecem comandos
    if len(texto) < 2 or texto.startswith("/"):
        return

    resultado = parse_gasto_mensagem(texto)

    if not resultado:
        await update.message.reply_text(
            "🤔 Não entendi. Para registrar um gasto, envie:\n"
            "`Descrição Valor`\n\n"
            "Exemplo: `Almoço 35`\n\n"
            "Digite /ajuda para ver todos os comandos.",
            parse_mode="Markdown",
        )
        return

    descricao, valor = resultado
    categoria = categorizar(descricao)
    emoji = obter_emoji_categoria(categoria)

    # Cria botões para confirmar ou mudar categoria
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ Confirmar ({emoji} {categoria})",
                callback_data=f"confirmar|{descricao}|{valor}|{categoria}",
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 Mudar Categoria",
                callback_data=f"mudar_cat|{descricao}|{valor}",
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancelar",
                callback_data="cancelar",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"💰 *Registrar gasto?*\n\n"
        f"📝 Descrição: *{descricao}*\n"
        f"💵 Valor: *{formatar_valor(valor)}*\n"
        f"{emoji} Categoria: *{categoria}*",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks de botões inline."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "cancelar":
        await query.edit_message_text("❌ Operação cancelada.")
        return

    if data.startswith("confirmar|"):
        parts = data.split("|")
        descricao = parts[1]
        valor = float(parts[2])
        categoria = parts[3]

        transacao_id = adicionar_transacao(user.id, "gasto", descricao, valor, categoria)

        texto = formatar_transacao_registrada(descricao, valor, categoria, "gasto", transacao_id)

        # Verifica orçamento
        orc = verificar_orcamento(user.id, categoria)
        if orc:
            if orc["percentual"] >= 100:
                texto += f"\n\n🚨 *ALERTA:* Orçamento de {categoria} estourado! ({orc['percentual']:.0f}%)"
            elif orc["percentual"] >= 80:
                texto += f"\n\n⚠️ *Atenção:* Orçamento de {categoria} em {orc['percentual']:.0f}%"

        await query.edit_message_text(texto, parse_mode="Markdown")
        return

    if data.startswith("mudar_cat|"):
        parts = data.split("|")
        descricao = parts[1]
        valor = float(parts[2])

        cats = listar_categorias_disponiveis()
        keyboard = []
        row = []
        for nome, emoji in cats:
            row.append(
                InlineKeyboardButton(
                    f"{emoji} {nome}",
                    callback_data=f"confirmar|{descricao}|{valor}|{nome}",
                )
            )
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📂 *Escolha a categoria:*\n\n"
            f"📝 {descricao} — {formatar_valor(valor)}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return


# ─── Handler de Erros ────────────────────────────────────────────────────────

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler global de erros."""
    logger.error(f"Erro: {context.error}", exc_info=context.error)

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ocorreu um erro inesperado. Tente novamente."
        )


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    """Função principal — inicia o bot."""
    # Inicializa o banco de dados
    init_db()
    logger.info("Banco de dados inicializado.")

    # Cria a aplicação
    app = Application.builder().token(BOT_TOKEN).build()

    # Registra handlers de comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ajuda", cmd_ajuda))
    app.add_handler(CommandHandler("help", cmd_ajuda))
    app.add_handler(CommandHandler("resumo", cmd_resumo))
    app.add_handler(CommandHandler("semana", cmd_semana))
    app.add_handler(CommandHandler("hoje", cmd_hoje))
    app.add_handler(CommandHandler("historico", cmd_historico))
    app.add_handler(CommandHandler("receita", cmd_receita))
    app.add_handler(CommandHandler("remover", cmd_remover))
    app.add_handler(CommandHandler("categorias", cmd_categorias))
    app.add_handler(CommandHandler("orcamento", cmd_orcamento))
    app.add_handler(CommandHandler("grafico", cmd_grafico))
    app.add_handler(CommandHandler("exportar", cmd_exportar))

    # Handler de callbacks (botões)
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Handler de mensagens de texto (registro de gastos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_texto))

    # Handler de erros
    app.add_error_handler(error_handler)

    # Inicia o bot
    logger.info("Bot iniciado! Aguardando mensagens...")
    print("✅ Bot iniciado com sucesso!")
    print("Pressione Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
