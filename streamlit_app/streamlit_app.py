from datetime import date, datetime
import pandas as pd
from zoneinfo import ZoneInfo
import streamlit as st

COLUNAS = [
    "timestamp", "nome", "data_nascimento", "idade", "telefone",
    "convenio", "prioridade", "motivo",
]
FUSO = ZoneInfo("America/Sao_Paulo")  # servidores rodam em UTC
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]


def calcular_idade(nascimento: date) -> int:
    hoje = datetime.now(FUSO).date()
    # subtrai 1 se ainda não fez aniversário este ano
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))


st.set_page_config(page_title="Cadastro de Pacientes", page_icon="🏥", layout="centered")
st.title("🏥 Cadastro de Pacientes")
st.caption("Recepção — preencha os dados do paciente que chegou.")

if "pacientes" not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)

with st.form("cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do paciente", placeholder="Ex.: Maria da Silva")
    data_nascimento = st.date_input(
        "Data de nascimento",
        value=None,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY",
    )
    telefone = st.text_input("Telefone (opcional)", placeholder="(11) 99999-9999")
    convenio = st.selectbox("Convênio", CONVENIOS)
    prioridade = st.slider("Prioridade do atendimento (5 = urgente)", 1, 5, 3)
    motivo = st.text_area("Motivo da consulta / observações")
    enviado = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)

if enviado:
    if not nome.strip():
        st.warning("⚠️ Informe o nome do paciente.")
    elif data_nascimento is None:
        st.warning("⚠️ Informe a data de nascimento do paciente.")
    else:
        nova_linha = {
            "timestamp": datetime.now(FUSO).strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome.strip(),
            "data_nascimento": data_nascimento.strftime("%d/%m/%Y"),
            "idade": calcular_idade(data_nascimento),
            "telefone": telefone.strip(),
            "convenio": convenio,
            "prioridade": int(prioridade),
            "motivo": motivo.strip(),
        }
        st.session_state.pacientes = pd.concat(
            [st.session_state.pacientes, pd.DataFrame([nova_linha], columns=COLUNAS)],
            ignore_index=True,
        )
        st.success(f"✅ Paciente {nova_linha['nome']} cadastrado!")

st.subheader("Últimos pacientes cadastrados")
st.dataframe(st.session_state.pacientes.tail(5), use_container_width=True, hide_index=True)
st.caption(f"Total nesta sessão: {len(st.session_state.pacientes)} paciente(s)")

csv = st.session_state.pacientes.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    data=csv,
    file_name="pacientes.csv",
    mime="text/csv",
    use_container_width=True,
    disabled=st.session_state.pacientes.empty,
)
