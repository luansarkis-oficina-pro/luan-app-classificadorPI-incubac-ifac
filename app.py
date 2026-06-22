import streamlit as st
import datetime
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER
import io

# ── LOGOS SVG embutidos em base64 ──────────────────────────────────────────
_SVG_IFAC = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 100">
  <rect x="6" y="6" width="20" height="20" rx="3" fill="#C8102E"/>
  <rect x="32" y="6" width="20" height="20" rx="3" fill="white"/>
  <rect x="58" y="6" width="20" height="20" rx="3" fill="white"/>
  <rect x="6" y="32" width="20" height="20" rx="3" fill="white"/>
  <rect x="32" y="32" width="20" height="20" rx="3" fill="white"/>
  <rect x="58" y="32" width="20" height="20" rx="3" fill="white"/>
  <rect x="6" y="58" width="20" height="20" rx="3" fill="white"/>
  <rect x="32" y="58" width="20" height="20" rx="3" fill="white"/>
  <rect x="58" y="58" width="20" height="20" rx="3" fill="white"/>
  <text x="92" y="38" font-family="Arial Black,Arial" font-weight="900" font-size="20" fill="white">INSTITUTO FEDERAL</text>
  <text x="93" y="62" font-family="Arial,sans-serif" font-size="16" fill="#ccc">Acre</text>
</svg>"""

_SVG_PROFNIT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 60">
  <text x="6" y="48" font-family="Arial,sans-serif" font-weight="700" font-size="44" font-style="italic" fill="white">profnit</text>
</svg>"""

def _b64(s):
    return base64.b64encode(s.encode()).decode()

LOGO_IFAC_B64    = _b64(_SVG_IFAC)
LOGO_PROFNIT_B64 = _b64(_SVG_PROFNIT)

def logo_html(b64, width="180px"):
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width:{width};height:auto;display:block;" />'

# ── CORES ──────────────────────────────────────────────────────────────────
RED   = "#C8102E"
GREEN = "#007A3D"
DARK  = "#0D0D0D"
CARD  = "#1A1A1A"
CARD2 = "#222222"
WHITE = "#F0F0F0"
LIGHT = "#CCCCCC"
INP   = "#2C2C2C"
BRD   = "#3A3A3A"

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Classificador de Cenários de PI — INCUBAC/IFAC",
    page_icon="⚖️", layout="wide", initial_sidebar_state="expanded"
)

