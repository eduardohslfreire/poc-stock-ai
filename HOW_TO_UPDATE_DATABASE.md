# 🔄 Como Atualizar o Banco de Dados

**Objetivo:** Regenerar o banco com os novos cenários adicionados (20 cenários de teste)

---

## ⚡ Método Rápido (Recomendado)

### Passo 1: Ativar ambiente virtual (se ainda não estiver)

```bash
cd /Users/efreire/poc-projects/poc-stock

# Se o venv não estiver ativo:
source venv/bin/activate  # Mac/Linux
# ou
venv\Scripts\activate     # Windows
```

### Passo 2: Executar o script de regeneração

```bash
python reseed_with_risk_scenarios.py
```

**O que vai acontecer:**
1. ⚠️ Pedirá confirmação (vai deletar dados existentes)
2. Digite: `yes`
3. 🗑️ Dropa banco de dados atual
4. 🏗️ Cria banco novo com schema
5. 📦 Gera produtos, fornecedores, compras, vendas
6. 🎯 **Adiciona 20 cenários especiais:**
   - 6 produtos sem pedido (CRITICAL)
   - 4 produtos com pedido insuficiente (HIGH)
   - 3 produtos com pedido atrasado (HIGH)
   - 2 produtos com pedido OK (LOW)
   - 5 produtos com problema operacional (CRITICAL)
7. ✅ Mostra resumo

**Tempo estimado:** 10-30 segundos

---

## 🔧 Método Alternativo (Se o primeiro não funcionar)

### Opção A: Executar seed diretamente

```bash
cd /Users/efreire/poc-projects/poc-stock
python database/seed_data.py
```

### Opção B: Usar o script setup

```bash
python setup_db.py
```

---

## 🧪 Como Validar que Funcionou

### Teste 1: Verificar cenários criados

```bash
python test_risk_scenarios.py
```

**Resultado esperado:**
```
📊 Found 15 products at risk
🔴 CRITICAL RISK: 6 products
🟠 HIGH RISK: 7 products
✅ ALL TESTS COMPLETED
```

### Teste 2: Testar tool diretamente

```bash
python -c "
from tools.stockout_risk import detect_imminent_stockout_risk
from tools.operational_availability import detect_operational_availability_issues

risk = detect_imminent_stockout_risk()
operational = detect_operational_availability_issues()

print(f'✅ Produtos em risco: {len(risk)}')
print(f'✅ Problemas operacionais: {len(operational)}')
"
```

---

## 📊 O Que Será Criado

### Cenários de Risco de Ruptura (15 produtos):

```
Scenario 4A: SEM Pedido de Compra
  • 6 produtos
  • Estoque: 8-25 unidades
  • Demanda: 5-10 un/dia
  • Pedidos: NENHUM
  • Vai zerar em: 2-5 dias

Scenario 4B: Pedido Insuficiente
  • 4 produtos
  • Estoque: 5-15 unidades
  • Demanda: 4-8 un/dia
  • Pedidos: 40-60 unidades (INSUFICIENTE)
  • Gap: 60-180 unidades

Scenario 4C: Pedido Atrasado
  • 3 produtos
  • Estoque: 10-20 unidades
  • Demanda: 3-6 un/dia
  • Pedidos: 80-120 unidades (10-15 dias ATRASADO)

Scenario 4D: Pedido OK
  • 2 produtos
  • Estoque: 15-30 unidades
  • Demanda: 3-5 un/dia
  • Pedidos: 120-180 unidades (SUFICIENTE)
```

### Cenários Operacionais (5 produtos):

```
Scenario 5: Problema Operacional
  • 5 produtos
  • Estoque: 100-150 unidades (TEM!)
  • Histórico: 4-8 un/dia (BOM)
  • Recentes: 1-2 vendas em 12 dias (PÉSSIMO)
  • Queda: 80-95%
  • Recebido: 12-14 dias atrás
```

---

## ⚠️ Problemas Comuns

### Erro 1: "ModuleNotFoundError: No module named 'faker'"

**Causa:** Dependências não instaladas

**Solução:**
```bash
source venv/bin/activate  # Ativar venv primeiro!
pip install -r requirements.txt
```

### Erro 2: "stock.db: Permission denied"

**Causa:** Arquivo de banco aberto em outro processo

**Solução:**
```bash
# Parar o app se estiver rodando
# Ctrl+C no terminal do streamlit

# Depois executar novamente
python reseed_with_risk_scenarios.py
```

### Erro 3: "stock.csv not found"

**Causa:** Arquivo CSV não existe na raiz

**Solução:**
```bash
# Verificar se arquivo existe
ls -la stock.csv

# Se não existir, o seed vai gerar produtos fake mesmo assim
# Mas é melhor ter o CSV para dados realistas
```

---

## 🎯 Comandos Completos (Copy & Paste)

### Para Mac/Linux:

