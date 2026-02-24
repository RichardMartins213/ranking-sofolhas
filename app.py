import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campanha Moto Zero KM", layout="wide")

# ===== CSS (visual campanha) =====
st.markdown("""
<style>
  .stApp { background: #0B0B0B; color: #FFFFFF; }
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}

  .hero {
    background: linear-gradient(90deg, rgba(11,143,59,0.25), rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.10);
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 14px;
  }
  .hero h1 { margin: 0; font-size: 34px; }
  .hero p { margin: 6px 0 0 0; opacity: 0.92; }

  .card {
    background: #141414;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 14px;
  }
  .medal { border-radius: 14px; padding: 12px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.05); }
  .gold   { background: rgba(255, 215, 0, 0.10); border-color: rgba(255, 215, 0, 0.30); }
  .silver { background: rgba(192, 192, 192, 0.10); border-color: rgba(192, 192, 192, 0.30); }
  .bronze { background: rgba(205, 127, 50, 0.12); border-color: rgba(205, 127, 50, 0.30); }
  .danger { background: rgba(255, 82, 82, 0.10); border-color: rgba(255, 82, 82, 0.30); }
  .muted { opacity: 0.88; }
</style>
""", unsafe_allow_html=True)

# ===== Header =====
c1, c2, c3 = st.columns([1.1, 3, 1.3])
with c1:
    st.image("logo.png", width=170)
