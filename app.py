import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campanha Moto Zero KM | Só Folhas", layout="wide")

# =========================
# ESTILO (mais profissional)
# =========================
st.markdown("""
<style>
  .stApp { background: #0B0B0B; color: #FFFFFF; }
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}

  .topbar {
    background: linear-gradient(90deg, rgba(11,143,59,0.22), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.10);
    padding: 16px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
  }
  .title { font-size: 30px; font-weight: 800; margin: 0; }
  .subtitle { margin: 6px 0 0 0; opacity: 0.88; }

  .chip {
    display:inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.06);
    font-size: 12px;
    margin-right: 8px;
    margin-top: 8px;
  }

  .panel {
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

  .kpi { font-size: 22px; font-weight: 800; margin: 0; }
  .muted { opacity: 0.85; }

  [data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    overflow: hidden;
  }
</style>
""", unsafe_allow_html=True)

# =========================
# CABEÇALHO
# =========================
c1, c2, c3 = st.columns([1.1, 3.3, 1.6])
with c1:
    st.image("logo.png", width=190)

with c2:
    st.markdown("""
    <div class="topbar">
      <div class="title">🏍️ Campanha Moto Zero KM</div>
      <div class="subtitle">Ranking por equipe e promotor • Atualize com Excel/CSV</div>
      <span class="chip">🥇 Top 3 com medalhas</span>
      <span class="chip">⚠️ Últimos destacados</span>
      <span class="chip">📱 Visual otimizado</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="panel">
      <b>Como usar</b>
      <div class="muted" style="margin-top:6px;">
        1) Envie o arquivo<br/>
        2) Selecione o mês<br/>
        3) Selecione a equipe<br/>
        4) Veja ranking e detalhes
      </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# REGRAS (mais bem explicadas)
# =========================
with st.expander("📌 Regras de pontuação (clique para ver)", expanded=False):
    st.markdown("""
**Pontuação diária (por promotor):**
- **Rotina MOKI 100%:** +1 ponto por dia (`Rotina_MOKI_100 = 1`)
- **Triagem de produtos:** +1 ponto por dia (`Triagem_Produtos = 1`)
- **Ações de vendas:** +5 pontos por ação (`Acoes_Vendas = quantidade`)

**Penalidades diárias:**
- **Falta sem atestado:** -5 pontos (`Falta_Sem_Atestado = 1`)
- **Falta com atestado:** -2 pontos (`Falta_Com_Atestado = 1`)
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

# =========================
# UPLOAD
# =========================
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

# Regra A: promotor fixo em uma equipe por mês
check = df.groupby(["Mes", "Promotor"])["Equipe"].nunique().reset_index(name="QtdEquipes")
problema = check[check["QtdEquipes"] > 1]
if not problema.empty:
    st.error("Existe promotor em MAIS DE UMA equipe no mesmo mês. Corrija antes de gerar o ranking.")
    st.dataframe(problema, use_container_width=True)
    st.stop()

# =========================
# FILTROS (Equipe primeiro)
# =========================
st.markdown("## 🔎 Filtros")

colA, colB, colC = st.columns([1.2, 1.2, 2])

meses = sorted(df["Mes"].unique())
with colA:
    mes_sel = st.selectbox("📅 Mês", meses, index=len(meses)-1)

dfm = df[df["Mes"] == mes_sel].copy()

equipes = sorted(dfm["Equipe"].unique())
with colB:
    equipe_sel = st.selectbox("👥 Selecione sua equipe (obrigatório)", ["— selecione —"] + equipes, index=0)

# trava: só mostra ranking depois de selecionar equipe
if equipe_sel == "— selecione —":
    st.warning("Selecione uma equipe para visualizar a classificação.")
    st.stop()

dfm = dfm[dfm["Equipe"] == equipe_sel].copy()

with colC:
    promotores = sorted(dfm["Promotor"].unique())
    prom_sel = st.selectbox("🧍 Ver detalhes de qual promotor?", ["— todos (apenas ranking) —"] + promotores, index=0)

# =========================
# CÁLCULO
# =========================
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

res = res.sort_values(["Score"], ascending=False).reset_index(drop=True)
res["Posição"] = res.index + 1

# =========================
# 1) RANKING (em cima)
# =========================
st.markdown(f"## 🏆 Ranking — {equipe_sel} ({mes_sel})")

# KPIs rápidos
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"<div class='panel'><div class='muted'>Promotores na equipe</div><div class='kpi'>{len(res)}</div></div>", unsafe_allow_html=True)
with k2:
    lider = res.iloc[0] if len(res) else None
    st.markdown(f"<div class='panel'><div class='muted'>Líder</div><div class='kpi'>{lider['Promotor'] if lider is not None else '-'}</div></div>", unsafe_allow_html=True)