```bash
# 1. Navegar até o projeto
cd /Users/efreire/poc-projects/poc-stock

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Instalar/atualizar dependências (se necessário)
pip install -r requirements.txt

# 4. Parar app se estiver rodando (Ctrl+C no terminal do streamlit)

# 5. Regenerar banco de dados
python reseed_with_risk_scenarios.py
# Digite: yes

# 6. Validar cenários
python test_risk_scenarios.py

# 7. Reiniciar app
python run_app.py
# ou
streamlit run app/streamlit_app.py
```

### Para Windows:

```cmd
REM 1. Navegar até o projeto
cd C:\Users\...\poc-stock

REM 2. Ativar ambiente virtual
venv\Scripts\activate

REM 3. Instalar dependências
pip install -r requirements.txt

REM 4. Regenerar banco
python reseed_with_risk_scenarios.py

REM 5. Validar
python test_risk_scenarios.py

REM 6. Reiniciar app
python run_app.py
```

---

## 📋 Checklist de Execução

Siga esta ordem:

- [ ] 1. Ativar venv
- [ ] 2. Verificar dependências instaladas
- [ ] 3. Parar aplicação se estiver rodando
- [ ] 4. Executar `python reseed_with_risk_scenarios.py`
- [ ] 5. Confirmar com `yes`
- [ ] 6. Aguardar conclusão (~30 segundos)
- [ ] 7. Executar teste de validação
- [ ] 8. Reiniciar aplicação

---

## ✅ Resultado Esperado

Após executar `python reseed_with_risk_scenarios.py`:

```
======================================================================
🔄 REGENERATING DATABASE WITH RISK SCENARIOS
======================================================================

⚠️  WARNING: This will DELETE all existing data!
======================================================================

Continue? (yes/no): yes

🚀 Starting database regeneration...

============================================================
🎲 Generating Fake Data for Stock Management POC
============================================================

📦 Step 1: Loading products from CSV...
   ✅ Loaded 20 products from stock.csv

📦 Step 2: Generating additional products...
   ✅ Generated 30 additional products

🏢 Step 3: Generating suppliers...
   ✅ Generated 12 suppliers

🛒 Step 4: Generating purchase orders (6 months)...
   ✅ Generated 85 purchase orders

💰 Step 5: Generating sales (6 months)...
   ✅ Generated 650 sales

📊 Step 6: Creating special scenarios...
   🎯 Creating imminent stockout risk scenarios...
      🔴 Produto A: 15 units, ~7 units/day demand, NO PO
      🔴 Produto B: 20 units, ~8 units/day demand, NO PO
      ... (mais 4)
      🟠 Produto C: 10 units, ~5 units/day, PO: 50 units (INSUFFICIENT)
      ... (mais 3)
      ⏰ Produto D: 15 units, ~4 units/day, PO: 100 units (DELAYED 12 days)
      ... (mais 2)
      ✅ Produto E: 25 units, ~4 units/day, PO: 150 units (OK)
      ... (mais 1)
   🏪 Creating operational availability issue scenarios...
      🏪 Produto F: Stock=145, Historical=5 un/day, Recent=2 sales in 12d (expected 60), Lost 58 sales! (Operational issue)
      ... (mais 4)
   ✅ Created special test scenarios (including 20 total scenarios)

✅ Data generation completed!

============================================================
📊 DATA SUMMARY
============================================================
Products: 50
Suppliers: 12
Purchase Orders: 93
Sales: 800
Total Stock Value: R$ 1,245,890.00
Period: 2025-08-08 to 2026-02-08
============================================================

======================================================================
✅ DATABASE REGENERATED SUCCESSFULLY!
======================================================================

📊 New Scenarios Created:
----------------------------------------------------------------------
1. 🔴 CRITICAL: 6 products without purchase orders
   ...
5. 🏪 OPERATIONAL: 5 products with operational issues
```

---

## 🚀 Depois de Regenerar

### Teste com o agente:

```bash
streamlit run app/streamlit_app.py
```

**Perguntas para testar os novos cenários:**

```
1. "Quais produtos têm risco de ficar sem estoque?"
   → Deve encontrar os 15 produtos em risco

2. "Me mostre produtos sem pedido de compra"
   → Deve encontrar os 6 produtos sem PO

3. "Há produtos com pedidos insuficientes?"
   → Deve encontrar os 4 produtos

4. "Quais pedidos estão atrasados?"
   → Deve encontrar os 3 pedidos

5. "Produtos com estoque mas não vendendo?"
   → Deve encontrar os 5 problemas operacionais

6. "Como está a situação geral do estoque?"
   → Dashboard com todos os alertas
```

---

## 💡 Dica Extra

Se quiser apenas atualizar sem interação:

```bash
# Passar 'yes' automaticamente
echo "yes" | python reseed_with_risk_scenarios.py
```

---

**Pronto! Execute o comando e o banco será atualizado com todos os novos cenários! 🎉**
