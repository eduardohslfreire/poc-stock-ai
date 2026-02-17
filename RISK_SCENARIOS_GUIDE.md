# 🎯 Guia de Cenários de Risco de Ruptura

**Criado:** 2026-02-08  
**Objetivo:** Testar a ferramenta `detect_imminent_stockout_risk()`

---

## 📋 Cenários Adicionados ao Banco de Dados

### Scenario 4A: Produtos SEM Pedido de Compra (CRÍTICO) 🔴

**Quantidade:** 6 produtos

**Características:**
- ✅ Estoque baixo: 8-25 unidades
- ✅ Alta demanda: 5-10 unidades/dia
- ❌ **SEM pedido de compra**
- ⏰ Vai zerar em: 2-5 dias

**Objetivo:**
Testar se o agente detecta corretamente produtos que vão ficar sem estoque e **não têm nenhum pedido de compra** para reposição.

**Ação esperada:**
```
🔴 CRITICAL
Recomendação: "URGENT: Create purchase order for X units immediately"
```

---

### Scenario 4B: Produtos COM Pedido Insuficiente (ALTO RISCO) 🟠

**Quantidade:** 4 produtos

**Características:**
- ✅ Estoque muito baixo: 5-15 unidades
- ✅ Alta demanda: 4-8 unidades/dia
- ⚠️ **Pedido insuficiente** (40-60 unidades)
- ⏰ Demanda 30 dias: 120-240 unidades
- 📊 Gap: 60-180 unidades

**Objetivo:**
Testar se o agente detecta que o pedido de compra existe, mas a **quantidade é insuficiente** para cobrir a demanda.

**Ação esperada:**
```
🟠 HIGH
Recomendação: "ORDER MORE: Pending orders insufficient. Need X additional units"
```

---

### Scenario 4C: Produtos COM Pedido Atrasado (ALTO RISCO) ⏰

**Quantidade:** 3 produtos

**Características:**
- ✅ Estoque baixo: 10-20 unidades
- ✅ Demanda média: 3-6 unidades/dia
- ⏰ **Pedido atrasado** (10-15 dias esperando)
- ✅ Quantidade suficiente (80-120 unidades)
- ⚠️ Status: AINDA PENDING

**Objetivo:**
Testar se o agente detecta pedidos que estão **há muito tempo pendentes** (provavelmente atrasados pelo fornecedor).

**Ação esperada:**
```
🟠 HIGH
Recomendação: "FOLLOW UP: Pending order is X days old. Contact supplier"
```

---

### Scenario 4D: Produtos COM Pedido Suficiente (BAIXO RISCO) ✅

**Quantidade:** 2 produtos

**Características:**
- ✅ Estoque ok: 15-30 unidades
- ✅ Demanda baixa-média: 3-5 unidades/dia
- ✅ **Pedido suficiente** (120-180 unidades)
- ✅ Pedido recente (1-3 dias atrás)
- ✅ Cobre 30+ dias de demanda

**Objetivo:**
Cenário de **controle positivo** - produto que está bem gerenciado para comparação.

**Ação esperada:**
```
🟢 LOW
Recomendação: "MONITOR: Pending orders should cover demand"
```

---

## 🚀 Como Regenerar o Banco de Dados

### Opção 1: Script Automático (Recomendado)

```bash
python reseed_with_risk_scenarios.py
```

**O que faz:**
1. ⚠️ Pergunta confirmação (vai deletar dados existentes)
2. 🗑️ Dropa o banco de dados atual
3. 🏗️ Cria banco novo
4. 📦 Gera produtos, fornecedores, vendas
5. 🎯 **Adiciona 15 produtos em cenários de risco**
6. ✅ Mostra resumo

### Opção 2: Script Manual

```bash
python setup_db.py
```

---

## 🧪 Como Testar os Cenários

### Teste 1: Validação Direta

```bash
python test_risk_scenarios.py
```

**Resultado esperado:**
```
🎯 TESTING IMMINENT STOCKOUT RISK SCENARIOS
📊 Found 15 products at risk

🔴 CRITICAL RISK: 6 products
🟠 HIGH RISK: 7 products
🟡 MEDIUM RISK: 0 products
🟢 LOW RISK: 2 products
```

### Teste 2: Via Agente (Streamlit)

```bash
streamlit run app/streamlit_app.py
```

**Perguntas para testar:**

1. **Teste Cenário 4A (sem PO):**
   ```
   "Quais produtos têm risco de ficar sem estoque?"
   "Me mostre produtos sem pedido de compra que vão zerar"
   ```
   
   Deve retornar: ~6 produtos CRÍTICOS sem pedido

2. **Teste Cenário 4B (PO insuficiente):**
   ```
   "Há produtos com pedidos de compra insuficientes?"
   "Mostre produtos que vão acabar mesmo com pedido pendente"
   ```
   
   Deve retornar: ~4 produtos com pedidos mas gap positivo

3. **Teste Cenário 4C (PO atrasado):**
   ```
   "Quais pedidos de compra estão atrasados?"
   "Me mostre pedidos pendentes há mais de 7 dias"
   ```
   
   Deve retornar: ~3 pedidos atrasados

