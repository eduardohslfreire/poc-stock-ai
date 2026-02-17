# 📋 Resumo: Detecção de Problema Operacional de Disponibilidade

**Data:** 2026-02-08  
**Solicitação:** Adicionar cenário de produtos recebidos mas não vendendo

---

## ✅ O Que Foi Implementado

### 1. **Nova Tool:** `detect_operational_availability_issues()` 🆕

**Arquivo:** `tools/operational_availability.py` (207 linhas)

**O que detecta:**
- Produtos com estoque POSITIVO
- Com histórico de vendas BOM
- Mas vendas RECENTES muito abaixo do esperado (>70% queda)
- Que receberam estoque recentemente (últimos 30 dias)

**Diferencial:** Identifica problema OPERACIONAL (produto existe mas não está acessível)

---

### 2. **Novo Cenário no Banco de Dados:** Scenario 5

**Arquivo:** `database/seed_data.py` (+100 linhas)

**Cria 5 produtos com:**
1. ✅ Vendas históricas boas (4-8 un/dia por 45 dias)
2. ✅ Pedido recebido 12-14 dias atrás (status: RECEIVED)
3. ✅ Estoque atual alto (100-150 unidades)
4. ❌ Vendas recentes baixíssimas (1-2 em 12 dias)
5. ❌ Queda de 80-95% nas vendas

---

### 3. **Registrado no Agente:** Tool #13

**Arquivo:** `agent/stock_agent.py`

**Palavras-chave para o LLM:**
- "estoque mas não vende"
- "parou de vender"
- "depósito não reposto"
- "problema operacional"
- "queda nas vendas"

**Total de ferramentas:** 13 (antes: 12)

---

## 🎯 Problema Resolvido

### Cenário Real:

```
ANTES (não detectava):
┌─────────────────────────────────────────────────────────────────┐
│ Produto X:                                                      │
│ • Comprado do fornecedor ✅                                     │
│ • Recebido no depósito ✅                                       │
│ • 150 unidades no sistema ✅                                    │
│ • MAS não vendendo ❌                                           │
│ • Perdendo vendas ❌                                            │
│                                                                 │
│ Sistema NÃO alertava nada!                                     │
└─────────────────────────────────────────────────────────────────┘

AGORA (detecta):
┌─────────────────────────────────────────────────────────────────┐
│ 🔴 ALERTA: Produto X - Problema Operacional                    │
│                                                                 │
│ • Estoque: 150 unidades (tem!)                                 │
│ • Histórico: 5 un/dia                                          │
│ • Recentes: 0.2 un/dia (queda de 96%)                         │
│ • Perdeu: 68 vendas = R$ 34.000                               │
│                                                                 │
│ 💡 Verificar se produto está nas prateleiras/online           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🆚 Comparação com Outras Tools

| Tool | Estoque | Vendas | Problema |
|------|---------|--------|----------|
| `detect_stock_rupture` | = 0 | Teve no passado | Já zerou |
| `detect_imminent_stockout_risk` | > 0 baixo | Altas | Vai zerar |
| `detect_availability_issues` | Histórico 0 | Durante stockouts | Crônico |
| **`detect_operational_availability_issues`** 🆕 | **> 0 alto** | **Caíram muito** | **Operacional** |

---

## 📊 Como Funciona

### Algoritmo:

```python
1. Pega produtos com estoque > 0

2. Calcula média histórica (60 dias atrás):
   vendas_históricas / 60 = média_histórica

3. Calcula média recente (últimos 14 dias):
   vendas_recentes / 14 = média_recente

4. Calcula queda:
   queda = (média_histórica - média_recente) / média_histórica × 100

5. Se queda > 70% E recebeu estoque recentemente:
   → ALERTA: Problema operacional!

6. Calcula impacto:
   perdas = (média_histórica × 14) - vendas_recentes
   receita_perdida = perdas × preço_venda
```

### Exemplo:

```
Produto: Mouse Gamer

Histórico (60d atrás): 180 vendas = 3 un/dia
Recentes (14d):        4 vendas = 0.3 un/dia
Queda:                 90%
Esperado:              3 × 14 = 42 vendas
Real:                  4 vendas
Perda:                 38 vendas = R$ 1.900
Estoque atual:         145 unidades (tem!)

