# 🚀 Deploy no Streamlit Community Cloud

Guia completo para fazer deploy da aplicação Stock AI Assistant no Streamlit Community Cloud.

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Preparação do Projeto](#preparação-do-projeto)
3. [Configuração do GitHub](#configuração-do-github)
4. [Deploy no Streamlit Cloud](#deploy-no-streamlit-cloud)
5. [Configuração de Secrets](#configuração-de-secrets)
6. [Verificação e Troubleshooting](#verificação-e-troubleshooting)

---

## 📌 Pré-requisitos

Antes de iniciar o deploy, você precisa de:

- ✅ **Conta GitHub** (gratuita)
- ✅ **Conta Streamlit Community Cloud** (gratuita) - [https://share.streamlit.io](https://share.streamlit.io)
- ✅ **OpenAI API Key** - [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- ✅ **Git** instalado localmente

---

## 🔧 Preparação do Projeto

### 1. Inicializar Repositório Git (se ainda não existe)

```bash
cd /Users/efreire/poc-projects/poc-stock

# Inicializar git (se necessário)
git init

# Adicionar todos os arquivos
git add .

# Criar commit inicial
git commit -m "Initial commit: Stock AI Assistant"
```

### 2. Verificar Arquivos Necessários

Os seguintes arquivos **já estão criados** e prontos:

- ✅ `requirements.txt` - Dependências Python
- ✅ `.streamlit/config.toml` - Configuração visual
- ✅ `.streamlit/secrets.toml.example` - Exemplo de secrets
- ✅ `.gitignore` - Ignora arquivos sensíveis
- ✅ `database/auto_seed.py` - Auto-popula banco de dados
- ✅ `app/streamlit_app.py` - App principal (atualizado para usar secrets)

### 3. Verificar .gitignore

Certifique-se de que os seguintes arquivos **NÃO** serão commitados:

```gitignore
.env
.streamlit/secrets.toml
stock.db
*.db
```

Isso garante que:
- ❌ Suas chaves API não serão expostas
- ❌ Banco de dados local não vai para o GitHub
- ✅ Projeto está seguro

---

## 🐙 Configuração do GitHub

### 1. Criar Repositório no GitHub

1. Acesse [https://github.com/new](https://github.com/new)
2. Preencha:
   - **Nome:** `poc-stock-ai` (ou nome de sua preferência)
   - **Visibilidade:** `Private` (recomendado) ou `Public`
   - **NÃO marque:** "Add a README file"
3. Clique em **Create repository**

### 2. Conectar Repositório Local

```bash
# Adicionar remote do GitHub (substitua SEU_USUARIO pelo seu username)
git remote add origin https://github.com/SEU_USUARIO/poc-stock-ai.git

# Fazer push do código
git branch -M main
git push -u origin main
```

### 3. Verificar Push

Acesse seu repositório no GitHub e confirme que todos os arquivos estão lá (exceto `.env`, `secrets.toml` e `*.db`).

---

## ☁️ Deploy no Streamlit Cloud

### 1. Acessar Streamlit Community Cloud

1. Vá para [https://share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Autorize o Streamlit a acessar seus repositórios

### 2. Criar Nova App

1. Clique em **"New app"**
2. Preencha o formulário:

```yaml
Repository: SEU_USUARIO/poc-stock-ai
Branch: main
Main file path: app/streamlit_app.py
App URL: poc-stock-ai (ou nome personalizado)
```

3. **NÃO clique em Deploy ainda!** Primeiro configure os secrets.

### 3. Configurar Secrets

Na mesma página do deploy, procure a seção **"Advanced settings"** → **"Secrets"**.

Cole o seguinte conteúdo (substituindo pela sua chave real):

```toml
[openai]
api_key = "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
model = "gpt-4o-mini"

[database]
url = "sqlite:///stock.db"
```

**⚠️ IMPORTANTE:**
- Substitua `sk-proj-XXXX...` pela sua chave OpenAI real
- **NUNCA** compartilhe essa chave publicamente
- Você pode obter uma chave em: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 4. Deploy Final

1. Clique em **"Deploy!"**
2. Aguarde ~2-5 minutos enquanto o Streamlit:
   - Clona o repositório
   - Instala dependências (`requirements.txt`)
   - Inicializa o banco de dados (auto-seed)
   - Inicia a aplicação

### 5. Primeira Execução

Na **primeira execução**, o sistema vai:

1. ✅ Detectar que o banco de dados não existe
2. ✅ Executar `auto_seed.py` automaticamente
3. ✅ Gerar ~100 produtos fake com dados realistas
4. ✅ Criar cenários de teste (rupturas, riscos, etc.)
5. ✅ Deixar tudo pronto para uso

Isso leva ~30 segundos no primeiro deploy.

---

## 🔐 Configuração de Secrets (Detalhado)

### Estrutura dos Secrets

O arquivo `.streamlit/secrets.toml` deve ter esta estrutura:

```toml
[openai]
api_key = "sua-chave-aqui"
model = "gpt-4o-mini"  # ou "gpt-4" se preferir

[database]
url = "sqlite:///stock.db"
```

### Como Obter a OpenAI API Key

1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Faça login ou crie uma conta
3. Clique em **"Create new secret key"**
4. Copie a chave (formato: `sk-proj-...`)
5. Cole nos secrets do Streamlit

### Editar Secrets Depois do Deploy

Se precisar atualizar os secrets:

1. Vá para seu app no Streamlit Cloud
2. Clique em **"⚙️ Settings"**
3. Clique em **"Secrets"**
4. Edite o conteúdo
5. Clique em **"Save"**
6. O app reiniciará automaticamente

---

## ✅ Verificação e Troubleshooting

### Verificar se o Deploy Funcionou

1. **URL da app:** `https://share.streamlit.io/SEU_USUARIO/poc-stock-ai`
2. **Status esperado:**
   - ✅ Página carrega sem erros
   - ✅ Mensagem "Agente inicializado" na sidebar
   - ✅ Modelo GPT aparece na sidebar
   - ✅ Perguntas de exemplo funcionam

### Problemas Comuns

#### ❌ Erro: "OPENAI_API_KEY not found"

**Causa:** Secrets não configurados corretamente

**Solução:**
1. Vá em Settings → Secrets
2. Verifique se o formato está correto:
   ```toml
   [openai]
   api_key = "sk-proj-..."
   ```
3. Salve e aguarde restart

#### ❌ Erro: "No module named 'faker'"

**Causa:** Dependências não instaladas

**Solução:**
1. Verifique se `requirements.txt` existe no repositório
2. Verifique se `faker==22.0.0` está listado
3. Faça push novamente se necessário

#### ❌ Erro: "Database is locked"

**Causa:** SQLite não é ideal para múltiplos usuários simultâneos

**Solução:**
- Para POC, isso é aceitável
- Para produção, migre para PostgreSQL (veja seção abaixo)

#### ❌ App fica "Connecting..." eternamente

**Causa:** Erro durante inicialização

**Solução:**
1. Clique em **"Manage app"** → **"Logs"**
2. Leia os logs para identificar o erro
3. Corrija e faça novo push

### Ver Logs da Aplicação

1. Acesse seu app no Streamlit Cloud
2. Clique em **"⋮"** (menu) → **"Manage app"**
3. Vá em **"Logs"**
4. Veja logs em tempo real

---

## 🗃️ Banco de Dados: SQLite vs PostgreSQL

### SQLite (Atual - Ideal para POC)

**✅ Vantagens:**
- Zero configuração
- Grátis
- Auto-seed funciona perfeitamente
- Ideal para demos e POCs

**⚠️ Limitações:**
- Banco é recriado a cada restart do app
- Não persiste dados entre deploys
- Não suporta múltiplos usuários escrevendo simultaneamente

### PostgreSQL (Para Produção)

Se você quiser persistência real:

1. **Criar banco PostgreSQL:**
   - [Neon](https://neon.tech) (grátis, recomendado)
   - [Supabase](https://supabase.com) (grátis)
   - [ElephantSQL](https://www.elephantsql.com) (grátis)

2. **Atualizar secrets:**
   ```toml
   [database]
   url = "postgresql://user:password@host:5432/dbname"
   ```

3. **Adicionar driver ao requirements.txt:**
   ```txt
   psycopg2-binary==2.9.9
   ```

4. **Executar seed manualmente:**
   Você precisará executar o seed uma vez manualmente no banco PostgreSQL.

---

## 🔄 Workflow de Desenvolvimento

### Fazer Mudanças no Código

```bash
# 1. Editar código localmente
# 2. Testar localmente
streamlit run app/streamlit_app.py

# 3. Commitar mudanças
git add .
git commit -m "Descrição das mudanças"

# 4. Push para GitHub
git push origin main

# 5. Streamlit Cloud detecta e faz redeploy automaticamente
```

### Rollback de Deploy

Se algo der errado:

1. Reverta o commit localmente:
   ```bash
   git revert HEAD
   git push origin main
   ```

2. Ou volte para um commit específico:
   ```bash
   git reset --hard COMMIT_HASH
   git push -f origin main
   ```

---

## 🎯 Checklist Completo de Deploy

Antes de fazer deploy, confirme:

- [ ] Código commitado no Git
- [ ] `.gitignore` configurado (não commita secrets)
- [ ] `requirements.txt` completo
- [ ] Repositório criado no GitHub
- [ ] Push feito para GitHub
- [ ] Conta criada no Streamlit Cloud
- [ ] App criada no Streamlit Cloud
- [ ] Secrets configurados (OpenAI API Key)
- [ ] Deploy realizado
- [ ] App testada (perguntas funcionam)

---

## 📚 Recursos Úteis

- **Streamlit Docs:** [https://docs.streamlit.io](https://docs.streamlit.io)
- **Deploy Docs:** [https://docs.streamlit.io/deploy](https://docs.streamlit.io/deploy)
- **Secrets Management:** [https://docs.streamlit.io/deploy/concepts/secrets](https://docs.streamlit.io/deploy/concepts/secrets)
- **Community Forum:** [https://discuss.streamlit.io](https://discuss.streamlit.io)

---

## 🎉 Pronto!

Sua aplicação Stock AI Assistant está no ar! 🚀

**Próximos passos:**
- Compartilhe a URL com seu time
- Teste diferentes perguntas
- Monitore logs para identificar melhorias
- Considere migrar para PostgreSQL se precisar persistência

---

**Dúvidas?** Consulte os logs ou abra uma issue no repositório.