with k3:
    if len(res) >= 2:
        diff = float(res.iloc[0]["Score"]) - float(res.iloc[1]["Score"])
        st.markdown(f"<div class='panel'><div class='muted'>Diferença p/ 2º</div><div class='kpi'>{diff:.0f} pts</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='panel'><div class='muted'>Diferença p/ 2º</div><div class='kpi'>-</div></div>", unsafe_allow_html=True)

# Top 3 (ouro/prata/bronze)
st.markdown("### 🥇 Destaques (Top 3)")
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
                f"<span class='muted'>Score: {row['Score']:.0f} • Ganhos: {row['Pontos_Ganhos']:.0f} • Perdas: {row['Pontos_Perdidos']:.0f}</span></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown("<div class='medal'><b>—</b><br><span class='muted'>Sem dados</span></div>", unsafe_allow_html=True)

# Ranking completo
st.markdown("### 📊 Classificação completa")
st.dataframe(
    res[["Posição", "Promotor", "Score", "Pontos_Ganhos", "Pontos_Perdidos"]],
    use_container_width=True
)

# Últimos (zona de atenção)
st.markdown("### ⚠️ Zona de atenção (últimos colocados)")
bottom = res.tail(3).sort_values("Score")
if len(bottom) == 0:
    st.write("Sem dados.")
else:
    for _, r in bottom.iterrows():
        st.markdown(
            f"<div class='medal danger'><b>{r['Promotor']}</b> "
            f"<span class='muted'>• Score: {r['Score']:.0f} • Ganhos: {r['Pontos_Ganhos']:.0f} • Perdas: {r['Pontos_Perdidos']:.0f}</span></div>",
            unsafe_allow_html=True
        )

# =========================
# 2) DETALHAMENTO (embaixo)
# =========================
st.markdown("## 🔍 Por que a pontuação está assim? (detalhamento)")

if prom_sel == "— todos (apenas ranking) —":
    st.info("Selecione um promotor no filtro acima para ver o detalhamento completo da pontuação.")
else:
    det = res[res["Promotor"] == prom_sel].copy()
    if det.empty:
        st.warning("Não encontrei dados para esse promotor no mês/equipe selecionados.")
    else:
        r = det.iloc[0]

        a, b = st.columns([1.3, 2.7])
        with a:
            st.markdown(
                f"""
                <div class="panel">
                  <div class="muted">Promotor</div>
                  <div class="kpi">{prom_sel}</div>
                  <div class="muted" style="margin-top:10px;">Score final</div>
                  <div class="kpi">{float(r["Score"]):.0f} pts</div>
                  <div class="muted" style="margin-top:6px;">Ganhos: {float(r["Pontos_Ganhos"]):.0f} • Perdas: {float(r["Pontos_Perdidos"]):.0f}</div>
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

        # opcional: mostrar linhas diárias desse promotor (auditoria)
        with st.expander("🧾 Ver lançamentos diários (auditoria)", expanded=False):
            base = dfm[dfm["Promotor"] == prom_sel].sort_values("Data")
            st.dataframe(
                base[["Data","Loja","Rotina_MOKI_100","Triagem_Produtos","Acoes_Vendas",
                      "Falta_Sem_Atestado","Falta_Com_Atestado","Produto_Sem_Qualidade","Nao_Cumpriu_Rotina",
                      "Meta_Quebra_Mes","Sem_Faltas_Atestado_Mes","Menor_Quebra_Regional_Mes","Acima_Meta_Quebra_12"]],
                use_container_width=True
            )