CSS = f"""
<style>
html,body,.stApp,[data-testid="stAppViewContainer"]{{background-color:{DARK}!important;color:{WHITE}!important;}}
[data-testid="stMain"],[data-testid="stMainBlockContainer"]{{background-color:{DARK}!important;}}
[data-testid="stSidebar"]{{background:#0A0A0A!important;border-right:1px solid #2a2a2a;}}
[data-testid="stSidebar"] *{{color:{WHITE}!important;}}
[data-testid="stSidebar"] hr{{border-color:#333!important;}}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] small{{color:{LIGHT}!important;}}
.header-bar{{background:linear-gradient(90deg,{RED} 0%,#6B0000 28%,#111 52%,#003d1f 76%,{GREEN} 100%);padding:16px 24px;border-radius:10px;margin-bottom:18px;}}
.header-bar h1{{color:white;margin:0;font-size:1.5rem;text-shadow:1px 1px 4px rgba(0,0,0,.7);}}
.header-bar p{{color:#ddd;margin:4px 0 0 0;font-size:.88rem;}}
.header-logos{{display:flex;align-items:center;gap:24px;margin-bottom:10px;}}
.block-card{{background:{CARD};border-left:5px solid {GREEN};border-radius:8px;padding:16px 20px;margin-bottom:16px;color:{WHITE};}}
.block-card.red{{border-left-color:{RED};}}
.block-card h3,.block-card p,.block-card span{{color:{WHITE}!important;}}
.result-card{{background:{CARD2};border-radius:8px;padding:18px 22px;margin-bottom:14px;border-top:4px solid {GREEN};color:{WHITE};}}
.result-card.infraction{{border-top-color:{RED};}}
.result-card *{{color:{WHITE}!important;}}
.tag-verde{{background:{GREEN};color:white;padding:2px 10px;border-radius:12px;font-size:.78rem;font-weight:700;display:inline-block;margin:2px;}}
.tag-vermelho{{background:{RED};color:white;padding:2px 10px;border-radius:12px;font-size:.78rem;font-weight:700;display:inline-block;margin:2px;}}
.step-pill{{display:inline-block;background:{RED};color:white;border-radius:20px;padding:4px 16px;font-weight:700;font-size:.85rem;margin-bottom:10px;}}
input[type="text"],input[type="password"],textarea,
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stPasswordInput"] input{{
  background-color:{INP}!important;color:{WHITE}!important;border:1.5px solid #555!important;border-radius:10px!important;padding:8px 14px!important;}}
[data-testid="stTextInput"] label,[data-testid="stPasswordInput"] label,[data-testid="stTextArea"] label{{color:{LIGHT}!important;font-weight:600;}}
.stRadio > label{{color:{WHITE}!important;font-weight:600;}}
.stRadio div[role="radiogroup"] label{{color:{LIGHT}!important;}}
.stRadio div[role="radiogroup"]{{background:{CARD}!important;border-radius:8px;padding:10px 14px;border:1px solid {BRD};}}
.stButton > button{{border-radius:8px!important;font-weight:700!important;font-size:.88rem!important;border:none!important;color:white!important;background:#333!important;}}
.stButton > button:hover{{background:#444!important;}}
.stButton > button[kind="primary"],div[data-testid="stFormSubmitButton"] > button{{background:linear-gradient(90deg,{RED},{GREEN})!important;color:white!important;border-radius:8px!important;font-weight:700!important;}}
[data-testid="stDownloadButton"] > button{{background:linear-gradient(90deg,{GREEN},#005a2d)!important;color:white!important;border-radius:8px!important;font-weight:700!important;}}
[data-testid="stProgressBar"] > div > div{{background:linear-gradient(90deg,{RED},{GREEN})!important;border-radius:6px;}}
[data-testid="stProgressBar"] > div{{background:#333!important;border-radius:6px;}}
[data-testid="stMetric"]{{background:{CARD}!important;border-radius:8px;padding:12px 16px;border:1px solid {BRD};}}
[data-testid="stMetric"] *{{color:{WHITE}!important;}}
[data-testid="stExpander"]{{background:{CARD}!important;border:1px solid {BRD}!important;border-radius:8px!important;color:{WHITE}!important;}}
[data-testid="stExpander"] summary{{color:{WHITE}!important;font-weight:700;}}
[data-testid="stExpander"] *{{color:{WHITE}!important;}}
[data-testid="stAlert"]{{border-radius:8px!important;}}
[data-testid="stInfo"]{{background:#1a2a3a!important;border-left-color:#4aa3df!important;}}
[data-testid="stWarning"]{{background:#2a2200!important;border-left-color:#ffcc00!important;}}
[data-testid="stError"]{{background:#2a0a0a!important;border-left-color:{RED}!important;}}
[data-testid="stInfo"] *,[data-testid="stWarning"] *,[data-testid="stError"] *{{color:{WHITE}!important;}}
.stCheckbox label{{color:{LIGHT}!important;}}
hr{{border-color:#2a2a2a!important;}}
.stCaption,small{{color:#999!important;}}
.footer-bar{{background:#0A0A0A;border-top:1px solid #2a2a2a;padding:14px 20px;border-radius:0 0 8px 8px;margin-top:30px;text-align:center;}}
.footer-bar p{{color:#888!important;font-size:.78rem;margin:2px 0;}}
.login-card{{background:{CARD};border-radius:12px;padding:32px 36px;border:1px solid {BRD};max-width:440px;margin:40px auto;text-align:center;}}
.login-card h2{{color:{WHITE};margin-bottom:8px;}}
.login-card p{{color:{LIGHT};margin-bottom:20px;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── BASE DE CENÁRIOS ──────────────────────────────────────────────────────
CENARIOS = {
  "C-01":{"nome":"Criação exclusiva do empreendimento (sem recursos do IFAC)","bloco":1,
    "titularidade":"Empreendimento (100%)",
    "instrumentos":["Declaração de PI pré-existente ou Parecer da COPII reconhecendo ausência de participação do IFAC"],
    "obrigacoes":["Comunicar à COPII para reconhecimento formal","Manter documentação comprobatória da criação","Assinar Termo de Confidencialidade no ingresso"],
    "checklist":["Declaração formal de PI pré-existente","Evidências de autoria/desenvolvimento anterior","Termo de Confidencialidade assinado","TASI assinado"],
    "base_legal":"Art. 28 do Regimento; Art. 11, Lei 10.973/2004","alerta":None},
  "C-17":{"nome":"PI pré-existente declarada no ingresso, sem uso de recursos do IFAC","bloco":1,
    "titularidade":"Empreendimento (100%)",
    "instrumentos":["Declaração formal de PI pré-existente arquivada pela COPII"],
    "obrigacoes":["Declarar toda PI pré-existente no ato da admissão","Apresentar documentação comprobatória","Comunicar aperfeiçoamento posterior que envolva recursos do IFAC"],
    "checklist":["Formulário de Declaração de PI Pré-existente","Cópias de pedidos de proteção/registros existentes","TASI com cláusula de reconhecimento de anterioridade"],
    "base_legal":"Art. 36 do Regimento; Art. 49, §3º do Regimento","alerta":None},
  "C-18":{"nome":"PI pré-existente aperfeiçoada com recursos do IFAC após ingresso","bloco":1,
    "titularidade":"PI original: Empreendimento | Aperfeiçoamento: Cotitularidade IFAC + Empreendimento",
    "instrumentos":["Declaração de anterioridade da PI original","Instrumento de cotitularidade sobre o aperfeiçoamento","TASI com cláusula específica"],
    "obrigacoes":["Comunicar à COPII antes de usar recursos do IFAC no aperfeiçoamento","Delimitar claramente o que é PI original e o que é aperfeiçoamento","Formalizar instrumento de cotitularidade antes do uso de laboratórios"],
    "checklist":["Declaração de anterioridade da PI original","Instrumento de cotitularidade (aperfeiçoamento)","Comunicado de Invenção ao NIT","TASI com cláusula específica de aperfeiçoamento"],
    "base_legal":"Art. 36, §3º; Art. 27 do Regimento","alerta":None},
  "C-02":{"nome":"Criação com uso de laboratório/infraestrutura do IFAC","bloco":2,
    "titularidade":"IFAC (titular) ou Cotitularidade IFAC + Empreendimento",
    "instrumentos":["Instrumento de cotitularidade ou cessão","TASI com cláusula específica de PI","Comunicado de Invenção ao NIT"],
    "obrigacoes":["Comunicar à COPII toda criação com uso de infraestrutura do IFAC","Não realizar depósito no INPI antes de manifestação da COPII","Assinar instrumento de cotitularidade antes de qualquer divulgação"],
    "checklist":["Comunicado de Invenção (formulário NIT)","Registro de uso de laboratório/equipamento","Instrumento de cotitularidade assinado","Termo de Confidencialidade","TASI com cláusula de PI"],
    "base_legal":"Arts. 26–27 do Regimento; Art. 16, Res. CONSU/IFAC nº 99/2022",
    "alerta":"⚠️ Não publicar resultados antes do depósito do pedido de patente. A COPII deve ser consultada antes de qualquer divulgação."},
  "C-03":{"nome":"Criação com participação inventiva de servidor do IFAC","bloco":2,
    "titularidade":"IFAC (titular) — servidor como coautor/inventor; eventual cotitularidade com o empreendimento",
    "instrumentos":["Instrumento de cotitularidade","Reconhecimento formal de autoria/inventoria do servidor","Comunicado de Invenção ao NIT"],
    "obrigacoes":["Comunicar imediatamente à COPII a participação de servidor na criação","Identificar e documentar a contribuição inventiva do servidor","Aguardar análise da COPII antes de qualquer depósito"],
    "checklist":["Comunicado de Invenção com identificação do servidor coautor","Declaração de participação inventiva do servidor","Instrumento de cotitularidade","Termo de Confidencialidade de todos os envolvidos"],
    "base_legal":"Art. 26 do Regimento; Art. 16, §4º, Res. 99/2022",
    "alerta":"⚠️ A participação de servidor do IFAC como inventor gera titularidade institucional automática."},
  "C-04":{"nome":"Criação por estudante/egresso com uso de estrutura do IFAC","bloco":2,
    "titularidade":"IFAC (titular) — criador reconhecido como inventor/autor",
    "instrumentos":["Comunicado de Invenção ao NIT","Instrumento de cessão se criador não tiver mais vínculo com o IFAC"],
    "obrigacoes":["Estudante/egresso deve comunicar criação ao NIT","Ser reconhecido formalmente como inventor/autor","Colaborar com o processo de proteção conduzido pelo IFAC"],
    "checklist":["Comunicado de Invenção (formulário NIT)","Comprovação de vínculo com o IFAC no período de criação","Instrumento de cessão (quando egresso sem vínculo atual)","Termo de Confidencialidade"],
    "base_legal":"Art. 16, §§5º e 6º, Res. 99/2022","alerta":None},
  "C-05":{"nome":"Criação em projeto cooperativo IFAC + empreendimento formalizado","bloco":2,
    "titularidade":"Cotitularidade IFAC + Empreendimento",
    "instrumentos":["Acordo de Parceria para PD&I","Contrato com cláusulas de titularidade, repartição e TT","TASI com cláusulas de PI"],
    "obrigacoes":["Formalizar o Acordo de Parceria ANTES do início das atividades conjuntas","Definir percentuais de titularidade e repartição de royalties","Comunicar qualquer resultado protegível à COPII imediatamente"],
    "checklist":["Acordo de Parceria PD&I assinado","Plano de trabalho definindo contribuições","Cláusulas de titularidade e repartição no contrato","Comunicado de Invenção ao NIT","Termo de Confidencialidade de todos os envolvidos"],
    "base_legal":"Arts. 27 e 29 do Regimento; Art. 29, Res. 99/2022; Decreto 9.283/2018","alerta":None},
  "C-06":{"nome":"Criação derivada de tecnologia pré-existente do IFAC","bloco":2,
    "titularidade":"IFAC (titular da tecnologia-base) — licenciamento ou TT necessário",
    "instrumentos":["Contrato de Licenciamento ou Transferência de Tecnologia","TASI com referência ao contrato de TT"],
    "obrigacoes":["Formalizar Contrato de Licenciamento antes de qualquer uso da tecnologia do IFAC","Pagar royalties conforme contrato","Comunicar aperfeiçoamentos à COPII"],
    "checklist":["Contrato de Licenciamento ou TT assinado","Comprovação de publicação de oferta tecnológica (se exclusivo)","Definição de royalties no instrumento","Termo de Confidencialidade"],
    "base_legal":"Art. 30, Res. 99/2022; Art. 54 do Regimento",
    "alerta":"⚠️ O licenciamento de tecnologia do IFAC NÃO decorre automaticamente do TASI. É necessário instrumento específico."},
  "C-07":{"nome":"Aperfeiçoamento de PI pré-existente do empreendimento com apoio do IFAC","bloco":2,
    "titularidade":"PI original: Empreendimento | PI aperfeiçoada: Cotitularidade IFAC + Empreendimento",
    "instrumentos":["Declaração de anterioridade","Instrumento de cotitularidade para o aperfeiçoamento"],
    "obrigacoes":["Declarar a PI original no ingresso","Comunicar à COPII no início do aperfeiçoamento com recursos do IFAC","Formalizar instrumento de cotitularidade específico para o aperfeiçoamento"],
    "checklist":["Declaração de PI pré-existente (original)","Comunicado do aperfeiçoamento ao NIT","Instrumento de cotitularidade","TASI com cláusula específica"],
    "base_legal":"Art. 27 do Regimento; Art. 49, §4º do Regimento","alerta":None},
  "C-08":{"nome":"Criação derivada de pesquisa acadêmica (spin-off / TCC / dissertação)","bloco":2,
    "titularidade":"IFAC (titular) — criador reconhecido; possível licenciamento preferencial ao criador incubado",
    "instrumentos":["Comunicado de Invenção","Instrumento de licenciamento diferenciado para o criador incubado"],
    "obrigacoes":["Comunicar ao NIT toda criação derivada de pesquisa institucional","Não explorar comercialmente sem formalizar o licenciamento","Solicitar licenciamento preferencial junto à COPII/NIT"],
    "checklist":["Comunicado de Invenção ao NIT","Comprovação da pesquisa-base (TCC, dissertação, projeto)","Instrumento de licenciamento para o criador-incubado","Termo de Confidencialidade"],
    "base_legal":"Art. 16, §§4º–6º, Res. 99/2022; Art. 57 do Regimento","alerta":None},
  "C-09":{"nome":"Criação em bioeconomia com patrimônio genético, sem recursos do IFAC","bloco":3,
    "titularidade":"Empreendimento (100%) — sujeito a obrigações de biodiversidade",
    "instrumentos":["Declaração de anterioridade","Comprovação de cadastro no SisGen"],
    "obrigacoes":["Registrar o acesso ao PG no SisGen ANTES de qualquer publicação, depósito ou comercialização","Verificar necessidade de repartição de benefícios (Lei 13.123/2015)","Comunicar à COPII para reconhecimento"],
    "checklist":["Cadastro no SisGen (comprovante)","Declaração de anterioridade","Verificação de obrigação de repartição de benefícios","Termo de Confidencialidade"],
    "base_legal":"Art. 30, §3º do Regimento; Lei 13.123/2015",
    "alerta":"⚠️ BIOECONOMIA: O cadastro no SisGen é OBRIGATÓRIO antes de qualquer publicação, depósito ou comercialização. A omissão pode gerar multa e nulidade do pedido."},
  "C-10":{"nome":"Criação em bioeconomia com uso de recursos do IFAC","bloco":3,
    "titularidade":"Cotitularidade IFAC + Empreendimento",
    "instrumentos":["Instrumento de cotitularidade","Comprovação de cadastro no SisGen","Instrumento de repartição de benefícios (quando aplicável)","TASI com cláusulas específicas de bioeconomia"],
    "obrigacoes":["Registrar no SisGen ANTES de qualquer publicação ou depósito","Comunicar imediatamente à COPII toda criação em bioeconomia","Formalizar instrumento de cotitularidade","Verificar obrigação de repartição de benefícios com comunidades tradicionais"],
    "checklist":["Cadastro no SisGen (comprovante)","Comunicado de Ativo Intelectual ao NIT","Instrumento de cotitularidade","Instrumento de repartição de benefícios (se CTA envolvido)","Termo de Confidencialidade específico para bioeconomia","TASI com cláusulas de bioeconomia"],
    "base_legal":"Arts. 30–31 do Regimento; Lei 13.123/2015; Res. 99/2022",
    "alerta":"⚠️ BIOECONOMIA + RECURSOS DO IFAC: Dupla obrigação — cotitularidade institucional E cadastro no SisGen."},
  "C-11":{"nome":"Criação em bioeconomia com envolvimento de comunidades tradicionais (CTA)","bloco":3,
    "titularidade":"Empreendimento e/ou cotitularidade com IFAC + obrigação de repartição com a comunidade",
    "instrumentos":["Instrumento de cotitularidade (quando aplicável)","Acordo de Repartição de Benefícios com a comunidade","CTA — Consentimento Prévio Informado","Cadastro no SisGen"],
    "obrigacoes":["Obter consentimento prévio informado da comunidade detentora","Cadastrar no SisGen","Formalizar Acordo de Repartição de Benefícios","Comunicar à COPII com toda documentação da comunidade","Nunca explorar CTA sem formalização prévia completa"],
    "checklist":["CTA — Consentimento Prévio Informado (firmado com a comunidade)","Cadastro no SisGen (comprovante)","Acordo de Repartição de Benefícios","Instrumento de cotitularidade (se recursos do IFAC usados)","Protocolo comunitário observado","Comunicado formal à COPII/NIT"],
    "base_legal":"Arts. 23, 43 do Regimento; Lei 13.123/2015; Protocolo de Nagoya; CDB",
    "alerta":"🚨 ALERTA MÁXIMO: A exploração de Conhecimento Tradicional Associado (CTA) sem consentimento da comunidade configura infração legal grave, com multa administrativa e embargo."},
  "C-12":{"nome":"Software / Programa de computador desenvolvido com recursos do IFAC","bloco":4,
    "titularidade":"IFAC (titular) ou cotitularidade, conforme participação",
    "instrumentos":["Comunicado ao NIT","Registro junto ao INPI (Lei 9.609/1998)"],
    "obrigacoes":["Comunicar à COPII o desenvolvimento do software","Manter documentação de versionamento, autoria e contribuições","Não disponibilizar publicamente sem autorização do IFAC","Verificar uso de componentes de terceiros e licenças abertas"],
    "checklist":["Comunicado de Software ao NIT","Documentação de versionamento e autoria","Análise de uso de código de terceiros/licenças","Pedido de Registro no INPI (Lei 9.609/98)","Termo de Confidencialidade"],
    "base_legal":"Art. 57 do Regimento; Lei 9.609/1998",
    "alerta":"⚠️ O desenvolvimento de software no âmbito da incubação NÃO afasta a análise institucional de titularidade."},
  "C-13":{"nome":"Cultivar / Espécie vegetal melhorada durante a incubação","bloco":4,
    "titularidade":"IFAC (titular) ou cotitularidade",
    "instrumentos":["Comunicado de Invenção ao NIT","Pedido de Proteção de Cultivar junto ao MAPA/CVRD"],
    "obrigacoes":["Comunicar à COPII o desenvolvimento da cultivar","Verificar necessidade de cadastro no SisGen (se envolver espécie nativa/PG)","Aguardar análise da COPII antes do pedido de proteção"],
    "checklist":["Comunicado de Invenção ao NIT","Documentação técnica da cultivar","Cadastro no SisGen (se espécie nativa/PG envolvida)","Pedido de Proteção de Cultivar (MAPA/CVRD)","Instrumento de cotitularidade (quando aplicável)"],
    "base_legal":"Art. 22, VII do Regimento; Lei 9.456/1997",
    "alerta":"⚠️ Cultivares derivadas de espécies nativas da Amazônia exigem, adicionalmente, cadastro no SisGen."},
  "C-14":{"nome":"Desenvolvimento de marca pelo empreendimento incubado","bloco":4,
    "titularidade":"Empreendimento (100%)",
    "instrumentos":["Declaração de PI pré-existente (se marca já existia)","Proibição expressa de uso indevido da marca IFAC/INCUBAC"],
    "obrigacoes":["Registrar a marca no INPI antes do uso comercial","Não associar a marca própria à marca IFAC sem autorização expressa","Declarar a marca no ato da admissão se já existente"],
    "checklist":["Pedido de Registro de Marca no INPI","Declaração de não uso da marca IFAC sem autorização","TASI com cláusula de uso da marca institucional"],
    "base_legal":"Arts. 40, 53 do Regimento; Lei 9.279/1996","alerta":None},
  "C-19":{"nome":"Know-how / Segredo industrial gerado no processo de incubação","bloco":4,
    "titularidade":"Titularidade ou cotitularidade do IFAC — proteção via sigilo e NDA",
    "instrumentos":["Termo de Confidencialidade específico","NDA — Non-Disclosure Agreement","Cláusula no TASI"],
    "obrigacoes":["Comunicar à COPII a existência do know-how estratégico","Assinar NDA com todos os envolvidos","Não divulgar processos, fórmulas ou metodologias sem autorização","Definir quais informações são confidenciais no instrumento"],
    "checklist":["NDA assinado por todos os envolvidos","Cláusula de know-how no TASI","Lista de informações classificadas como confidenciais","Comunicado à COPII"],
    "base_legal":"Art. 22, IX do Regimento; Art. 2, XXXII, Res. 99/2022","alerta":None},
  "C-20":{"nome":"Indicação Geográfica (IG) de produto do território acreano","bloco":4,
    "titularidade":"Coletivo de produtores/cooperativa — IFAC como apoiador técnico",
    "instrumentos":["Acordo de parceria técnica","Orientação ao registro no INPI"],
    "obrigacoes":["Organizar o coletivo de produtores (associação/cooperativa) antes do pedido","Elaborar regulamento de uso com apoio do IFAC","Protocolar pedido no INPI em nome do coletivo"],
    "checklist":["Constituição da associação/cooperativa de produtores","Regulamento de uso da IG","Pedido de Registro no INPI","Acordo de parceria técnica com o IFAC","Delimitação geográfica documentada"],
    "base_legal":"Art. 22, VIII do Regimento; Lei 9.279/1996, arts. 177–182","alerta":None},
  "C-15":{"nome":"Uso indevido da marca IFAC/INCUBAC pelo empreendimento incubado","bloco":5,
    "titularidade":"Não gera PI — configura INFRAÇÃO",
    "instrumentos":["Notificação formal pela Coordenação do Núcleo","Rescisão do TASI em caso de reincidência"],
    "obrigacoes":["Cessar imediatamente o uso indevido","Responder formalmente à notificação institucional","Comprovar correção do uso irregular"],
    "checklist":["Auto de notificação lavrado pela Coordenação","Prazo para regularização definido","Comprovante de cessação do uso indevido","Registro do ocorrido no prontuário do empreendimento"],
    "base_legal":"Arts. 40, 51, 53 do Regimento; Res. 190/2024",
    "alerta":"🚨 INFRAÇÃO: O uso indevido da marca IFAC pode induzir terceiros a erro. Sujeita à rescisão do TASI e responsabilidade civil."},
  "C-16":{"nome":"Criação com participação de duas ICTs (ex: IFAC + UFAC)","bloco":6,
    "titularidade":"Cotitularidade IFAC + outra ICT",
    "instrumentos":["Acordo de Parceria entre as ICTs","Instrumento específico de cotitularidade"],
    "obrigacoes":["Formalizar Acordo de Parceria entre as instituições antes do início das atividades conjuntas","Definir percentuais de cotitularidade, responsabilidade pelo depósito e repartição de royalties","Ambas as ICTs devem conduzir conjuntamente o processo de proteção"],
    "checklist":["Acordo de Parceria entre IFAC e outra ICT (assinado pelos dirigentes)","Instrumento de cotitularidade específico","Plano de trabalho conjunto definido","Comunicado de Invenção enviado ao NIT de ambas as ICTs","Termo de Confidencialidade de todos os participantes"],
    "base_legal":"Art. 29, Res. 99/2022; Decreto 9.283/2018, art. 37","alerta":None},
}

BLOCOS = {
  1:{"nome":"Origem da Criação",          "icon":"🔍","cor":"verde",    "cenarios":["C-01","C-17","C-18"]},
  2:{"nome":"Uso de Recursos do IFAC",    "icon":"🏛️","cor":"verde",    "cenarios":["C-02","C-03","C-04","C-05","C-06","C-07","C-08"]},
  3:{"nome":"Bioeconomia Amazônica",       "icon":"🌿","cor":"verde",    "cenarios":["C-09","C-10","C-11"]},
  4:{"nome":"Tipos Específicos de Ativos","icon":"💡","cor":"verde",    "cenarios":["C-12","C-13","C-14","C-19","C-20"]},
  5:{"nome":"Infrações",                  "icon":"🚨","cor":"vermelho", "cenarios":["C-15"]},
  6:{"nome":"Parcerias Institucionais",   "icon":"🤝","cor":"verde",    "cenarios":["C-16"]},
}

PERGUNTAS = [
  {"id":"q1","pergunta":"A criação/ativo intelectual foi desenvolvida ANTES do ingresso na INCUBAC?",
   "opcoes":["Sim, antes do ingresso","Não, foi criada durante a incubação","Sim, mas foi aperfeiçoada durante a incubação com recursos do IFAC"]},
  {"id":"q2","pergunta":"Foram utilizados laboratórios, equipamentos ou outros recursos materiais do IFAC?",
   "opcoes":["Sim","Não"]},
  {"id":"q3","pergunta":"Houve participação inventiva de servidor, pesquisador ou professor do IFAC?",
   "opcoes":["Sim","Não"]},
  {"id":"q4","pergunta":"A criação envolve estudante, egresso ou bolsista vinculado ao IFAC como criador?",
   "opcoes":["Sim","Não"]},
  {"id":"q5","pergunta":"Existe Acordo de Parceria formal formalizado entre o IFAC e o empreendimento?",
   "opcoes":["Sim","Não"]},
  {"id":"q6","pergunta":"A criação é derivada de tecnologia já existente de titularidade do IFAC?",
   "opcoes":["Sim","Não"]},
  {"id":"q7","pergunta":"A criação envolve bioeconomia, recursos biológicos nativos da Amazônia ou patrimônio genético?",
   "opcoes":["Sim, sem uso de recursos do IFAC","Sim, com uso de recursos do IFAC","Sim, com envolvimento de comunidades tradicionais (CTA)","Não"]},
  {"id":"q8","pergunta":"Qual é o tipo principal do ativo intelectual desenvolvido?",
   "opcoes":["Patente de invenção / Modelo de utilidade","Software / Programa de computador","Cultivar / Espécie vegetal melhorada","Marca","Know-how / Segredo industrial","Indicação Geográfica","Outro (DI, topografia, direito autoral)"]},
  {"id":"q9","pergunta":"O desenvolvimento envolveu parceria formal com outra ICT (ex: UFAC, EMBRAPA)?",
   "opcoes":["Sim","Não"]},
  {"id":"q10","pergunta":"Houve uso indevido da marca IFAC ou INCUBAC (sem autorização expressa)?",
   "opcoes":["Sim","Não"]},
]

PBLOCO = {1:["q1"],2:["q2","q3","q4","q5","q6"],3:["q7"],4:["q8"],5:["q10"],6:["q9"]}

def diagnostico(r):
    f=[]
    if r.get("q10")=="Sim": f.append("C-15")
    if r.get("q9")=="Sim":  f.append("C-16")
    q1=r.get("q1","")
    if   q1=="Sim, antes do ingresso":                                              f.append("C-17")
    elif q1=="Sim, mas foi aperfeiçoada durante a incubação com recursos do IFAC":  f.append("C-18")
    q7=r.get("q7","")
    if   q7=="Sim, sem uso de recursos do IFAC":                                    f.append("C-09")
    elif q7=="Sim, com uso de recursos do IFAC":                                    f.append("C-10")
    elif q7=="Sim, com envolvimento de comunidades tradicionais (CTA)":             f.append("C-11")
    q8=r.get("q8","")
    if   q8=="Software / Programa de computador":                                   f.append("C-12")
    elif q8=="Cultivar / Espécie vegetal melhorada":                                f.append("C-13")
    elif q8=="Marca":                                                               f.append("C-14")
    elif q8=="Know-how / Segredo industrial":                                       f.append("C-19")
    elif q8=="Indicação Geográfica":                                                f.append("C-20")
    if q1=="Não, foi criada durante a incubação":
        if   r.get("q5")=="Sim": f.append("C-05")
        elif r.get("q3")=="Sim": f.append("C-03")
        elif r.get("q4")=="Sim": f.append("C-04")
        elif r.get("q2")=="Sim": f.append("C-02")
        elif r.get("q6")=="Sim": f.append("C-06")
        else:                    f.append("C-01")
    return list(dict.fromkeys(f))

def gerar_pdf(nome,emp,data_r,respostas,cids):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    story=[]
    stls=getSampleStyleSheet()
    cR=colors.HexColor("#C8102E"); cG=colors.HexColor("#007A3D")
    cD=colors.HexColor("#0D0D0D"); cL=colors.HexColor("#F5F5F5"); cGr=colors.HexColor("#888")
    tit=ParagraphStyle("tit",parent=stls["Title"],fontSize=14,textColor=colors.white,alignment=TA_CENTER,fontName="Helvetica-Bold",spaceAfter=4)
    h1s=ParagraphStyle("h1",parent=stls["Heading1"],fontSize=12,textColor=cR,spaceAfter=5,fontName="Helvetica-Bold")
    h2s=ParagraphStyle("h2",parent=stls["Heading2"],fontSize=10,textColor=cG,spaceAfter=3,fontName="Helvetica-Bold")
    bds=ParagraphStyle("bd",parent=stls["Normal"],fontSize=9.5,spaceAfter=3,leading=13,textColor=colors.HexColor("#222"))
    sms=ParagraphStyle("sm",parent=stls["Normal"],fontSize=8.5,textColor=cGr,spaceAfter=3,leading=12)
    als=ParagraphStyle("al",parent=stls["Normal"],fontSize=9,textColor=cR,spaceAfter=3,leading=13,fontName="Helvetica-Bold")
    hd=[[Paragraph('<font color="white"><b>INCUBAC/IFAC — Classificador de Cenários de PI</b><br/><font size="9">Instituto Federal de Educação, Ciência e Tecnologia do Acre</font></font>',tit)]]
    ht=Table(hd,colWidths=[17*cm])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cD),("LEFTPADDING",(0,0),(-1,-1),14),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
    story.append(ht); story.append(Spacer(1,.4*cm))
    inf=[[Paragraph("<b>Respondente:</b>",bds),Paragraph(nome,bds),Paragraph("<b>Data:</b>",bds),Paragraph(data_r,bds)],
         [Paragraph("<b>Empreendimento:</b>",bds),Paragraph(emp,bds),Paragraph("<b>Cenários:</b>",bds),Paragraph(str(len(cids)),bds)]]
    it=Table(inf,colWidths=[3.5*cm,6*cm,3*cm,4.5*cm])
    it.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cL),("GRID",(0,0),(-1,-1),.5,colors.HexColor("#E0E0E0")),("LEFTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(it); story.append(Spacer(1,.3*cm))
    story.append(HRFlowable(width="100%",thickness=2,color=cR)); story.append(Spacer(1,.3*cm))
    story.append(Paragraph("CENÁRIOS DE PI IDENTIFICADOS",h1s)); story.append(Spacer(1,.2*cm))
    for cid in cids:
        c=CENARIOS[cid]; hc=cR if cid=="C-15" else cG
        ch=[[Paragraph(f'<font color="white"><b>{cid} — {c["nome"]}</b></font>',ParagraphStyle("ch",parent=stls["Normal"],fontSize=10,textColor=colors.white,fontName="Helvetica-Bold"))]]
        ct=Table(ch,colWidths=[17*cm])
        ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),hc),("LEFTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(ct)
        dd=[[Paragraph("<b>Titularidade:</b>",bds),Paragraph(c["titularidade"],bds)],[Paragraph("<b>Base Legal:</b>",bds),Paragraph(c["base_legal"],sms)]]
        dt=Table(dd,colWidths=[3.5*cm,13.5*cm])
        dt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cL),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#E8E8E8")),("LEFTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(dt)
        story.append(Paragraph("Instrumentos Jurídicos Obrigatórios:",h2s))
        for i in c["instrumentos"]: story.append(Paragraph(f"• {i}",bds))
        story.append(Paragraph("Obrigações do Empreendimento:",h2s))
        for o in c["obrigacoes"]:   story.append(Paragraph(f"• {o}",bds))
        story.append(Paragraph("Checklist de Documentos:",h2s))
        for d in c["checklist"]:
            cr=Table([[Paragraph("□",bds),Paragraph(d,bds)]],colWidths=[.6*cm,16.4*cm])
            cr.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
            story.append(cr)
        if c["alerta"]:
            ar=Table([[Paragraph(c["alerta"],als)]],colWidths=[17*cm])
            ar.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FFF3F3")),("LEFTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
            story.append(ar)
        story.append(Spacer(1,.3*cm)); story.append(HRFlowable(width="100%",thickness=.4,color=colors.HexColor("#E0E0E0"))); story.append(Spacer(1,.2*cm))
    story.append(Paragraph("RESPOSTAS DO DIAGNÓSTICO",h1s))
    qd=[["#","Pergunta","Resposta"]]
    for q in PERGUNTAS: qd.append([q["id"].upper(),q["pergunta"],respostas.get(q["id"],"—")])
    qt=Table(qd,colWidths=[1*cm,10*cm,6*cm])
    qt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),cD),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,cL]),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#DDDDDD")),("LEFTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(qt); story.append(Spacer(1,.5*cm))
    story.append(Paragraph("<i>Classificação automática — competência definitiva da COPII/NIT. Ferramenta desenvolvida na disciplina Oficina Profissional por discente do PROFNIT/IFAC.</i>",sms))
    doc.build(story); buf.seek(0); return buf

# ── SESSION STATE ─────────────────────────────────────────────────────────
for k,v in [("modulo","respondente"),("bloco",0),("respostas",{}),
            ("nome",""),("empreendimento",""),("concluido",False),
            ("db",[]),("auth_gestao",False)]:
    if k not in st.session_state: st.session_state[k]=v

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(logo_html(LOGO_IFAC_B64,"190px"),unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:12px;'>{logo_html(LOGO_PROFNIT_B64,'130px')}</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚖️ Classificador de Cenários de PI")
    st.markdown(f"<small style='color:#aaa;'>INCUBAC — Instituto Federal do Acre</small>",unsafe_allow_html=True)
    st.markdown("---")
    sel=st.radio("**Módulo de acesso:**",["🧑‍💼 Respondente","🔒 Painel de Gestão"],key="nav",
                  index=0 if st.session_state["modulo"]=="respondente" else 1)
    st.session_state["modulo"]="respondente" if "Respondente" in sel else "gestao"
    if st.session_state["modulo"]=="respondente":
        st.markdown("---"); st.markdown("**Blocos do Diagnóstico:**")
        ba=st.session_state.get("bloco",0)
        for nb,b in BLOCOS.items():
            mk=f"{'▶️' if ba==nb else b['icon']} **Bloco {nb}** — {b['nome']}"
            st.markdown(mk)
    st.markdown("---")
    st.markdown("""<div style="font-size:.72rem;color:#888;line-height:1.7;">
