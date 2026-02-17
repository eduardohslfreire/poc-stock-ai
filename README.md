# 🤖 POC - AI Agent for Stock Management

Prova de Conceito de um sistema de gestão de estoque com agente de IA para análise inteligente e suporte à decisão operacional.

## 🎯 Objetivo

Demonstrar como IA pode auxiliar gestores na identificação de problemas, otimização de compras e redução de perdas através de análise conversacional de dados.

## ✨ Funcionalidades

### Casos de Uso do Agente de IA (11 Ferramentas):

#### 📦 Gestão de Estoque
1. **🔴 Detecção de Ruptura** - Produtos zerados com demanda recente
2. **💰 Estoque Parado** - Capital imobilizado em produtos sem giro
3. **⚠️ Problemas de Disponibilidade** - Rupturas recorrentes e taxa de disponibilidade

#### 💵 Análise Financeira
4. **💔 Detecção de Perdas** - Divergências e perdas não registradas
5. **📊 Análise de Lucratividade** - Margens, ROI e rentabilidade por produto

#### 📈 Inteligência de Negócio
6. **🏆 Top Produtos** - Rankings por receita, quantidade ou frequência
7. **🏷️ Classificação ABC** - Curva de Pareto 80/20
8. **⏱️ Análise de Giro** - Tempo médio de permanência no estoque

#### 🤝 Fornecedores & Compras
9. **👥 Performance de Fornecedores** - Ranking por taxa de giro e vendas
10. **🛒 Sugestões de Compra** - Recomendações inteligentes baseadas em demanda

#### 🎯 Dashboard
11. **📊 Alertas Consolidados** - Visão completa da saúde do estoque

## 🛠️ Stack Tecnológica

- **Database:** SQLite (arquivo) - Zero configuração
- **Backend:** Python + SQLAlchemy
- **AI Framework:** LangChain
- **LLM:** OpenAI GPT-4o-mini
- **Frontend:** Streamlit

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- OpenAI API Key

### Instalação

```bash
# 1. Clone o repositório
git clone <repository-url>
cd poc-stock

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# 5. Inicialize o banco de dados
python setup_db.py

# 6. Gere dados de demonstração (6 meses)
python database/seed_data.py

# 7. [Opcional] Verifique os dados gerados
python verify_data.py

# 8. Execute a aplicação (launcher recomendado)
python run_app.py

# Ou execute diretamente:
# streamlit run app/streamlit_app.py
```

A aplicação estará disponível em: `http://localhost:8501`

### 🎬 Primeira Execução

Na primeira vez, o launcher irá verificar:
- ✅ Ambiente virtual ativado
- ✅ Arquivo `.env` configurado
- ✅ `OPENAI_API_KEY` definida
- ✅ Banco de dados inicializado

---

## ☁️ Deploy no Streamlit Community Cloud

Este projeto está pronto para deploy no Streamlit Cloud! 🚀

### ⚡ Quick Deploy (5 minutos)

