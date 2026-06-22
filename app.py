import streamlit as st
import json
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Classificador de Cenários de PI — INCUBAC/IFAC",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

IFAC_RED   = "#C8102E"
IFAC_GREEN = "#007A3D"
IFAC_LIGHT = "#F5F5F5"
IFAC_DARK  = "#1A1A2E"
IFAC_GRAY  = "#6C757D"

st.markdown(f"""
<style>
  /* Reset global */
  body, .stApp {{ background-color: {IFAC_LIGHT}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {IFAC_DARK} 0%, #16213E 100%);
    color: white;
  }}
  [data-testid="stSidebar"] * {{ color: white !important; }}
  [data-testid="stSidebar"] .stRadio label {{ color: white !important; }}

  /* Header bar */
  .header-bar {{
    background: linear-gradient(90deg, {IFAC_RED} 0%, {IFAC_DARK} 60%, {IFAC_GREEN} 100%);
    padding: 18px 24px;
    border-radius: 8px;
    margin-bottom: 20px;
    color: white;
  }}
  .header-bar h1 {{ color: white; margin: 0; font-size: 1.7rem; }}
  .header-bar p  {{ color: #ddd; margin: 4px 0 0 0; font-size: 0.95rem; }}

  /* Block card */
  .block-card {{
    background: white;
    border-left: 6px solid {IFAC_GREEN};
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }}
  .block-card.red {{ border-left-color: {IFAC_RED}; }}

  /* Tags */
  .tag-verde {{
    background: {IFAC_GREEN}; color: white;
    padding: 2px 10px; border-radius: 12px;
    font-size: 0.78rem; font-weight: 600;
    display: inline-block; margin: 2px;
  }}
  .tag-vermelho {{
    background: {IFAC_RED}; color: white;
    padding: 2px 10px; border-radius: 12px;
    font-size: 0.78rem; font-weight: 600;
    display: inline-block; margin: 2px;
  }}
  .tag-gray {{
    background: {IFAC_GRAY}; color: white;
    padding: 2px 10px; border-radius: 12px;
    font-size: 0.78rem; font-weight: 600;
    display: inline-block; margin: 2px;
  }}

  /* Result card */
  .result-card {{
    background: white;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.09);
    border-top: 4px solid {IFAC_GREEN};
  }}
  .result-card.infraction {{ border-top-color: {IFAC_RED}; }}

  /* Step indicator */
  .step-pill {{
    display: inline-block;
    background: {IFAC_RED};
    color: white;
    border-radius: 20px;
    padding: 4px 16px;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 8px;
  }}

  /* Botão limpar */
  .stButton > button {{
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85rem;
  }}

  /* Divider */
  hr {{ border-color: #e0e0e0; }}

  /* Admin table */
  .admin-row {{
    background: white;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-left: 4px solid {IFAC_GREEN};
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BASE DE DADOS — CENÁRIOS
# ─────────────────────────────────────────────
CENARIOS = {
  "C-01": {
    "nome": "Criação exclusiva do empreendimento",
    "bloco": 1,
    "titularidade": "Empreendimento (100%)",
    "instrumentos": ["Declaração de PI pré-existente ou Parecer da COPII reconhecendo ausência de participação do IFAC"],
    "obrigacoes": [
      "Comunicar à COPII para reconhecimento formal",
      "Manter documentação comprobatória da criação anterior à incubação",
      "Assinar Termo de Confidencialidade no ingresso"
    ],
    "checklist": [
      "Declaração formal de PI pré-existente",
      "Evidências de autoria/desenvolvimento anterior",
      "Termo de Confidencialidade assinado",
      "TASI assinado"
    ],
    "base_legal": "Art. 28 do Regimento Interno; Art. 11, Lei 10.973/2004",
    "alerta": None
  },
  "C-17": {
    "nome": "PI pré-existente declarada no ingresso, sem uso de recursos do IFAC",
    "bloco": 1,
    "titularidade": "Empreendimento (100%)",
    "instrumentos": ["Declaração formal de PI pré-existente arquivada pela COPII"],
    "obrigacoes": [
      "Declarar toda PI pré-existente no ato da admissão",
      "Apresentar documentação comprobatória (pedidos de registro, depósitos, contratos)",
      "Comunicar qualquer aperfeiçoamento posterior que envolva recursos do IFAC"
    ],
    "checklist": [
      "Formulário de Declaração de PI Pré-existente",
      "Cópias de pedidos de proteção/registros existentes",
      "TASI com cláusula de reconhecimento de anterioridade"
    ],
    "base_legal": "Art. 36 do Regimento; Art. 49, §3º do Regimento",
    "alerta": None
  },
  "C-18": {
    "nome": "PI pré-existente aperfeiçoada com recursos do IFAC após ingresso",
    "bloco": 1,
    "titularidade": "PI original: Empreendimento | Aperfeiçoamento: Cotitularidade IFAC + Empreendimento",
    "instrumentos": [
      "Declaração de anterioridade da PI original",
      "Instrumento de cotitularidade sobre o aperfeiçoamento",
      "TASI com cláusula específica"
    ],
    "obrigacoes": [
      "Comunicar à COPII o início do aperfeiçoamento antes de qualquer uso de recursos do IFAC",
      "Delimitar claramente o que é PI original e o que é aperfeiçoamento novo",
      "Formalizar instrumento de cotitularidade antes da utilização de laboratórios ou orientação especializada"
    ],
    "checklist": [
      "Declaração de anterioridade da PI original",
      "Instrumento de cotitularidade (aperfeiçoamento)",
      "Comunicado de Invenção ao NIT",
      "TASI com cláusula específica de aperfeiçoamento"
    ],
    "base_legal": "Art. 36, §3º; Art. 27 do Regimento",
    "alerta": None
  },
  "C-02": {
    "nome": "Criação com uso de laboratório/infraestrutura do IFAC",
    "bloco": 2,
    "titularidade": "IFAC (titular) ou Cotitularidade IFAC + Empreendimento (conforme grau de participação)",
    "instrumentos": [
      "Instrumento de cotitularidade ou cessão",
      "TASI com cláusula específica de PI",
      "Comunicado de Invenção ao NIT"
    ],
    "obrigacoes": [
      "Comunicar à COPII toda criação desenvolvida com uso de infraestrutura do IFAC",
      "Não realizar depósito no INPI antes de manifestação da COPII",
      "Assinar instrumento de cotitularidade antes de qualquer divulgação"
    ],
    "checklist": [
      "Comunicado de Invenção (formulário NIT)",
      "Registro de uso de laboratório/equipamento",
      "Instrumento de cotitularidade assinado",
      "Termo de Confidencialidade",
      "TASI com cláusula de PI"
    ],
    "base_legal": "Arts. 26–27 do Regimento; Art. 16, Res. CONSU/IFAC nº 99/2022",
    "alerta": "⚠️ Não publicar resultados antes do depósito do pedido de patente. A COPII deve ser consultada antes de qualquer divulgação."
  },
  "C-03": {
    "nome": "Criação com orientação técnica de servidor do IFAC",
    "bloco": 2,
    "titularidade": "IFAC (titular) — servidor como coautor/inventor; eventual cotitularidade com o empreendimento",
    "instrumentos": [
      "Instrumento de cotitularidade",
      "Reconhecimento formal de autoria/inventoria do servidor",
      "Comunicado de Invenção ao NIT"
    ],
    "obrigacoes": [
      "Comunicar imediatamente à COPII a participação de servidor na criação",
      "Identificar e documentar a contribuição inventiva do servidor",
      "Aguardar análise da COPII antes de qualquer depósito"
    ],
    "checklist": [
      "Comunicado de Invenção com identificação do servidor coautor",
      "Declaração de participação inventiva do servidor",
      "Instrumento de cotitularidade",
      "Termo de Confidencialidade de todos os envolvidos"
    ],
    "base_legal": "Art. 26 do Regimento; Art. 16, §4º, Res. 99/2022",
    "alerta": "⚠️ A participação de servidor do IFAC como inventor gera titularidade institucional automática. O IFAC é titular dos direitos."
  },
  "C-04": {
    "nome": "Criação por estudante/egresso com uso de estrutura do IFAC",
    "bloco": 2,
    "titularidade": "IFAC (titular) — criador reconhecido como inventor/autor",
    "instrumentos": [
      "Comunicado de Invenção ao NIT",
      "Instrumento de cessão se criador não tiver mais vínculo com o IFAC"
    ],
    "obrigacoes": [
      "Estudante/egresso deve comunicar criação ao NIT",
      "Ser reconhecido formalmente como inventor/autor",
      "Colaborar com o processo de proteção conduzido pelo IFAC"
    ],
    "checklist": [
      "Comunicado de Invenção (formulário NIT)",
      "Comprovação de vínculo com o IFAC no período de criação",
      "Instrumento de cessão (quando egresso sem vínculo atual)",
      "Termo de Confidencialidade"
    ],
    "base_legal": "Art. 16, §§5º e 6º, Res. 99/2022",
    "alerta": None
  },
  "C-05": {
    "nome": "Criação em projeto cooperativo IFAC + empreendimento",
    "bloco": 2,
    "titularidade": "Cotitularidade IFAC + Empreendimento",
    "instrumentos": [
      "Acordo de Parceria para PD&I",
      "Contrato específico com cláusulas de titularidade, repartição e TT",
      "TASI com cláusulas de PI"
    ],
    "obrigacoes": [
      "Formalizar o Acordo de Parceria ANTES do início das atividades conjuntas",
      "Definir em contrato: percentuais de titularidade, responsabilidade pelo depósito, repartição de royalties",
      "Comunicar qualquer resultado protegível à COPII imediatamente"
    ],
    "checklist": [
      "Acordo de Parceria PD&I assinado",
      "Plano de trabalho definindo contribuições de cada parte",
      "Cláusulas de titularidade e repartição no contrato",
      "Comunicado de Invenção ao NIT",
      "Termo de Confidencialidade de todos os envolvidos"
    ],
    "base_legal": "Arts. 27 e 29 do Regimento; Art. 29, Res. 99/2022; Decreto 9.283/2018",
    "alerta": None
  },
  "C-06": {
    "nome": "Criação derivada de tecnologia pré-existente do IFAC",
    "bloco": 2,
    "titularidade": "IFAC (titular da tecnologia-base) — licenciamento ou TT necessário",
    "instrumentos": [
      "Contrato de Licenciamento ou Transferência de Tecnologia",
      "TASI com referência ao contrato de TT"
    ],
    "obrigacoes": [
      "Formalizar Contrato de Licenciamento antes de qualquer uso da tecnologia do IFAC",
      "Pagar royalties conforme contrato",
      "Comunicar aperfeiçoamentos à COPII"
    ],
    "checklist": [
      "Contrato de Licenciamento ou TT assinado",
      "Comprovação de publicação de oferta tecnológica (se exclusivo)",
      "Definição de royalties no instrumento",
      "Termo de Confidencialidade"
    ],
    "base_legal": "Art. 30, Res. 99/2022; Art. 54 do Regimento",
    "alerta": "⚠️ O licenciamento ou TT de tecnologia do IFAC NÃO decorre automaticamente do TASI. É necessário instrumento específico."
  },
  "C-07": {
    "nome": "Aperfeiçoamento de PI pré-existente do empreendimento com apoio do IFAC",
    "bloco": 2,
    "titularidade": "PI original: Empreendimento | PI aperfeiçoada: Cotitularidade IFAC + Empreendimento",
    "instrumentos": [
      "Declaração de anterioridade",
      "Instrumento de cotitularidade para o aperfeiçoamento"
    ],
    "obrigacoes": [
      "Declarar a PI original no ingresso",
      "Comunicar à COPII no início de qualquer aperfeiçoamento com recursos do IFAC",
      "Formalizar instrumento de cotitularidade específico para o aperfeiçoamento"
    ],
    "checklist": [
      "Declaração de PI pré-existente (original)",
      "Comunicado do aperfeiçoamento ao NIT",
      "Instrumento de cotitularidade",
      "TASI com cláusula específica"
    ],
    "base_legal": "Art. 27 do Regimento; Art. 49, §4º do Regimento",
    "alerta": None
  },
  "C-08": {
    "nome": "Criação derivada de pesquisa acadêmica (spin-off / TCC / dissertação)",
    "bloco": 2,
    "titularidade": "IFAC (titular) — criador reconhecido; possível licenciamento preferencial ao criador incubado",
    "instrumentos": [
      "Comunicado de Invenção",
      "Instrumento de licenciamento diferenciado para o criador incubado"
    ],
    "obrigacoes": [
      "Comunicar ao NIT toda criação derivada de pesquisa institucional",
      "Não explorar comercialmente sem formalizar o licenciamento",
      "Solicitar licenciamento preferencial junto à COPII/NIT"
    ],
    "checklist": [
      "Comunicado de Invenção ao NIT",
      "Comprovação da pesquisa-base (TCC, dissertação, projeto)",
      "Instrumento de licenciamento para o criador-incubado",
      "Termo de Confidencialidade"
    ],
    "base_legal": "Art. 16, §§4º–6º, Res. 99/2022; Art. 57 do Regimento",
    "alerta": None
  },
  "C-09": {
    "nome": "Criação em bioeconomia com patrimônio genético — sem uso de recursos do IFAC",
    "bloco": 3,
    "titularidade": "Empreendimento (100%) — sujeito a obrigações de biodiversidade",
    "instrumentos": [
      "Declaração de anterioridade",
      "Comprovação de cadastro no SisGen"
    ],
    "obrigacoes": [
      "Registrar o acesso ao patrimônio genético no SisGen ANTES de qualquer publicação, depósito ou comercialização",
      "Verificar necessidade de repartição de benefícios (Lei 13.123/2015)",
      "Comunicar à COPII para reconhecimento da ausência de participação do IFAC"
    ],
    "checklist": [
      "Cadastro no SisGen (comprovante)",
      "Declaração de anterioridade",
      "Verificação de obrigação de repartição de benefícios",
      "Termo de Confidencialidade"
    ],
    "base_legal": "Art. 30, §3º do Regimento; Lei 13.123/2015",
    "alerta": "⚠️ BIOECONOMIA: O cadastro no SisGen é OBRIGATÓRIO antes de qualquer publicação, depósito de patente ou comercialização. A omissão pode gerar multa e nulidade do pedido."
  },
  "C-10": {
    "nome": "Criação em bioeconomia com uso de recursos do IFAC",
    "bloco": 3,
    "titularidade": "Cotitularidade IFAC + Empreendimento",
    "instrumentos": [
      "Instrumento de cotitularidade",
      "Comprovação de cadastro no SisGen",
      "Instrumento de repartição de benefícios (quando aplicável)",
      "TASI com cláusulas específicas de bioeconomia"
    ],
    "obrigacoes": [
      "Registrar no SisGen ANTES de qualquer publicação ou depósito",
      "Comunicar imediatamente à COPII toda criação em bioeconomia",
      "Formalizar instrumento de cotitularidade",
      "Verificar obrigação de repartição de benefícios com comunidades tradicionais"
    ],
    "checklist": [
      "Cadastro no SisGen (comprovante)",
      "Comunicado de Ativo Intelectual ao NIT",
      "Instrumento de cotitularidade",
      "Instrumento de repartição de benefícios (se CTA envolvido)",
      "Termo de Confidencialidade específico para bioeconomia",
      "TASI com cláusulas de bioeconomia"
    ],
    "base_legal": "Arts. 30–31 do Regimento; Lei 13.123/2015; Res. 99/2022",
    "alerta": "⚠️ BIOECONOMIA + RECURSOS DO IFAC: Dupla obrigação — cotitularidade institucional E cadastro no SisGen. Ambos são pré-requisitos para o apoio institucional à proteção."
  },
  "C-11": {
    "nome": "Criação em bioeconomia com envolvimento de comunidades tradicionais",
    "bloco": 3,
    "titularidade": "Empreendimento e/ou cotitularidade com IFAC + obrigação de repartição com a comunidade",
    "instrumentos": [
      "Instrumento de cotitularidade (quando aplicável)",
      "Acordo de Repartição de Benefícios com a comunidade",
      "CTA — Consentimento Prévio Informado",
      "Cadastro no SisGen"
    ],
    "obrigacoes": [
      "Obter consentimento prévio informado da comunidade detentora",
      "Cadastrar no SisGen",
      "Formalizar Acordo de Repartição de Benefícios",
      "Comunicar à COPII com toda documentação relativa à comunidade",
      "Nunca explorar CTA sem formalização prévia completa"
    ],
    "checklist": [
      "CTA — Consentimento Prévio Informado (documento firmado com a comunidade)",
      "Cadastro no SisGen (comprovante)",
      "Acordo de Repartição de Benefícios",
      "Instrumento de cotitularidade (se recursos do IFAC foram usados)",
      "Protocolo comunitário observado",
      "Comunicado formal à COPII/NIT"
    ],
    "base_legal": "Arts. 23, 43 do Regimento; Lei 13.123/2015; Protocolo de Nagoya; CDB",
    "alerta": "🚨 ALERTA MÁXIMO: A exploração de Conhecimento Tradicional Associado (CTA) sem consentimento da comunidade e sem repartição de benefícios configura infração legal grave, com multa administrativa, embargo e vedação de apoio institucional."
  },
  "C-12": {
    "nome": "Software/Programa de computador desenvolvido com recursos do IFAC",
    "bloco": 4,
    "titularidade": "IFAC (titular) ou cotitularidade, conforme participação",
    "instrumentos": [
      "Comunicado de Invenção ao NIT",
      "Registro junto ao INPI (Lei 9.609/1998)"
    ],
    "obrigacoes": [
      "Comunicar à COPII o desenvolvimento do software",
      "Manter documentação de versionamento, autoria e contribuições",
      "Não disponibilizar publicamente sem autorização do IFAC",
      "Verificar uso de componentes de terceiros e licenças abertas"
    ],
    "checklist": [
      "Comunicado de Software ao NIT",
      "Documentação de versionamento e autoria",
      "Análise de uso de código de terceiros/licenças",
      "Pedido de Registro no INPI (Lei 9.609/98)",
      "Termo de Confidencialidade"
    ],
    "base_legal": "Art. 57 do Regimento; Lei 9.609/1998",
    "alerta": "⚠️ O desenvolvimento de software, algoritmo ou sistema no âmbito da incubação NÃO afasta a análise institucional de titularidade, mesmo quando se trata de código criado pelo empreendedor."
  },
  "C-13": {
    "nome": "Cultivar / espécie vegetal melhorada durante a incubação",
    "bloco": 4,
    "titularidade": "IFAC (titular) ou cotitularidade",
    "instrumentos": [
      "Comunicado de Invenção ao NIT",
      "Pedido de Proteção de Cultivar junto ao MAPA/CVRD"
    ],
    "obrigacoes": [
      "Comunicar à COPII o desenvolvimento da cultivar",
      "Verificar necessidade de cadastro no SisGen (se envolver espécie nativa/PG)",
      "Aguardar análise da COPII antes do pedido de proteção"
    ],
    "checklist": [
      "Comunicado de Invenção ao NIT",
      "Documentação técnica da cultivar",
      "Cadastro no SisGen (se espécie nativa/PG envolvida)",
      "Pedido de Proteção de Cultivar (MAPA/CVRD)",
      "Instrumento de cotitularidade (quando aplicável)"
    ],
    "base_legal": "Art. 22, VII do Regimento; Lei 9.456/1997",
    "alerta": "⚠️ Cultivares derivadas de espécies nativas da Amazônia exigem, adicionalmente, cadastro no SisGen e podem envolver obrigações de repartição de benefícios."
  },
  "C-14": {
    "nome": "Desenvolvimento de marca pelo empreendimento incubado",
    "bloco": 4,
    "titularidade": "Empreendimento (100%)",
    "instrumentos": [
      "Declaração de PI pré-existente (se marca já existia)",
      "Proibição expressa de uso indevido da marca IFAC/INCUBAC"
    ],
    "obrigacoes": [
      "Registrar a marca no INPI antes do uso comercial",
      "Não associar a marca própria à marca IFAC sem autorização expressa",
      "Declarar a marca no ato da admissão se já existente"
    ],
    "checklist": [
      "Pedido de Registro de Marca no INPI",
      "Declaração de não uso da marca IFAC sem autorização",
      "TASI com cláusula de uso da marca institucional"
    ],
    "base_legal": "Arts. 40, 53 do Regimento; Lei 9.279/1996",
    "alerta": None
  },
  "C-19": {
    "nome": "Know-how / segredo industrial gerado no processo de incubação",
    "bloco": 4,
    "titularidade": "Titularidade ou cotitularidade do IFAC — proteção via sigilo e NDA",
    "instrumentos": [
      "Termo de Confidencialidade específico",
      "NDA — Non-Disclosure Agreement",
      "Cláusula no TASI"
    ],
    "obrigacoes": [
      "Comunicar à COPII a existência do know-how estratégico",
      "Assinar NDA com todos os envolvidos no processo",
      "Não divulgar processos, fórmulas, metodologias sem autorização",
      "Definir quais informações são confidenciais no instrumento"
    ],
    "checklist": [
      "NDA assinado por todos os envolvidos",
      "Cláusula de know-how no TASI",
      "Lista de informações classificadas como confidenciais",
      "Comunicado à COPII"
    ],
    "base_legal": "Art. 22, IX do Regimento; Art. 2, XXXII, Res. 99/2022",
    "alerta": None
  },
  "C-20": {
    "nome": "Indicação Geográfica (IG) de produto do território acreano",
    "bloco": 4,
    "titularidade": "Coletivo de produtores/cooperativa (IG não tem titular individual) — IFAC como apoiador técnico",
    "instrumentos": [
      "Acordo de parceria técnica",
      "Orientação ao registro no INPI"
    ],
    "obrigacoes": [
      "Organizar o coletivo de produtores (associação/cooperativa) antes do pedido",
      "Elaborar regulamento de uso com apoio do IFAC",
      "Protocolar pedido no INPI em nome do coletivo"
    ],
    "checklist": [
      "Constituição da associação/cooperativa de produtores",
      "Regulamento de uso da IG",
      "Pedido de Registro no INPI",
      "Acordo de parceria técnica com o IFAC",
      "Delimitação geográfica documentada"
    ],
    "base_legal": "Art. 22, VIII do Regimento; Lei 9.279/1996, arts. 177–182",
    "alerta": None
  },
  "C-15": {
    "nome": "Uso indevido da marca IFAC/INCUBAC pelo empreendimento incubado",
    "bloco": 5,
    "titularidade": "Não gera PI — configura INFRAÇÃO",
    "instrumentos": [
      "Notificação formal pela Coordenação do Núcleo",
      "Rescisão do TASI em caso de reincidência"
    ],
    "obrigacoes": [
      "Cessar imediatamente o uso indevido",
      "Responder formalmente à notificação institucional",
      "Comprovar correção do uso irregular"
    ],
    "checklist": [
      "Auto de notificação lavrado pela Coordenação",
      "Prazo para regularização definido",
      "Comprovante de cessação do uso indevido",
      "Registro do ocorrido no prontuário do empreendimento"
    ],
    "base_legal": "Arts. 40, 51, 53 do Regimento; Res. 190/2024",
    "alerta": "🚨 INFRAÇÃO: O uso indevido da marca IFAC pode induzir terceiros a erro quanto à titularidade e responsabilidade institucional. Sujeita à rescisão do TASI e responsabilidade civil."
  },
  "C-16": {
    "nome": "Criação com participação de duas ICTs (ex: IFAC + UFAC)",
    "bloco": 6,
    "titularidade": "Cotitularidade IFAC + outra ICT",
    "instrumentos": [
      "Acordo de Parceria entre as ICTs",
      "Instrumento específico de cotitularidade"
    ],
    "obrigacoes": [
      "Formalizar Acordo de Parceria entre as instituições antes do início das atividades",
      "Definir percentuais de cotitularidade, responsabilidade pelo depósito e repartição de royalties",
      "Ambas as ICTs devem conduzir conjuntamente o processo de proteção"
    ],
    "checklist": [
      "Acordo de Parceria entre IFAC e outra ICT (assinado pelos dirigentes)",
      "Instrumento de cotitularidade específico",
      "Plano de trabalho conjunto definido",
      "Comunicado de Invenção enviado ao NIT de ambas as ICTs",
      "Termo de Confidencialidade de todos os participantes"
    ],
    "base_legal": "Art. 29, Res. 99/2022; Decreto 9.283/2018, art. 37",
    "alerta": None
  }
}

BLOCOS = {
  1: {"nome": "Origem da Criação", "icon": "🔍", "cor": "verde", "cenarios": ["C-01","C-17","C-18"]},
  2: {"nome": "Uso de Recursos do IFAC", "icon": "🏛️", "cor": "verde", "cenarios": ["C-02","C-03","C-04","C-05","C-06","C-07","C-08"]},
  3: {"nome": "Bioeconomia Amazônica", "icon": "🌿", "cor": "verde", "cenarios": ["C-09","C-10","C-11"]},
  4: {"nome": "Tipos Específicos de Ativos", "icon": "💡", "cor": "verde", "cenarios": ["C-12","C-13","C-14","C-19","C-20"]},
  5: {"nome": "Infrações", "icon": "🚨", "cor": "vermelho", "cenarios": ["C-15"]},
  6: {"nome": "Parcerias Institucionais", "icon": "🤝", "cor": "verde", "cenarios": ["C-16"]}
}

PERGUNTAS_DIAGNOSTICO = [
  {"id": "q1", "pergunta": "A criação/ativo intelectual foi desenvolvida ANTES do ingresso na INCUBAC?",
   "opcoes": ["Sim, antes do ingresso", "Não, foi criada durante a incubação", "Sim, mas foi aperfeiçoada durante a incubação com recursos do IFAC"]},
  {"id": "q2", "pergunta": "Foram utilizados laboratórios, equipamentos, espaços maker ou outros recursos materiais do IFAC?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q3", "pergunta": "Houve participação inventiva (contribuição técnica/científica) de servidor, pesquisador ou professor do IFAC?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q4", "pergunta": "A criação envolve estudante, egresso ou bolsista vinculado ao IFAC como criador?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q5", "pergunta": "Existe Acordo de Parceria formal ou projeto cooperativo formalizado entre o IFAC e o empreendimento?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q6", "pergunta": "A criação é derivada (baseada) em tecnologia já existente de titularidade do IFAC?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q7", "pergunta": "A criação envolve bioeconomia, uso de recursos biológicos nativos da Amazônia ou patrimônio genético?",
   "opcoes": ["Sim, sem uso de recursos do IFAC", "Sim, com uso de recursos do IFAC", "Sim, com envolvimento de comunidades tradicionais (conhecimento tradicional associado - CTA)", "Não"]},
  {"id": "q8", "pergunta": "Qual é o tipo principal do ativo intelectual desenvolvido?",
   "opcoes": ["Patente de invenção / Modelo de utilidade", "Software / Programa de computador", "Cultivar / Espécie vegetal melhorada", "Marca", "Know-how / Segredo industrial", "Indicação Geográfica", "Outro (inclui DI, topografia de CI, direito autoral)"]},
  {"id": "q9", "pergunta": "O desenvolvimento envolveu parceria formal com outra Instituição Científica e Tecnológica (ICT), como UFAC, EMBRAPA, etc.?",
   "opcoes": ["Sim", "Não"]},
  {"id": "q10", "pergunta": "Houve uso indevido da marca IFAC ou INCUBAC pelo empreendimento (sem autorização expressa)?",
   "opcoes": ["Sim", "Não"]}
]


def diagnostico_cenarios(respostas):
    cenarios_identificados = []
    r = respostas

    q1 = r.get("q1","")
    q2 = r.get("q2","")
    q3 = r.get("q3","")
    q4 = r.get("q4","")
    q5 = r.get("q5","")
    q6 = r.get("q6","")
    q7 = r.get("q7","")
    q8 = r.get("q8","")
    q9 = r.get("q9","")
    q10 = r.get("q10","")

    if q10 == "Sim":
        cenarios_identificados.append("C-15")

    if q9 == "Sim":
        cenarios_identificados.append("C-16")

    if q1 == "Sim, antes do ingresso":
        cenarios_identificados.append("C-17")
    elif q1 == "Sim, mas foi aperfeiçoada durante a incubação com recursos do IFAC":
        cenarios_identificados.append("C-18")

    if q7 == "Sim, sem uso de recursos do IFAC":
        cenarios_identificados.append("C-09")
    elif q7 == "Sim, com uso de recursos do IFAC":
        cenarios_identificados.append("C-10")
    elif q7 == "Sim, com envolvimento de comunidades tradicionais (conhecimento tradicional associado - CTA)":
        cenarios_identificados.append("C-11")

    if q8 == "Software / Programa de computador":
        cenarios_identificados.append("C-12")
    elif q8 == "Cultivar / Espécie vegetal melhorada":
        cenarios_identificados.append("C-13")
    elif q8 == "Marca":
        cenarios_identificados.append("C-14")
    elif q8 == "Know-how / Segredo industrial":
        cenarios_identificados.append("C-19")
    elif q8 == "Indicação Geográfica":
        cenarios_identificados.append("C-20")

    if q1 == "Não, foi criada durante a incubação":
        if q5 == "Sim":
            cenarios_identificados.append("C-05")
        elif q3 == "Sim":
            cenarios_identificados.append("C-03")
        elif q4 == "Sim":
            cenarios_identificados.append("C-04")
        elif q2 == "Sim":
            cenarios_identificados.append("C-02")
        elif q6 == "Sim":
            cenarios_identificados.append("C-06")
        elif q8 == "Patente de invenção / Modelo de utilidade":
            c = CENARIOS.get("C-08")
            if c:
                cenarios_identificados.append("C-08")
        else:
            cenarios_identificados.append("C-01")

    cenarios_identificados = list(dict.fromkeys(cenarios_identificados))
    return cenarios_identificados


def gerar_pdf(nome_respondente, empreendimento, data_resposta, respostas, cenarios_ids):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()

    RED   = colors.HexColor("#C8102E")
    GREEN = colors.HexColor("#007A3D")
    DARK  = colors.HexColor("#1A1A2E")
    GRAY  = colors.HexColor("#6C757D")
    LIGHT = colors.HexColor("#F5F5F5")

    title_style = ParagraphStyle("title", parent=styles["Title"],
        fontSize=16, textColor=colors.white, alignment=TA_CENTER,
        spaceAfter=4, fontName="Helvetica-Bold")
    h1_style = ParagraphStyle("h1", parent=styles["Heading1"],
        fontSize=13, textColor=RED, spaceAfter=6, fontName="Helvetica-Bold")
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"],
        fontSize=11, textColor=GREEN, spaceAfter=4, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("body", parent=styles["Normal"],
        fontSize=9.5, spaceAfter=4, leading=14)
    small_style = ParagraphStyle("small", parent=styles["Normal"],
        fontSize=8.5, textColor=GRAY, spaceAfter=3, leading=12)
    alert_style = ParagraphStyle("alert", parent=styles["Normal"],
        fontSize=9, textColor=RED, spaceAfter=4, leading=13,
        fontName="Helvetica-Bold")

    header_data = [[Paragraph(
        '<font color="white"><b>INCUBAC/IFAC</b><br/>'
        'Classificador de Cenários de Propriedade Intelectual<br/>'
        '<font size="9">Instituto Federal de Educação, Ciência e Tecnologia do Acre</font></font>',
        title_style)]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [6,6,6,6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    info_data = [
        ["Respondente:", nome_respondente, "Data:", data_resposta],
        ["Empreendimento:", empreendimento, "Nº de Cenários:", str(len(cenarios_ids))]
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 6*cm, 3*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=RED))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("CENÁRIOS DE PI IDENTIFICADOS", h1_style))
    story.append(Spacer(1, 0.2*cm))

    for cid in cenarios_ids:
        c = CENARIOS[cid]
        is_infraction = cid == "C-15"

        cor_header = RED if is_infraction else GREEN

        header_row = [[Paragraph(
            f'<font color="white"><b>{cid} — {c["nome"]}</b></font>',
            ParagraphStyle("ch", parent=styles["Normal"],
                fontSize=10.5, textColor=colors.white, fontName="Helvetica-Bold"))]]
        ct = Table(header_row, colWidths=[17*cm])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), cor_header),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))
        story.append(ct)

        detail_data = [
            [Paragraph("<b>Titularidade:</b>", body_style),
             Paragraph(c["titularidade"], body_style)],
            [Paragraph("<b>Base Legal:</b>", body_style),
             Paragraph(c["base_legal"], small_style)],
        ]
        dt = Table(detail_data, colWidths=[3.5*cm, 13.5*cm])
        dt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8F8F8")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#E8E8E8")),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(dt)

        story.append(Paragraph("Instrumentos Jurídicos Obrigatórios:", h2_style))
        for inst in c["instrumentos"]:
            story.append(Paragraph(f"• {inst}", body_style))

        story.append(Paragraph("Obrigações do Empreendimento:", h2_style))
        for ob in c["obrigacoes"]:
            story.append(Paragraph(f"• {ob}", body_style))

        story.append(Paragraph("Checklist de Documentos:", h2_style))
        check_rows = [[Paragraph("□", body_style), Paragraph(doc_item, body_style)]
                      for doc_item in c["checklist"]]
        if check_rows:
            ctbl = Table(check_rows, colWidths=[0.6*cm, 16.4*cm])
            ctbl.setStyle(TableStyle([
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ]))
            story.append(ctbl)

        if c["alerta"]:
            story.append(Spacer(1, 0.1*cm))
            alerta_data = [[Paragraph(c["alerta"], alert_style)]]
            at = Table(alerta_data, colWidths=[17*cm])
            at.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF3F3")),
                ("LEFTLINECOLOR", (0,0), (0,-1), RED),
                ("LEFTLINEWIDTH", (0,0), (0,-1), 3),
                ("LEFTPADDING", (0,0), (-1,-1), 10),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(at)

        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E0E0E0")))
        story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("RESPOSTAS DO DIAGNÓSTICO", h1_style))
    story.append(Spacer(1, 0.2*cm))

    q_data = [["#", "Pergunta", "Resposta"]]
    for q in PERGUNTAS_DIAGNOSTICO:
        resp = respostas.get(q["id"], "Não respondida")
        q_data.append([q["id"].upper(), q["pergunta"], resp])

    q_table = Table(q_data, colWidths=[1*cm, 10*cm, 6*cm])
    q_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
    ]))
    story.append(q_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<i>Documento gerado automaticamente pelo Classificador de Cenários de PI — INCUBAC/IFAC. "
        "A classificação definitiva dos cenários é de competência da COPII/NIT, conforme arts. 24 e 25 "
        "do Regimento Interno dos Núcleos Incubadores da INCUBAC/IFAC.</i>",
        small_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


def salvar_resposta(nome, empreendimento, respostas, cenarios):
    if "respostas_db" not in st.session_state:
        st.session_state["respostas_db"] = []
    entrada = {
        "id": len(st.session_state["respostas_db"]) + 1,
        "nome": nome,
        "empreendimento": empreendimento,
        "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "respostas": respostas,
        "cenarios": cenarios
    }
    st.session_state["respostas_db"].append(entrada)


# ─────────────────────────────────────────────
# INICIALIZAÇÃO DO SESSION STATE
# ─────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "respondente"
if "bloco_atual" not in st.session_state:
    st.session_state["bloco_atual"] = 0
if "respostas" not in st.session_state:
    st.session_state["respostas"] = {}
if "nome" not in st.session_state:
    st.session_state["nome"] = ""
if "empreendimento" not in st.session_state:
    st.session_state["empreendimento"] = ""
if "concluido" not in st.session_state:
    st.session_state["concluido"] = False
if "respostas_db" not in st.session_state:
    st.session_state["respostas_db"] = []

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚖️ Classificador PI")
    st.markdown("**INCUBAC / IFAC**")
    st.markdown("---")
    pagina_sel = st.radio(
        "Módulo:",
        ["🧑‍💼 Respondente", "📊 Painel de Gestão"],
        key="nav_radio"
    )
    st.session_state["pagina"] = "respondente" if "Respondente" in pagina_sel else "gestao"
    st.markdown("---")
    st.markdown("**Blocos do Diagnóstico:**")
    for nb, b in BLOCOS.items():
        st.markdown(f"{b['icon']} **Bloco {nb}** — {b['nome']}")
    st.markdown("---")
    st.caption("© INCUBAC/IFAC · Regimento Interno dos Núcleos Incubadores · Res. CONSU/IFAC nº 99/2022")


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <h1>⚖️ Classificador de Cenários de PI</h1>
  <p>INCUBAC — Incubadora de Empreendimentos de Impacto do IFAC &nbsp;|&nbsp; 
  Propriedade Intelectual & Transferência de Tecnologia</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO RESPONDENTE
# ─────────────────────────────────────────────
if st.session_state["pagina"] == "respondente":

    ETAPAS = ["Identificação", "Bloco 1", "Bloco 2", "Bloco 3", "Bloco 4", "Bloco 5", "Bloco 6", "Resultado"]
    bloco = st.session_state["bloco_atual"]

    # Barra de progresso
    progresso = bloco / (len(ETAPAS) - 1)
    st.progress(progresso)
    col_et = st.columns(len(ETAPAS))
    for i, e in enumerate(ETAPAS):
        cor = IFAC_RED if i == bloco else (IFAC_GREEN if i < bloco else IFAC_GRAY)
        peso = "700" if i == bloco else "400"
        col_et[i].markdown(f"<p style='text-align:center;color:{cor};font-weight:{peso};font-size:0.72rem;'>{e}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # ── ETAPA 0: IDENTIFICAÇÃO ──
    if bloco == 0:
        st.markdown('<div class="step-pill">Etapa 1 de 7 — Identificação</div>', unsafe_allow_html=True)
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Identificação do Respondente")
        st.markdown("Preencha os dados abaixo para iniciar o diagnóstico.")
        nome_inp = st.text_input("Nome completo do respondente", value=st.session_state["nome"], key="nome_inp")
        emp_inp  = st.text_input("Nome do empreendimento / startup", value=st.session_state["empreendimento"], key="emp_inp")
        st.markdown('</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1,4])
        with col1:
            if st.button("🗑️ Limpar", key="limpar_id"):
                st.session_state["nome"] = ""
                st.session_state["empreendimento"] = ""
                st.rerun()
        with col2:
            if st.button("Avançar →", type="primary", key="avancar_0"):
                if nome_inp and emp_inp:
                    st.session_state["nome"] = nome_inp
                    st.session_state["empreendimento"] = emp_inp
                    st.session_state["bloco_atual"] = 1
                    st.rerun()
                else:
                    st.warning("Por favor, preencha nome e empreendimento para continuar.")

    # ── BLOCOS 1–6 ──
    elif 1 <= bloco <= 6:
        b_info = BLOCOS[bloco]
        st.markdown(f'<div class="step-pill">Bloco {bloco} de 6 — {b_info["icon"]} {b_info["nome"]}</div>', unsafe_allow_html=True)

        borda = IFAC_RED if b_info["cor"] == "vermelho" else IFAC_GREEN
        st.markdown(f'<div class="block-card{"  red" if b_info["cor"] == "vermelho" else ""}">', unsafe_allow_html=True)
        st.markdown(f"### {b_info['icon']} {b_info['nome']}")
        st.caption(f"Cenários: {', '.join(b_info['cenarios'])}")
        st.markdown("Responda as perguntas abaixo relativas a este bloco.")
        st.markdown('</div>', unsafe_allow_html=True)

        PERGUNTAS_BLOCO = {
          1: ["q1"],
          2: ["q2","q3","q4","q5","q6"],
          3: ["q7"],
          4: ["q8"],
          5: ["q10"],
          6: ["q9"]
        }
        perguntas_bloco = PERGUNTAS_BLOCO.get(bloco, [])
        perguntas_obj = [p for p in PERGUNTAS_DIAGNOSTICO if p["id"] in perguntas_bloco]

        for pq in perguntas_obj:
            st.markdown(f"**{pq['pergunta']}**")
            cur = st.session_state["respostas"].get(pq["id"], None)
            idx = pq["opcoes"].index(cur) if cur in pq["opcoes"] else None
            resp = st.radio("", pq["opcoes"], index=idx, key=f"radio_{bloco}_{pq['id']}", horizontal=False)
            if resp:
                st.session_state["respostas"][pq["id"]] = resp
            st.markdown("---")

        col_l, col_v, col_a = st.columns([1,1,3])
        with col_l:
            if st.button("← Voltar", key=f"voltar_{bloco}"):
                st.session_state["bloco_atual"] = bloco - 1
                st.rerun()
        with col_v:
            if st.button("🗑️ Limpar bloco", key=f"limpar_{bloco}"):
                for pq in perguntas_obj:
                    if pq["id"] in st.session_state["respostas"]:
                        del st.session_state["respostas"][pq["id"]]
                st.rerun()
        with col_a:
            if st.button("Avançar →" if bloco < 6 else "Ver Resultado →", type="primary", key=f"avancar_{bloco}"):
                respondidas = all(pq["id"] in st.session_state["respostas"] for pq in perguntas_obj)
                if respondidas:
                    st.session_state["bloco_atual"] = bloco + 1
                    st.rerun()
                else:
                    st.warning("Responda todas as perguntas deste bloco antes de avançar.")

    # ── ETAPA 7: RESULTADO ──
    elif bloco == 7:
        st.markdown('<div class="step-pill">Resultado — Diagnóstico Concluído</div>', unsafe_allow_html=True)

        cenarios_ids = diagnostico_cenarios(st.session_state["respostas"])
        nome  = st.session_state["nome"]
        emp   = st.session_state["empreendimento"]
        data  = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        if not st.session_state["concluido"]:
            salvar_resposta(nome, emp, dict(st.session_state["respostas"]), cenarios_ids)
            st.session_state["concluido"] = True

        st.markdown(f"""
        <div class="result-card">
          <b>Respondente:</b> {nome} &nbsp;&nbsp; <b>Empreendimento:</b> {emp}<br/>
          <b>Data:</b> {data} &nbsp;&nbsp;
          <span class="tag-verde">{len(cenarios_ids)} cenário(s) identificado(s)</span>
        </div>
        """, unsafe_allow_html=True)

        if not cenarios_ids:
            st.info("Nenhum cenário específico foi identificado com base nas suas respostas. Consulte a COPII/NIT para análise individualizada.")
        else:
            for cid in cenarios_ids:
                c = CENARIOS[cid]
                is_inf = cid == "C-15"
                borda_cor = IFAC_RED if is_inf else IFAC_GREEN
                cls = "result-card infraction" if is_inf else "result-card"

                st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)

                tag_cls = "tag-vermelho" if is_inf else "tag-verde"
                st.markdown(f'<span class="{tag_cls}">{cid}</span>', unsafe_allow_html=True)
                st.markdown(f"### {c['nome']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**⚖️ Titularidade:**")
                    st.info(c["titularidade"])
                    st.markdown(f"**📄 Instrumentos Jurídicos Obrigatórios:**")
                    for inst in c["instrumentos"]:
                        st.markdown(f"- {inst}")
                with col_b:
                    st.markdown(f"**✅ Obrigações do Empreendimento:**")
                    for ob in c["obrigacoes"]:
                        st.markdown(f"- {ob}")
                    st.markdown(f"**📋 Checklist de Documentos:**")
                    for doc_item in c["checklist"]:
                        st.checkbox(doc_item, key=f"check_{cid}_{doc_item[:20]}")

                st.markdown(f"**📚 Base Legal:** `{c['base_legal']}`")

                if c["alerta"]:
                    st.error(c["alerta"])

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

        st.markdown("### 📥 Exportar Relatório")
        pdf_buf = gerar_pdf(nome, emp, data, st.session_state["respostas"], cenarios_ids)
        st.download_button(
            label="⬇️ Baixar Relatório em PDF",
            data=pdf_buf,
            file_name=f"relatorio_PI_{emp.replace(' ','_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            type="primary"
        )

        st.markdown("---")
        col_r, col_n = st.columns(2)
        with col_r:
            if st.button("← Revisar Respostas"):
                st.session_state["bloco_atual"] = 6
                st.session_state["concluido"] = False
                st.rerun()
        with col_n:
            if st.button("🔄 Novo Diagnóstico"):
                for k in ["bloco_atual","respostas","nome","empreendimento","concluido"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()


# ─────────────────────────────────────────────
# MÓDULO GESTÃO
# ─────────────────────────────────────────────
else:
    st.markdown("## 📊 Painel de Gestão — COPII/NIT")
    st.markdown("Visualização de todos os diagnósticos realizados pelos empreendimentos incubados.")

    db = st.session_state.get("respostas_db", [])

    if not db:
        st.info("Nenhum diagnóstico foi realizado ainda. Os resultados aparecerão aqui conforme os empreendimentos concluírem o processo.")
    else:
        st.markdown(f"**Total de diagnósticos:** {len(db)}")

        col_m1, col_m2, col_m3 = st.columns(3)
        cenarios_count = {}
        for entrada in db:
            for cid in entrada["cenarios"]:
                cenarios_count[cid] = cenarios_count.get(cid,0) + 1
        cenario_mais = max(cenarios_count, key=cenarios_count.get) if cenarios_count else "—"
        col_m1.metric("Diagnósticos Realizados", len(db))
        col_m2.metric("Cenário Mais Frequente", cenario_mais)
        col_m3.metric("Alertas de Bioeconomia", sum(1 for e in db if any(c in ["C-09","C-10","C-11"] for c in e["cenarios"])))

        st.markdown("---")

        busca = st.text_input("🔍 Buscar por nome ou empreendimento:", key="busca_gestao")

        for entrada in reversed(db):
            if busca and busca.lower() not in entrada["nome"].lower() and busca.lower() not in entrada["empreendimento"].lower():
                continue

            with st.expander(f"#{entrada['id']} — {entrada['empreendimento']} | {entrada['nome']} | {entrada['data']}"):
                col1, col2 = st.columns([2,3])
                with col1:
                    st.markdown(f"**Respondente:** {entrada['nome']}")
                    st.markdown(f"**Empreendimento:** {entrada['empreendimento']}")
                    st.markdown(f"**Data:** {entrada['data']}")
                with col2:
                    st.markdown("**Cenários Identificados:**")
                    for cid in entrada["cenarios"]:
                        c = CENARIOS[cid]
                        is_inf = cid == "C-15"
                        tag_cls = "tag-vermelho" if is_inf else "tag-verde"
                        st.markdown(f'<span class="{tag_cls}">{cid}</span> {c["nome"]}', unsafe_allow_html=True)

                st.markdown("**Respostas do Diagnóstico:**")
                for q in PERGUNTAS_DIAGNOSTICO:
                    resp = entrada["respostas"].get(q["id"], "—")
                    st.markdown(f"<small><b>{q['id'].upper()}:</b> {q['pergunta'][:70]}... → <i>{resp}</i></small>", unsafe_allow_html=True)

                pdf_buf_g = gerar_pdf(
                    entrada["nome"], entrada["empreendimento"],
                    entrada["data"], entrada["respostas"], entrada["cenarios"]
                )
                st.download_button(
                    label=f"⬇️ PDF — {entrada['empreendimento']}",
                    data=pdf_buf_g,
                    file_name=f"relatorio_PI_{entrada['empreendimento'].replace(' ','_')}_{entrada['id']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_gestao_{entrada['id']}"
                )
