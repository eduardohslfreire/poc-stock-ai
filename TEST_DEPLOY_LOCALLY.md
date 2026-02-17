# 🧪 Testar Deploy Localmente

Antes de fazer deploy no Streamlit Cloud, teste localmente com a mesma configuração.

---

## 🎯 Objetivo

Simular o ambiente do Streamlit Cloud localmente para:
- ✅ Verificar se auto-seed funciona
- ✅ Testar secrets.toml
- ✅ Garantir compatibilidade

---

## 📋 Pré-requisitos

```bash
# Ambiente virtual ativado
source venv/bin/activate  # Mac/Linux
# ou: venv\Scripts\activate  # Windows

# Dependências instaladas
pip install -r requirements.txt
```

---

## 🔧 Configuração Local

### 1. Criar arquivo de secrets

```bash
# Copiar template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Editar e adicionar sua API key
# Abra .streamlit/secrets.toml e cole:
```

Conteúdo de `.streamlit/secrets.toml`:

```toml
[openai]
api_key = "sk-proj-COLE_SUA_CHAVE_AQUI"
model = "gpt-4o-mini"

[database]
url = "sqlite:///stock.db"
```

**⚠️ IMPORTANTE:**
- Substitua `COLE_SUA_CHAVE_AQUI` pela sua OpenAI API Key real
- Este arquivo **NÃO** será commitado (está no .gitignore)

---

## 🧪 Testes

### Teste 1: Verificar Auto-Seed

```bash
# Remover banco existente (para simular primeiro deploy)
rm -f stock.db

# Testar auto-seed
python -c "
from database.auto_seed import auto_seed_if_needed
result = auto_seed_if_needed(force=False, verbose=True)
print(f'\n✅ Auto-seed concluído: {result}')
"
```

**Resultado esperado:**
```
=================================================================
🌱 AUTO-SEEDING DATABASE
=================================================================

This is the first run. Generating fake data...
This will take ~30 seconds.

[... logs de criação de dados ...]

✅ Database seeded successfully!

✅ Auto-seed concluído: True
```

---

### Teste 2: Verificar Secrets no Streamlit

```bash
# Executar app
streamlit run app/streamlit_app.py
```

**Verificações:**

```
✅ App inicia sem erros
✅ Não pede OPENAI_API_KEY
✅ Sidebar mostra "✅ Agente inicializado"
✅ Sidebar mostra "🤖 Modelo: gpt-4o-mini"
✅ Perguntas de exemplo funcionam
```

---

### Teste 3: Simular Deploy Limpo

Este teste simula o que acontece no Streamlit Cloud no primeiro deploy.

```bash
# 1. Remover banco e cache
rm -f stock.db
rm -rf .streamlit/cache

# 2. Executar app
streamlit run app/streamlit_app.py

# 3. Observar logs no terminal
# Deve aparecer:
# - "🌱 AUTO-SEEDING DATABASE"
# - "✅ Database seeded successfully!"
```

**Tempo esperado:** ~30 segundos na primeira execução

---

### Teste 4: Verificar Dados Gerados

```bash
python -c "
from database.connection import SessionLocal
from database.schema import Product, SaleOrder, PurchaseOrder

session = SessionLocal()

products = session.query(Product).count()
sales = session.query(SaleOrder).count()
purchases = session.query(PurchaseOrder).count()

print(f'\n📊 Dados Gerados:')
print(f'  • Produtos: {products}')
print(f'  • Vendas: {sales}')
print(f'  • Ordens de Compra: {purchases}')

session.close()
"
```

**Resultado esperado:**
```
📊 Dados Gerados:
  • Produtos: ~100
  • Vendas: ~300
  • Ordens de Compra: ~80
```

---

## 🎯 Teste Completo de Funcionalidades

Com o app rodando (`streamlit run app/streamlit_app.py`):

### 1. Teste Básico

**Pergunta:** "Como está meu estoque hoje?"

**Esperado:**
- ✅ Resposta com estatísticas
- ✅ Número de produtos
- ✅ Alertas críticos (se houver)

### 2. Teste de Análise

**Pergunta:** "Quais produtos têm risco de ficar sem estoque?"

**Esperado:**
- ✅ Lista de produtos em risco
- ✅ Dias restantes de estoque
- ✅ Status de pedidos pendentes

### 3. Teste de Sugestão

**Pergunta:** "Quais produtos devo comprar?"

**Esperado:**
- ✅ Lista de sugestões
- ✅ Quantidades recomendadas
- ✅ Prioridades (alta/média/baixa)

### 4. Teste de Dashboard

