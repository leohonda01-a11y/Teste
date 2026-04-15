"""
Módulo de banco de dados para o Assistente Financeiro Telegram.
Usa SQLite para armazenar transações, categorias e orçamentos.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financeiro.db")


def get_connection():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            nome TEXT,
            criado_em TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            emoji TEXT DEFAULT '📦',
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id),
            UNIQUE(user_id, nome)
        );

        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'receita')),
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data TEXT DEFAULT (date('now', 'localtime')),
            criado_em TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id)
        );

        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            categoria TEXT,
            valor_limite REAL NOT NULL,
            mes TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usuarios(user_id),
            UNIQUE(user_id, categoria, mes)
        );

        CREATE INDEX IF NOT EXISTS idx_transacoes_user ON transacoes(user_id);
        CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
        CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo);
    """)

    conn.commit()
    conn.close()


def registrar_usuario(user_id: int, nome: str):
    """Registra um novo usuário ou atualiza o nome."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO usuarios (user_id, nome) VALUES (?, ?)",
        (user_id, nome),
    )
    conn.commit()
    conn.close()


def adicionar_categoria_padrao(user_id: int):
    """Adiciona categorias padrão para um novo usuário."""
    categorias_padrao = [
        ("Alimentação", "🍔"),
        ("Transporte", "🚗"),
        ("Moradia", "🏠"),
        ("Saúde", "💊"),
        ("Educação", "📚"),
        ("Lazer", "🎮"),
        ("Roupas", "👕"),
        ("Mercado", "🛒"),
        ("Contas", "💡"),
        ("Assinaturas", "📱"),
        ("Outros", "📦"),
    ]
    conn = get_connection()
    for nome, emoji in categorias_padrao:
        conn.execute(
            "INSERT OR IGNORE INTO categorias (user_id, nome, emoji) VALUES (?, ?, ?)",
            (user_id, nome, emoji),
        )
    conn.commit()
    conn.close()


def listar_categorias(user_id: int) -> list:
    """Lista todas as categorias de um usuário."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT nome, emoji FROM categorias WHERE user_id = ? ORDER BY nome",
        (user_id,),
    ).fetchall()
    conn.close()
    return [(r["nome"], r["emoji"]) for r in rows]


def adicionar_transacao(
    user_id: int,
    tipo: str,
    descricao: str,
    valor: float,
    categoria: str = "Outros",
    data: Optional[str] = None,
) -> int:
    """Adiciona uma nova transação (gasto ou receita)."""
    conn = get_connection()
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.execute(
        "INSERT INTO transacoes (user_id, tipo, descricao, valor, categoria, data) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, tipo, descricao, valor, categoria, data),
    )
    transacao_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transacao_id


def remover_transacao(user_id: int, transacao_id: int) -> bool:
    """Remove uma transação pelo ID."""
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM transacoes WHERE id = ? AND user_id = ?",
        (transacao_id, user_id),
    )
    removido = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return removido


def obter_ultimas_transacoes(user_id: int, limite: int = 10) -> list:
    """Retorna as últimas transações de um usuário."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, tipo, descricao, valor, categoria, data
           FROM transacoes WHERE user_id = ?
           ORDER BY criado_em DESC LIMIT ?""",
        (user_id, limite),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resumo_mes(user_id: int, mes: Optional[str] = None) -> dict:
    """
    Retorna o resumo financeiro de um mês.
    mes no formato 'YYYY-MM'. Se None, usa o mês atual.
    """
    if mes is None:
        mes = datetime.now().strftime("%Y-%m")

    conn = get_connection()

    # Total de gastos
    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND strftime('%Y-%m', data) = ?""",
        (user_id, mes),
    ).fetchone()
    total_gastos = row["total"]

    # Total de receitas
    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'receita' AND strftime('%Y-%m', data) = ?""",
        (user_id, mes),
    ).fetchone()
    total_receitas = row["total"]

    # Gastos por categoria
    rows = conn.execute(
        """SELECT categoria, SUM(valor) as total, COUNT(*) as qtd
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND strftime('%Y-%m', data) = ?
           GROUP BY categoria ORDER BY total DESC""",
        (user_id, mes),
    ).fetchall()
    gastos_por_categoria = [
        {"categoria": r["categoria"], "total": r["total"], "qtd": r["qtd"]}
        for r in rows
    ]

    # Quantidade de transações
    row = conn.execute(
        """SELECT COUNT(*) as qtd FROM transacoes
           WHERE user_id = ? AND strftime('%Y-%m', data) = ?""",
        (user_id, mes),
    ).fetchone()
    qtd_transacoes = row["qtd"]

    conn.close()

    return {
        "mes": mes,
        "total_gastos": total_gastos,
        "total_receitas": total_receitas,
        "saldo": total_receitas - total_gastos,
        "gastos_por_categoria": gastos_por_categoria,
        "qtd_transacoes": qtd_transacoes,
    }