with c2:
    st.markdown("""
    <div class="hero">
      <h1>🏍️ Campanha Moto Zero KM</h1>
      <p class="muted">Ranking automático por equipe e por promotor • Envie o Excel/CSV e pronto</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="card">
      <b>Regras</b>
      <div class="muted" style="margin-top:6px;">
      Rotina +1/dia<br>
      Triagem +1/dia<br>
      Ações +5 cada<br>
      Falta s/atestado -5<br>
      Falta c/atestado -2<br>
      Prod. s/qualid. -2<br>
      Não cumpriu rotina -5<br>
      Fechamento: +20/+10/+10 e -10
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## 📤 Upload do arquivo")
arquivo = st.file_uploader("Envie CSV ou Excel", type=["csv", "xlsx"])

# ===== Colunas esperadas =====
COLS = [
    "Data", "Equipe", "Promotor", "Loja",
    "Rotina_MOKI_100", "Triagem_Produtos", "Acoes_Vendas",
    "Falta_Sem_Atestado", "Falta_Com_Atestado",
    "Produto_Sem_Qualidade", "Nao_Cumpriu_Rotina",
    "Meta_Quebra_Mes", "Sem_Faltas_Atestado_Mes", "Menor_Quebra_Regional_Mes",
    "Acima_Meta_Quebra_12"
]

def to_num(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

if not arquivo:
    st.info("Envie um arquivo para gerar o ranking.")
    st.stop()

# ===== Ler arquivo =====
if arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

# ===== Validar colunas =====
faltando = [c for c in COLS if c not in df.columns]
if faltando:
    st.error(f"Faltam colunas no arquivo: {faltando}")
    st.stop()

# ===== Tipos =====
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
if df["Data"].isna().any():
    st.error("Algumas linhas estão com 'Data' inválida. Corrija no Excel/CSV.")
    st.stop()

df["Mes"] = df["Data"].dt.to_period("M").astype(str)

num_cols = [c for c in COLS if c not in ["Data","Equipe","Promotor","Loja"]]
df = to_num(df, num_cols)

# ===== Checagem: promotor fixo em 1 equipe por mês =====
check = df.groupby(["Mes","Promotor"])["Equipe"].nunique().reset_index(name="QtdEquipes")
problema = check[check["QtdEquipes"] > 1]
if not problema.empty:
    st.error("Existe promotor em MAIS DE UMA equipe no mesmo mês. Corrija antes de gerar o ranking.")
    st.dataframe(problema, use_container_width=True)
    st.stop()

# ===== Filtros =====
meses = sorted(df["Mes"].unique())
mes_sel = st.selectbox("📅 Mês", meses, index=len(meses)-1)

dfm = df[df["Mes"] == mes_sel].copy()

equipes = ["Todas"] + sorted(dfm["Equipe"].unique())
equipe_sel = st.selectbox("👥 Equipe", equipes, index=0)

if equipe_sel != "Todas":
    dfm = dfm[dfm["Equipe"] == equipe_sel]

promotores = ["Todos"] + sorted(dfm["Promotor"].unique())
prom_sel = st.selectbox("🧍 Promotor", promotores, index=0)

if prom_sel != "Todos":
    dfm = dfm[dfm["Promotor"] == prom_sel]

# ===== Cálculo =====
dfm["Pontos_Ganhos"] = (
    dfm["Rotina_MOKI_100"] * 1 +
    dfm["Triagem_Produtos"] * 1 +
    dfm["Acoes_Vendas"] * 5 +
    dfm["Meta_Quebra_Mes"] * 20 +
    dfm["Sem_Faltas_Atestado_Mes"] * 10 +
    dfm["Menor_Quebra_Regional_Mes"] * 10
)

dfm["Pontos_Perdidos"] = (
    dfm["Falta_Sem_Atestado"] * 5 +
    dfm["Falta_Com_Atestado"] * 2 +
    dfm["Produto_Sem_Qualidade"] * 2 +
    dfm["Nao_Cumpriu_Rotina"] * 5 +
    dfm["Acima_Meta_Quebra_12"] * 10
)

dfm["Score"] = dfm["Pontos_Ganhos"] - dfm["Pontos_Perdidos"]

res = dfm.groupby(["Equipe","Promotor"], as_index=False).agg(
    Score=("Score","sum"),
    Pontos_Ganhos=("Pontos_Ganhos","sum"),
    Pontos_Perdidos=("Pontos_Perdidos","sum"),
    Rotina=("Rotina_MOKI_100","sum"),
    Triagem=("Triagem_Produtos","sum"),
    Acoes=("Acoes_Vendas","sum"),
    FaltasSem=("Falta_Sem_Atestado","sum"),
    FaltasCom=("Falta_Com_Atestado","sum"),
    ProdSemQual=("Produto_Sem_Qualidade","sum"),
    NaoCumpriu=("Nao_Cumpriu_Rotina","sum"),
)

res = res.sort_values(["Equipe","Score"], ascending=[True, False]).reset_index(drop=True)
res["Posição"] = res.groupby("Equipe").cumcount() + 1

st.markdown("## 🏆 Ranking")
st.dataframe(res[["Equipe","Posição","Promotor","Score","Pontos_Ganhos","Pontos_Perdidos"]], use_container_width=True)

# ===== Top 3 + últimos =====
st.markdown("## 🥇 Destaques")

# Se o filtro estiver em uma equipe específica, mostramos top/últimos dessa equipe.
# Se estiver "Todas", mostramos por equipe (uma seção por equipe).
equipes_mostrar = sorted(res["Equipe"].unique())

for eq in equipes_mostrar:
    sub = res[res["Equipe"] == eq].copy()
    st.markdown(f"### 👥 {eq}")

    top3 = sub.head(3)
    cols = st.columns(3)
    medals = [("gold","🥇 1º lugar"), ("silver","🥈 2º lugar"), ("bronze","🥉 3º lugar")]
    for i in range(3):
        with cols[i]:
            if i < len(top3):
                row = top3.iloc[i]
                klass, title = medals[i]
                st.markdown(
                    f"<div class='medal {klass}'><b>{title}</b><br>"
                    f"<span style='font-size:18px'>{row['Promotor']}</span><br>"
                    f"<span class='muted'>Score: {row['Score']:.0f}</span></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div class='medal'><b>—</b><br><span class='muted'>Sem dados</span></div>", unsafe_allow_html=True)

    # últimos 3 (se tiver)
    st.markdown("**⚠️ Atenção (últimos colocados)**")
    bottom = sub.tail(3).sort_values("Score")
    if len(bottom) == 0:
        st.write("Sem dados.")
    else:
        for _, r in bottom.iterrows():
            st.markdown(
                f"<div class='medal danger'><b>{r['Promotor']}</b> "
                f"<span class='muted'>• Score: {r['Score']:.0f}</span></div>",
                unsafe_allow_html=True
            )

st.markdown("## 🔎 Detalhamento (para auditoria)")
st.dataframe(
    res[["Equipe","Posição","Promotor","Score","Rotina","Triagem","Acoes","FaltasSem","FaltasCom","ProdSemQual","NaoCumpriu"]],
    use_container_width=True
)