© INCUBAC/IFAC · Regimento Interno dos Núcleos Incubadores<br/>
Res. CONSU/IFAC nº 99/2022<br/><br/>
<i>Esta ferramenta de classificador de cenários de PI foi desenvolvida a partir da disciplina de
<b>Oficina Profissional</b> por discente de mestrado do <b>PROFNIT</b>.</i>
</div>""",unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-bar">
  <div class="header-logos">
    {logo_html(LOGO_IFAC_B64,"210px")}
    <div style="flex:1"></div>
    {logo_html(LOGO_PROFNIT_B64,"120px")}
  </div>
  <h1>⚖️ Classificador de Cenários de PI</h1>
  <p>INCUBAC — Incubadora de Empreendimentos de Impacto do IFAC &nbsp;|&nbsp; Propriedade Intelectual &amp; Transferência de Tecnologia</p>
</div>
""",unsafe_allow_html=True)

# ── MÓDULO RESPONDENTE ────────────────────────────────────────────────────
if st.session_state["modulo"]=="respondente":
    ETAPAS=["Identificação","Bloco 1","Bloco 2","Bloco 3","Bloco 4","Bloco 5","Bloco 6","Resultado"]
    bl=st.session_state["bloco"]
    st.progress(bl/(len(ETAPAS)-1))
    cols=st.columns(len(ETAPAS))
    for i,e in enumerate(ETAPAS):
        cor=RED if i==bl else (GREEN if i<bl else "#555")
        peso="700" if i==bl else "400"
        cols[i].markdown(f"<p style='text-align:center;color:{cor};font-weight:{peso};font-size:.7rem;'>{e}</p>",unsafe_allow_html=True)
    st.markdown("---")
    if bl==0:
        st.markdown('<div class="step-pill">Etapa 1 de 7 — Identificação</div>',unsafe_allow_html=True)
        st.markdown('<div class="block-card"><h3>👤 Identificação do Respondente</h3><p>Preencha os dados para iniciar o diagnóstico de cenários de PI.</p></div>',unsafe_allow_html=True)
        nv=st.text_input("👤 Nome completo do respondente",value=st.session_state["nome"],key="ni",placeholder="Ex.: Maria da Silva")
        ev=st.text_input("🏢 Nome do empreendimento / startup",value=st.session_state["empreendimento"],key="ei",placeholder="Ex.: BioAcreTech")
        c1,c2=st.columns([1,4])
        with c1:
            if st.button("🗑️ Limpar",key="lmp0"):
                st.session_state["nome"]=""; st.session_state["empreendimento"]=""; st.rerun()
        with c2:
            if st.button("Avançar →",type="primary",key="av0"):
                if nv and ev:
                    st.session_state["nome"]=nv; st.session_state["empreendimento"]=ev
                    st.session_state["bloco"]=1; st.rerun()
                else: st.warning("Preencha nome e empreendimento para continuar.")
    elif 1<=bl<=6:
        bi=BLOCOS[bl]
        st.markdown(f'<div class="step-pill">Bloco {bl} de 6 — {bi["icon"]} {bi["nome"]}</div>',unsafe_allow_html=True)
        cls="block-card red" if bi["cor"]=="vermelho" else "block-card"
        st.markdown(f'<div class="{cls}"><h3>{bi["icon"]} {bi["nome"]}</h3></div>',unsafe_allow_html=True)
        st.caption(f"Cenários cobertos: {', '.join(bi['cenarios'])}")
        pergs=[p for p in PERGUNTAS if p["id"] in PBLOCO.get(bl,[])]
        for pq in pergs:
            st.markdown(f"**{pq['pergunta']}**")
            cur=st.session_state["respostas"].get(pq["id"],None)
            idx=pq["opcoes"].index(cur) if cur in pq["opcoes"] else None
            resp=st.radio("",pq["opcoes"],index=idx,key=f"r{bl}{pq['id']}")
            if resp: st.session_state["respostas"][pq["id"]]=resp
            st.markdown("---")
        c1,c2,c3=st.columns([1,1,3])
        with c1:
            if st.button("← Voltar",key=f"vt{bl}"):
                st.session_state["bloco"]=bl-1; st.rerun()
        with c2:
            if st.button("🗑️ Limpar bloco",key=f"lmp{bl}"):
                for pq in pergs: st.session_state["respostas"].pop(pq["id"],None)
                st.rerun()
        with c3:
            lbl="Avançar →" if bl<6 else "Ver Resultado →"
            if st.button(lbl,type="primary",key=f"av{bl}"):
                if all(pq["id"] in st.session_state["respostas"] for pq in pergs):
                    st.session_state["bloco"]=bl+1; st.rerun()
                else: st.warning("Responda todas as perguntas antes de avançar.")
    elif bl==7:
        st.markdown('<div class="step-pill">✅ Diagnóstico Concluído — Resultado</div>',unsafe_allow_html=True)
        cids=diagnostico(st.session_state["respostas"])
        nome=st.session_state["nome"]; emp=st.session_state["empreendimento"]
        data=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        if not st.session_state["concluido"]:
            st.session_state["db"].append({"id":len(st.session_state["db"])+1,"nome":nome,"empreendimento":emp,"data":data,"respostas":dict(st.session_state["respostas"]),"cenarios":cids})
            st.session_state["concluido"]=True
        st.markdown(f'<div class="result-card"><b>Respondente:</b> {nome} &nbsp;&nbsp; <b>Empreendimento:</b> {emp}<br/><b>Data:</b> {data} &nbsp;&nbsp; <span class="tag-verde">{len(cids)} cenário(s) identificado(s)</span></div>',unsafe_allow_html=True)
        if not cids: st.info("Nenhum cenário específico identificado. Consulte a COPII/NIT para análise individualizada.")
        for cid in cids:
            c=CENARIOS[cid]
            cls="result-card infraction" if cid=="C-15" else "result-card"
            st.markdown(f'<div class="{cls}">',unsafe_allow_html=True)
            tc="tag-vermelho" if cid=="C-15" else "tag-verde"
            st.markdown(f'<span class="{tc}">{cid}</span>',unsafe_allow_html=True)
            st.markdown(f"### {c['nome']}")
            ca,cb=st.columns(2)
            with ca:
                st.markdown("**⚖️ Titularidade:**"); st.info(c["titularidade"])
                st.markdown("**📄 Instrumentos Obrigatórios:**")
                for i in c["instrumentos"]: st.markdown(f"- {i}")
            with cb:
                st.markdown("**✅ Obrigações:**")
                for o in c["obrigacoes"]: st.markdown(f"- {o}")
                st.markdown("**📋 Checklist:**")
                for di in c["checklist"]: st.checkbox(di,key=f"ck{cid}{di[:18]}")
            st.markdown(f"**📚 Base Legal:** `{c['base_legal']}`")
            if c["alerta"]: st.error(c["alerta"])
            st.markdown('</div>',unsafe_allow_html=True); st.markdown("---")
        st.markdown("### 📥 Exportar Relatório em PDF")
        pdf_b=gerar_pdf(nome,emp,data,st.session_state["respostas"],cids)
        st.download_button("⬇️ Baixar Relatório em PDF",data=pdf_b,
            file_name=f"relatorio_PI_{emp.replace(' ','_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",type="primary")
        st.markdown("---")
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Revisar Respostas"):
                st.session_state["bloco"]=6; st.session_state["concluido"]=False; st.rerun()
        with c2:
            if st.button("🔄 Novo Diagnóstico"):
                for k in ["bloco","respostas","nome","empreendimento","concluido"]: st.session_state.pop(k,None)
                st.rerun()
