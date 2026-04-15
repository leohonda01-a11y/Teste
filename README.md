# Assistente Financeiro Telegram 💰🤖

Um bot completo para Telegram que ajuda você a gerenciar suas finanças pessoais de forma rápida, simples e automática.

Este projeto foi desenvolvido em Python utilizando a biblioteca `python-telegram-bot` e SQLite para armazenamento local.

## 🌟 Funcionalidades

O Assistente Financeiro foi desenhado para ser o mais prático possível:

- **Registro Rápido:** Envie apenas `Almoço 35` e o bot registra o gasto automaticamente.
- **Categorização Inteligente:** Identifica a categoria do gasto baseado em palavras-chave na descrição (ex: "Uber" vai para Transporte, "Mercado" vai para Alimentação/Mercado).
- **Controle de Orçamento:** Defina limites de gastos mensais por categoria e receba alertas quando estiver perto de estourar.
- **Resumos e Relatórios:** Consulte seus gastos do dia, da semana ou do mês.
- **Gráficos Visuais:** Gere gráficos de pizza para ver onde seu dinheiro está indo.
- **Exportação:** Exporte todas as suas transações do mês para um arquivo CSV (compatível com Excel/Google Sheets).

## 🚀 Como Começar

### 1. Criar o Bot no Telegram

Antes de rodar o código, você precisa criar um bot no Telegram e obter um Token:

1. Abra o Telegram e pesquise por **@BotFather**.
2. Envie o comando `/newbot`.
3. Siga as instruções para dar um nome e um *username* ao seu bot.
4. O BotFather fornecerá um **Token de Acesso** (uma string longa de letras e números). Guarde-o com segurança.

### 2. Rodar no seu Computador (Local)

Para rodar o bot no seu próprio computador, siga os passos abaixo:

**Pré-requisitos:**
- Python 3.10 ou superior
- Pip (gerenciador de pacotes do Python)

**Instalação:**

1. Clone ou baixe este repositório.
2. Abra o terminal na pasta do projeto.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o Token do seu bot:
   - Crie uma cópia do arquivo `.env.exemplo` e renomeie para `.env`.
   - Como alternativa, você pode definir a variável de ambiente diretamente no terminal:
     ```bash
     # Linux/macOS
     export TELEGRAM_BOT_TOKEN="seu_token_aqui"
     
     # Windows (PowerShell)
     set TELEGRAM_BOT_TOKEN="seu_token_aqui"
     ```
5. Inicie o bot:
   ```bash
   python bot.py
   ```
6. O terminal mostrará "✅ Bot iniciado com sucesso!". Agora é só ir no Telegram e mandar um `/start` para o seu bot.

### 3. Hospedar na Nuvem (Gratuito)

Se você não quer deixar seu computador ligado 24h, pode hospedar o bot gratuitamente na nuvem.

**Opção Recomendada: Render.com**

1. Crie uma conta gratuita em [Render.com](https://render.com).
2. Suba o código deste projeto para um repositório no seu GitHub.
3. No painel do Render, clique em **New** > **Web Service** (ou Background Worker).
4. Conecte seu repositório do GitHub.
5. Configurações:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. Na seção **Environment Variables**, adicione:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: `seu_token_aqui`
7. Clique em **Create** e aguarde o deploy finalizar.

*Nota sobre o SQLite no Render:* O plano gratuito do Render apaga os arquivos locais a cada novo deploy. Para um uso real na nuvem, recomenda-se alterar o banco de dados para PostgreSQL (o Render oferece um banco de dados PostgreSQL gratuito).

## 📱 Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot e registra o usuário |
| `/ajuda` | Mostra a lista completa de comandos |
| `/resumo` | Mostra o resumo financeiro do mês atual |
| `/semana` | Mostra o resumo financeiro da semana |
| `/hoje` | Mostra o resumo financeiro de hoje |
| `/historico` | Lista as últimas transações registradas |
| `/receita` | Registra uma nova receita (ex: `/receita Salário 5000`) |
| `/remover` | Remove uma transação pelo ID (ex: `/remover 123`) |
| `/categorias` | Lista todas as categorias disponíveis |
| `/orcamento` | Visualiza ou define orçamentos (ex: `/orcamento Alimentação 500`) |
| `/grafico` | Gera um gráfico visual dos gastos do mês |
| `/exportar` | Exporta as transações do mês para CSV |

## 🛠️ Estrutura do Projeto

- `bot.py`: Arquivo principal, contém os *handlers* do Telegram e a lógica do bot.
- `database.py`: Funções para interagir com o banco de dados SQLite.
- `categorias.py`: Lógica de categorização automática usando palavras-chave.
- `formatacao.py`: Funções para formatar os textos e mensagens que o bot envia.
- `graficos.py`: Geração de gráficos visuais usando a biblioteca Matplotlib.
- `requirements.txt`: Lista de dependências do Python.

## 📝 Licença

Este projeto é de código aberto e pode ser modificado e distribuído livremente.
