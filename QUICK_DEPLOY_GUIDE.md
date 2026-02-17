# ⚡ Guia Rápido de Deploy (5 minutos)

Siga este guia visual para fazer deploy no Streamlit Cloud rapidamente.

---

## 📋 Pré-requisitos

Antes de começar, tenha em mãos:

```
✅ Conta GitHub (gratuita)
✅ Conta Streamlit Cloud (gratuita)  
✅ OpenAI API Key (https://platform.openai.com/api-keys)
```

---

## 🔑 Passo 1: Obter OpenAI API Key (2 min)

```
1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie conta
3. Clique em "Create new secret key"
4. Nomeie: "streamlit-stock-ai"
5. Copie a chave (formato: sk-proj-XXXXX...)
   ⚠️ ATENÇÃO: Copie AGORA! Não aparecerá novamente.
```

**Salve temporariamente:**
```
Minha API Key: sk-proj-_________________________________
```

---

## 🐙 Passo 2: Push para GitHub (1 min)

```bash
# No terminal, dentro da pasta do projeto:

# Inicializar git (se necessário)
git init

# Adicionar arquivos
git add .

# Commitar
git commit -m "Initial commit: Stock AI Assistant"

# Criar repositório no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/poc-stock-ai.git
git branch -M main
git push -u origin main
```

**Substituir:**
- `SEU_USUARIO` pelo seu username do GitHub

**Verificar:**
```
✅ Acessar https://github.com/SEU_USUARIO/poc-stock-ai
✅ Confirmar que os arquivos estão lá
✅ Verificar que .env e stock.db NÃO estão no repositório
```

---

## ☁️ Passo 3: Deploy no Streamlit Cloud (2 min)

### 3.1 Criar App

```
1. Acesse: https://share.streamlit.io
2. Login com GitHub
3. Clique em "New app"
```

### 3.2 Configurar App

Preencha o formulário:

```yaml
┌─────────────────────────────────────────┐
│ Repository: SEU_USUARIO/poc-stock-ai    │
│ Branch: main                            │
│ Main file path: app/streamlit_app.py   │
│ App URL: poc-stock-ai                   │
└─────────────────────────────────────────┘
```

### 3.3 Configurar Secrets

**IMPORTANTE:** Antes de clicar em "Deploy", configure os secrets!

1. Clique em **"Advanced settings"**
2. Na seção **"Secrets"**, cole:

```toml
[openai]
api_key = "sk-proj-COLE_SUA_CHAVE_AQUI"
model = "gpt-4o-mini"

[database]
url = "sqlite:///stock.db"
```

**⚠️ IMPORTANTE:**
- Substitua `sk-proj-COLE_SUA_CHAVE_AQUI` pela chave que você copiou no Passo 1
- Mantenha as aspas
- Não adicione espaços extras

### 3.4 Deploy

```
1. Clique em "Deploy!"
2. Aguarde 2-5 minutos
3. Observe os logs da inicialização
```

---

## ✅ Passo 4: Verificar Deploy (30 seg)

### Sinais de Sucesso

```
✅ URL da app está ativa (https://SEU_USUARIO-poc-stock-ai.streamlit.app)
✅ Página carrega sem erros
✅ Sidebar mostra "✅ Agente inicializado"
✅ Sidebar mostra "🤖 Modelo: gpt-4o-mini"
✅ Mensagem de boas-vindas aparece
✅ Exemplos de perguntas na sidebar
```

### Teste Rápido

Clique em uma pergunta de exemplo:

```
💬 "Como está meu estoque hoje?"
```

**Resposta esperada:**
- ✅ Agente responde com estatísticas
- ✅ Mostra número de produtos
- ✅ Mostra alertas críticos

---

## ❌ Troubleshooting Rápido

### Problema: "OPENAI_API_KEY not found"