→ CRÍTICO: Produto tem estoque mas não está vendendo!
```

---

## 🧪 Como Testar

### 1. Regenerar Banco:
```bash
python reseed_with_risk_scenarios.py
```

### 2. Testar Tool:
```python
from tools.operational_availability import detect_operational_availability_issues

issues = detect_operational_availability_issues()
print(f"Problemas encontrados: {len(issues)}")  # Esperado: 5
```

### 3. Testar com Agente:
```bash
streamlit run app/streamlit_app.py
```

**Perguntas:**
- "Produtos com estoque mas não vendendo?"
- "Produtos presos no depósito?"
- "Queda nas vendas com estoque disponível?"

---

## 📁 Arquivos Criados/Modificados

### Novos (2):
- ✅ `tools/operational_availability.py` (207 linhas)
- ✅ `OPERATIONAL_AVAILABILITY_GUIDE.md` (documentação)

### Modificados (3):
- ✅ `database/seed_data.py` (+100 linhas)
- ✅ `tools/__init__.py` (+5 linhas)
- ✅ `agent/stock_agent.py` (+20 linhas)

**Total:** ~330 linhas de código + documentação

---

## 🎯 Casos de Uso Habilitados

| Pergunta do Usuário | Tool Chamada | Resultado |
|---------------------|--------------|-----------|
| "Produtos com estoque mas sem vendas" | `detect_operational_availability_issues` | 5 produtos |
| "Produtos que pararam de vender" | `detect_operational_availability_issues` | 5 produtos |
| "Produtos no depósito não repostos" | `detect_operational_availability_issues` | 5 produtos |
| "Problemas operacionais de estoque" | `detect_operational_availability_issues` | 5 produtos |

---

## 💡 Por Que Isso É Importante?

### Problema Real no Varejo:

1. **Ruptura Fantasma:**
   - Sistema diz: "Tem estoque"
   - Cliente vê: "Não tem na prateleira"
   - Resultado: Venda perdida

2. **Causas Comuns:**
   - Produto no depósito sem repor
   - Erro no sistema de disponibilidade online
   - Produto em local errado na loja
   - Problema de merchandising/exposição

3. **Impacto Financeiro:**
   - Clientes frustrados
   - Vendas perdidas
   - Concorrentes ganham o cliente
   - Capital parado (tem estoque mas não gira)

### Com a Nova Tool:

```
✅ Detecta o problema automaticamente
✅ Calcula o impacto financeiro
✅ Sugere ação corretiva específica
✅ Permite agir ANTES de perder mais vendas
```

---

## 📈 Estatísticas

### Dados Fake Gerados:

| Métrica | Valor |
|---------|-------|
| Produtos com problema | 5 |
| Vendas históricas (cada) | ~200 vendas |
| Vendas recentes (cada) | 1-2 vendas |
| Queda média | 80-95% |
| Receita perdida (total) | ~R$ 150.000 |

### Cenários Totais no Banco:

| Tipo | Quantidade |
|------|------------|
| Sem pedido (4A) | 6 |
| Pedido insuficiente (4B) | 4 |
| Pedido atrasado (4C) | 3 |
| Pedido OK (4D) | 2 |
| **Problema operacional (5)** | **5** |
| **TOTAL** | **20 cenários** |

---

## ✅ Checklist Final

- [x] Tool implementada
- [x] Cenário adicionado no seed
- [x] Tool registrada no agente
- [x] Exports atualizados
- [x] Documentação completa
- [x] Guia de teste criado
- [ ] Testar com banco regenerado (próximo passo)
- [ ] Validar com agente (próximo passo)

---

## 🎉 Resultado

**Sistema agora detecta 3 tipos diferentes de problemas:**

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  1. 🔴 RUPTURA (estoque = 0)                                  │
│     Tool: detect_stock_rupture()                              │
│     Quando: Produto JÁ zerou                                  │
│                                                                │
│  2. ⚠️ RISCO DE RUPTURA (vai zerar)                           │
│     Tool: detect_imminent_stockout_risk()                     │
│     Quando: Produto VAI zerar em breve                        │
│                                                                │
│  3. 🏪 PROBLEMA OPERACIONAL (tem mas não vende) 🆕            │
│     Tool: detect_operational_availability_issues()            │
│     Quando: Produto TEM estoque mas NÃO está acessível       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Cobertura completa de problemas de disponibilidade! 📦✨**