4. **Teste Dashboard Geral:**
   ```
   "Como está a situação do estoque?"
   "Me dê um resumo dos alertas"
   ```
   
   Deve incluir: Alertas de "IMMINENT_STOCKOUT"

### Teste 3: Via Python Direto

```python
from tools.stockout_risk import detect_imminent_stockout_risk

# Detectar produtos em risco nos próximos 7 dias
at_risk = detect_imminent_stockout_risk(
    days_forecast=30,
    days_history=90,
    min_days_threshold=7
)

print(f"Produtos em risco: {len(at_risk)}")

# Filtrar por nível de risco
critical = [p for p in at_risk if p['risk_level'] == 'CRITICAL']
print(f"CRÍTICOS: {len(critical)}")

# Filtrar por cenário
no_po = [p for p in at_risk if p['pending_orders']['count'] == 0]
print(f"Sem pedido de compra: {len(no_po)}")
```

---

## 📊 Dados Gerados

### Por Cenário:

| Cenário | Produtos | Estoque | Demanda/dia | Pedido PO | Status |
|---------|----------|---------|-------------|-----------|--------|
| **4A** | 6 | 8-25 | 5-10 | ❌ Nenhum | 🔴 CRITICAL |
| **4B** | 4 | 5-15 | 4-8 | ⚠️ 40-60 (insuf.) | 🟠 HIGH |
| **4C** | 3 | 10-20 | 3-6 | ⏰ 80-120 (atrasado) | 🟠 HIGH |
| **4D** | 2 | 15-30 | 3-5 | ✅ 120-180 (OK) | 🟢 LOW |
| **Total** | **15** | - | - | - | - |

### Vendas Simuladas:

Cada produto recebe:
- **10-14 dias** de histórico de vendas
- Vendas **diárias consistentes** (simula demanda real)
- Quantidade por venda: ±2 unidades da média diária

---

## 🎯 Validação Esperada

### Checklist de Teste:

- [ ] ✅ **6 produtos** detectados SEM pedido de compra
- [ ] ✅ **4 produtos** detectados COM pedido insuficiente
- [ ] ✅ **3 produtos** detectados COM pedido atrasado (>7 dias)
- [ ] ✅ **2 produtos** detectados COM pedido suficiente (baixo risco)
- [ ] ✅ Cálculo correto de `days_until_stockout`
- [ ] ✅ Cálculo correto de `gap_quantity`
- [ ] ✅ Detecção de pedidos atrasados (`is_delayed`)
- [ ] ✅ Classificação correta de `risk_level`
- [ ] ✅ Recomendações específicas por cenário

---

## 🐛 Troubleshooting

### Problema: "Found 0 products at risk"

**Possíveis causas:**
1. Banco não foi regenerado com novos cenários
2. Produtos não têm vendas recentes no período

**Solução:**
```bash
python reseed_with_risk_scenarios.py
```

### Problema: "Agente não chama a ferramenta correta"

**Possíveis causas:**
1. Ferramenta não está registrada no agente
2. Descrição da ferramenta não tem palavras-chave certas

**Solução:**
Verificar `agent/stock_agent.py` - deve ter `detect_imminent_stockout_risk` registrado como Tool #1

### Problema: "Pedidos não aparecem como atrasados"

**Possíveis causas:**
1. Threshold de atraso é > 7 dias
2. Pedidos foram criados recentemente

**Verificação:**
```python
from tools.stockout_risk import get_pending_order_summary

pending = get_pending_order_summary()
delayed = [p for p in pending if p['is_delayed']]
print(f"Pedidos atrasados: {len(delayed)}")
```

---

## 📝 Estrutura dos Dados

### Produtos Criados:

```python
Product(
    name="Produto em Risco X",
    current_stock=15,  # Baixo
    # ... outros campos ...
)
```

### Vendas Criadas:

```python
# Para cada produto, 10-14 vendas nos últimos dias
SaleOrder(
    order_number="RISK-NO-PO-0-1-1234",
    sale_date=datetime.now() - timedelta(days=1),
    status='PAID'
)
```

### Pedidos de Compra:

```python
# Cenário 4B: Insuficiente
PurchaseOrder(
    order_number="PO-INSUF-0-5678",
    order_date=datetime.now() - timedelta(days=2),
    status='PENDING',
    # items: 50 unidades (insuficiente para 150 necessárias)
)

# Cenário 4C: Atrasado
PurchaseOrder(
    order_number="PO-DELAY-0-9012",
    order_date=datetime.now() - timedelta(days=12),  # 12 dias atrás!
    status='PENDING',
    # items: 100 unidades (suficiente mas atrasado)
)
```

---

## ✅ Próximos Passos

1. **Regenerar DB:**
   ```bash
   python reseed_with_risk_scenarios.py
   ```

2. **Validar cenários:**
   ```bash
   python test_risk_scenarios.py
   ```

3. **Testar com agente:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

4. **Verificar alertas:**
   - Dashboard deve mostrar alertas de "IMMINENT_STOCKOUT"
   - Produtos críticos devem aparecer primeiro

---

**Cenários prontos para teste! 🎉**
