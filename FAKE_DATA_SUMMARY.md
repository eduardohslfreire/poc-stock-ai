# 📊 Resumo: Dados Fake para Cenários de Risco

**Data:** 2026-02-08  
**Objetivo:** Adicionar dados simulados para testar `detect_imminent_stockout_risk()`

---

## ✅ O Que Foi Feito

### 1. Arquivo Modificado: `database/seed_data.py`

**Localização:** Função `create_special_scenarios()` (linha 371)

**Adição:** Scenario 4 - Imminent Stockout Risk (15 produtos em 4 sub-cenários)

---

## 🎯 Cenários Criados

### Resumo Visual:

```
┌────────────────────────────────────────────────────────────────┐
│  Scenario 4A: SEM Pedido de Compra (6 produtos)              │
├────────────────────────────────────────────────────────────────┤
│  Estoque: 8-25 unidades                                        │
│  Demanda: 5-10 un/dia                                         │
│  Pedidos: ❌ NENHUM                                           │
│  Risco: 🔴 CRITICAL                                           │
│  Dias até ruptura: 2-5 dias                                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  Scenario 4B: Pedido Insuficiente (4 produtos)               │
├────────────────────────────────────────────────────────────────┤
│  Estoque: 5-15 unidades                                        │
│  Demanda: 4-8 un/dia (120-240 em 30 dias)                    │
│  Pedidos: ⚠️ 40-60 unidades (INSUFICIENTE)                   │
│  Risco: 🟠 HIGH                                               │
│  Gap: 60-180 unidades                                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  Scenario 4C: Pedido Atrasado (3 produtos)                   │
├────────────────────────────────────────────────────────────────┤
│  Estoque: 10-20 unidades                                       │
│  Demanda: 3-6 un/dia                                          │
│  Pedidos: ⏰ 80-120 unidades (10-15 dias ATRASADO)           │
│  Risco: 🟠 HIGH                                               │
│  Status: AINDA PENDING                                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  Scenario 4D: Pedido Suficiente (2 produtos)                 │
├────────────────────────────────────────────────────────────────┤
│  Estoque: 15-30 unidades                                       │
│  Demanda: 3-5 un/dia                                          │
│  Pedidos: ✅ 120-180 unidades (OK, recente)                  │
│  Risco: 🟢 LOW                                                │
│  Controle positivo para comparação                            │
└────────────────────────────────────────────────────────────────┘
```

---

## 📦 Dados Gerados por Produto

### Para CADA um dos 15 produtos:

1. **Estoque ajustado** para nível de risco apropriado
2. **Vendas recentes** (10-14 dias):
   - Vendas diárias consistentes
   - Quantidade baseada na demanda configurada
   - Status: PAID (vendas concretizadas)

3. **Pedidos de compra** (conforme cenário):
   - Scenario A: Nenhum pedido
   - Scenario B: Pedido insuficiente (PENDING)
   - Scenario C: Pedido atrasado (PENDING há 10-15 dias)
   - Scenario D: Pedido suficiente e recente (PENDING)

---

## 🔢 Estatísticas

| Métrica | Valor |
|---------|-------|
| **Produtos em risco** | 15 |
| **Vendas geradas** | ~150-200 (10-14 por produto) |
| **Pedidos criados** | 9 (4B: 4 + 4C: 3 + 4D: 2) |
| **Produtos CRITICAL** | 6 |
| **Produtos HIGH** | 7 |
| **Produtos LOW** | 2 |

---

## 🚀 Como Usar

### Passo 1: Regenerar Banco de Dados

```bash
python reseed_with_risk_scenarios.py
```

**Resultado:**
- ✅ Banco de dados limpo
- ✅ Produtos, fornecedores, vendas criados
- ✅ 15 produtos em cenários de risco adicionados
- ✅ Histórico de vendas simulado
- ✅ Pedidos de compra criados (conforme cenário)

### Passo 2: Validar Cenários

```bash
python test_risk_scenarios.py
```

**Resultado esperado:**
```
📊 Found 15 products at risk

🔴 CRITICAL RISK: 6 products
🟠 HIGH RISK: 7 products
🟢 LOW RISK: 2 products

✅ ALL TESTS COMPLETED
```

### Passo 3: Testar com Agente

```bash
streamlit run app/streamlit_app.py
```