else:
    if not st.session_state["auth_gestao"]:
        st.markdown(f'<div class="login-card"><h2>🔒 Acesso Restrito</h2><p>Painel exclusivo para <b>COPII / NIT</b> e gestores da INCUBAC.<br/>Informe a senha institucional para continuar.</p></div>',unsafe_allow_html=True)
        cc=st.columns([1,2,1])
        with cc[1]:
            senha_in=st.text_input("Senha de acesso:",type="password",key="sin",placeholder="Senha institucional")
            if st.button("🔓 Acessar Painel de Gestão",type="primary",key="btn_login"):
                if senha_in=="ifac.incubac.2026@":
                    st.session_state["auth_gestao"]=True; st.rerun()
                else: st.error("Senha incorreta. Acesso negado.")
    else:
        ch,cs=st.columns([5,1])
        with ch: st.markdown("## 📊 Painel de Gestão — COPII/NIT")
        with cs:
            if st.button("🔒 Sair"):
                st.session_state["auth_gestao"]=False; st.rerun()
        st.markdown("Visualização de todos os diagnósticos realizados pelos empreendimentos incubados.")
        db=st.session_state.get("db",[])
        if not db: st.info("Nenhum diagnóstico realizado ainda.")
        else:
            freq={}
            for e in db:
                for cid in e["cenarios"]: freq[cid]=freq.get(cid,0)+1
            cmf=max(freq,key=freq.get) if freq else "—"
            nb=sum(1 for e in db if any(c in ["C-09","C-10","C-11"] for c in e["cenarios"]))
            m1,m2,m3=st.columns(3)
            m1.metric("Total de Diagnósticos",len(db))
            m2.metric("Cenário Mais Frequente",cmf)
            m3.metric("Alertas de Bioeconomia",nb)
            st.markdown("---")
            busca=st.text_input("🔍 Buscar por nome ou empreendimento:",key="busca",placeholder="Digite para filtrar...")
            for ent in reversed(db):
                if busca and busca.lower() not in ent["nome"].lower() and busca.lower() not in ent["empreendimento"].lower(): continue
                with st.expander(f"#{ent['id']} — {ent['empreendimento']}  |  {ent['nome']}  |  {ent['data']}"):
                    g1,g2=st.columns([2,3])
                    with g1:
                        st.markdown(f"**Respondente:** {ent['nome']}")
                        st.markdown(f"**Empreendimento:** {ent['empreendimento']}")
                        st.markdown(f"**Data:** {ent['data']}")
                    with g2:
                        st.markdown("**Cenários Identificados:**")
                        for cid in ent["cenarios"]:
                            tc="tag-vermelho" if cid=="C-15" else "tag-verde"
                            st.markdown(f'<span class="{tc}">{cid}</span> {CENARIOS[cid]["nome"]}',unsafe_allow_html=True)
                    st.markdown("**Respostas:**")
                    for q in PERGUNTAS:
                        resp=ent["respostas"].get(q["id"],"—")
                        st.markdown(f"<small><b>{q['id'].upper()}:</b> {q['pergunta'][:70]}... → <i>{resp}</i></small>",unsafe_allow_html=True)
                    pg=gerar_pdf(ent["nome"],ent["empreendimento"],ent["data"],ent["respostas"],ent["cenarios"])
                    st.download_button(f"⬇️ PDF — {ent['empreendimento']}",data=pg,
                        file_name=f"relatorio_PI_{ent['empreendimento'].replace(' ','_')}_{ent['id']}.pdf",
                        mime="application/pdf",key=f"pg{ent['id']}")

st.markdown("""
<div class="footer-bar">
  <p>© INCUBAC/IFAC · Regimento Interno dos Núcleos Incubadores · Res. CONSU/IFAC nº 99/2022</p>
  <p>Esta ferramenta de <b>Classificador de Cenários de PI</b> foi desenvolvida a partir da disciplina de
  <b>Oficina Profissional</b> por discente de mestrado do
  <b>PROFNIT</b> (Programa de Pós-Graduação em Propriedade Intelectual e Transferência de Tecnologia para a Inovação).</p>
</div>
""",unsafe_allow_html=True)
