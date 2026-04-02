import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Log Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — dark terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #151820;
    --border:    #252a36;
    --accent:    #4fffb0;
    --accent2:   #7b5ea7;
    --warn:      #ffb347;
    --error:     #ff5757;
    --text:      #e2e8f0;
    --muted:     #6b7385;
    --radius:    10px;
}

/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Header bar */
.header-bar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 24px;
}
.header-bar .logo {
    font-size: 2rem;
}
.header-bar h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: var(--accent);
    margin: 0;
    letter-spacing: -0.5px;
}
.header-bar p {
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    margin: 2px 0 0 0;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
}
.metric-card.warn::before { background: var(--warn); }
.metric-card.error::before { background: var(--error); }
.metric-card.purple::before { background: var(--accent2); }
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    margin-top: 4px;
}

/* Section headings */
.section-head {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 28px 0 12px 0;
    padding-left: 10px;
    border-left: 3px solid var(--accent);
}

/* Log table badge colors */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Sidebar labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: var(--muted) !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* Status pill */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 99px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
}
.status-pill.ok  { background: rgba(79,255,176,0.12); color: var(--accent); border: 1px solid rgba(79,255,176,0.3); }
.status-pill.err { background: rgba(255,87,87,0.12);  color: var(--error);  border: 1px solid rgba(255,87,87,0.3); }

/* Plotly chart containers */
.js-plotly-plot { border-radius: var(--radius); overflow: hidden; }

/* Info/warning boxes */
.info-box {
    background: rgba(79,255,176,0.05);
    border: 1px solid rgba(79,255,176,0.2);
    border-radius: var(--radius);
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--muted);
    margin-bottom: 16px;
}
.info-box span { color: var(--accent); font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#e2e8f0", size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    colorway=["#4fffb0", "#7b5ea7", "#ffb347", "#ff5757", "#4fc3f7", "#f06292"],
    xaxis=dict(gridcolor="#252a36", linecolor="#252a36", zerolinecolor="#252a36"),
    yaxis=dict(gridcolor="#252a36", linecolor="#252a36", zerolinecolor="#252a36"),
)

LABEL_COLORS = {
    "error":          "#ff5757",
    "security":       "#ffb347",
    "authentication": "#4fc3f7",
    "backup":         "#4fffb0",
    "system":         "#7b5ea7",
    "workflow":       "#f06292",
    "user_activity":  "#80cbc4",
    "deprecation":    "#ffe082",
}

def label_color(lbl: str) -> str:
    lbl_lower = lbl.lower() if isinstance(lbl, str) else ""
    for k, v in LABEL_COLORS.items():
        if k in lbl_lower:
            return v
    return "#6b7385"

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <div class="logo">🧠</div>
  <div>
    <h1>Log Classifier</h1>
    <p>regex · bert · llm &nbsp;|&nbsp; intelligent log analysis dashboard</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], help="Needs `source` and `log_message` columns")
    api_url = st.text_input("FastAPI Endpoint", "http://localhost:8000/classify/")

    st.divider()
    st.markdown("### 🔗 API Status")

    api_ok = False
    try:
        resp = requests.get("http://localhost:8000/docs", timeout=1)
        api_ok = resp.status_code == 200
    except Exception:
        api_ok = False

    if api_ok:
        st.markdown('<span class="status-pill ok">● Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill err">● Not Running</span>', unsafe_allow_html=True)
        st.caption("Start with: `uvicorn server:app --reload`")

    st.divider()
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("### 📖 About")
    st.caption("""
**Pipeline:**
1. Regex → fast pattern matching
2. BERT → embedding-based ML
3. LLM  → semantic understanding

LegacyCRM logs bypass to LLM directly.
    """)

# ─────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────
if uploaded_file:
    st.session_state["uploaded_file"] = uploaded_file
    df_raw = pd.read_csv(uploaded_file)

    st.markdown('<p class="section-head">📂 Raw Data Preview</p>', unsafe_allow_html=True)

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
        <div class="info-box">
          <span>{len(df_raw):,}</span> rows &nbsp;·&nbsp;
          <span>{df_raw.shape[1]}</span> columns &nbsp;·&nbsp;
          Sources: <span>{", ".join(df_raw["source"].unique()) if "source" in df_raw.columns else "N/A"}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        classify_clicked = st.button("🚀 Classify Logs", use_container_width=True, type="primary")

    st.dataframe(
        df_raw.head(10),
        use_container_width=True,
        height=220,
    )

    if classify_clicked:
        with st.spinner("Running classification pipeline…"):
            try:
                f = st.session_state["uploaded_file"]
                response = requests.post(
                    api_url,
                    files={"file": (f.name, f.getvalue(), "text/csv")}
                )
                if response.status_code == 200:
                    st.session_state["classified_df"] = pd.read_csv(io.BytesIO(response.content))
                    st.success("✅ Classification complete!")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure `uvicorn server:app --reload` is running.")

