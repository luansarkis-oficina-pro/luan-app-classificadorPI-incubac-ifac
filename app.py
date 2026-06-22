import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from fpdf import FPDF
import io
import base64
import copy

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tabela de Cenários de Propriedade Intelectual - Classificador de cenários PI — INCUBAC/IFAC",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CAMINHOS DE ARQUIVOS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPOSTAS_FILE = os.path.join(BASE_DIR, "respostas.json")
SENHA_FILE = os.path.join(BASE_DIR, "senha.json")

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
/* Fundo escuro global */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0d0d0d !important;
    color: #ffffff !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #111111 !important; }

/* Header com degradê vermelho → verde IFAC */
.ifac-header {
    background: linear-gradient(135deg, #C8102E 0%, #7a1028 40%, #007030 70%, #00843D 100%);
    padding: 28px 32px 20px 32px;
    border-radius: 0 0 12px 12px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(200,16,46,0.25);
}
.ifac-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 4px 0;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    letter-spacing: 2px;
}
.ifac-header p {
    font-size: 0.95rem;
    color: #f0f0f0;
    margin: 0;
    opacity: 0.92;
}

/* Inputs claros para contraste */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select {
    background-color: #f0f0f0 !important;
    color: #1a1a1a !important;
    border: 1.5px solid #cccccc !important;
    border-radius: 6px !important;
    font-size: 0.95rem;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #C8102E !important;
    box-shadow: 0 0 0 2px rgba(200,16,46,0.2) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label {
    color: #e0e0e0 !important;
    font-weight: 500;
}

/* Radio buttons */
div[data-testid="stRadio"] label { color: #e0e0e0 !important; }
div[data-testid="stRadio"] div[role="radiogroup"] { gap: 6px; }

/* Botões */
div[data-testid="stButton"] > button {
    background-color: #C8102E;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    padding: 8px 20px;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background-color: #a00d24 !important;
    color: #fff !important;
}
.btn-secondary div[data-testid="stButton"] > button {
    background-color: #333333 !important;
    color: #ffffff !important;
}
.btn-secondary div[data-testid="stButton"] > button:hover {
    background-color: #444444 !important;
}
.btn-green div[data-testid="stButton"] > button {
    background-color: #00843D !important;
    color: #ffffff !important;
}
.btn-green div[data-testid="stButton"] > button:hover {
    background-color: #005f2b !important;
}
.btn-warning div[data-testid="stButton"] > button {
    background-color: #e07b00 !important;
    color: #ffffff !important;
}
.btn-warning div[data-testid="stButton"] > button:hover {
    background-color: #b86200 !important;
}

/* Cards de bloco */
.bloco-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 4px solid #C8102E;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 16px;
}
.bloco-card h3 { color: #ff4d6a; margin-top: 0; }
.bloco-title {
    background: linear-gradient(90deg, #C8102E22, transparent);
    border-left: 4px solid #C8102E;
    padding: 10px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 16px;
}
.bloco-title h2 { color: #ff8096; margin: 0; font-size: 1.2rem; }

/* Progresso */
.progress-bar-outer {
    background: #2a2a2a;
    border-radius: 20px;
    height: 10px;
    width: 100%;
    margin-bottom: 16px;
}
.progress-bar-inner {
    background: linear-gradient(90deg, #C8102E, #00843D);
    border-radius: 20px;
    height: 10px;
    transition: width 0.4s;
}

/* Expander / detalhes */
details summary { color: #ff8096 !important; font-weight: 600; }
div[data-testid="stExpander"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}

/* Dataframe / tabelas */
div[data-testid="stDataFrame"] { background: #1a1a1a; }

/* Rodapé fixo */
.rodape-fixo {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #111111;
    border-top: 1px solid #2a2a2a;
    padding: 7px 24px;
    font-size: 0.68rem;
    color: #888888;
    text-align: center;
    z-index: 9999;
}

/* Alertas customizados */
.alert-success {
    background: #003d1f;
    border: 1px solid #00843D;
    border-radius: 6px;
    padding: 12px 16px;
    color: #66ffaa;
    margin-bottom: 12px;
}
.alert-warning {
    background: #3d2200;
    border: 1px solid #e07b00;
    border-radius: 6px;
    padding: 12px 16px;
    color: #ffcc66;
    margin-bottom: 12px;
}
.alert-info {
    background: #001a3d;
    border: 1px solid #0066cc;
    border-radius: 6px;
    padding: 12px 16px;
    color: #66aaff;
    margin-bottom: 12px;
}
.cenario-badge {
    display: inline-block;
    background: linear-gradient(135deg, #C8102E, #00843D);
    color: #ffffff;
    font-weight: 800;
    font-size: 1.4rem;
    padding: 8px 24px;
    border-radius: 30px;
    margin: 8px 0;
    letter-spacing: 1px;
}
.detalhe-row {
    display: flex;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #2a2a2a;
}
.detalhe-label { color: #aaaaaa; min-width: 180px; font-size: 0.88rem; }
.detalhe-valor { color: #ffffff; font-size: 0.88rem; }

/* Scrollbar escuro */
::-webkit-scrollbar { width: 8px; background: #1a1a1a; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }

/* Padding bottom para rodapé */
.main-content-pad { padding-bottom: 60px; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# FUNÇÕES DE DADOS — JSON
# ─────────────────────────────────────────────

def carregar_respostas():
    if os.path.exists(RESPOSTAS_FILE):
        with open(RESPOSTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_resposta(diagnostico: dict):
    dados = carregar_respostas()
    dados.append(diagnostico)
    with open(RESPOSTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# FUNÇÕES DE SENHA — hashlib
# ─────────────────────────────────────────────
SENHA_PADRAO = "ifac2026of"


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def carregar_senha_hash() -> str:
    if os.path.exists(SENHA_FILE):
        with open(SENHA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d.get("hash", _hash_senha(SENHA_PADRAO))
    return _hash_senha(SENHA_PADRAO)


def salvar_senha(nova_senha: str):
    with open(SENHA_FILE, "w", encoding="utf-8") as f:
        json.dump({"hash": _hash_senha(nova_senha)}, f)


def verificar_senha(senha: str) -> bool:
    return _hash_senha(senha) == carregar_senha_hash()


# ─────────────────────────────────────────────
# DADOS DE CENÁRIOS
# ─────────────────────────────────────────────
CENARIOS = {
    "C-01": {
        "titulo": "Criação sem uso de recursos do IFAC",
        "titularidade": "Titularidade do Empreendimento (100%)",
        "instrumentos": ["Declaração de PI pré-existente", "Parecer da COPII"],
        "base_legal": "Art. 28 do Regimento; Art. 11, Lei 10.973/2004",
        "obrigacoes": "Apresentar declaração formal de que a criação é anterior ou independente de recursos do IFAC.",
        "checklist": ["Declaração de PI"],
    },
    "C-02": {
        "titulo": "Criação pelo empreendedor com recursos do IFAC",
        "titularidade": "IFAC (titular) ou cotitularidade IFAC + Empreendimento",
        "instrumentos": ["Instrumento de cotitularidade ou cessão", "TASI"],
        "base_legal": "Art. 26–27 do Regimento; Art. 16, Res. 99/2022",
        "obrigacoes": "Emitir Comunicado de Invenção ao NIT; formalizar instrumento de cotitularidade ou cessão.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "Termo de Confidencialidade/NDA"],
    },
    "C-03": {
        "titulo": "Criação com servidor/pesquisador do IFAC",
        "titularidade": "IFAC (titular) — servidor como coautor/inventor",
        "instrumentos": ["Instrumento de cotitularidade", "Reconhecimento formal de autoria"],
        "base_legal": "Art. 26 do Regimento; Art. 16, §4º, Res. 99/2022",
        "obrigacoes": "Emitir Comunicado de Invenção; registrar contribuição do servidor; formalizar cotitularidade.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "Termo de Confidencialidade/NDA"],
    },
    "C-04": {
        "titulo": "Criação por estudante/bolsista com recursos do IFAC",
        "titularidade": "IFAC (titular) — criador reconhecido como inventor/autor",
        "instrumentos": ["Comunicado de Invenção ao NIT", "Instrumento de cessão"],
        "base_legal": "Art. 16, §§5º e 6º, Res. 99/2022",
        "obrigacoes": "Comunicar invenção ao NIT em até 30 dias; celebrar instrumento de cessão com o IFAC.",
        "checklist": ["Comunicado de Invenção", "Termo de Confidencialidade/NDA"],
    },
    "C-05": {
        "titulo": "Parceria formal IFAC + Empreendimento",
        "titularidade": "Cotitularidade IFAC + Empreendimento",
        "instrumentos": ["Acordo de Parceria PD&I"],
        "base_legal": "Arts. 27 e 29 do Regimento; Decreto 9.283/2018",
        "obrigacoes": "Formalizar Acordo de Parceria PD&I antes do início das atividades; registrar cotitularidade.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "Acordo de Parceria PD&I", "Termo de Confidencialidade/NDA"],
    },
    "C-06": {
        "titulo": "Derivação de tecnologia existente do IFAC",
        "titularidade": "IFAC (titular da tecnologia-base) — licenciamento necessário",
        "instrumentos": ["Contrato de Licenciamento ou TT"],
        "base_legal": "Art. 30, Res. 99/2022; Art. 54 do Regimento",
        "obrigacoes": "Celebrar Contrato de Licenciamento ou Transferência de Tecnologia com o IFAC antes de usar a tecnologia-base.",
        "checklist": ["Contrato de Licenciamento/TT", "Termo de Confidencialidade/NDA"],
    },
    "C-07": {
        "titulo": "Aperfeiçoamento de tecnologia pré-existente com recursos do IFAC",
        "titularidade": "Cotitularidade IFAC + Empreendimento para aperfeiçoamento",
        "instrumentos": ["Declaração de anterioridade", "Instrumento de cotitularidade"],
        "base_legal": "Art. 27 do Regimento",
        "obrigacoes": "Declarar anterioridade da tecnologia original; formalizar cotitularidade do aperfeiçoamento.",
        "checklist": ["Instrumento de Cotitularidade", "Termo de Confidencialidade/NDA"],
    },
    "C-08": {
        "titulo": "Criação por servidor/pesquisador com possível licenciamento preferencial",
        "titularidade": "IFAC (titular) — possível licenciamento preferencial ao criador",
        "instrumentos": ["Comunicado de Invenção", "Instrumento de licenciamento"],
        "base_legal": "Art. 16, §§4º–6º, Res. 99/2022",
        "obrigacoes": "Emitir Comunicado de Invenção; avaliar concessão de licença preferencial ao criador.",
        "checklist": ["Comunicado de Invenção", "Termo de Confidencialidade/NDA"],
    },
    "C-09": {
        "titulo": "Bioeconomia amazônica sem recursos do IFAC",
        "titularidade": "Empreendimento (100%) + obrigações de biodiversidade",
        "instrumentos": ["Declaração de anterioridade", "SisGen"],
        "base_legal": "Art. 30, §3º do Regimento; Lei 13.123/2015",
        "obrigacoes": "Realizar cadastro no SisGen antes de qualquer acesso ao patrimônio genético. Cumprir obrigações da Lei 13.123/2015.",
        "checklist": ["Declaração de PI", "SisGen", "Termo de Confidencialidade/NDA"],
    },
    "C-10": {
        "titulo": "Bioeconomia amazônica com recursos do IFAC",
        "titularidade": "Cotitularidade IFAC + Empreendimento",
        "instrumentos": ["Instrumento de cotitularidade", "SisGen", "Repartição de benefícios"],
        "base_legal": "Arts. 30–31 do Regimento; Lei 13.123/2015",
        "obrigacoes": "Registrar no SisGen antes de publicação/depósito/comercialização. Formalizar repartição de benefícios.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "SisGen", "Termo de Confidencialidade/NDA"],
    },
    "C-11": {
        "titulo": "Bioeconomia com conhecimento tradicional de comunidade",
        "titularidade": "Cotitularidade + repartição de benefícios com comunidade",
        "instrumentos": ["Cotitularidade", "Acordo de Repartição", "CTA", "SisGen"],
        "base_legal": "Arts. 23, 43 do Regimento; Lei 13.123/2015; Protocolo de Nagoya",
        "obrigacoes": "Obter Consentimento Prévio Informado (CTA) da comunidade. Registrar no SisGen. Formalizar acordo de repartição de benefícios.",
        "checklist": ["Instrumento de Cotitularidade", "SisGen", "Acordo de Repartição + CTA", "Termo de Confidencialidade/NDA"],
    },
    "C-12": {
        "titulo": "Software com recursos do IFAC",
        "titularidade": "IFAC (titular) ou cotitularidade",
        "instrumentos": ["Comunicado de Invenção", "Registro INPI (Lei 9.609/98)"],
        "base_legal": "Art. 57 do Regimento; Lei 9.609/1998",
        "obrigacoes": "Comunicar imediatamente ao NIT. Não divulgar sem licença. Solicitar registro no INPI.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "Termo de Confidencialidade/NDA"],
    },
    "C-13": {
        "titulo": "Cultivar com recursos do IFAC",
        "titularidade": "IFAC (titular) ou cotitularidade",
        "instrumentos": ["Comunicado de Invenção", "Pedido de Proteção de Cultivar MAPA/CVRD"],
        "base_legal": "Art. 22, VII do Regimento; Lei 9.456/1997",
        "obrigacoes": "Comunicar invenção ao NIT em 30 dias. Não comercializar sem proteção. Registrar SisGen se houver patrimônio genético.",
        "checklist": ["Comunicado de Invenção", "Instrumento de Cotitularidade", "Termo de Confidencialidade/NDA"],
    },
    "C-14": {
        "titulo": "Marca do empreendimento",
        "titularidade": "Empreendimento (100%)",
        "instrumentos": ["Declaração de PI pré-existente", "Proibição de uso indevido da marca IFAC"],
        "base_legal": "Arts. 40, 53 do Regimento; Lei 9.279/1996",
        "obrigacoes": "Registrar marca antes do uso comercial. Proibido uso de elementos da marca IFAC sem autorização.",
        "checklist": ["Declaração de PI", "Termo de Confidencialidade/NDA"],
    },
    "C-15": {
        "titulo": "Uso indevido de marca/infrações",
        "titularidade": "Não gera PI — configura infração",
        "instrumentos": ["Notificação formal", "Rescisão do TASI"],
        "base_legal": "Arts. 40, 51, 53 do Regimento; Res. 190/2024",
        "obrigacoes": "ATENÇÃO: Situação configura infração ao Regimento. O IFAC deverá ser notificado formalmente. Pode acarretar rescisão do TASI.",
        "checklist": ["Notificação formal"],
    },
    "C-16": {
        "titulo": "Parceria com outra ICT",
        "titularidade": "Cotitularidade IFAC + outra ICT",
        "instrumentos": ["Acordo de Parceria entre ICTs", "Instrumento de cotitularidade"],
        "base_legal": "Art. 29, Res. 99/2022; Decreto 9.283/2018, art. 37",
        "obrigacoes": "Formalizar Acordo de Parceria entre as ICTs antes do início das atividades. Definir cotitularidade proporcional.",
        "checklist": ["Instrumento de Cotitularidade", "Acordo de Parceria PD&I", "Termo de Confidencialidade/NDA"],
    },
    "C-17": {
        "titulo": "Criação anterior à incubação (PI pré-existente)",
        "titularidade": "Empreendimento (100%)",
        "instrumentos": ["Declaração formal de PI pré-existente"],
        "base_legal": "Art. 36 do Regimento; Art. 49, §3º do Regimento",
        "obrigacoes": "Apresentar declaração formal de anterioridade antes da assinatura do TASI.",
        "checklist": ["Declaração de PI", "Termo de Confidencialidade/NDA"],
    },
    "C-18": {
        "titulo": "PI pré-existente aperfeiçoada com recursos do IFAC",
        "titularidade": "Cotitularidade para aperfeiçoamento",
        "instrumentos": ["Declaração de anterioridade", "Instrumento de cotitularidade"],
        "base_legal": "Art. 36, §3º do Regimento",
        "obrigacoes": "Declarar anterioridade da tecnologia original. Formalizar cotitularidade do aperfeiçoamento realizado com recursos do IFAC.",
        "checklist": ["Instrumento de Cotitularidade", "Declaração de PI", "Termo de Confidencialidade/NDA"],
    },
    "C-19": {
        "titulo": "Know-how / Segredo industrial",
        "titularidade": "Titularidade ou cotitularidade do IFAC — proteção via sigilo/NDA",
        "instrumentos": ["Termo de Confidencialidade", "Cláusula no TASI"],
        "base_legal": "Art. 22, IX do Regimento; Art. 2, XXXII, Res. 99/2022",
        "obrigacoes": "Manter sigilo imediato. Não divulgar a terceiros sem autorização. Celebrar NDA com todos os envolvidos.",
        "checklist": ["Termo de Confidencialidade/NDA"],
    },
    "C-20": {
        "titulo": "Indicação Geográfica (IG)",
        "titularidade": "Coletivo de produtores (IG coletiva)",
        "instrumentos": ["Acordo de parceria técnica", "Orientação ao registro no INPI"],
        "base_legal": "Art. 22, VIII do Regimento; Lei 9.279/1996, arts. 177–182",
        "obrigacoes": "A IG é de natureza coletiva. Não pode ser registrada individualmente. Orientar produtores para registro coletivo no INPI.",
        "checklist": ["Termo de Confidencialidade/NDA"],
    },
}

REPARTICAO_GANHOS = {
    "PI exclusiva do IFAC": "1/3 ao criador · 1/3 ao campus · 1/3 ao NIT",
    "Cotitularidade": "Proporcional conforme instrumento de cotitularidade",
    "PI exclusiva do Empreendimento": "100% ao empreendimento",
    "Licenciamento": "Empreendimento paga royalties ao IFAC conforme contrato",
    "Bioeconomia/CTA": "Percentual reservado à comunidade tradicional (Lei 13.123/2015)",
}

OBRIGACOES_TIPO = {
    "Patente": "Prazo: 30 dias. Vedação: publicação antes do depósito.",
    "Marca": "Prazo: antes do uso comercial. Vedação: uso indevido da marca IFAC.",
    "Software": "Prazo: imediato. Vedação: divulgação sem licença.",
    "Cultivar": "Prazo: 30 dias. SisGen obrigatório se houver PG. Vedação: comercialização sem proteção.",
    "Bioativo com PG": "Prazo: imediato. SisGen obrigatório antes de publicação/depósito/comercialização.",
    "Know-how": "Prazo: imediato. Vedação: divulgação a terceiros sem autorização.",
    "Conhecimento Tradicional": "Prazo: imediato. SisGen + CNCT obrigatórios. Vedação: exploração sem consentimento.",
    "IG": "Não se aplica individualmente. Vedação: uso individualizado de IG coletiva.",
}

NUCLEOS = [
    "Selecione...",
    "Campus Rio Branco",
    "Campus Cruzeiro do Sul",
    "Campus Sena Madureira",
    "Campus Tarauacá",
    "Campus Feijó",
    "Campus Xapuri",
    "Campus Brasileia",
    "Campus Placas",
    "Outro",
]

# ─────────────────────────────────────────────
# LÓGICA DE CENÁRIO
# ─────────────────────────────────────────────

def identificar_cenario(respostas: dict) -> list:
    """
    Retorna uma lista de cenários identificados com base nas respostas do wizard.
    """
    cenarios = []

    b1 = respostas.get("bloco1", {})
    b2 = respostas.get("bloco2", {})
    b3 = respostas.get("bloco3", {})
    b4 = respostas.get("bloco4", {})
    b5 = respostas.get("bloco5", {})
    b6 = respostas.get("bloco6", {})

    # BLOCO 1 — Origem
    criacao_anterior = b1.get("C-01_anterior", "")
    aperfeicoamento = b1.get("C-18_aperfeicoamento", "")
    uso_recursos_anterior = b1.get("C-18_recursos", "")

    if criacao_anterior == "Sim":
        if uso_recursos_anterior == "Sim" or aperfeicoamento == "Sim":
            cenarios.append("C-18")
        else:
            cenarios.append("C-17")
        # Continua verificando outros blocos
    else:
        # BLOCO 2 — Recursos do IFAC
        uso_recursos = b2.get("C-02_uso_recursos", "")
        if uso_recursos == "Não":
            cenarios.append("C-01")
        elif uso_recursos == "Sim":
            contribuidor = b2.get("C-02_contribuidor", "")
            if contribuidor == "Só o empreendedor com recursos do IFAC":
                cenarios.append("C-02")
            elif contribuidor == "Empreendedor + servidor/pesquisador do IFAC":
                cenarios.append("C-03")
            elif contribuidor == "Estudante/bolsista com recursos do IFAC":
                cenarios.append("C-04")
            elif contribuidor == "IFAC e empreendimento em parceria formal (PD&I)":
                cenarios.append("C-05")
            elif contribuidor == "Derivado de tecnologia já existente do IFAC":
                cenarios.append("C-06")

            # Aperfeiçoamento com recursos?
            aper_recursos = b2.get("C-07_aperfeicoamento", "")
            if aper_recursos == "Sim" and "C-06" not in cenarios:
                cenarios.append("C-07")

            # Servidor como titular preferencial?
            lic_pref = b2.get("C-08_licenciamento", "")
            if lic_pref == "Sim" and "C-03" not in cenarios:
                cenarios.append("C-08")

    # BLOCO 3 — Bioeconomia
    bioeco = b3.get("C-09_bioeconomia", "")
    bioeco_recursos = b3.get("C-10_recursos", "")
    bioeco_ct = b3.get("C-11_conhecimento", "")

    if bioeco == "Sim":
        if bioeco_ct == "Sim":
            cenarios.append("C-11")
        elif bioeco_recursos == "Sim":
            cenarios.append("C-10")
        else:
            cenarios.append("C-09")

    # BLOCO 4 — Tipo específico
    tipo_ativo = b4.get("C-12_tipo_ativo", "")
    if tipo_ativo == "Software":
        cenarios.append("C-12")
    elif tipo_ativo == "Cultivar":
        cenarios.append("C-13")
    elif tipo_ativo == "Marca":
        cenarios.append("C-14")
    elif tipo_ativo == "Know-how / Segredo industrial":
        cenarios.append("C-19")
    elif tipo_ativo == "Indicação Geográfica (IG)":
        cenarios.append("C-20")

    # BLOCO 5 — Infrações
    infracao = b5.get("C-15_infracao", "")
    if infracao == "Sim":
        cenarios.append("C-15")

    # BLOCO 6 — Parceria ICT
    parceria = b6.get("C-16_parceria", "")
    if parceria == "Sim":
        cenarios.append("C-16")

    # Deduplicar mantendo ordem
    seen = set()
    result = []
    for c in cenarios:
        if c not in seen:
            seen.add(c)
            result.append(c)

    return result if result else ["C-01"]


# ─────────────────────────────────────────────
# GERAÇÃO DE PDF
# ─────────────────────────────────────────────

def gerar_pdf(diagnostico: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Tenta usar fonte UTF-8 disponível, fallback para latin
    try:
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True)
        FONTE = "DejaVu"
    except Exception:
        FONTE = "Helvetica"

    def header_section(title, r=200, g=16, b=46):
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(FONTE, "B", 11)
        pdf.cell(0, 9, title, border=0, ln=1, fill=True, align="L")
        pdf.set_text_color(30, 30, 30)
        pdf.ln(1)

    def row(label, value):
        pdf.set_font(FONTE, "B", 9)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(55, 7, label + ":", border=0, ln=0, fill=True)
        pdf.set_font(FONTE, "", 9)
        pdf.set_fill_color(255, 255, 255)
        pdf.multi_cell(0, 7, str(value), border=0, fill=False)

    # Cabeçalho
    pdf.set_fill_color(200, 16, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(FONTE, "B", 16)
    pdf.cell(0, 14, "CLASS PI — INCUBAC/IFAC", border=0, ln=1, fill=True, align="C")
    pdf.set_font(FONTE, "", 10)
    pdf.set_fill_color(0, 132, 61)
    pdf.cell(0, 8, "Relatório de Diagnóstico de Propriedade Intelectual", border=0, ln=1, fill=True, align="C")
    pdf.ln(4)

    # Dados do respondente
    pdf.set_text_color(30, 30, 30)
    header_section("1. DADOS DO RESPONDENTE")
    info = diagnostico.get("info", {})
    row("Nome", info.get("nome", "-"))
    row("Empreendimento", info.get("empreendimento", "-"))
    row("E-mail", info.get("email", "-"))
    row("Núcleo Incubador", info.get("nucleo", "-"))
    row("Data do Diagnóstico", info.get("data", "-"))
    pdf.ln(4)

    # Cenários identificados
    cenarios_ids = diagnostico.get("cenarios", [])
    header_section("2. CENÁRIO(S) IDENTIFICADO(S)", 0, 100, 60)
    if cenarios_ids:
        for cid in cenarios_ids:
            c = CENARIOS.get(cid, {})
            pdf.set_font(FONTE, "B", 10)
            pdf.set_text_color(200, 16, 46)
            pdf.cell(0, 8, f"{cid}: {c.get('titulo', '')}", ln=1)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font(FONTE, "", 9)
            row("  Titularidade", c.get("titularidade", "-"))
            row("  Base Legal", c.get("base_legal", "-"))
            row("  Obrigações", c.get("obrigacoes", "-"))
            pdf.ln(2)
    else:
        pdf.set_font(FONTE, "", 9)
        pdf.cell(0, 8, "Nenhum cenário identificado.", ln=1)
    pdf.ln(4)

    # Instrumentos obrigatórios
    header_section("3. INSTRUMENTOS OBRIGATÓRIOS", 30, 30, 150)
    for cid in cenarios_ids:
        c = CENARIOS.get(cid, {})
        if c.get("instrumentos"):
            pdf.set_font(FONTE, "B", 9)
            pdf.set_text_color(60, 60, 200)
            pdf.cell(0, 7, f"  [{cid}]", ln=1)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font(FONTE, "", 9)
            for instr in c["instrumentos"]:
                pdf.cell(10, 6, "", ln=0)
                pdf.cell(0, 6, f"• {instr}", ln=1)
    pdf.ln(4)

    # Repartição de ganhos
    header_section("4. REPARTIÇÃO DE GANHOS (conforme regulamento)", 100, 60, 0)
    pdf.set_font(FONTE, "", 9)
    pdf.set_text_color(30, 30, 30)
    for tipo, descr in REPARTICAO_GANHOS.items():
        pdf.set_font(FONTE, "B", 9)
        pdf.cell(0, 6, f"  {tipo}:", ln=1)
        pdf.set_font(FONTE, "", 9)
        pdf.cell(10, 6, "", ln=0)
        pdf.cell(0, 6, descr, ln=1)
    pdf.ln(4)

    # Checklist de documentos
    header_section("5. CHECKLIST DE DOCUMENTOS NECESSÁRIOS", 60, 0, 100)
    todos_docs = set()
    for cid in cenarios_ids:
        c = CENARIOS.get(cid, {})
        for doc in c.get("checklist", []):
            todos_docs.add(doc)
    pdf.set_font(FONTE, "", 9)
    pdf.set_text_color(30, 30, 30)
    if todos_docs:
        for doc in sorted(todos_docs):
            pdf.cell(10, 7, "", ln=0)
            pdf.cell(6, 7, "[ ]", ln=0)
            pdf.cell(0, 7, doc, ln=1)
    else:
        pdf.cell(0, 7, "Nenhum documento específico identificado.", ln=1)
    pdf.ln(4)

    # Obrigações por tipo
    header_section("6. OBRIGAÇÕES POR TIPO DE ATIVO", 0, 80, 120)
    pdf.set_font(FONTE, "", 9)
    pdf.set_text_color(30, 30, 30)
    for tipo, descr in OBRIGACOES_TIPO.items():
        pdf.set_font(FONTE, "B", 9)
        pdf.cell(0, 6, f"  {tipo}:", ln=1)
        pdf.set_font(FONTE, "", 9)
        pdf.cell(10, 6, "", ln=0)
        pdf.multi_cell(0, 6, descr, ln=1)
    pdf.ln(4)

    # Respostas detalhadas
    header_section("7. RESPOSTAS DETALHADAS DO DIAGNÓSTICO", 40, 40, 40)
    pdf.set_font(FONTE, "", 8)
    pdf.set_text_color(30, 30, 30)
    blocos_labels = {
        "bloco1": "Bloco 1 — Origem da Criação",
        "bloco2": "Bloco 2 — Uso de Recursos do IFAC",
        "bloco3": "Bloco 3 — Bioeconomia Amazônica",
        "bloco4": "Bloco 4 — Tipos Específicos de Ativos",
        "bloco5": "Bloco 5 — Infrações",
        "bloco6": "Bloco 6 — Parcerias Institucionais",
    }
    for bkey, blabel in blocos_labels.items():
        bd = diagnostico.get("respostas", {}).get(bkey, {})
        if bd:
            pdf.set_font(FONTE, "B", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 7, f"  {blabel}", ln=1)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font(FONTE, "", 8)
            for k, v in bd.items():
                if v:
                    pdf.cell(10, 5, "", ln=0)
                    pdf.multi_cell(0, 5, f"• {k}: {v}")
            pdf.ln(1)
    pdf.ln(4)

    # Rodapé
    pdf.set_font(FONTE, "", 7)
    pdf.set_text_color(120, 120, 120)
    footer = (
        "© INCUBAC/IFAC · Regimento Interno dos Núcleos Incubadores · Res. CONSU/IFAC nº 99/2022 · "
        "Esta ferramenta de classificador de cenários de PI foi desenvolvida a partir da disciplina de "
        "oficina profissional por discente de mestrado do PROFNIT."
    )
    pdf.multi_cell(0, 4, footer, align="C")

    return bytes(pdf.output())


def pdf_download_link(pdf_bytes: bytes, filename: str, label: str) -> str:
    b64 = base64.b64encode(pdf_bytes).decode()
    return (
        f'<a href="data:application/pdf;base64,{b64}" download="{filename}" '
        f'style="background:#C8102E;color:#fff;padding:8px 18px;border-radius:6px;'
        f'text-decoration:none;font-weight:600;">{label}</a>'
    )


# ─────────────────────────────────────────────
# INICIALIZAÇÃO DE SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "modulo": "respondente",          # "respondente" | "gestor"
        "gestor_autenticado": False,
        "bloco_atual": 0,                  # 0=dados pessoais, 1–6=blocos, 7=resultado
        "respostas": {
            "bloco1": {},
            "bloco2": {},
            "bloco3": {},
            "bloco4": {},
            "bloco5": {},
            "bloco6": {},
        },
        "info": {
            "nome": "",
            "empreendimento": "",
            "email": "",
            "nucleo": "Selecione...",
        },
        "pular_confirmacao": None,          # bloco sendo pulado (aguarda confirmação)
        "envio_confirmado": False,
        "diagnostico_enviado": None,
        "trocar_senha_mode": False,
        "detalhe_idx": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
<div class="ifac-header">
  <h1>⚖️ CLASS PI</h1>
  <p>Classificador de Cenários de Propriedade Intelectual · INCUBAC/IFAC</p>
</div>
""",
    unsafe_allow_html=True,
)

# Barra de navegação superior
col_nav1, col_nav2, col_nav3 = st.columns([6, 2, 2])
with col_nav3:
    if not st.session_state.gestor_autenticado:
        if st.button("🔐 Painel de Gestão", key="btn_painel"):
            st.session_state.modulo = "login_gestor"
            st.rerun()
    else:
        if st.button("👤 Sair do Painel", key="btn_sair_gestor"):
            st.session_state.gestor_autenticado = False
            st.session_state.modulo = "respondente"
            st.rerun()

with col_nav2:
    if st.session_state.modulo != "respondente" and not st.session_state.gestor_autenticado:
        if st.button("← Formulário", key="btn_volta_form"):
            st.session_state.modulo = "respondente"
            st.rerun()

st.markdown('<div class="main-content-pad">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO: LOGIN GESTOR
# ─────────────────────────────────────────────
def modulo_login_gestor():
    st.markdown("### 🔐 Painel de Gestão — Autenticação")
    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)

    with st.form("form_login"):
        senha_input = st.text_input("Senha de acesso", type="password", placeholder="Digite a senha")
        submit = st.form_submit_button("Entrar")
        if submit:
            if verificar_senha(senha_input):
                st.session_state.gestor_autenticado = True
                st.session_state.modulo = "gestor"
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO: GESTOR
# ─────────────────────────────────────────────
def modulo_gestor():
    st.markdown("## 📊 Painel de Gestão — Diagnósticos")

    # Barra de ações do gestor
    col_g1, col_g2 = st.columns([4, 2])
    with col_g2:
        if st.button("🔑 Criar nova senha", key="btn_trocar_senha"):
            st.session_state.trocar_senha_mode = not st.session_state.get("trocar_senha_mode", False)
            st.rerun()

    # Troca de senha
    if st.session_state.get("trocar_senha_mode", False):
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### Alterar senha de acesso")
        with st.form("form_nova_senha"):
            nova1 = st.text_input("Nova senha", type="password")
            nova2 = st.text_input("Confirmar nova senha", type="password")
            salvar_btn = st.form_submit_button("Salvar nova senha")
            if salvar_btn:
                if not nova1:
                    st.error("A senha não pode ser vazia.")
                elif nova1 != nova2:
                    st.error("As senhas não coincidem.")
                elif len(nova1) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                else:
                    salvar_senha(nova1)
                    st.session_state.trocar_senha_mode = False
                    st.markdown('<div class="alert-success">✅ Senha alterada com sucesso!</div>', unsafe_allow_html=True)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Lista de diagnósticos
    dados = carregar_respostas()
    if not dados:
        st.markdown('<div class="alert-info">ℹ️ Nenhum diagnóstico enviado ainda.</div>', unsafe_allow_html=True)
        return

    st.markdown(f"**Total de diagnósticos:** {len(dados)}")
    st.markdown("---")

    for i, diag in enumerate(reversed(dados)):
        idx_real = len(dados) - 1 - i
        info = diag.get("info", {})
        cenarios_ids = diag.get("cenarios", [])
        cenarios_str = ", ".join(cenarios_ids) if cenarios_ids else "—"

        with st.expander(
            f"#{idx_real + 1} · {info.get('nome', 'Sem nome')} · "
            f"{info.get('empreendimento', '—')} · {info.get('data', '—')} · Cenários: {cenarios_str}"
        ):
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                st.markdown(
                    f"""
<div class="detalhe-row"><span class="detalhe-label">Nome</span><span class="detalhe-valor">{info.get('nome', '—')}</span></div>
<div class="detalhe-row"><span class="detalhe-label">Empreendimento</span><span class="detalhe-valor">{info.get('empreendimento', '—')}</span></div>
<div class="detalhe-row"><span class="detalhe-label">E-mail</span><span class="detalhe-valor">{info.get('email', '—')}</span></div>
<div class="detalhe-row"><span class="detalhe-label">Núcleo Incubador</span><span class="detalhe-valor">{info.get('nucleo', '—')}</span></div>
<div class="detalhe-row"><span class="detalhe-label">Data</span><span class="detalhe-valor">{info.get('data', '—')}</span></div>
<div class="detalhe-row"><span class="detalhe-label">Cenário(s) Identificado(s)</span><span class="detalhe-valor" style="color:#ff8096;font-weight:700;">{cenarios_str}</span></div>
""",
                    unsafe_allow_html=True,
                )
                # Títulos dos cenários
                for cid in cenarios_ids:
                    c = CENARIOS.get(cid, {})
                    st.markdown(
                        f'<div class="detalhe-row"><span class="detalhe-label" style="padding-left:16px">{cid}</span>'
                        f'<span class="detalhe-valor" style="color:#aaddff">{c.get("titulo","")}</span></div>',
                        unsafe_allow_html=True,
                    )

            with col_d2:
                # Gerar PDF
                try:
                    pdf_bytes = gerar_pdf(diag)
                    fname = f"ClassPI_{info.get('nome','diag').replace(' ','_')}_{info.get('data','').replace('/','')}.pdf"
                    link = pdf_download_link(pdf_bytes, fname, "⬇️ Baixar PDF")
                    st.markdown(link, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

            # Respostas detalhadas
            st.markdown("**Respostas do diagnóstico:**")
            blocos_labels = {
                "bloco1": "Bloco 1 — Origem da Criação",
                "bloco2": "Bloco 2 — Uso de Recursos do IFAC",
                "bloco3": "Bloco 3 — Bioeconomia Amazônica",
                "bloco4": "Bloco 4 — Tipos Específicos de Ativos",
                "bloco5": "Bloco 5 — Infrações",
                "bloco6": "Bloco 6 — Parcerias Institucionais",
            }
            for bkey, blabel in blocos_labels.items():
                bd = diag.get("respostas", {}).get(bkey, {})
                if bd:
                    st.markdown(f"*{blabel}*")
                    for k, v in bd.items():
                        if v:
                            st.markdown(f"&nbsp;&nbsp;• **{k}:** {v}", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO: RESPONDENTE — HELPERS
# ─────────────────────────────────────────────

BLOCOS_INFO = [
    {"id": 0, "nome": "Dados do Respondente", "icon": "👤"},
    {"id": 1, "nome": "Bloco 1 — Origem da Criação", "icon": "📌"},
    {"id": 2, "nome": "Bloco 2 — Uso de Recursos do IFAC", "icon": "🏛️"},
    {"id": 3, "nome": "Bloco 3 — Bioeconomia Amazônica", "icon": "🌿"},
    {"id": 4, "nome": "Bloco 4 — Tipos Específicos de Ativos", "icon": "💼"},
    {"id": 5, "nome": "Bloco 5 — Infrações", "icon": "⚠️"},
    {"id": 6, "nome": "Bloco 6 — Parcerias Institucionais", "icon": "🤝"},
    {"id": 7, "nome": "Resultado", "icon": "✅"},
]
TOTAL_BLOCOS = 7  # 0 a 7


def barra_progresso(bloco_atual):
    pct = int((bloco_atual / TOTAL_BLOCOS) * 100)
    st.markdown(
        f"""
<div style="margin-bottom:6px;color:#aaa;font-size:0.85rem;">
  Etapa {bloco_atual} de {TOTAL_BLOCOS} — {BLOCOS_INFO[min(bloco_atual, 7)]['icon']} {BLOCOS_INFO[min(bloco_atual, 7)]['nome']}
</div>
<div class="progress-bar-outer">
  <div class="progress-bar-inner" style="width:{pct}%;"></div>
</div>
""",
        unsafe_allow_html=True,
    )


def botoes_bloco(bloco_key: str, bloco_id: int):
    """Renderiza botões Limpar / Pular na lateral. Retorna (limpar_clicado, pular_clicado)."""
    c1, c2, c3 = st.columns([3, 1, 1])
    limpar = False
    pular = False
    with c2:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("🧹 Limpar Respostas", key=f"limpar_{bloco_key}_{bloco_id}"):
            limpar = True
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="btn-warning">', unsafe_allow_html=True)
        if st.button("⏭️ Pular Bloco", key=f"pular_{bloco_key}_{bloco_id}"):
            pular = True
        st.markdown('</div>', unsafe_allow_html=True)
    return limpar, pular


def confirmacao_pular(bloco_id: int):
    """Exibe popup de confirmação de pular bloco. Retorna True se confirmado."""
    st.markdown(
        '<div class="alert-warning">⚠️ <b>Deseja realmente pular este bloco?</b><br>'
        "Algumas perguntas podem ser obrigatórias para a correta identificação do cenário de PI.</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-warning">', unsafe_allow_html=True)
        if st.button("Sim, pular bloco", key=f"confirmar_pular_{bloco_id}"):
            return True
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("Cancelar", key=f"cancelar_pular_{bloco_id}"):
            st.session_state.pular_confirmacao = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    return False


# ─────────────────────────────────────────────
# DADOS PESSOAIS (Etapa 0)
# ─────────────────────────────────────────────
def etapa_dados_pessoais():
    barra_progresso(0)
    st.markdown('<div class="bloco-title"><h2>👤 Dados do Respondente</h2></div>', unsafe_allow_html=True)

    info = st.session_state.info

    nome = st.text_input(
        "Nome completo *",
        value=info.get("nome", ""),
        placeholder="Digite seu nome completo",
        key="dp_nome",
    )
    empreendimento = st.text_input(
        "Nome do empreendimento / startup *",
        value=info.get("empreendimento", ""),
        placeholder="Nome do seu negócio",
        key="dp_empreendimento",
    )
    email = st.text_input(
        "E-mail *",
        value=info.get("email", ""),
        placeholder="seu@email.com",
        key="dp_email",
    )
    nucleo = st.selectbox(
        "Núcleo Incubador *",
        options=NUCLEOS,
        index=NUCLEOS.index(info.get("nucleo", "Selecione...")) if info.get("nucleo", "Selecione...") in NUCLEOS else 0,
        key="dp_nucleo",
    )

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="btn-green">', unsafe_allow_html=True)
    if st.button("Iniciar Diagnóstico →", key="btn_iniciar"):
        erros = []
        if not nome.strip():
            erros.append("Nome completo")
        if not empreendimento.strip():
            erros.append("Empreendimento")
        if not email.strip() or "@" not in email:
            erros.append("E-mail válido")
        if nucleo == "Selecione...":
            erros.append("Núcleo Incubador")
        if erros:
            st.error(f"Preencha os campos obrigatórios: {', '.join(erros)}")
        else:
            st.session_state.info = {
                "nome": nome.strip(),
                "empreendimento": empreendimento.strip(),
                "email": email.strip(),
                "nucleo": nucleo,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            st.session_state.bloco_atual = 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 1 — Origem da Criação
# ─────────────────────────────────────────────
def bloco1():
    barra_progresso(1)
    st.markdown('<div class="bloco-title"><h2>📌 Bloco 1 — Origem da Criação</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b1", 1)
    if limpar:
        st.session_state.respostas["bloco1"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 1
        st.rerun()

    if st.session_state.pular_confirmacao == 1:
        if confirmacao_pular(1):
            st.session_state.respostas["bloco1"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 2
            st.rerun()
        return

    b1 = st.session_state.respostas["bloco1"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-01 / C-17 — Momento da Criação")
    st.markdown("Esta seção identifica se a criação intelectual surgiu antes ou durante a incubação.")

    b1["C-01_anterior"] = st.radio(
        "A criação (tecnologia, produto, processo, marca, software etc.) foi desenvolvida ANTES do início da incubação no IFAC? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b1.get("C-01_anterior", "Selecione...")),
        key="b1_anterior",
    )

    if b1.get("C-01_anterior") == "Sim":
        st.markdown(
            '<div class="alert-info">ℹ️ Se a criação é anterior, responda as próximas questões sobre aperfeiçoamento.</div>',
            unsafe_allow_html=True,
        )
        b1["C-18_aperfeicoamento"] = st.radio(
            "C-18: Após o início da incubação, a criação pré-existente foi significativamente APERFEIÇOADA ou modificada? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b1.get("C-18_aperfeicoamento", "Selecione...")),
            key="b1_aper",
        )
        if b1.get("C-18_aperfeicoamento") == "Sim":
            b1["C-18_recursos"] = st.radio(
                "C-18: Esse aperfeiçoamento utilizou recursos do IFAC (laboratório, equipamentos, orientação, bolsa)? *",
                options=["Selecione...", "Sim", "Não"],
                index=["Selecione...", "Sim", "Não"].index(b1.get("C-18_recursos", "Selecione...")),
                key="b1_aper_rec",
            )
        else:
            b1.pop("C-18_recursos", None)
    else:
        b1.pop("C-18_aperfeicoamento", None)
        b1.pop("C-18_recursos", None)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # Botões de navegação
    col_nav_a, col_nav_b = st.columns([1, 5])
    with col_nav_b:
        limpar2, _ = botoes_bloco("b1_bot", 10)
        if limpar2:
            st.session_state.respostas["bloco1"] = {}
            st.rerun()

    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b1_voltar"):
            st.session_state.bloco_atual = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b1_avancar"):
            erros = []
            if b1.get("C-01_anterior", "Selecione...") == "Selecione...":
                erros.append("Pergunta C-01/C-17 (criação anterior à incubação)")
            if b1.get("C-01_anterior") == "Sim":
                if b1.get("C-18_aperfeicoamento", "Selecione...") == "Selecione...":
                    erros.append("C-18: Houve aperfeiçoamento?")
                if b1.get("C-18_aperfeicoamento") == "Sim" and b1.get("C-18_recursos", "Selecione...") == "Selecione...":
                    erros.append("C-18: Aperfeiçoamento usou recursos do IFAC?")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 2
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 2 — Uso de Recursos do IFAC
# ─────────────────────────────────────────────
def bloco2():
    barra_progresso(2)
    st.markdown('<div class="bloco-title"><h2>🏛️ Bloco 2 — Uso de Recursos do IFAC</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b2", 2)
    if limpar:
        st.session_state.respostas["bloco2"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 2
        st.rerun()

    if st.session_state.pular_confirmacao == 2:
        if confirmacao_pular(2):
            st.session_state.respostas["bloco2"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 3
            st.rerun()
        return

    b2 = st.session_state.respostas["bloco2"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-02 — Uso de Recursos Institucionais do IFAC")

    b2["C-02_uso_recursos"] = st.radio(
        "Para o desenvolvimento desta criação, foram utilizados recursos do IFAC (laboratórios, equipamentos, infraestrutura, orientação de servidores, bolsas institucionais)? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b2.get("C-02_uso_recursos", "Selecione...")),
        key="b2_uso",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if b2.get("C-02_uso_recursos") == "Sim":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-02/C-03/C-04/C-05/C-06 — Contribuição para a Criação")

        contribuidores = [
            "Selecione...",
            "Só o empreendedor com recursos do IFAC",
            "Empreendedor + servidor/pesquisador do IFAC",
            "Estudante/bolsista com recursos do IFAC",
            "IFAC e empreendimento em parceria formal (PD&I)",
            "Derivado de tecnologia já existente do IFAC",
        ]
        b2["C-02_contribuidor"] = st.radio(
            "Quem contribuiu para o desenvolvimento desta criação? *",
            options=contribuidores,
            index=contribuidores.index(b2.get("C-02_contribuidor", "Selecione...")),
            key="b2_contrib",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-07 — Aperfeiçoamento com Recursos do IFAC")

        b2["C-07_aperfeicoamento"] = st.radio(
            "C-07: Esta criação é um aperfeiçoamento de tecnologia/produto pré-existente do empreendimento, desenvolvido com recursos do IFAC? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b2.get("C-07_aperfeicoamento", "Selecione...")),
            key="b2_aper",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-08 — Licenciamento Preferencial")

        b2["C-08_licenciamento"] = st.radio(
            "C-08: O criador (servidor, estudante ou empreendedor) deseja solicitar licenciamento preferencial desta criação ao IFAC? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b2.get("C-08_licenciamento", "Selecione...")),
            key="b2_lic",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-03/C-04/C-05/C-06 — Detalhes do uso de recursos")

        recursos_tipos = [
            "Laboratório / equipamentos",
            "Orientação de servidor/pesquisador do IFAC",
            "Bolsa institucional (PIBIC, PIBITI, etc.)",
            "Infraestrutura de TI/computação",
            "Acesso a base de dados/acervos do IFAC",
            "Financiamento direto (projeto, edital)",
            "Outro",
        ]
        b2["C-05_recursos_tipos"] = st.multiselect(
            "C-03/C-04/C-05: Que tipos de recursos do IFAC foram utilizados? (Selecione todos que se aplicam) *",
            options=recursos_tipos,
            default=b2.get("C-05_recursos_tipos", []),
            key="b2_rec_tipos",
        )

        b2["C-06_tecnologia_base"] = st.radio(
            "C-06: Existe tecnologia-base do IFAC (patente, software, metodologia registrada) que foi ponto de partida para esta criação? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b2.get("C-06_tecnologia_base", "Selecione...")),
            key="b2_tecbase",
        )
        if b2.get("C-06_tecnologia_base") == "Sim":
            b2["C-06_tecnologia_descricao"] = st.text_area(
                "Descreva brevemente a tecnologia-base do IFAC utilizada: *",
                value=b2.get("C-06_tecnologia_descricao", ""),
                placeholder="Ex.: Software de gestão X registrado pelo Campus Y, metodologia Z...",
                key="b2_tecbase_desc",
            )
        else:
            b2.pop("C-06_tecnologia_descricao", None)

        st.markdown('</div>', unsafe_allow_html=True)

    elif b2.get("C-02_uso_recursos") == "Não":
        st.markdown(
            '<div class="alert-success">✅ Sem uso de recursos do IFAC — possível cenário C-01. Continue para verificar outros aspectos.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<br>', unsafe_allow_html=True)
    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b2_voltar"):
            st.session_state.bloco_atual = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b2_avancar"):
            erros = []
            uso = b2.get("C-02_uso_recursos", "Selecione...")
            if uso == "Selecione...":
                erros.append("Uso de recursos do IFAC")
            if uso == "Sim":
                if b2.get("C-02_contribuidor", "Selecione...") == "Selecione...":
                    erros.append("Quem contribuiu para a criação")
                if b2.get("C-07_aperfeicoamento", "Selecione...") == "Selecione...":
                    erros.append("C-07: Aperfeiçoamento com recursos do IFAC")
                if b2.get("C-08_licenciamento", "Selecione...") == "Selecione...":
                    erros.append("C-08: Licenciamento preferencial")
                if not b2.get("C-05_recursos_tipos"):
                    erros.append("Tipos de recursos utilizados")
                if b2.get("C-06_tecnologia_base", "Selecione...") == "Selecione...":
                    erros.append("C-06: Tecnologia-base do IFAC")
                if b2.get("C-06_tecnologia_base") == "Sim" and not b2.get("C-06_tecnologia_descricao", "").strip():
                    erros.append("C-06: Descrição da tecnologia-base")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 3
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 3 — Bioeconomia Amazônica
# ─────────────────────────────────────────────
def bloco3():
    barra_progresso(3)
    st.markdown('<div class="bloco-title"><h2>🌿 Bloco 3 — Bioeconomia Amazônica</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b3", 3)
    if limpar:
        st.session_state.respostas["bloco3"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 3
        st.rerun()

    if st.session_state.pular_confirmacao == 3:
        if confirmacao_pular(3):
            st.session_state.respostas["bloco3"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 4
            st.rerun()
        return

    b3 = st.session_state.respostas["bloco3"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-09 — Envolvimento com Bioeconomia/Biodiversidade Amazônica")
    st.markdown(
        "_Patrimônio genético: material genético de origem vegetal, animal, microbiana ou qualquer "
        "outro tipo com valor real ou potencial (Lei 13.123/2015)._"
    )

    b3["C-09_bioeconomia"] = st.radio(
        "A criação envolve acesso a patrimônio genético (espécies da Amazônia), bioativos, extratos naturais ou recursos da biodiversidade brasileira? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b3.get("C-09_bioeconomia", "Selecione...")),
        key="b3_bio",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if b3.get("C-09_bioeconomia") == "Sim":
        st.markdown(
            '<div class="alert-warning">⚠️ SisGen obrigatório antes de qualquer publicação, depósito de patente ou comercialização (Lei 13.123/2015).</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-10 — Recursos do IFAC + Bioeconomia")

        b3["C-10_recursos"] = st.radio(
            "C-10: O desenvolvimento desta criação com bioativos utilizou recursos do IFAC (laboratório, pesquisa, infraestrutura)? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b3.get("C-10_recursos", "Selecione...")),
            key="b3_rec",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-11 — Conhecimento Tradicional")

        b3["C-11_conhecimento"] = st.radio(
            "C-11: A criação baseia-se ou foi desenvolvida a partir de conhecimento tradicional de comunidade indígena, quilombola ou local? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b3.get("C-11_conhecimento", "Selecione...")),
            key="b3_ct",
        )
        if b3.get("C-11_conhecimento") == "Sim":
            b3["C-11_comunidade"] = st.text_input(
                "Identifique a comunidade tradicional envolvida (nome/localização): *",
                value=b3.get("C-11_comunidade", ""),
                placeholder="Ex.: Comunidade Ribeirinha do Rio Purus, TI Kaxinawá...",
                key="b3_comunidade",
            )
            st.markdown(
                '<div class="alert-warning">⚠️ Obrigatório: Consentimento Prévio Informado (CTA), SisGen e Acordo de Repartição de Benefícios (Protocolo de Nagoya).</div>',
                unsafe_allow_html=True,
            )
        else:
            b3.pop("C-11_comunidade", None)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### Detalhes do Patrimônio Genético")

        b3["C-09_especie"] = st.text_input(
            "Informe a(s) espécie(s) ou recurso(s) genético(s) utilizados: *",
            value=b3.get("C-09_especie", ""),
            placeholder="Ex.: Açaí (Euterpe oleracea), andiroba (Carapa guianensis)...",
            key="b3_especie",
        )

        b3["C-09_sisgen"] = st.radio(
            "Já foi realizado o cadastro no SisGen (Sistema Nacional de Gestão do Patrimônio Genético)? *",
            options=["Selecione...", "Sim", "Não", "Em andamento"],
            index=["Selecione...", "Sim", "Não", "Em andamento"].index(b3.get("C-09_sisgen", "Selecione...")),
            key="b3_sisgen",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif b3.get("C-09_bioeconomia") == "Não":
        b3.pop("C-10_recursos", None)
        b3.pop("C-11_conhecimento", None)
        b3.pop("C-11_comunidade", None)
        b3.pop("C-09_especie", None)
        b3.pop("C-09_sisgen", None)
        st.markdown(
            '<div class="alert-success">✅ Sem envolvimento com bioeconomia amazônica neste diagnóstico.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<br>', unsafe_allow_html=True)
    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b3_voltar"):
            st.session_state.bloco_atual = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b3_avancar"):
            erros = []
            bio = b3.get("C-09_bioeconomia", "Selecione...")
            if bio == "Selecione...":
                erros.append("Envolvimento com bioeconomia (C-09)")
            if bio == "Sim":
                if b3.get("C-10_recursos", "Selecione...") == "Selecione...":
                    erros.append("C-10: Uso de recursos do IFAC com bioativos")
                if b3.get("C-11_conhecimento", "Selecione...") == "Selecione...":
                    erros.append("C-11: Conhecimento tradicional")
                if b3.get("C-11_conhecimento") == "Sim" and not b3.get("C-11_comunidade", "").strip():
                    erros.append("C-11: Identificação da comunidade")
                if not b3.get("C-09_especie", "").strip():
                    erros.append("Espécie(s) ou recurso(s) genético(s)")
                if b3.get("C-09_sisgen", "Selecione...") == "Selecione...":
                    erros.append("Cadastro no SisGen")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 4
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 4 — Tipos Específicos de Ativos
# ─────────────────────────────────────────────
def bloco4():
    barra_progresso(4)
    st.markdown('<div class="bloco-title"><h2>💼 Bloco 4 — Tipos Específicos de Ativos</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b4", 4)
    if limpar:
        st.session_state.respostas["bloco4"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 4
        st.rerun()

    if st.session_state.pular_confirmacao == 4:
        if confirmacao_pular(4):
            st.session_state.respostas["bloco4"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 5
            st.rerun()
        return

    b4 = st.session_state.respostas["bloco4"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-12/C-13/C-14/C-19/C-20 — Classificação do Ativo de PI")
    st.markdown("Identifique o tipo principal do ativo intelectual criado.")

    tipos_ativo = [
        "Selecione...",
        "Invenção / Modelo de utilidade (Patente)",
        "Software",
        "Cultivar (variedade vegetal)",
        "Marca",
        "Desenho industrial",
        "Know-how / Segredo industrial",
        "Indicação Geográfica (IG)",
        "Obra literária/artística/científica (Direito Autoral)",
        "Método / Processo / Tecnologia (não patenteável separadamente)",
        "Outro / Não se enquadra nas categorias acima",
    ]

    b4["C-12_tipo_ativo"] = st.radio(
        "Qual é o tipo principal do ativo de propriedade intelectual? *",
        options=tipos_ativo,
        index=tipos_ativo.index(b4.get("C-12_tipo_ativo", "Selecione...")) if b4.get("C-12_tipo_ativo", "Selecione...") in tipos_ativo else 0,
        key="b4_tipo",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    tipo = b4.get("C-12_tipo_ativo", "Selecione...")

    if tipo == "Software":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-12 — Detalhes do Software")
        b4["C-12_nome_software"] = st.text_input(
            "Nome/descrição do software: *",
            value=b4.get("C-12_nome_software", ""),
            placeholder="Ex.: Sistema de gestão agrícola, Aplicativo de telediagnóstico...",
            key="b4_sw_nome",
        )
        b4["C-12_tipo_software"] = st.radio(
            "Tipo de software: *",
            options=["Selecione...", "Aplicativo web/mobile", "Sistema desktop", "Script/algoritmo", "Firmware/embarcado", "Outro"],
            index=["Selecione...", "Aplicativo web/mobile", "Sistema desktop", "Script/algoritmo", "Firmware/embarcado", "Outro"].index(
                b4.get("C-12_tipo_software", "Selecione...")
            ),
            key="b4_sw_tipo",
        )
        b4["C-12_codigo_fonte"] = st.radio(
            "O código-fonte está em posse do empreendimento? *",
            options=["Selecione...", "Sim", "Não", "Parcialmente"],
            index=["Selecione...", "Sim", "Não", "Parcialmente"].index(b4.get("C-12_codigo_fonte", "Selecione...")),
            key="b4_sw_cod",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo == "Cultivar (variedade vegetal)":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-13 — Detalhes da Cultivar")
        b4["C-13_nome_cultivar"] = st.text_input(
            "Nome/denominação da cultivar: *",
            value=b4.get("C-13_nome_cultivar", ""),
            placeholder="Ex.: Cultivar de pupunha com alta produtividade...",
            key="b4_cv_nome",
        )
        b4["C-13_especie_cultivar"] = st.text_input(
            "Espécie botânica (nome científico): *",
            value=b4.get("C-13_especie_cultivar", ""),
            placeholder="Ex.: Bactris gasipaes var. gasipaes",
            key="b4_cv_esp",
        )
        b4["C-13_distinta"] = st.radio(
            "A cultivar é claramente distinguível de outras variedades existentes? *",
            options=["Selecione...", "Sim", "Não", "Em avaliação"],
            index=["Selecione...", "Sim", "Não", "Em avaliação"].index(b4.get("C-13_distinta", "Selecione...")),
            key="b4_cv_dist",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo == "Marca":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-14 — Detalhes da Marca")
        b4["C-14_nome_marca"] = st.text_input(
            "Nome/denominação da marca: *",
            value=b4.get("C-14_nome_marca", ""),
            placeholder="Ex.: AmazôniaFresh, BioAcre...",
            key="b4_mk_nome",
        )
        b4["C-14_tipo_marca"] = st.radio(
            "Tipo de marca: *",
            options=["Selecione...", "Nominativa (só texto)", "Figurativa (só figura)", "Mista (texto + figura)", "Tridimensional"],
            index=["Selecione...", "Nominativa (só texto)", "Figurativa (só figura)", "Mista (texto + figura)", "Tridimensional"].index(
                b4.get("C-14_tipo_marca", "Selecione...")
            ),
            key="b4_mk_tipo",
        )
        b4["C-14_uso_marca_ifac"] = st.radio(
            "A marca contém elementos visuais, nomes ou siglas do IFAC? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b4.get("C-14_uso_marca_ifac", "Selecione...")),
            key="b4_mk_ifac",
        )
        if b4.get("C-14_uso_marca_ifac") == "Sim":
            st.markdown(
                '<div class="alert-warning">⚠️ ATENÇÃO: O uso de marca/nome/sigla do IFAC sem autorização é vedado pelos Arts. 40 e 53 do Regimento. '
                "Consulte o NIT imediatamente.</div>",
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo == "Know-how / Segredo industrial":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-19 — Detalhes do Know-how / Segredo Industrial")
        b4["C-19_descricao_kh"] = st.text_area(
            "Descreva brevemente o know-how ou segredo industrial (não revele detalhes confidenciais): *",
            value=b4.get("C-19_descricao_kh", ""),
            placeholder="Ex.: Processo proprietário de fermentação, formulação química exclusiva...",
            key="b4_kh_desc",
        )
        b4["C-19_nda_celebrado"] = st.radio(
            "Já foi celebrado Termo de Confidencialidade (NDA) com todos os envolvidos? *",
            options=["Selecione...", "Sim", "Não"],
            index=["Selecione...", "Sim", "Não"].index(b4.get("C-19_nda_celebrado", "Selecione...")),
            key="b4_kh_nda",
        )
        if b4.get("C-19_nda_celebrado") == "Não":
            st.markdown(
                '<div class="alert-warning">⚠️ Celebre imediatamente o NDA com todos que têm acesso ao know-how antes de qualquer divulgação.</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo == "Indicação Geográfica (IG)":
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### C-20 — Detalhes da Indicação Geográfica")
        b4["C-20_produto"] = st.text_input(
            "Produto/serviço que receberá a IG: *",
            value=b4.get("C-20_produto", ""),
            placeholder="Ex.: Castanha do Acre, Borracha Extrativista do Acre...",
            key="b4_ig_prod",
        )
        b4["C-20_regiao"] = st.text_input(
            "Região geográfica de origem: *",
            value=b4.get("C-20_regiao", ""),
            placeholder="Ex.: Vale do Juruá, Município de Epitaciolândia...",
            key="b4_ig_reg",
        )
        b4["C-20_coletivo"] = st.radio(
            "Há um coletivo de produtores/associação organizada para solicitar o registro da IG? *",
            options=["Selecione...", "Sim", "Não", "Em formação"],
            index=["Selecione...", "Sim", "Não", "Em formação"].index(b4.get("C-20_coletivo", "Selecione...")),
            key="b4_ig_col",
        )
        st.markdown(
            '<div class="alert-info">ℹ️ A IG é de natureza coletiva — não pode ser registrada individualmente. Orientação ao coletivo para registro no INPI.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo not in ("Selecione...",):
        st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
        st.markdown("#### Descrição complementar")
        b4["C-12_descricao_geral"] = st.text_area(
            "Descreva brevemente a criação intelectual: *",
            value=b4.get("C-12_descricao_geral", ""),
            placeholder="Descreva o que foi criado, para que serve e como funciona...",
            key="b4_desc_geral",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b4_voltar"):
            st.session_state.bloco_atual = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b4_avancar"):
            erros = []
            tipo_sel = b4.get("C-12_tipo_ativo", "Selecione...")
            if tipo_sel == "Selecione...":
                erros.append("Tipo do ativo de PI")
            if tipo_sel == "Software":
                if not b4.get("C-12_nome_software", "").strip():
                    erros.append("Nome/descrição do software")
                if b4.get("C-12_tipo_software", "Selecione...") == "Selecione...":
                    erros.append("Tipo de software")
                if b4.get("C-12_codigo_fonte", "Selecione...") == "Selecione...":
                    erros.append("Código-fonte em posse do empreendimento")
            elif tipo_sel == "Cultivar (variedade vegetal)":
                if not b4.get("C-13_nome_cultivar", "").strip():
                    erros.append("Nome da cultivar")
                if not b4.get("C-13_especie_cultivar", "").strip():
                    erros.append("Espécie botânica")
                if b4.get("C-13_distinta", "Selecione...") == "Selecione...":
                    erros.append("Distinção da cultivar")
            elif tipo_sel == "Marca":
                if not b4.get("C-14_nome_marca", "").strip():
                    erros.append("Nome da marca")
                if b4.get("C-14_tipo_marca", "Selecione...") == "Selecione...":
                    erros.append("Tipo de marca")
                if b4.get("C-14_uso_marca_ifac", "Selecione...") == "Selecione...":
                    erros.append("Uso de elementos do IFAC na marca")
            elif tipo_sel == "Know-how / Segredo industrial":
                if not b4.get("C-19_descricao_kh", "").strip():
                    erros.append("Descrição do know-how")
                if b4.get("C-19_nda_celebrado", "Selecione...") == "Selecione...":
                    erros.append("NDA celebrado")
            elif tipo_sel == "Indicação Geográfica (IG)":
                if not b4.get("C-20_produto", "").strip():
                    erros.append("Produto/serviço para a IG")
                if not b4.get("C-20_regiao", "").strip():
                    erros.append("Região geográfica")
                if b4.get("C-20_coletivo", "Selecione...") == "Selecione...":
                    erros.append("Coletivo de produtores")
            elif tipo_sel not in ("Selecione...",):
                if not b4.get("C-12_descricao_geral", "").strip():
                    erros.append("Descrição da criação")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 5
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 5 — Infrações
# ─────────────────────────────────────────────
def bloco5():
    barra_progresso(5)
    st.markdown('<div class="bloco-title"><h2>⚠️ Bloco 5 — Infrações (C-15)</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b5", 5)
    if limpar:
        st.session_state.respostas["bloco5"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 5
        st.rerun()

    if st.session_state.pular_confirmacao == 5:
        if confirmacao_pular(5):
            st.session_state.respostas["bloco5"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 6
            st.rerun()
        return

    b5 = st.session_state.respostas["bloco5"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-15 — Uso Indevido da Marca IFAC / Infrações ao Regimento")
    st.markdown(
        "_Este bloco verifica se há situação de uso indevido ou infração ao regimento. "
        "Responda com honestidade — o objetivo é regularizar a situação._"
    )

    b5["C-15_infracao"] = st.radio(
        "O empreendimento utilizou ou utiliza a marca, nome, logotipo, brasão ou qualquer identidade visual do IFAC sem autorização expressa da Reitoria ou do NIT? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b5.get("C-15_infracao", "Selecione...")),
        key="b5_marca",
    )
    if b5.get("C-15_infracao") == "Sim":
        st.markdown(
            '<div class="alert-warning">⚠️ SITUAÇÃO DE INFRAÇÃO — Arts. 40, 51 e 53 do Regimento; Res. CONSU/IFAC nº 190/2024. '
            "O IFAC poderá emitir notificação formal e rescindir o TASI. Regularize imediatamente junto ao NIT.</div>",
            unsafe_allow_html=True,
        )

    b5["C-15_publicacao_indevida"] = st.radio(
        "Houve publicação/divulgação de resultados, produtos ou tecnologias desenvolvidos com recursos do IFAC sem comunicação prévia ao NIT? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b5.get("C-15_publicacao_indevida", "Selecione...")),
        key="b5_pub",
    )
    if b5.get("C-15_publicacao_indevida") == "Sim":
        st.markdown(
            '<div class="alert-warning">⚠️ A publicação antes da comunicação ao NIT pode comprometer o patenteamento. '
            "Consulte o NIT com urgência para avaliar o impacto.</div>",
            unsafe_allow_html=True,
        )

    b5["C-15_comercializacao_irregular"] = st.radio(
        "O empreendimento está comercializando produto/tecnologia desenvolvido com recursos do IFAC sem instrumento formal de autorização (licença, cessão, TT)? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b5.get("C-15_comercializacao_irregular", "Selecione...")),
        key="b5_com",
    )
    if b5.get("C-15_comercializacao_irregular") == "Sim":
        st.markdown(
            '<div class="alert-warning">⚠️ Comercialização sem instrumento formal pode configurar uso irregular de PI pública. '
            "Regularize junto ao NIT imediatamente.</div>",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b5_voltar"):
            st.session_state.bloco_atual = 4
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b5_avancar"):
            erros = []
            if b5.get("C-15_infracao", "Selecione...") == "Selecione...":
                erros.append("Uso indevido de marca IFAC")
            if b5.get("C-15_publicacao_indevida", "Selecione...") == "Selecione...":
                erros.append("Publicação sem comunicação ao NIT")
            if b5.get("C-15_comercializacao_irregular", "Selecione...") == "Selecione...":
                erros.append("Comercialização sem instrumento formal")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 6
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 6 — Parcerias Institucionais
# ─────────────────────────────────────────────
def bloco6():
    barra_progresso(6)
    st.markdown('<div class="bloco-title"><h2>🤝 Bloco 6 — Parcerias Institucionais (C-16)</h2></div>', unsafe_allow_html=True)

    limpar, pular = botoes_bloco("b6", 6)
    if limpar:
        st.session_state.respostas["bloco6"] = {}
        st.rerun()
    if pular:
        st.session_state.pular_confirmacao = 6
        st.rerun()

    if st.session_state.pular_confirmacao == 6:
        if confirmacao_pular(6):
            st.session_state.respostas["bloco6"] = {}
            st.session_state.pular_confirmacao = None
            st.session_state.bloco_atual = 7
            st.rerun()
        return

    b6 = st.session_state.respostas["bloco6"]

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### C-16 — Parceria com Outra ICT (Instituição Científica e Tecnológica)")

    b6["C-16_parceria"] = st.radio(
        "A criação foi desenvolvida em parceria com outra ICT (universidade, instituto de pesquisa, outro IF, Embrapa etc.)? *",
        options=["Selecione...", "Sim", "Não"],
        index=["Selecione...", "Sim", "Não"].index(b6.get("C-16_parceria", "Selecione...")),
        key="b6_parc",
    )

    if b6.get("C-16_parceria") == "Sim":
        b6["C-16_ict_nome"] = st.text_input(
            "Nome da(s) ICT(s) parceira(s): *",
            value=b6.get("C-16_ict_nome", ""),
            placeholder="Ex.: UFAC, Embrapa Acre, Instituto Mamirauá...",
            key="b6_ict_nome",
        )
        b6["C-16_acordo_formalizado"] = st.radio(
            "Existe Acordo de Parceria PD&I ou convênio formal entre o IFAC e a(s) ICT(s) parceira(s)? *",
            options=["Selecione...", "Sim", "Não", "Em elaboração"],
            index=["Selecione...", "Sim", "Não", "Em elaboração"].index(b6.get("C-16_acordo_formalizado", "Selecione...")),
            key="b6_acordo",
        )
        if b6.get("C-16_acordo_formalizado") == "Não":
            st.markdown(
                '<div class="alert-warning">⚠️ A parceria sem instrumento formal pode gerar conflitos de titularidade. '
                "Formalize o Acordo de Parceria PD&I antes de qualquer atividade conjunta (Decreto 9.283/2018, Art. 37).</div>",
                unsafe_allow_html=True,
            )
        b6["C-16_percentual_contribuicao"] = st.text_input(
            "Qual é o percentual estimado de contribuição de cada instituição para a criação? *",
            value=b6.get("C-16_percentual_contribuicao", ""),
            placeholder="Ex.: IFAC 40% · UFAC 60% ou IFAC 50% · Embrapa 50%",
            key="b6_perc",
        )
    else:
        b6.pop("C-16_ict_nome", None)
        b6.pop("C-16_acordo_formalizado", None)
        b6.pop("C-16_percentual_contribuicao", None)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="bloco-card">', unsafe_allow_html=True)
    st.markdown("#### Informações Complementares")

    b6["C-16_descricao_criacao"] = st.text_area(
        "Descreva brevemente a criação intelectual objeto deste diagnóstico: *",
        value=b6.get("C-16_descricao_criacao", ""),
        placeholder="Contextualize: o que foi criado, para que serve, em que área de aplicação...",
        key="b6_descricao",
        height=100,
    )

    b6["C-16_observacoes"] = st.text_area(
        "Observações adicionais (opcional):",
        value=b6.get("C-16_observacoes", ""),
        placeholder="Informações relevantes que não foram cobertas nas perguntas anteriores...",
        key="b6_obs",
        height=80,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    col_v, _, col_av = st.columns([2, 4, 2])
    with col_v:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Voltar", key="b6_voltar"):
            st.session_state.bloco_atual = 5
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_av:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Avançar →", key="b6_avancar"):
            erros = []
            parc = b6.get("C-16_parceria", "Selecione...")
            if parc == "Selecione...":
                erros.append("Parceria com outra ICT (C-16)")
            if parc == "Sim":
                if not b6.get("C-16_ict_nome", "").strip():
                    erros.append("Nome da(s) ICT(s) parceira(s)")
                if b6.get("C-16_acordo_formalizado", "Selecione...") == "Selecione...":
                    erros.append("Acordo formalizado com a ICT parceira")
                if not b6.get("C-16_percentual_contribuicao", "").strip():
                    erros.append("Percentual de contribuição por instituição")
            if not b6.get("C-16_descricao_criacao", "").strip():
                erros.append("Descrição da criação intelectual")
            if erros:
                st.error("Responda todas as perguntas obrigatórias:\n- " + "\n- ".join(erros))
            else:
                st.session_state.bloco_atual = 7
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ETAPA 7 — RESULTADO / ENVIO
# ─────────────────────────────────────────────
def etapa_resultado():
    barra_progresso(7)
    st.markdown('<div class="bloco-title"><h2>✅ Resultado do Diagnóstico</h2></div>', unsafe_allow_html=True)

    # Identifica cenários
    cenarios_ids = identificar_cenario(st.session_state.respostas)

    # Exibe cenários
    st.markdown("### Cenário(s) Identificado(s):")
    for cid in cenarios_ids:
        c = CENARIOS.get(cid, {})
        st.markdown(
            f'<div style="margin:8px 0;"><span class="cenario-badge">{cid}</span> &nbsp; '
            f'<span style="font-size:1.1rem;color:#e0e0e0">{c.get("titulo","")}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Resumo por cenário
    for cid in cenarios_ids:
        c = CENARIOS.get(cid, {})
        with st.expander(f"📋 Detalhes: {cid} — {c.get('titulo', '')}", expanded=len(cenarios_ids) == 1):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Titularidade:** {c.get('titularidade', '—')}")
                st.markdown(f"**Base Legal:** {c.get('base_legal', '—')}")
            with col_b:
                st.markdown("**Instrumentos obrigatórios:**")
                for instr in c.get("instrumentos", []):
                    st.markdown(f"- {instr}")
            st.markdown(f"**Obrigações:** {c.get('obrigacoes', '—')}")
            st.markdown("**Checklist de documentos:**")
            for doc in c.get("checklist", []):
                st.markdown(f"- [ ] {doc}")

    st.markdown("---")

    # Repartição de ganhos
    with st.expander("💰 Tabela de Repartição de Ganhos"):
        for tipo, descr in REPARTICAO_GANHOS.items():
            st.markdown(f"**{tipo}:** {descr}")

    st.markdown("---")

    # Confirmar envio
    if not st.session_state.envio_confirmado:
        st.markdown("### Enviar Diagnóstico")
        st.markdown(
            '<div class="alert-info">ℹ️ Ao enviar, o diagnóstico será registrado e ficará disponível no Painel de Gestão do INCUBAC/IFAC.</div>',
            unsafe_allow_html=True,
        )

        col_v, _, col_env = st.columns([2, 3, 3])
        with col_v:
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            if st.button("← Voltar ao Bloco 6", key="res_voltar"):
                st.session_state.bloco_atual = 6
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_env:
            st.markdown('<div class="btn-green">', unsafe_allow_html=True)
            if st.button("📤 Enviar Diagnóstico", key="res_enviar"):
                st.session_state.pular_confirmacao = "envio"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.pular_confirmacao == "envio":
            st.markdown(
                '<div class="alert-warning">⚠️ <b>Confirmar envio do diagnóstico?</b><br>'
                "Após o envio, os dados serão registrados no sistema do INCUBAC/IFAC.</div>",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-green">', unsafe_allow_html=True)
                if st.button("✅ Confirmar Envio", key="confirmar_envio"):
                    diagnostico = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "info": copy.deepcopy(st.session_state.info),
                        "respostas": copy.deepcopy(st.session_state.respostas),
                        "cenarios": cenarios_ids,
                        "timestamp": datetime.now().isoformat(),
                    }
                    salvar_resposta(diagnostico)
                    st.session_state.diagnostico_enviado = diagnostico
                    st.session_state.envio_confirmado = True
                    st.session_state.pular_confirmacao = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                if st.button("Cancelar", key="cancelar_envio"):
                    st.session_state.pular_confirmacao = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Envio concluído
        st.markdown(
            '<div class="alert-success">✅ <b>Diagnóstico enviado com sucesso!</b><br>'
            "Seu diagnóstico foi registrado no sistema INCUBAC/IFAC.</div>",
            unsafe_allow_html=True,
        )

        diag = st.session_state.diagnostico_enviado
        if diag:
            # Gerar e oferecer PDF
            try:
                pdf_bytes = gerar_pdf(diag)
                info = diag.get("info", {})
                fname = f"ClassPI_{info.get('nome','diag').replace(' ','_')}_{info.get('data','').replace('/','').replace(':','').replace(' ','')}.pdf"
                link = pdf_download_link(pdf_bytes, fname, "⬇️ Baixar Relatório PDF Completo")
                st.markdown(link, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🔄 Iniciar Novo Diagnóstico", key="novo_diag"):
            # Reset completo
            st.session_state.bloco_atual = 0
            st.session_state.respostas = {
                "bloco1": {}, "bloco2": {}, "bloco3": {},
                "bloco4": {}, "bloco5": {}, "bloco6": {},
            }
            st.session_state.info = {
                "nome": "", "empreendimento": "", "email": "", "nucleo": "Selecione...",
            }
            st.session_state.envio_confirmado = False
            st.session_state.diagnostico_enviado = None
            st.session_state.pular_confirmacao = None
            st.rerun()


# ─────────────────────────────────────────────
# ROTEADOR PRINCIPAL
# ─────────────────────────────────────────────
modulo = st.session_state.modulo

if modulo == "login_gestor":
    modulo_login_gestor()
elif modulo == "gestor" and st.session_state.gestor_autenticado:
    modulo_gestor()
else:
    # Módulo respondente
    bloco = st.session_state.bloco_atual
    if bloco == 0:
        etapa_dados_pessoais()
    elif bloco == 1:
        bloco1()
    elif bloco == 2:
        bloco2()
    elif bloco == 3:
        bloco3()
    elif bloco == 4:
        bloco4()
    elif bloco == 5:
        bloco5()
    elif bloco == 6:
        bloco6()
    elif bloco == 7:
        etapa_resultado()

# ─────────────────────────────────────────────
# RODAPÉ FIXO
# ─────────────────────────────────────────────
st.markdown("</div>", unsafe_allow_html=True)  # fecha main-content-pad
st.markdown(
    """
<div class="rodape-fixo">
  © INCUBAC/IFAC · Regimento Interno dos Núcleos Incubadores · Res. CONSU/IFAC nº 99/2022 ·
  Esta ferramenta de classificador de cenários de PI foi desenvolvida a partir da disciplina de oficina profissional
  por discente de mestrado do PROFNIT.
</div>
""",
    unsafe_allow_html=True,
)
