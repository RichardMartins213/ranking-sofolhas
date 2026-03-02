import streamlit as st

# ======= ESTILO GLOBAL (escuro + verde) =======
st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding-top: 0.8rem; max-width: 1300px;}

  /* fundo com glow verde */
  .sf-bg {
    position: fixed;
    inset: 0;
    background:
      radial-gradient(60% 50% at 50% 18%, rgba(0,180,90,0.22), rgba(0,0,0,0.92) 70%),
      radial-gradient(40% 30% at 20% 10%, rgba(0,180,90,0.12), transparent 70%),
      radial-gradient(40% 30% at 80% 10%, rgba(0,180,90,0.10), transparent 70%);
    z-index: -10;
  }

  /* topbar */
  .sf-topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding: 10px 12px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(8px);
    margin-bottom: 16px;
  }
  .sf-brand {
    display:flex;
    gap: 12px;
    align-items:center;
  }
  .sf-brand .sf-small {opacity:.75; font-size: 12px; margin:0;}
  .sf-brand .sf-name {font-size: 16px; font-weight: 800; margin:0;}
  .sf-pill {
    border-radius: 999px;
    padding: 8px 12px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.92);
    font-weight: 700;
    font-size: 13px;
  }

  /* HERO */
  .sf-hero {
    padding: 26px 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    background:
      radial-gradient(80% 120% at 50% 0%, rgba(22,163,74,0.18), rgba(0,0,0,0) 60%),
      rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    text-align:center;
    margin-bottom: 10px;
  }
  .sf-chip {
    display:inline-flex;
    align-items:center;
    gap: 8px;
    padding: 7px 12px;
    border-radius: 999px;
    border: 1px solid rgba(22,163,74,0.35);
    background: rgba(22,163,74,0.12);
    color: #16a34a;
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 12px;
  }
  .sf-title {
    margin:0;
    font-size: 54px;
    font-weight: 900;
    letter-spacing: -1px;
    line-height: 1.05;
    color: rgba(255,255,255,0.96);
    text-shadow: 0 8px 28px rgba(0,0,0,0.45);
  }
  .sf-title span { color: #16a34a; }
  .sf-sub {
    margin: 10px 0 0 0;
    opacity: .82;
    font-size: 15px;
  }
  .sf-month {
    margin-top: 12px;
    color: #16a34a;
    font-weight: 900;
  }

  /* Tabs mais "empresa" */
  div[data-baseweb="tab-list"] button {
    font-size: 15px !important;
    font-weight: 800 !important;
    color: rgba(255,255,255,0.82) !important;
  }
  div[data-baseweb="tab-list"] button[aria-selected="true"]{
    color: #16a34a !important;
  }

  /* caixas de filtros (faixa como no print) */
  .sf-filters {
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.04);
    border-radius: 18px;
    padding: 16px;
    margin-top: 10px;
    margin-bottom: 18px;
  }

</style>
<div class="sf-bg"></div>
""", unsafe_allow_html=True)

# ======= TOPO (logo + botão admin) =======
left, right = st.columns([6,2], vertical_alignment="center")
with left:
    c1, c2 = st.columns([1,10], vertical_alignment="center")
    with c1:
        st.image("logo.png", width=52)
    with c2:
        st.markdown("""
        <div>
          <p class="sf-small">SÓ FOLHAS</p>
          <p class="sf-name">Campanha Moto Zero KM</p>
        </div>
        """, unsafe_allow_html=True)

with right:
    # aqui você coloca seu botão/área de admin
    st.markdown("<div style='display:flex;justify-content:flex-end;'>", unsafe_allow_html=True)
    st.button("🔐 Administrador", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======= HERO CENTRAL (igual ao print) =======
mes_destaque = "Fevereiro de 2024"  # depois você substitui pelo mês selecionado

st.markdown(f"""
<div class="sf-hero">
  <div class="sf-chip">🏆 Oficial de classificação</div>
  <h1 class="sf-title">Campanha <span>Moto Zero KM</span></h1>
  <p class="sf-sub">Acompanhe o desempenho dos promotores em tempo real</p>
  <div class="sf-month">{mes_destaque}</div>
</div>
""", unsafe_allow_html=True)

# ======= ABAS (iguais do print) =======
tab1, tab2 = st.tabs(["Classificação", "Minha Pontuação"])

with tab1:
    # faixa de filtros como no print
    st.markdown('<div class="sf-filters">', unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)
    with colA:
        st.selectbox("MÊS", ["Todos os meses", "2026-01", "2026-02"])
    with colB:
        st.selectbox("EQUIPE", ["Selecione a equipe", "Equipe A", "Equipe B", "Equipe C"])
    with colC:
        st.selectbox("PROMOTOR", ["Todos os promotores", "João Silva", "Maria Santos"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🏆 Pódio")
    # aqui entra seus cards do pódio e a tabela do ranking

with tab2:
    st.info("Selecione um promotor para ver o detalhamento da pontuação.")