def resumo_semana(user_id: int) -> dict:
    """Retorna o resumo financeiro da semana atual."""
    hoje = datetime.now()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
    fim_semana = (hoje + timedelta(days=6 - hoje.weekday())).strftime("%Y-%m-%d")

    conn = get_connection()

    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND data BETWEEN ? AND ?""",
        (user_id, inicio_semana, fim_semana),
    ).fetchone()
    total_gastos = row["total"]

    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'receita' AND data BETWEEN ? AND ?""",
        (user_id, inicio_semana, fim_semana),
    ).fetchone()
    total_receitas = row["total"]

    rows = conn.execute(
        """SELECT categoria, SUM(valor) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND data BETWEEN ? AND ?
           GROUP BY categoria ORDER BY total DESC""",
        (user_id, inicio_semana, fim_semana),
    ).fetchall()
    gastos_por_categoria = [
        {"categoria": r["categoria"], "total": r["total"]} for r in rows
    ]

    conn.close()

    return {
        "inicio": inicio_semana,
        "fim": fim_semana,
        "total_gastos": total_gastos,
        "total_receitas": total_receitas,
        "saldo": total_receitas - total_gastos,
        "gastos_por_categoria": gastos_por_categoria,
    }


def resumo_hoje(user_id: int) -> dict:
    """Retorna o resumo financeiro do dia atual."""
    hoje = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()

    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND data = ?""",
        (user_id, hoje),
    ).fetchone()
    total_gastos = row["total"]

    rows = conn.execute(
        """SELECT id, descricao, valor, categoria
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND data = ?
           ORDER BY criado_em DESC""",
        (user_id, hoje),
    ).fetchall()
    transacoes = [dict(r) for r in rows]

    conn.close()

    return {
        "data": hoje,
        "total_gastos": total_gastos,
        "transacoes": transacoes,
    }


def definir_orcamento(user_id: int, categoria: str, valor: float, mes: Optional[str] = None):
    """Define um orçamento mensal para uma categoria."""
    if mes is None:
        mes = datetime.now().strftime("%Y-%m")
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO orcamentos (user_id, categoria, valor_limite, mes)
           VALUES (?, ?, ?, ?)""",
        (user_id, categoria, valor, mes),
    )
    conn.commit()
    conn.close()


def verificar_orcamento(user_id: int, categoria: str) -> Optional[dict]:
    """Verifica o status do orçamento para uma categoria no mês atual."""
    mes = datetime.now().strftime("%Y-%m")
    conn = get_connection()

    orc = conn.execute(
        "SELECT valor_limite FROM orcamentos WHERE user_id = ? AND categoria = ? AND mes = ?",
        (user_id, categoria, mes),
    ).fetchone()

    if not orc:
        conn.close()
        return None

    row = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as gasto
           FROM transacoes
           WHERE user_id = ? AND tipo = 'gasto' AND categoria = ? AND strftime('%Y-%m', data) = ?""",
        (user_id, categoria, mes),
    ).fetchone()

    conn.close()

    limite = orc["valor_limite"]
    gasto = row["gasto"]

    return {
        "categoria": categoria,
        "limite": limite,
        "gasto": gasto,
        "restante": limite - gasto,
        "percentual": (gasto / limite * 100) if limite > 0 else 0,
    }


def listar_orcamentos(user_id: int, mes: Optional[str] = None) -> list:
    """Lista todos os orçamentos de um usuário para um mês."""
    if mes is None:
        mes = datetime.now().strftime("%Y-%m")
    conn = get_connection()
    rows = conn.execute(
        "SELECT categoria, valor_limite FROM orcamentos WHERE user_id = ? AND mes = ?",
        (user_id, mes),
    ).fetchall()
    conn.close()

    resultados = []
    for r in rows:
        info = verificar_orcamento(user_id, r["categoria"])
        if info:
            resultados.append(info)
    return resultados


def exportar_transacoes_csv(user_id: int, mes: Optional[str] = None) -> str:
    """Exporta transações para CSV e retorna o caminho do arquivo."""
    import csv

    if mes is None:
        mes = datetime.now().strftime("%Y-%m")

    conn = get_connection()
    rows = conn.execute(
        """SELECT data, tipo, descricao, valor, categoria
           FROM transacoes
           WHERE user_id = ? AND strftime('%Y-%m', data) = ?
           ORDER BY data""",
        (user_id, mes),
    ).fetchall()
    conn.close()

    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"exportacao_{user_id}_{mes}.csv",
    )

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Tipo", "Descrição", "Valor (R$)", "Categoria"])
        for r in rows:
            writer.writerow([r["data"], r["tipo"], r["descricao"], f"{r['valor']:.2f}", r["categoria"]])

    return filepath
