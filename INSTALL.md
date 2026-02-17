# 📦 Instruções de Instalação

## 1. Ambiente Virtual

O ambiente virtual já foi criado. Para ativá-lo:

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

## 2. Instalar Dependências

### Opção A: Instalação via pip (Recomendado)

```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Opção B: Se houver problemas de SSL (Fury PyPI)

```bash
# Use o PyPI público diretamente
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Opção C: Instalação manual (se tudo mais falhar)

```bash
pip install sqlalchemy==2.0.25
pip install langchain==0.1.4
pip install langchain-openai==0.0.5
pip install langchain-community==0.0.16
pip install openai==1.10.0
pip install streamlit==1.30.0
pip install faker==22.0.0
pip install pandas==2.1.4
pip install python-dotenv==1.0.0
pip install pydantic==2.5.3
```

## 3. Verificar Instalação

```bash
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import langchain; print('✅ LangChain:', langchain.__version__)"
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)"
```

## 4. Configurar Ambiente

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env e adicione sua OPENAI_API_KEY
# Use nano, vim, ou qualquer editor de texto
nano .env
```

## 5. Inicializar Database

```bash
python setup_db.py
```

## 6. Popular com Dados Fake (próximo passo)

```bash
# Após criar o seed_data.py
python database/seed_data.py
```

## 7. Rodar Aplicação

```bash
streamlit run app/streamlit_app.py
```

## Troubleshooting

### Erro de SSL/Certificado

Se você estiver no ambiente corporativo do Mercado Libre:

```bash
# Configure o pip para usar o repositório Fury
pip config set global.index-url https://pypi.artifacts.furycloud.io

# Ou instale com --trusted-host
pip install --trusted-host pypi.artifacts.furycloud.io <package>
```

### Python não encontrado

```bash
# Verifique sua versão do Python
python3 --version

# Use python3 se necessário
python3 setup_db.py
```

## Status Atual

✅ Estrutura do projeto criada  
✅ Ambiente virtual criado  
✅ Modelos de database definidos  
⏳ Pendente: Instalar dependências  
⏳ Pendente: Criar seed_data.py  
⏳ Pendente: Implementar tools  
⏳ Pendente: Configurar agent  
⏳ Pendente: Criar interface Streamlit  