**Solução:**
```
1. Clique em "⚙️ Settings" (canto superior direito)
2. Clique em "Secrets"
3. Verifique se o formato está correto:
   [openai]
   api_key = "sk-proj-..."
4. Salve
5. Aguarde restart automático
```

### Problema: App não carrega

**Solução:**
```
1. Clique em "⋮" (menu) → "Manage app"
2. Clique em "Logs"
3. Leia o erro
4. Veja DEPLOY_STREAMLIT.md seção "Troubleshooting"
```

### Problema: "No module named 'faker'"

**Solução:**
```
1. Verifique se requirements.txt existe no GitHub
2. Verifique se tem: faker==22.0.0
3. Faça push novamente se necessário
```

---

## 🎨 Personalização (Opcional)

### Mudar URL da App

```
1. Settings → General
2. App URL: escolha novo nome
3. Save
```

### Mudar Tema/Cores

Edite `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"  # Cor principal
backgroundColor = "#FFFFFF"  # Fundo
```

---

## 🔄 Atualizar App

### Fazer mudanças

```bash
# 1. Editar código localmente
# 2. Testar: streamlit run app/streamlit_app.py
# 3. Commitar
git add .
git commit -m "Atualização X"

# 4. Push
git push origin main

# 5. Streamlit Cloud faz redeploy automaticamente! 🎉
```

---

## 📊 Fluxo Visual

```
┌──────────────┐
│  Obter API   │  1. OpenAI API Key
│     Key      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Push para   │  2. git push → GitHub
│    GitHub    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Criar App   │  3. Streamlit Cloud
│  Streamlit   │     + Configurar Secrets
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Deploy!    │  4. Auto-seed DB
│              │     + App online
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Testar     │  5. Fazer perguntas
│     App      │     + Compartilhar URL
└──────────────┘
```

---

## ⏱️ Tempo Estimado

```
┌─────────────────────────┬──────────┐
│ Passo 1: API Key        │ 2 min    │
│ Passo 2: GitHub Push    │ 1 min    │
│ Passo 3: Deploy Config  │ 2 min    │
│ Passo 4: Verificação    │ 30 seg   │
├─────────────────────────┼──────────┤
│ TOTAL                   │ ~5 min   │
└─────────────────────────┴──────────┘
```

**Nota:** Primeira build do Streamlit leva ~2-5 min adicional.

---

## 🎯 Checklist Final

Antes de considerar concluído:

```
□ Repositório criado no GitHub
□ Código commitado e enviado
□ App criada no Streamlit Cloud
□ Secrets configurados corretamente
□ Deploy realizado com sucesso
□ App carrega sem erros
□ Agente responde perguntas
□ Dados fake foram carregados
□ URL da app funciona
□ Compartilhado com time (opcional)
```

---

## 📚 Próximos Passos

Após deploy bem-sucedido:

1. **Compartilhe:** Envie URL para seu time
2. **Monitore:** Acompanhe logs inicialmente
3. **Documente:** Anote questões frequentes
4. **Explore:** Teste diferentes perguntas
5. **Melhore:** Considere feedback e ajustes

---

## 🆘 Precisa de Ajuda?

### Documentação Completa
- **[DEPLOY_STREAMLIT.md](./DEPLOY_STREAMLIT.md)** - Guia detalhado
- **[DEPLOYMENT_CHANGES.md](./DEPLOYMENT_CHANGES.md)** - O que foi modificado

### Recursos Externos
- [Streamlit Docs](https://docs.streamlit.io/deploy)
- [Streamlit Forum](https://discuss.streamlit.io)
- [OpenAI API Docs](https://platform.openai.com/docs)

---

## 🎉 Parabéns!

Sua aplicação Stock AI Assistant está no ar! 🚀

```
 _______________
|   🎉 DEPLOY   |
|    COMPLETO!  |
|_______________|
     ||  ||
     ||  ||
    _||__||_
   |________|
```

**Aproveite sua app de IA na nuvem!**
