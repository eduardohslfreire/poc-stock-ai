# 🤖 Modos de Agente - LangChain

## 📊 Configuração Atual

**Modo:** OpenAI Function Calling  
**Arquivo:** `agent/stock_agent.py`  
**Função:** `create_openai_functions_agent()`

---

## 🔀 Comparação de Modos

### 1. OpenAI Function Calling (Atual) ⭐

```python
from langchain.agents import create_openai_functions_agent

agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
```

**Como funciona:**
- Usa API nativa de function calling da OpenAI
- Tools são enviadas como `functions` no request
- Modelo retorna JSON estruturado: `{"name": "tool_name", "arguments": {...}}`
- LangChain executa a tool e passa resultado de volta

**Prós:**
- ✅ **Mais preciso** - parsing confiável (JSON estruturado)
- ✅ **Menos tokens** - não precisa escrever "pensamentos"
- ✅ **Mais rápido** - menos overhead
- ✅ **Parallel calling** - pode chamar múltiplas tools simultaneamente
- ✅ **Melhor para produção** - mais estável

**Contras:**
- ❌ Específico OpenAI (não funciona com Anthropic, Llama, etc.)
- ❌ Menos transparente (não vê raciocínio intermediário)

**Quando usar:**
- ✅ Produção com OpenAI
- ✅ Precisa de confiabilidade
- ✅ Quer minimizar custos/latência

---

### 2. ReAct (Reasoning + Acting)

```python
from langchain.agents import create_react_agent

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt
)
```

**Como funciona:**
- Usa prompting para fazer modelo "pensar em voz alta"
- Padrão: `Thought → Action → Action Input → Observation`
- LangChain faz parsing do texto para extrair tool calls

**Exemplo de execução:**
```
Question: Como está meu estoque?

Thought: Preciso verificar o status do estoque usando o dashboard.
Action: get_stock_alerts
Action Input: atual
Observation: {"health_score": 65, "critical_alerts": 3, ...}

Thought: Os dados mostram 3 alertas críticos. Vou formatar isso para o usuário.
Final Answer: Seu estoque está com status FAIR (65/100). Há 3 alertas críticos...
```

**Prós:**
- ✅ **Funciona com qualquer LLM** (OpenAI, Anthropic, Llama, etc.)
- ✅ **Transparente** - vê cada passo do raciocínio
- ✅ **Bom para debug** - entende porque pegou determinada tool
- ✅ **Flexível** - pode customizar formato do prompt

**Contras:**
- ❌ **Mais tokens** - escreve pensamentos completos
- ❌ **Mais lento** - mais geração de texto
- ❌ **Menos confiável** - parsing de texto pode falhar
- ❌ **Não suporta parallel calling**

**Quando usar:**
- ✅ Precisa de compatibilidade com múltiplos LLMs
- ✅ Debug e desenvolvimento
- ✅ Quer entender raciocínio do agente
- ✅ Modelo não suporta function calling

---

### 3. OpenAI Tools Agent (Mais recente)

```python
from langchain.agents import create_openai_tools_agent

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
```

**Como funciona:**
- Evolução do Functions Agent
- Usa endpoint `tools` em vez de `functions`
- Mais features e melhor suporte

**Prós:**
- ✅ Tudo do Functions Agent
- ✅ Melhor suporte a parallel calling
- ✅ Mais features futuras da OpenAI

**Contras:**
- ❌ Ainda específico OpenAI

**Quando usar:**
- ✅ OpenAI + quer features mais recentes
- ✅ Migração do Functions Agent

---

### 4. Structured Chat Agent

```python
from langchain.agents import create_structured_chat_agent

agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
```

**Como funciona:**
- Similar ao ReAct mas com formato mais estruturado
- Bom para tools que precisam de múltiplos inputs complexos

**Quando usar:**
- ✅ Tools com schemas complexos
- ✅ Precisa de mais controle sobre inputs

---

## 🎯 Recomendações

### Para este projeto (Stock AI)

**Produção:** OpenAI Function Calling (atual) ⭐
- Mais confiável para análises de estoque
- Menos tokens = menor custo
- Tools bem definidas (não precisam de raciocínio visível)

**Desenvolvimento/Debug:** ReAct
- Use `agent/stock_agent_react.py` para ver raciocínio
- Útil se precisar entender porque está escolhendo certas tools

---

## 🔧 Como Trocar de Modo

### Opção 1: Usar ReAct temporariamente

```python
# Em app/streamlit_app.py, linha 101
# Trocar:
from agent.stock_agent import create_stock_agent

# Por:
from agent.stock_agent_react import create_stock_agent_react as create_stock_agent
```

### Opção 2: Variável de ambiente

Adicionar no `agent/stock_agent.py`:

```python
agent_mode = os.getenv('AGENT_MODE', 'functions')  # 'functions' ou 'react'

if agent_mode == 'react':
    agent = create_react_agent(llm, tools, react_prompt)
else:
    agent = create_openai_functions_agent(llm, tools, prompt)
```

---

## 📊 Comparação de Custos (estimado)

Para uma pergunta típica:

| Modo | Tokens (aprox) | Custo (GPT-4o-mini) | Velocidade |
|------|----------------|---------------------|------------|
| **Functions** | 500-800 | $0.0001 | ⚡⚡⚡ |
| **ReAct** | 1200-2000 | $0.0003 | ⚡⚡ |
| **Tools** | 500-800 | $0.0001 | ⚡⚡⚡ |

*Para 1000 queries/mês:*
- Functions: ~$0.10
- ReAct: ~$0.30

---

## 🧪 Como Testar ReAct

```python
# Terminal
cd /Users/efreire/poc-projects/poc-stock
source venv/bin/activate

# Python
from agent.stock_agent_react import create_stock_agent_react
from agent.stock_agent import query_agent

agent = create_stock_agent_react()
response = query_agent(agent, "Como está meu estoque?")
print(response)
```

Você verá o output detalhado:
```
> Entering new AgentExecutor chain...

Thought: Preciso verificar o status geral do estoque
Action: get_stock_alerts
Action Input: atual
Observation: {"health_score": 65, ...}

Thought: Agora sei a situação do estoque
Final Answer: Seu estoque está...
```

---

## 📚 Referências

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

## 💡 Conclusão

**Para este projeto:**
- ✅ **Mantenha Function Calling** (atual)
- ✅ Use ReAct apenas para debug se necessário
- ✅ Considere Tools Agent se quiser features mais recentes

**A configuração atual é ótima para produção!** 🎯