**Perguntas:**
- "Quais produtos têm risco de ficar sem estoque?"
- "Me mostre produtos sem pedido de compra"
- "Há pedidos atrasados?"

---

## 📋 Arquivos Criados/Modificados

### Modificado:
1. ✅ `database/seed_data.py` (+200 linhas)
   - Scenario 4A: Sem pedido
   - Scenario 4B: Pedido insuficiente
   - Scenario 4C: Pedido atrasado
   - Scenario 4D: Pedido suficiente

### Novos:
1. ✅ `reseed_with_risk_scenarios.py` - Script de regeneração
2. ✅ `test_risk_scenarios.py` - Script de validação
3. ✅ `RISK_SCENARIOS_GUIDE.md` - Guia completo
4. ✅ `FAKE_DATA_SUMMARY.md` - Este arquivo

---

## 🎯 Objetivo dos Cenários

### Testar 4 Situações Diferentes:

1. **Sem Pedido (4A):**
   - ❌ Nenhuma ação de reposição
   - 🎯 Teste: Agente deve alertar CRITICAL

2. **Pedido Insuficiente (4B):**
   - ⚠️ Tem pedido mas não basta
   - 🎯 Teste: Agente deve calcular gap

3. **Pedido Atrasado (4C):**
   - ⏰ Pedido está há muito tempo PENDING
   - 🎯 Teste: Agente deve detectar atraso

4. **Pedido OK (4D):**
   - ✅ Situação bem gerenciada
   - 🎯 Teste: Controle positivo (baixo risco)

---

## ✅ Validação

### Checklist de Teste:

- [ ] 6 produtos sem pedido detectados
- [ ] 4 produtos com pedido insuficiente detectados
- [ ] 3 produtos com pedido atrasado detectados
- [ ] 2 produtos com pedido OK (baixo risco)
- [ ] `days_until_stockout` calculado corretamente
- [ ] `gap_quantity` calculado corretamente
- [ ] `is_delayed` funcionando (threshold: 7 dias)
- [ ] Recomendações específicas por cenário
- [ ] Dashboard mostra alertas IMMINENT_STOCKOUT

---

## 🔄 Processo Completo

```
1. Modificar seed_data.py
   ↓
2. Executar reseed_with_risk_scenarios.py
   ↓
3. Banco de dados regenerado com 15 produtos em risco
   ↓
4. Executar test_risk_scenarios.py
   ↓
5. Validar que cenários foram criados corretamente
   ↓
6. Testar com agente (Streamlit)
   ↓
7. Verificar que ferramenta é chamada corretamente
```

---

## 💡 Exemplos de Produtos Criados

### Exemplo: Cenário 4A (Sem Pedido)

```python
Nome: "Produto XYZ"
Estoque atual: 15 unidades
Vendas diárias: ~7 unidades
Dias até ruptura: 2.1 dias
Pedidos pendentes: NENHUM
Risk level: CRITICAL
Recomendação: "URGENT: Create purchase order for 195 units immediately"
```

### Exemplo: Cenário 4B (Insuficiente)

```python
Nome: "Produto ABC"
Estoque atual: 10 unidades
Vendas diárias: ~6 unidades
Pedido pendente: 50 unidades
Demanda 30 dias: 180 unidades
Gap: 120 unidades (180 - 10 - 50)
Risk level: HIGH
Recomendação: "ORDER MORE: Need 120 additional units"
```

### Exemplo: Cenário 4C (Atrasado)

```python
Nome: "Produto DEF"
Estoque atual: 15 unidades
Pedido pendente: 100 unidades
Dias pendente: 12 dias (> 7 threshold)
Risk level: HIGH
Recomendação: "FOLLOW UP: Pending order is 12 days old. Contact supplier"
```

---

## 🎉 Resultado Final

**Banco de dados agora contém:**
- ✅ Dados realistas de 6 meses
- ✅ 15 produtos em cenários de risco específicos
- ✅ Histórico de vendas consistente
- ✅ Pedidos de compra em diferentes estados
- ✅ Pronto para testar ferramenta preventiva

**Ferramenta testável:**
```python
detect_imminent_stockout_risk()
```

**Agente pode responder:**
- "Quais produtos têm risco de ficar sem estoque?" ✅
- "Me mostre produtos sem pedido de compra" ✅
- "Há pedidos atrasados?" ✅

**Tudo pronto! 🚀**
