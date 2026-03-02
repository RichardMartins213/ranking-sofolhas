import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campanha Moto Zero KM | Só Folhas", layout="wide")

# -------------------------
# ESTILO (nível empresa)
# -------------------------
st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1200px;}
  .sf-header {
    display:flex; align-items:center; justify-content:space-between;
    padding: 14px 16px; border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.04);
    margin-bottom: 14px;
  }
  .sf-title {font-size: 22px; font-weight: 800; margin:0;}
  .sf-sub {opacity: .8; margin:4px 0 0 0;}
  .sf-card {
    padding: 14px; border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.04);
  }
  .sf-kpi {font-size: 20px; font-weight: 800; margin:0;}
  .sf-muted {opacity:.8; font-size: 13px;}

  .medal { border-radius: 14px; padding: 12px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.05); }
  .gold   { background: rgba(255, 215, 0, 0.10); border-color: rgba(255, 215, 0, 0.30); }
  .silver { background: rgba(192, 192, 192, 0.10); border-color: rgba(192, 192, 192, 0.30); }
  .bronze { background: rgba(205, 127, 50, 0.12); border-color: rgba(205, 127, 50, 0.30); }
  .danger { background: rgba(255, 82, 82, 0.10); border-color: rgba(255, 82, 82, 0.30); }

  [data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    overflow: hidden;
  }

  .sidebar-box {
    padding: 12px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.04);
    margin-bottom: 10px;
  }
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
left, right = st.columns([3, 1])
with left:
    st.markdown("""
    <div class="sf-header">
      <div>
        <div class="sf-title">🏍️ Campanha Moto Zero KM</div>
        <div class="sf-sub">Painel oficial de classificação • Só Folhas</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with right:
    st.image("logo.png", width=150)

# -------------------------
# REGRAS (bem explicadas)
# -------------------------
with st.expander("📌 Regras de pontuação (clique para ver)", expanded=False):
    st.markdown("""
**Pontuação diária (por promotor):**
- **Rotina MOKI 100%:** +1 ponto por dia (`Rotina_MOKI_100 = 1`)
- **Triagem de produtos:** +1 ponto por dia (`Triagem_Produtos = 1`)
- **Ações de vendas:** +5 pontos por ação (`Acoes_Vendas = quantidade`)

**Penalidades diárias:**
- **Falta sem atestado:** -5 pontos por dia (`Falta_Sem_Atestado = 1`)
- **Falta com atestado:** -2 pontos por dia (`Falta_Com_Atestado = 1`)
- **Produto sem qualidade na loja:** -2 por ocorrência (`Produto_Sem_Qualidade = quantidade`)
- **Não cumprimento da rotina:** -5 por ocorrência (`Nao_Cumpriu_Rotina = quantidade`)

**Ajustes mensais (preencher somente no último dia do mês/fechamento):**
- **Meta de quebra do mês:** +20 (`Meta_Quebra_Mes = 1`)
- **Sem faltas/atestado no mês:** +10 (`Sem_Faltas_Atestado_Mes = 1`)
- **Menor quebra regional do mês:** +10 (`Menor_Quebra_Regional_Mes = 1`)
- **Fechou acima da meta de 12%:** -10 (`Acima_Meta_Quebra_12 = 1`)

**Score final do mês:**  
**Score = Pontos ganhos – Pontos perdidos**
""")

# -------------------------
# UPLOAD (por enquanto continua no mesmo app)
# Depois podemos esconder com login admin, quando você quiser.
# -------------------------
st.markdown("## 📤 Envio do arquivo")
arquivo = st.file_uploader("Envie CSV ou Excel", type=["csv", "xlsx"])

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
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

if not arquivo:
    st.info("Envie um arquivo para gerar o ranking.")
    st.stop()

if arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

faltando = [c for c in COLS if c not in df.columns]
if faltando:
    st.error(f"Faltam colunas no arquivo: {faltando}")
    st.stop()

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
if df["Data"].isna().any():
    st.error("Algumas linhas estão com 'Data' inválida. Corrija no Excel/CSV (ex: 2026-02-24).")
    st.stop()

df["Mes"] = df["Data"].dt.to_period("M").astype(str)

num_cols = [c for c in COLS if c not in ["Data", "Equipe", "Promotor", "Loja"]]
df = to_num(df, num_cols)

# validação: promotor não pode estar em 2 equipes no mesmo mês
check = df.groupby(["Mes", "Promotor"])["Equipe"].nunique().reset_index(name="QtdEquipes")
problema = check[check["QtdEquipes"] > 1]
if not problema.empty:
    st.error("Existe promotor em MAIS DE UMA equipe no mesmo mês. Corrija antes de gerar o ranking.")
    st.dataframe(problema, use_container_width=True)
    st.stop()

# -------------------------
# SIDEBAR: FILTROS (Equipe obrigatório)
# -------------------------
st.sidebar.image("logo.png", width=140)
st.sidebar.markdown("### 🎛️ Filtros")

meses = sorted(df["Mes"].unique())
mes_sel = st.sidebar.selectbox("📅 Mês", meses, index=len(meses)-1)

dfm = df[df["Mes"] == mes_sel].copy()

equipes = sorted(dfm["Equipe"].unique())
equipe_sel = st.sidebar.selectbox("👥 Equipe (obrigatório)", ["— Selecione —"] + equipes, index=0)

st.sidebar.markdown("<div class='sidebar-box'><b>Dica</b><br><span style='opacity:.8'>Selecione a equipe para liberar a classificação.</span></div>", unsafe_allow_html=True)

if equipe_sel == "— Selecione —":
    st.info("👥 Selecione sua equipe na barra lateral para visualizar a classificação.")
    st.stop()

dfm = dfm[dfm["Equipe"] == equipe_sel].copy()

promotores = sorted(dfm["Promotor"].unique())
prom_sel = st.sidebar.selectbox("🧍 Promotor (opcional)", ["— Todos —"] + promotores, index=0)

# -------------------------
# CÁLCULO
# -------------------------
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

res = dfm.groupby(["Equipe", "Promotor"], as_index=False).agg(
    Score=("Score", "sum"),
    Pontos_Ganhos=("Pontos_Ganhos", "sum"),
    Pontos_Perdidos=("Pontos_Perdidos", "sum"),
    Rotina=("Rotina_MOKI_100", "sum"),
    Triagem=("Triagem_Produtos", "sum"),
    Acoes=("Acoes_Vendas", "sum"),
    FaltaSem=("Falta_Sem_Atestado", "sum"),
    FaltaCom=("Falta_Com_Atestado", "sum"),
    ProdSemQual=("Produto_Sem_Qualidade", "sum"),
    NaoCumpriu=("Nao_Cumpriu_Rotina", "sum"),
    MetaQuebra=("Meta_Quebra_Mes", "sum"),
    SemFaltasMes=("Sem_Faltas_Atestado_Mes", "sum"),
    MenorQuebraMes=("Menor_Quebra_Regional_Mes", "sum"),
    Acima12=("Acima_Meta_Quebra_12", "sum"),
)

res = res.sort_values("Score", ascending=False).reset_index(drop=True)
res["Posição"] = res.index + 1

# -------------------------
# ABAS: Classificação / Minha pontuação
# -------------------------
tab1, tab2 = st.tabs(["🏆 Classificação", "👤 Minha pontuação"])

with tab1:
    c1, c2, c3 = st.columns(3)
    lider = res.iloc[0] if len(res) else None
    diff = float(res.iloc[0]["Score"]) - float(res.iloc[1]["Score"]) if len(res) > 1 else 0

    c1.markdown(f"<div class='sf-card'><div class='sf-muted'>Equipe</div><div class='sf-kpi'>{equipe_sel}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='sf-card'><div class='sf-muted'>Líder</div><div class='sf-kpi'>{lider['Promotor'] if lider is not None else '-'}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='sf-card'><div class='sf-muted'>Diferença p/ 2º</div><div class='sf-kpi'>{diff:.0f} pts</div></div>", unsafe_allow_html=True)

    st.markdown("### 🥇 Pódio (Top 3)")
    top3 = res.head(3)
    cols = st.columns(3)
    medals = [("gold", "🥇 1º lugar"), ("silver", "🥈 2º lugar"), ("bronze", "🥉 3º lugar")]
    for i in range(3):
        with cols[i]:
            if i < len(top3):
                row = top3.iloc[i]
                klass, title = medals[i]
                st.markdown(
                    f"<div class='medal {klass}'><b>{title}</b><br>"
                    f"<span style='font-size:18px'>{row['Promotor']}</span><br>"
                    f"<span class='sf-muted'>Score: {row['Score']:.0f} • Ganhos: {row['Pontos_Ganhos']:.0f} • Perdas: {row['Pontos_Perdidos']:.0f}</span></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div class='medal'><b>—</b><br><span class='sf-muted'>Sem dados</span></div>", unsafe_allow_html=True)

    st.markdown("### 📊 Ranking da equipe")
    st.dataframe(
        res[["Posição", "Promotor", "Score", "Pontos_Ganhos", "Pontos_Perdidos"]],
        use_container_width=True
    )

    st.markdown("### ⚠️ Zona de atenção (últimos colocados)")
    bottom = res.tail(3).sort_values("Score")
    if len(bottom) == 0:
        st.write("Sem dados.")
    else:
        for _, r in bottom.iterrows():
            st.markdown(
                f"<div class='medal danger'><b>{r['Promotor']}</b> "
                f"<span class='sf-muted'>• Score: {r['Score']:.0f} • Ganhos: {r['Pontos_Ganhos']:.0f} • Perdas: {r['Pontos_Perdidos']:.0f}</span></div>",
                unsafe_allow_html=True
            )

with tab2:
    if prom_sel == "— Todos —":
        st.info("Selecione um promotor na barra lateral para ver o detalhamento da pontuação.")
    else:
        det = res[res["Promotor"] == prom_sel].copy()
        if det.empty:
            st.warning("Não encontrei dados para esse promotor no mês/equipe selecionados.")
        else:
            r = det.iloc[0]

            a, b = st.columns([1.2, 2.8])
            with a:
                st.markdown(
                    f"""
                    <div class="sf-card">
                      <div class="sf-muted">Promotor</div>
                      <div class="sf-kpi">{prom_sel}</div>
                      <div class="sf-muted" style="margin-top:10px;">Score final</div>
                      <div class="sf-kpi">{float(r["Score"]):.0f} pts</div>
                      <div class="sf-muted" style="margin-top:6px;">Ganhos: {float(r["Pontos_Ganhos"]):.0f} • Perdas: {float(r["Pontos_Perdidos"]):.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with b:
                st.markdown("### ✅ Ganhos (o que somou pontos)")
                ganhos = pd.DataFrame([
                    ["Rotina MOKI (dias)", r["Rotina"], "+1 por dia"],
                    ["Triagem (dias)", r["Triagem"], "+1 por dia"],
                    ["Ações de vendas", r["Acoes"], "+5 por ação"],
                    ["Meta de quebra do mês", r["MetaQuebra"], "+20 (fechamento)"],
                    ["Sem faltas/atestado no mês", r["SemFaltasMes"], "+10 (fechamento)"],
                    ["Menor quebra regional do mês", r["MenorQuebraMes"], "+10 (fechamento)"],
                ], columns=["Item", "Quantidade/Status", "Regra"])
                st.dataframe(ganhos, use_container_width=True)

                st.markdown("### ❌ Perdas (o que tirou pontos)")
                perdas = pd.DataFrame([
                    ["Falta sem atestado (dias)", r["FaltaSem"], "-5 por dia"],
                    ["Falta com atestado (dias)", r["FaltaCom"], "-2 por dia"],
                    ["Produto sem qualidade", r["ProdSemQual"], "-2 por ocorrência"],
                    ["Não cumpriu rotina", r["NaoCumpriu"], "-5 por ocorrência"],
                    ["Acima da meta de 12% (mês)", r["Acima12"], "-10 (fechamento)"],
                ], columns=["Item", "Quantidade/Status", "Regra"])
                st.dataframe(perdas, use_container_width=True)

            with st.expander("🧾 Ver lançamentos diários (auditoria)", expanded=False):
                base = dfm[dfm["Promotor"] == prom_sel].sort_values("Data")
                st.dataframe(
                    base[["Data","Loja","Rotina_MOKI_100","Triagem_Produtos","Acoes_Vendas",
                          "Falta_Sem_Atestado","Falta_Com_Atestado","Produto_Sem_Qualidade","Nao_Cumpriu_Rotina",
                          "Meta_Quebra_Mes","Sem_Faltas_Atestado_Mes","Menor_Quebra_Regional_Mes","Acima_Meta_Quebra_12"]],
                    use_container_width=True
                )
