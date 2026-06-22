# Class PI — Classificador de Cenários de Propriedade Intelectual

**INCUBAC/IFAC — Instituto Federal do Acre**

Ferramenta interativa para diagnóstico e classificação de cenários de Propriedade Intelectual no âmbito da incubação de empresas e startups do IFAC.

---

## Descrição

O **Class PI** é um wizard de diagnóstico dividido em 6 blocos temáticos que identifica automaticamente os cenários de PI aplicáveis a cada criação intelectual incubada no IFAC, com base no Regimento Interno dos Núcleos Incubadores (Res. CONSU/IFAC nº 99/2022). Ao final do diagnóstico, gera um relatório PDF completo com:

- Cenário(s) identificado(s)
- Titularidade e instrumentos obrigatórios
- Base legal aplicável
- Obrigações do empreendimento
- Checklist de documentos necessários
- Tabela de repartição de ganhos

### Cenários cobertos

| Cenário | Descrição |
|---------|-----------|
| C-01 | Criação sem uso de recursos do IFAC |
| C-02 | Criação pelo empreendedor com recursos do IFAC |
| C-03 | Criação com servidor/pesquisador do IFAC |
| C-04 | Criação por estudante/bolsista com recursos do IFAC |
| C-05 | Parceria formal IFAC + Empreendimento |
| C-06 | Derivação de tecnologia existente do IFAC |
| C-07 | Aperfeiçoamento com recursos do IFAC |
| C-08 | Possível licenciamento preferencial ao criador |
| C-09 | Bioeconomia amazônica sem recursos do IFAC |
| C-10 | Bioeconomia amazônica com recursos do IFAC |
| C-11 | Bioeconomia com conhecimento tradicional |
| C-12 | Software com recursos do IFAC |
| C-13 | Cultivar com recursos do IFAC |
| C-14 | Marca do empreendimento |
| C-15 | Uso indevido de marca/infrações |
| C-16 | Parceria com outra ICT |
| C-17 | PI pré-existente à incubação |
| C-18 | PI pré-existente aperfeiçoada com recursos do IFAC |
| C-19 | Know-how / Segredo industrial |
| C-20 | Indicação Geográfica (IG) |

---

## Módulos

### Módulo 1 — Respondente (acesso público)
Wizard de diagnóstico com 6 blocos + etapa de dados pessoais. Todas as perguntas são obrigatórias. Ao final, o diagnóstico é enviado e o respondente pode baixar o relatório em PDF.

### Módulo 2 — Painel de Gestão (protegido por senha)
- Acesso via botão "Painel de Gestão" na interface
- Senha padrão: `ifac2026of`
- Funcionalidades: listar diagnósticos enviados, visualizar detalhes, baixar PDF por diagnóstico, alterar senha

---

## Estrutura de Arquivos

```
classpi/
├── app.py                  # Aplicação principal Streamlit
├── requirements.txt        # Dependências Python
├── README.md               # Este arquivo
├── .streamlit/
│   └── config.toml         # Tema e configurações do Streamlit
├── respostas.json          # Diagnósticos enviados (gerado automaticamente)
└── senha.json              # Hash da senha do gestor (gerado automaticamente)
```

---

## Como Rodar Localmente

### Pré-requisitos
- Python 3.9+
- pip

### Instalação

```bash
# Clone ou copie o repositório
cd classpi

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`.

### Opcional — Ambiente virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# ou
venv\Scripts\activate           # Windows

pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy no Streamlit Cloud

1. **Fork ou suba este repositório** para o GitHub (repositório público ou privado).

2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com sua conta GitHub.

3. Clique em **"New app"** e selecione:
   - Repositório: seu repositório no GitHub
   - Branch: `main`
   - Arquivo principal: `app.py`

4. Clique em **"Deploy"**.

> **Atenção:** No Streamlit Cloud, os arquivos `respostas.json` e `senha.json` são temporários — ao reiniciar o servidor, os dados são perdidos. Para persistência, considere usar um banco de dados externo (ex.: Supabase, Firebase, Google Sheets API).

### Variáveis de ambiente (opcional)

Para maior segurança no deploy, você pode definir a senha inicial via secrets do Streamlit Cloud:

Crie o arquivo `.streamlit/secrets.toml` localmente (não enviar para o GitHub):
```toml
SENHA_INICIAL = "sua_senha_segura_aqui"
```

---

## Segurança

- A senha do gestor é armazenada como hash SHA-256 em `senha.json` — nunca em texto puro.
- Os diagnósticos são armazenados localmente em `respostas.json` (JSON simples).
- Não há transmissão de dados para servidores externos.

---

## Base Legal

- Regimento Interno dos Núcleos Incubadores — Res. CONSU/IFAC nº 99/2022
- Lei nº 10.973/2004 (Lei de Inovação)
- Decreto nº 9.283/2018 (Marco Legal de CT&I)
- Lei nº 9.609/1998 (Software)
- Lei nº 9.456/1997 (Cultivares)
- Lei nº 9.279/1996 (Propriedade Industrial)
- Lei nº 13.123/2015 (Biodiversidade/PG)
- Protocolo de Nagoya (CTA/repartição de benefícios)
- Res. CONSU/IFAC nº 190/2024

---

## Créditos

Ferramenta desenvolvida a partir da disciplina de **Oficina Profissional** por discente de mestrado do **PROFNIT (Programa de Pós-Graduação em Propriedade Intelectual e Transferência de Tecnologia para a Inovação)**.

**INCUBAC/IFAC** — Programa de Incubação de Empresas e Startups  
Instituto Federal de Educação, Ciência e Tecnologia do Acre — IFAC

---

© INCUBAC/IFAC · Todos os direitos reservados