# ─────────────────────────────────────────────
# CLASSIFIED RESULTS
# ─────────────────────────────────────────────
if "classified_df" in st.session_state:
    cdf = st.session_state["classified_df"].copy()

    # ── Metrics ─────────────────────────────
    st.markdown('<p class="section-head">📊 Summary Metrics</p>', unsafe_allow_html=True)

    total     = len(cdf)
    n_labels  = cdf["target_label"].nunique() if "target_label" in cdf.columns else 0
    n_sources = cdf["source"].nunique()       if "source"       in cdf.columns else 0
    top_label = cdf["target_label"].mode()[0] if "target_label" in cdf.columns and total > 0 else "—"

    # Count error/security-related for the warning metric
    if "target_label" in cdf.columns:
        alert_count = cdf["target_label"].str.lower().str.contains("error|security|fail|unauthorized", na=False).sum()
    else:
        alert_count = 0

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Total Logs</div>
        <div class="metric-value">{total:,}</div>
        <div class="metric-sub">classified rows</div>
      </div>
      <div class="metric-card purple">
        <div class="metric-label">Unique Labels</div>
        <div class="metric-value">{n_labels}</div>
        <div class="metric-sub">distinct categories</div>
      </div>
      <div class="metric-card warn">
        <div class="metric-label">Alert Logs</div>
        <div class="metric-value">{alert_count:,}</div>
        <div class="metric-sub">error / security / fail</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Top Label</div>
        <div class="metric-value" style="font-size:1.1rem;padding-top:4px">{top_label}</div>
        <div class="metric-sub">most frequent class</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ─────────────────────────────
    st.markdown('<p class="section-head">🎯 Filters</p>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        selected_labels = st.multiselect(
            "Label(s)",
            options=sorted(cdf["target_label"].unique()) if "target_label" in cdf.columns else [],
        )
    with fc2:
        source_opts = sorted(cdf["source"].unique()) if "source" in cdf.columns else []
        selected_sources = st.multiselect("Source(s)", options=source_opts)
    with fc3:
        search_q = st.text_input("🔍 Search log messages", placeholder="keyword…")

    filtered = cdf.copy()
    if selected_labels:
        filtered = filtered[filtered["target_label"].isin(selected_labels)]
    if selected_sources:
        filtered = filtered[filtered["source"].isin(selected_sources)]
    if search_q:
        filtered = filtered[filtered["log_message"].str.contains(search_q, case=False, na=False)]

    # ── Filtered table ───────────────────────
    st.markdown(f'<p class="section-head">📋 Classified Logs &nbsp;<span style="color:#6b7385;font-size:0.7rem">({len(filtered):,} rows)</span></p>', unsafe_allow_html=True)

    # Colour-code target_label column with st.dataframe column config
    st.dataframe(
        filtered,
        use_container_width=True,
        height=360,
        column_config={
            "target_label": st.column_config.TextColumn("Target Label", width="medium"),
            "source":       st.column_config.TextColumn("Source",       width="medium"),
            "log_message":  st.column_config.TextColumn("Log Message",  width="large"),
        },
    )

    # ── Charts row 1 ────────────────────────
    st.markdown('<p class="section-head">📈 Visualisations</p>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "target_label" in filtered.columns:
            lc = filtered["target_label"].value_counts().reset_index()
            lc.columns = ["Label", "Count"]
            colors = [label_color(l) for l in lc["Label"]]
            fig_bar = go.Figure(go.Bar(
                x=lc["Label"], y=lc["Count"],
                marker_color=colors,
                text=lc["Count"], textposition="outside",
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
            ))
            fig_bar.update_layout(title="Label Distribution", **PLOTLY_LAYOUT)
            st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        if "target_label" in filtered.columns:
            pie_fig = go.Figure(go.Pie(
                labels=lc["Label"],
                values=lc["Count"],
                hole=0.55,
                marker_colors=[label_color(l) for l in lc["Label"]],
                textfont_size=11,
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
            ))
            pie_fig.update_layout(title="Label Share", **PLOTLY_LAYOUT,
                                  legend=dict(font=dict(size=10)))
            st.plotly_chart(pie_fig, use_container_width=True)

    # ── Charts row 2 ────────────────────────
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        if "source" in filtered.columns and "target_label" in filtered.columns:
            cross_tab = pd.crosstab(filtered["source"], filtered["target_label"])
            heatmap_fig = go.Figure(go.Heatmap(
                z=cross_tab.values,
                x=cross_tab.columns.tolist(),
                y=cross_tab.index.tolist(),
                colorscale=[[0, "#151820"], [0.5, "#7b5ea7"], [1, "#4fffb0"]],
                text=cross_tab.values,
                texttemplate="%{text}",
                hovertemplate="Source: %{y}<br>Label: %{x}<br>Count: %{z}<extra></extra>",
            ))
            heatmap_fig.update_layout(title="Source × Label Heatmap", **PLOTLY_LAYOUT)
            st.plotly_chart(heatmap_fig, use_container_width=True)

    with chart_col4:
        if "source" in filtered.columns:
            sc = filtered["source"].value_counts().reset_index()
            sc.columns = ["Source", "Count"]
            fig_src = go.Figure(go.Bar(
                x=sc["Count"], y=sc["Source"],
                orientation="h",
                marker_color="#7b5ea7",
                text=sc["Count"], textposition="outside",
                hovertemplate="<b>%{y}</b><br>Logs: %{x}<extra></extra>",
            ))
            fig_src.update_layout(title="Logs per Source", **PLOTLY_LAYOUT,
                                  yaxis=dict(autorange="reversed", gridcolor="#252a36"))
            st.plotly_chart(fig_src, use_container_width=True)

    # ── Timeline (if timestamp column present) ─
    if "timestamp" in filtered.columns:
        st.markdown('<p class="section-head">⏳ Timeline</p>', unsafe_allow_html=True)
        filtered["timestamp"] = pd.to_datetime(filtered["timestamp"], errors="coerce")
        timeline = (
            filtered.dropna(subset=["timestamp"])
            .groupby([pd.Grouper(key="timestamp", freq="D"), "target_label"])
            .size()
            .reset_index(name="count")
        )
        if not timeline.empty:
            fig_line = px.line(
                timeline, x="timestamp", y="count", color="target_label",
                color_discrete_map={l: label_color(l) for l in timeline["target_label"].unique()},
            )
            fig_line.update_layout(title="Daily Log Volume by Label", **PLOTLY_LAYOUT)
            st.plotly_chart(fig_line, use_container_width=True)

    # ── Single log inspector ─────────────────
    st.markdown('<p class="section-head">🔬 Single Log Inspector</p>', unsafe_allow_html=True)
    if not filtered.empty:
        row_idx = st.slider("Select row", 0, max(0, len(filtered) - 1), 0, label_visibility="collapsed")
        row = filtered.iloc[row_idx]
        ic1, ic2 = st.columns([1, 3])
        with ic1:
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;">
              <div class="metric-label">Source</div>
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#4fc3f7;margin-bottom:12px">{row.get('source','—')}</div>
              <div class="metric-label">Label</div>
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:{label_color(str(row.get('target_label','')))};">{row.get('target_label','—')}</div>
            </div>
            """, unsafe_allow_html=True)
        with ic2:
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:var(--text);line-height:1.6;">
              {row.get('log_message','—')}
            </div>
            """, unsafe_allow_html=True)

    # ── Download ─────────────────────────────
    st.markdown('<p class="section-head">📥 Export</p>', unsafe_allow_html=True)
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=filtered.to_csv(index=False),
            file_name=f"classified_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            label="⬇️ Download Full Results CSV",
            data=cdf.to_csv(index=False),
            file_name=f"all_classified_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

elif "uploaded_file" not in st.session_state:
    # Welcome / empty state
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#6b7385;">
      <div style="font-size:3rem;margin-bottom:16px">🧠</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#e2e8f0;margin-bottom:8px">
        Ready to classify
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;max-width:420px;margin:0 auto">
        Upload a CSV with <code style="color:#4fffb0">source</code> and
        <code style="color:#4fffb0">log_message</code> columns using the
        sidebar, then hit <strong>Classify Logs</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)