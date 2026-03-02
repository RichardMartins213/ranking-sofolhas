import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campanha Moto Zero KM", layout="wide")

# =========================
# LOGIN STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# TOPO
# =========================
col1, col2 = st.columns([4,1])

with col1:
    st.image("logo.png", width=180)
    st.title("🏍️ Campanha Moto Zero KM")

with col2:
    if st.session_state.logged_in:
        if st.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        if st.button("🔐 Área Administrativa"):
            st.session_state.show_login = True

# =========================
# LOGIN
# =========================
if st.session_state.get("show_login") and not st.session_state.logged_in:
    st.markdown("## 🔐 Login Administrador")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if (
            user == st.secrets["ADMIN_USER"]
            and password == st.secrets["ADMIN_PASSWORD"]
        ):
            st.session_state.logged_in = True
            st.session_state.show_login = False
            st.success("Login realizado com sucesso.")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# =========================
# UPLOAD (SÓ ADMIN)
# =========================
if st.session_state.logged_in:
    st.markdown("## 📤 Atualizar Ranking")
    arquivo = st.file_uploader("Envie CSV ou Excel", type=["csv", "xlsx"])

    if arquivo:
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)

        df.to_csv("dados.csv", index=False)
        st.success("Dados atualizados com sucesso!")

# =========================
# CARREGAR DADOS
# =========================
try:
    df = pd.read_csv("dados.csv")
except:
    st.warning("Nenhum dado carregado ainda.")
    st.stop()

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Mes"] = df["Data"].dt.to_period("M").astype(str)

# =========================
# FILTROS
# =========================
mes_sel = st.selectbox("📅 Mês", sorted(df["Mes"].unique()))
dfm = df[df["Mes"] == mes_sel]

equipes = sorted(dfm["Equipe"].unique())
equipe_sel = st.selectbox("👥 Selecione sua equipe", ["Selecione"] + equipes)

if equipe_sel == "Selecione":
    st.stop()

dfm = dfm[dfm["Equipe"] == equipe_sel]

# =========================
# CÁLCULO
# =========================
dfm["Ganhos"] = (
    dfm["Rotina_MOKI_100"] +
    dfm["Triagem_Produtos"] +
    dfm["Acoes_Vendas"]*5 +
    dfm["Meta_Quebra_Mes"]*20 +
    dfm["Sem_Faltas_Atestado_Mes"]*10 +
    dfm["Menor_Quebra_Regional_Mes"]*10
)

dfm["Perdas"] = (
    dfm["Falta_Sem_Atestado"]*5 +
    dfm["Falta_Com_Atestado"]*2 +
    dfm["Produto_Sem_Qualidade"]*2 +
    dfm["Nao_Cumpriu_Rotina"]*5 +
    dfm["Acima_Meta_Quebra_12"]*10
)

dfm["Score"] = dfm["Ganhos"] - dfm["Perdas"]

res = dfm.groupby("Promotor", as_index=False)["Score"].sum()
res = res.sort_values("Score", ascending=False).reset_index(drop=True)
res["Posição"] = res.index + 1

# =========================
# RANKING
# =========================
st.markdown("## 🏆 Ranking da Equipe")

st.dataframe(res, use_container_width=True)