1. **Push para GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/SEU_USUARIO/poc-stock-ai.git
   git push -u origin main
   ```

2. **Deploy no Streamlit:**
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Conecte seu repositório GitHub
   - Configure sua OpenAI API Key em Settings → Secrets:
     ```toml
     [openai]
     api_key = "sk-proj-..."
     model = "gpt-4o-mini"
     ```
   - Deploy!

3. **Pronto!** O banco será populado automaticamente no primeiro run.

### 📖 Documentação Completa

- **[DEPLOY_STREAMLIT.md](./DEPLOY_STREAMLIT.md)** - Guia completo passo a passo
- **[DEPLOYMENT_CHANGES.md](./DEPLOYMENT_CHANGES.md)** - Resumo dos ajustes feitos

**Características do Deploy:**
- ✅ Auto-populate banco de dados
- ✅ Secrets gerenciados de forma segura
- ✅ Zero configuração adicional
- ✅ Funciona local + cloud com mesmo código

---

### ⚠️ Problemas Conhecidos

Se encontrar **segmentation fault (exit code 139)** ao executar o agente, veja [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para soluções específicas de macOS/Linux.

**Enquanto isso, todas as ferramentas funcionam independentemente:**
```bash
python test_tool_8.py  # Dashboard completo
python test_tools_9_10_11.py  # Análises avançadas
```

## 📁 Estrutura do Projeto

```
poc-stock/
├── database/          # Modelos, conexão e gerador de dados
├── tools/             # Ferramentas do agente (análises)
├── agent/             # Configuração do agente LangChain
├── app/               # Interface Streamlit
├── tests/             # Testes unitários
├── stock.db           # Database SQLite (gerado automaticamente)
└── stock.csv          # Dados de exemplo para seed
```

## 💬 Exemplos de Perguntas

Experimente fazer essas perguntas ao agente:

### 📊 Visão Geral
- "Como está meu estoque hoje?"
- "Me dê um resumo completo da situação"
- "Quais são os problemas mais críticos?"

### 🔴 Problemas e Alertas
- "Quais produtos estão em ruptura?"
- "Mostre produtos com problemas de disponibilidade"
- "Identifique possíveis perdas no estoque"
- "Quais produtos estão parados há muito tempo?"

### 💰 Análise Financeira
- "Analise a lucratividade dos meus produtos"
- "Quanto capital está parado em estoque?"
- "Quais produtos têm melhor margem?"
- "Mostre produtos não lucrativos"

### 📈 Vendas e Performance
- "Quais os 10 produtos mais vendidos?"
- "Classifique meus produtos por ABC"
- "Mostre a curva de Pareto"
- "Analise o giro de estoque"

### 🛒 Compras e Fornecedores
- "O que devo comprar urgente?"
- "Quais fornecedores têm melhor performance?"
- "Sugira um pedido de compra"
- "Agrupe sugestões por fornecedor"

## 📊 Dados de Demonstração

O banco de dados é populado com **6 meses de histórico simulado**:

- 50-100 produtos (baseados em dados reais de varejo)
- 10-15 fornecedores
- 100-150 ordens de compra
- 500-1000 vendas
- ~3000 movimentos de estoque

Padrões realistas incluem:
- Produtos com sazonalidade
- Regra 80/20 (poucos produtos com alto giro)
- Produtos "mortos" (comprados mas não vendidos)
- Rupturas de estoque simuladas
- Perdas ocasionais

## 🔧 Configuração Avançada

### Migração para PostgreSQL

Se precisar migrar para PostgreSQL no futuro:

1. Instale o driver: `pip install psycopg2-binary`
2. Atualize `.env`: `DATABASE_URL=postgresql://user:pass@localhost:5432/stock_db`
3. Execute seed novamente: `python database/seed_data.py`

**Nenhuma mudança de código é necessária!** (SQLAlchemy é agnóstico)

## 📈 Custos

- **POC completa (100 queries):** ~$0.05 USD
- **Uso mensal moderado (1000 queries):** ~$0.50 USD

## 🧪 Testes

```bash
# Executar testes unitários
pytest tests/

# Executar com coverage
pytest --cov=. tests/
```

## 📝 Documentação Completa

Veja [RFC-POC-STOCK-AI-AGENT.md](./RFC-POC-STOCK-AI-AGENT.md) para:
- Especificações técnicas completas
- Detalhamento dos casos de uso
- Queries SQL de cada ferramenta
- Arquitetura do sistema
- Roadmap de implementação

## 🤝 Contribuindo

Esta é uma POC. Contribuições são bem-vindas!

## 📄 Licença

MIT License

## 🙋 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub.

---

**Status:** ✅ POC Completa e Funcional

**Última Atualização:** 2026-01-27

**Features:** 11 ferramentas de análise | Interface conversacional | 6 meses de dados históricos