**Pergunta:** "Mostre um resumo completo"

**Esperado:**
- ✅ Visão geral do estoque
- ✅ Alertas consolidados
- ✅ Métricas principais

---

## ⚠️ Troubleshooting Local

### Erro: "OPENAI_API_KEY not found"

**Causa:** secrets.toml não configurado

**Solução:**
```bash
# Verificar se arquivo existe
ls -la .streamlit/secrets.toml

# Se não existir, criar:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Editar e adicionar API key
```

---

### Erro: "ModuleNotFoundError: No module named 'X'"

**Causa:** Dependências não instaladas ou venv não ativado

**Solução:**
```bash
# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | grep streamlit
pip list | grep langchain
pip list | grep openai
```

---

### Erro: "Database is locked"

**Causa:** Múltiplas instâncias acessando o banco

**Solução:**
```bash
# Parar todos os processos Python
pkill -f streamlit
pkill -f python

# Remover banco e recriar
rm stock.db
python -c "from database.auto_seed import auto_seed_if_needed; auto_seed_if_needed()"
```

---

### Erro: "Invalid API Key"

**Causa:** API Key incorreta ou inválida

**Solução:**
```bash
# 1. Obter nova key: https://platform.openai.com/api-keys
# 2. Atualizar .streamlit/secrets.toml
# 3. Reiniciar app (Ctrl+C e rodar novamente)
```

---

## 🔍 Verificar Configuração

### Script de Diagnóstico

Salve como `check_deploy_ready.py`:

```python
#!/usr/bin/env python3
"""Check if deployment configuration is ready."""

import os
from pathlib import Path

print("\n🔍 Verificando configuração de deploy...\n")

checks = []

# 1. Verificar requirements.txt
req_file = Path("requirements.txt")
checks.append(("requirements.txt existe", req_file.exists()))

# 2. Verificar .streamlit/config.toml
config_file = Path(".streamlit/config.toml")
checks.append((".streamlit/config.toml existe", config_file.exists()))

# 3. Verificar .streamlit/secrets.toml.example
secrets_example = Path(".streamlit/secrets.toml.example")
checks.append((".streamlit/secrets.toml.example existe", secrets_example.exists()))

# 4. Verificar database/auto_seed.py
auto_seed = Path("database/auto_seed.py")
checks.append(("database/auto_seed.py existe", auto_seed.exists()))

# 5. Verificar app/streamlit_app.py
app_file = Path("app/streamlit_app.py")
checks.append(("app/streamlit_app.py existe", app_file.exists()))

# 6. Verificar .gitignore
gitignore = Path(".gitignore")
if gitignore.exists():
    content = gitignore.read_text()
    checks.append((".gitignore ignora secrets.toml", "secrets.toml" in content))
    checks.append((".gitignore ignora .env", ".env" in content))

# 7. Verificar secrets.toml local (opcional)
secrets_local = Path(".streamlit/secrets.toml")
checks.append((".streamlit/secrets.toml configurado (local)", secrets_local.exists()))

# Imprimir resultados
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")

# Resumo
passed = sum(1 for _, result in checks if result)
total = len(checks)

print(f"\n{'='*50}")
print(f"Resultado: {passed}/{total} checks passaram")
print(f"{'='*50}\n")

if passed == total:
    print("🎉 Projeto pronto para deploy!")
else:
    print("⚠️ Alguns itens precisam de atenção.")
    print("Consulte DEPLOY_STREAMLIT.md para mais detalhes.")
```

Execute:

```bash
python check_deploy_ready.py
```

---

## ✅ Checklist de Teste Local

Antes de fazer deploy, confirme:

```
□ secrets.toml configurado localmente
□ Auto-seed testado e funcionando
□ App inicia sem erros
□ Agente responde perguntas
□ Dados fake são gerados
□ Nenhum erro nos logs
□ Performance aceitável
□ .gitignore ignora secrets
```

---

## 🚀 Pronto para Deploy?

Se todos os testes passaram:

1. ✅ **Commit e Push:**
   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud deploy"
   git push origin main
   ```

2. ✅ **Deploy no Streamlit Cloud:**
   - Siga: `QUICK_DEPLOY_GUIDE.md`

---

## 📚 Próximos Passos

Após testes locais bem-sucedidos:

- **Deploy:** Siga `QUICK_DEPLOY_GUIDE.md` ou `DEPLOY_STREAMLIT.md`
- **Monitore:** Acompanhe logs do Streamlit Cloud
- **Compartilhe:** Envie URL para seu time

---

**Boa sorte com os testes! 🧪**
