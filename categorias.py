"""
Módulo de categorização automática de gastos.
Usa palavras-chave para identificar a categoria de uma transação.
"""

# Mapeamento de palavras-chave para categorias
PALAVRAS_CHAVE = {
    "Alimentação": [
        "almoço", "almoco", "janta", "jantar", "café", "cafe", "lanche",
        "restaurante", "pizza", "hamburguer", "hamburger", "sushi",
        "ifood", "rappi", "uber eats", "delivery", "comida", "padaria",
        "açaí", "acai", "sorvete", "doceria", "pastel", "coxinha",
        "marmita", "marmitex", "bar", "cerveja", "churrasco", "salgado",
        "bolo", "pão", "pao", "biscoito", "chocolate", "doce",
    ],
    "Transporte": [
        "uber", "99", "taxi", "táxi", "gasolina", "combustível",
        "combustivel", "estacionamento", "pedágio", "pedagio",
        "ônibus", "onibus", "metrô", "metro", "trem", "passagem",
        "bilhete", "recarga transporte", "ipva", "seguro carro",
        "manutenção carro", "oficina", "pneu", "óleo", "oleo",
        "lavagem", "moto", "bike",
    ],
    "Moradia": [
        "aluguel", "condomínio", "condominio", "iptu", "reforma",
        "móvel", "movel", "decoração", "decoracao", "mudança",
        "mudanca", "imobiliária", "imobiliaria", "seguro casa",
    ],
    "Saúde": [
        "farmácia", "farmacia", "remédio", "remedio", "médico",
        "medico", "consulta", "exame", "hospital", "dentista",
        "plano de saúde", "plano saude", "academia", "suplemento",
        "vitamina", "psicólogo", "psicologo", "terapia", "vacina",
        "óculos", "oculos", "lente",
    ],
    "Educação": [
        "curso", "livro", "faculdade", "escola", "mensalidade",
        "material escolar", "caderno", "apostila", "udemy",
        "alura", "rocketseat", "inglês", "ingles", "aula",
        "treinamento", "workshop", "certificação", "certificacao",
    ],
    "Lazer": [
        "cinema", "teatro", "show", "ingresso", "viagem",
        "hotel", "airbnb", "passeio", "parque", "praia",
        "festa", "balada", "boate", "karaoke", "jogo",
        "game", "netflix", "spotify", "disney", "hbo",
        "amazon prime", "streaming", "presente",
    ],
    "Roupas": [
        "roupa", "camisa", "camiseta", "calça", "calca",
        "sapato", "tênis", "tenis", "vestido", "saia",
        "bermuda", "short", "jaqueta", "casaco", "meia",
        "cueca", "calcinha", "sutiã", "sutia", "chinelo",
        "sandália", "sandalia", "bolsa", "acessório", "acessorio",
        "relógio", "relogio", "anel", "brinco", "colar",
    ],
    "Mercado": [
        "mercado", "supermercado", "feira", "hortifruti",
        "açougue", "acougue", "peixaria", "atacadão", "atacadao",
        "atacado", "compras", "mantimentos", "arroz", "feijão",
        "feijao", "carne", "fruta", "verdura", "legume",
        "leite", "ovo", "ovos",
    ],
    "Contas": [
        "luz", "energia", "água", "agua", "gás", "gas",
        "internet", "telefone", "celular", "conta", "boleto",
        "fatura", "cartão", "cartao", "parcela", "prestação",
        "prestacao", "imposto", "taxa",
    ],
    "Assinaturas": [
        "assinatura", "mensalidade", "plano", "premium",
        "pro", "plus", "anual", "trimestral",
        "chatgpt", "openai", "github", "icloud", "google one",
    ],
    "Presentes": [
        "Presente", "Presentes",
    ],
}


def categorizar(descricao: str) -> str:
    """
    Tenta categorizar automaticamente uma transação com base na descrição.
    Retorna o nome da categoria ou 'Outros' se não encontrar correspondência.
    """
    descricao_lower = descricao.lower().strip()

    for categoria, palavras in PALAVRAS_CHAVE.items():
        for palavra in palavras:
            if palavra in descricao_lower:
                return categoria

    return "Outros"


def obter_emoji_categoria(categoria: str) -> str:
    """Retorna o emoji correspondente a uma categoria."""
    emojis = {
        "Alimentação": "🍔",
        "Transporte": "🚗",
        "Moradia": "🏠",
        "Saúde": "💊",
        "Educação": "📚",
        "Lazer": "🎮",
        "Roupas": "👕",
        "Mercado": "🛒",
        "Contas": "💡",
        "Assinaturas": "📱",
        "Presentes": "🎁",
        "Outros": "📦",
    }
    return emojis.get(categoria, "📦")


def listar_categorias_disponiveis() -> list:
    """Retorna a lista de categorias disponíveis com seus emojis."""
    return [
        (cat, obter_emoji_categoria(cat))
        for cat in PALAVRAS_CHAVE.keys()
    ] + [("Outros", "📦")]
