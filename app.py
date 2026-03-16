"""
UN WFP CHAD — Dashboard Distribution Encours — Dash + Plotly
"""

import json, os, base64 as _b64, math
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc

# ── BRAND — WFP Official Colors (extracted from logo) ────────────────────────
T_NAVY    = "#004F87"   # WFP dark navy blue
T_BLUE    = "#0069B5"   # WFP primary blue (exact from logo)
T_BLUE2   = "#0079C7"   # WFP medium blue
T_LIGHT   = "#DBEBF5"   # WFP light blue (exact from logo)
T_TEAL    = "#0095A8"   # UN teal accent
T_GREEN   = "#1A7A4A"   # Success green
T_GREEN_L = "#D4EDE1"   # Green light
T_ORANGE  = "#E07B2A"   # Warning orange
T_ORANGE_L= "#FDF0E0"   # Orange light
T_RED     = "#C0392B"   # Alert red
WHITE     = "#FFFFFF"
GRAY_BG   = "#F2F6FA"   # Page background
GRAY_LINE = "#D5E3EF"   # Borders
GRAY_TEXT = "#4A6080"   # Secondary text
FONT      = "'Open Sans','Source Sans Pro','Segoe UI',Arial,sans-serif"

# ── CIBLES ───────────────────────────────────────────────────────────────────
TARGET_V = 16_940
TARGET_M = 410_872_000
BASE_V   = 12_028
BASE_M   = 342_432_000
BASE_B   = 42_804

DATA_FILE = "data.json"

def load():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else []

def save(e):
    json.dump(e, open(DATA_FILE,"w"), indent=2, ensure_ascii=False)

def fmt(n): return f"{int(n):,}".replace(",", "\u202f")
def pct(a, b): return min(100.0, a / b * 100) if b else 0

def compute(entries):
    av = sum(e["v"] for e in entries)
    am = sum(e["m"] for e in entries)
    ab = sum(e.get("b",0) for e in entries)
    tv = BASE_V + av; tm = BASE_M + am; tb = BASE_B + ab
    return dict(
        tot_v=tv, tot_m=tm, tot_b=tb,
        rst_v=max(0,TARGET_V-tv), rst_m=max(0,TARGET_M-tm),
        pct_v=pct(tv,TARGET_V),   pct_m=pct(tm,TARGET_M),
    )

def compute_trend(entries, t):
    """Calcule jours restants pour atteindre l'objectif selon le rythme actuel."""
    if not entries:
        return dict(avg_daily=0, days_remaining=None, est_date=None)
    # Grouper par date unique
    by_date = {}
    for e in entries:
        by_date[e["date"]] = by_date.get(e["date"], 0) + e["v"]
    n_days = len(by_date)
    total_added = sum(by_date.values())
    avg_daily = total_added / n_days if n_days else 0
    if avg_daily <= 0:
        return dict(avg_daily=0, days_remaining=None, est_date=None)
    remaining = max(0, TARGET_V - t["tot_v"])
    days_remaining = math.ceil(remaining / avg_daily)
    est_date = datetime.today() + timedelta(days=days_remaining)
    return dict(avg_daily=round(avg_daily, 1), days_remaining=days_remaining, est_date=est_date)

# ── LOGO WFP (PNG officiel) ──────────────────────────────────────────────────
LOGO_B64 = "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"

LOGO_IMG = html.Img(
    src=f"data:image/png;base64,{LOGO_B64}",
    style={"height":"68px","width":"auto","flexShrink":"0","objectFit":"contain"},
)

# ── CHART ────────────────────────────────────────────────────────────────────
def build_chart(entries):
    se    = sorted(entries, key=lambda e: e["date"])
    dates = [e["date"] for e in se]
    dv    = [e["v"]         for e in se]
    db    = [e.get("b",0)   for e in se]

    cumul, cd = BASE_V, []
    for v in dv:
        cumul += v; cd.append(cumul)

    # Calcul rythme réel
    t_temp = compute(entries)
    tr = compute_trend(entries, t_temp)
    avg = tr["avg_daily"] if tr["avg_daily"] > 0 else (TARGET_V - BASE_V) / 10

    # Projection de la tendance à partir du dernier cumul
    nproj = max(6, math.ceil((TARGET_V - cumul) / avg) + 2) if avg > 0 else 8
    all_lbl = list(dates)
    last = datetime.strptime(dates[-1], "%Y-%m-%d") if dates else datetime.today()
    for i in range(1, nproj + 1):
        all_lbl.append((last + timedelta(days=i)).strftime("%Y-%m-%d"))

    fl   = lambda d: d[8:] + "/" + d[5:7]
    xlbl = [fl(d) for d in all_lbl]
    xsh  = [fl(d) for d in dates]

    # Tendance : du dernier cumul vers l'objectif au rythme moyen
    trend_start = cumul if cumul else BASE_V
    trend = [trend_start + i * avg for i in range(len(all_lbl))]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=xsh, y=db,
        name="Bénéficiaires / Jour",
        marker_color="#5EB3E4", marker_line_width=0, opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Bénéficiaires : <b>%{y:,.0f}</b><extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=xsh, y=dv,
        name="Ménages / Jour",
        marker_color=T_BLUE, marker_line_width=0, opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Ménages : <b>%{y:,.0f}</b><extra></extra>",
    ), secondary_y=False)

    if cd:
        fig.add_trace(go.Scatter(
            x=xsh, y=cd,
            name="Cumul Ménages",
            mode="lines+markers",
            line=dict(color=T_NAVY, width=3),
            marker=dict(size=7, color=T_NAVY, line=dict(width=2, color=WHITE)),
            hovertemplate="<b>%{x}</b><br>Cumul : <b>%{y:,.0f}</b><extra></extra>",
        ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=xlbl, y=trend,
        name="Tendance (rythme actuel)",
        mode="lines",
        line=dict(color=T_ORANGE, width=2, dash="dot"),
        hovertemplate="Tendance : %{y:,.0f}<extra></extra>",
    ), secondary_y=True)

    fig.add_hline(
        y=TARGET_V, secondary_y=True,
        line_dash="dash", line_color=T_GREEN, line_width=1.8,
        annotation_text=f"  Objectif : {fmt(TARGET_V)} ménages",
        annotation_position="top left",
        annotation_font=dict(color=T_GREEN, size=12, family=FONT),
    )

    fig.update_layout(
        font_family=FONT, font_size=13,
        plot_bgcolor="#FAFCFE", paper_bgcolor=WHITE,
        margin=dict(l=0, r=0, t=14, b=0),
        barmode="group", bargap=0.22, bargroupgap=0.05,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=12, color=GRAY_TEXT),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=T_NAVY, font_size=13, font_family=FONT, font_color=WHITE, bordercolor=T_BLUE2),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color=GRAY_TEXT), linecolor=GRAY_LINE, tickangle=-30),
        yaxis=dict(
            title=dict(text="Bénéficiaires / Ménages · Jour", font=dict(color=GRAY_TEXT, size=12)),
            showgrid=True, gridcolor="#E8EFF5", gridwidth=1,
            tickfont=dict(size=12, color=GRAY_TEXT), zeroline=False,
        ),
        yaxis2=dict(
            title=dict(text="Cumul Ménages", font=dict(color=T_NAVY, size=12)),
            tickfont=dict(size=12, color=T_NAVY),
            range=[0, TARGET_V * 1.08], showgrid=False, zeroline=False,
        ),
    )
    return fig

EMPTY_FIG = go.Figure(layout=dict(
    plot_bgcolor=WHITE, paper_bgcolor=WHITE,
    margin=dict(l=0,r=0,t=0,b=0),
    xaxis=dict(visible=False), yaxis=dict(visible=False),
    annotations=[dict(
        text="Ajoutez une première saisie pour afficher le graphique",
        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        font=dict(size=15, color=GRAY_TEXT, family=FONT),
    )],
))

def build_pie_chart(t):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Ménages (Vouchers)", "Montant XAF"],
    )
    # Donut Ménages
    fig.add_trace(go.Pie(
        labels=["Distribués", "Restant"],
        values=[t["tot_v"], t["rst_v"]],
        hole=0.62,
        marker_colors=[T_BLUE, "#DCE8F5"],
        textinfo="percent",
        textfont=dict(size=13, family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} ménages<br>%{percent}<extra></extra>",
        showlegend=False,
    ), row=1, col=1)
    # Donut Montant
    fig.add_trace(go.Pie(
        labels=["Servi", "Restant"],
        values=[t["tot_m"], t["rst_m"]],
        hole=0.62,
        marker_colors=[T_TEAL, "#DCF0EC"],
        textinfo="percent",
        textfont=dict(size=13, family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} XAF<br>%{percent}<extra></extra>",
        showlegend=False,
    ), row=1, col=2)
    # Annotations au centre des donuts
    fig.add_annotation(
        text=f"<b>{t['pct_v']:.1f}%</b>",
        x=0.21, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=20, color=T_BLUE, family=FONT),
    )
    fig.add_annotation(
        text=f"<b>{t['pct_m']:.1f}%</b>",
        x=0.79, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=20, color=T_TEAL, family=FONT),
    )
    fig.update_layout(
        font_family=FONT,
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        margin=dict(l=10, r=10, t=32, b=10),
        showlegend=False,
        annotations=[
            dict(text=f"<b>{t['pct_v']:.1f}%</b>", x=0.21, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(size=22, color=T_BLUE, family=FONT)),
            dict(text=f"<b>{t['pct_m']:.1f}%</b>", x=0.79, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(size=22, color=T_TEAL, family=FONT)),
            dict(text="Ménages", x=0.21, y=0.35, xref="paper", yref="paper", showarrow=False, font=dict(size=10, color=GRAY_TEXT, family=FONT)),
            dict(text="Montant", x=0.79, y=0.35, xref="paper", yref="paper", showarrow=False, font=dict(size=10, color=GRAY_TEXT, family=FONT)),
        ],
    )
    fig.update_traces(marker=dict(line=dict(color=WHITE, width=2)))
    return fig

# ── COMPOSANTS ───────────────────────────────────────────────────────────────
def stat_block(label, value, sub="", color=T_NAVY):
    return html.Div([
        html.Div(label,  className="stat-lbl"),
        html.Div(value,  className="stat-val", style={"color": color}),
        html.Div(sub,    className="stat-sub") if sub else None,
    ], className="stat-block")

def make_trend_card(tr, t):
    if tr["days_remaining"] is None:
        return html.Div([
            html.Div("📊", style={"fontSize":"2rem","marginBottom":"8px"}),
            html.Div("Ajoutez des saisies pour calculer la projection.",
                     style={"fontSize":".82rem","color":GRAY_TEXT,"textAlign":"center"}),
        ], className="trend-empty")

    color = T_GREEN if tr["days_remaining"] <= 14 else (T_BLUE if tr["days_remaining"] <= 30 else T_ORANGE)
    bg    = T_GREEN_L if tr["days_remaining"] <= 14 else (T_LIGHT if tr["days_remaining"] <= 30 else T_ORANGE_L)

    return html.Div([

        # Ligne 1 — 2 mini stats
        html.Div([
            html.Div([
                html.Div("Rythme moyen", className="tc-lbl"),
                html.Div([
                    html.Span(fmt(tr["avg_daily"]), className="tc-val",
                              style={"color": T_BLUE}),
                    html.Span(" / jour", className="tc-unit"),
                ]),
            ], className="tc-stat"),
            html.Div(className="tc-sep"),
            html.Div([
                html.Div("Restant", className="tc-lbl"),
                html.Div([
                    html.Span(fmt(t["rst_v"]), className="tc-val",
                              style={"color": T_ORANGE}),
                    html.Span(" ménages", className="tc-unit"),
                ]),
            ], className="tc-stat"),
        ], className="tc-row"),

        # Ligne 2 — résultat principal
        html.Div([
            html.Div([
                html.Div(str(tr["days_remaining"]), className="tc-days",
                         style={"color": color}),
                html.Div(f"jour{'s' if tr['days_remaining']>1 else ''}",
                         className="tc-days-lbl", style={"color": color}),
            ], className="tc-days-block",
               style={"background": bg, "borderColor": color}),
            html.Div([
                html.Div("Objectif estimé atteint dans",
                         style={"fontSize":".72rem","color":GRAY_TEXT,
                                "fontWeight":"600","textTransform":"uppercase",
                                "letterSpacing":".5px","marginBottom":"4px"}),
                html.Div(tr["est_date"].strftime("%d %b %Y").upper(),
                         style={"fontSize":"1rem","fontWeight":"800",
                                "color": color}),
            ]),
        ], className="tc-result"),

    ], className="tc-card")

# ── APP ──────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap",
    ],
    title="UN WFP CHAD · Distribution Encours",
)

app.layout = lambda: html.Div([
    dcc.Store(id="store", data=load(), storage_type="local"),
    dcc.Store(id="del-id"),
    dcc.ConfirmDialog(id="confirm-del",
                      message="Confirmer la suppression de cette entrée ?"),

    # ── HEADER ──────────────────────────────────────────────────────────────
    html.Header([
        html.Div([
            LOGO_IMG,
            html.Div(className="hdr-divider"),
            html.Div([
                html.Div("UN WFP CHAD", className="hdr-org"),
                html.Div("TABLEAU DE BORD — DISTRIBUTION ENCOURS",
                         className="hdr-title"),
                html.Div("Suivi opérationnel · Ménages · Bénéficiaires · Montants XAF",
                         className="hdr-sub"),
            ]),
            html.Div([
                html.Div([
                    html.Div("Rapport du",       className="meta-lbl"),
                    html.Div(datetime.today().strftime("%d %b %Y").upper(),
                             className="meta-val"),
                ], className="meta-block"),
                html.Div(className="meta-sep"),
                html.Div([
                    html.Div("Taux de réalisation", className="meta-lbl"),
                    html.Div(id="hdr-taux",          className="meta-val accent"),
                ], className="meta-block"),
                html.Div(className="meta-sep"),
                html.Div([
                    html.Div("Dernière saisie", className="meta-lbl"),
                    html.Div(id="hdr-last",     className="meta-val"),
                ], className="meta-block"),
            ], className="hdr-meta"),
        ], className="hdr-body"),
    ]),

    # ── PAGE ────────────────────────────────────────────────────────────────
    html.Div([

        # ── KPI GRID ────────────────────────────────────────────────────────
        html.Div([

            # Bénéficiaires
            html.Div([
                html.Div([
                    html.Span("👥", style={"fontSize":"28px"}),
                    html.Span("BÉNÉFICIAIRES SERVIS", className="mc-lbl"),
                ], className="mc-head"),
                html.Div(id="kpi-benef", className="mc-big"),
                html.Div("Total cumulé depuis le début", className="mc-note"),
            ], className="mc mc-blue-light"),

            # Ménages
            html.Div([
                html.Div([
                    html.Span("🏠", style={"fontSize":"28px"}),
                    html.Span("MÉNAGES — VOUCHERS", className="mc-lbl"),
                ], className="mc-head"),
                html.Div(id="kpi-v"),
            ], className="mc mc-white"),

            # Montant
            html.Div([
                html.Div([
                    html.Span("💰", style={"fontSize":"28px"}),
                    html.Span("MONTANT XAF", className="mc-lbl"),
                ], className="mc-head"),
                html.Div(id="kpi-m"),
            ], className="mc mc-white"),

        ], className="kpi-grid"),

        # ── GRAPHIQUE ───────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div("ÉVOLUTION JOURNALIÈRE & TENDANCE VERS L'OBJECTIF",
                             className="section-lbl"),
                    html.Div("Bénéficiaires · Ménages · Cumul · Projection",
                             className="card-sub"),
                ]),
                html.Div(id="chart-badge", className="badge"),
            ], className="chart-hdr"),
            dcc.Graph(
                id="main-chart",
                figure=EMPTY_FIG,
                config={
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["select2d","lasso2d"],
                    "displaylogo": False,
                    "toImageButtonOptions": {
                        "format":"png","filename":"wfp_distribution",
                        "width":1400,"height":520,"scale":2,
                    },
                },
                style={"height":"400px"},
            ),
        ], className="chart-card"),

        # ── PIE + PROJECTION ─────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div("TAUX DE RÉALISATION", className="section-lbl"),
                        html.Div("Ménages & Montant XAF", className="card-sub"),
                    ], className="chart-hdr"),
                    dcc.Graph(
                        id="pie-chart",
                        config={"displayModeBar": False},
                        style={"height": "240px"},
                    ),
                ], className="chart-card h-100"),
            ], md=7),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div("PROJECTION OBJECTIF", className="section-lbl"),
                    ], className="chart-hdr"),
                    html.Div(id="trend-body"),
                ], className="chart-card h-100"),
            ], md=5),
        ], className="g-3 mb-3"),

        # ── TABLEAU ──────────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div("DONNÉES JOURNALIÈRES", className="section-lbl"),
                    html.Span(id="row-count", className="badge"),
                ], style={"display":"flex","alignItems":"center","gap":"14px"}),
            ], className="table-hdr"),
            html.Div(id="table-area", style={"overflowX": "auto"}),
        ], className="table-card"),

        # ── FORMULAIRE ──────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("SAISIE JOURNALIÈRE", className="section-lbl"),
                html.Div("Renseignez les données de distribution du jour", className="card-sub"),
            ], className="form-hdr"),
            html.Div([
                html.Div([
                    html.Label("Date", className="field-lbl"),
                    dcc.DatePickerSingle(
                        id="f-date", date=date.today().isoformat(),
                        display_format="DD/MM/YYYY",
                        style={"width": "100%"},
                    ),
                ], className="fg"),
                html.Div([
                    html.Label("Bénéficiaires servis", className="field-lbl"),
                    dcc.Input(id="f-ben", type="number", min=0,
                              placeholder="ex : 4 250", className="finput"),
                ], className="fg"),
                html.Div([
                    html.Label("Ménages (Vouchers)", className="field-lbl"),
                    dcc.Input(id="f-vch", type="number", min=0,
                              placeholder="ex : 850", className="finput"),
                ], className="fg"),
                html.Div([
                    html.Label("Montant XAF", className="field-lbl"),
                    dcc.Input(id="f-amt", type="number", min=0,
                              placeholder="ex : 20 450 000", className="finput"),
                ], className="fg"),
                html.Div([
                    html.Button("＋ Ajouter", id="btn-add", className="btn-primary"),
                    html.Button("⬇ CSV",     id="btn-csv", className="btn-sec"),
                    dcc.Download(id="download"),
                ], className="fg fg-btns"),
            ], className="form-grid"),
            html.Div(id="form-msg"),
        ], className="form-card"),

        # FOOTER
        html.Footer([
            html.Div([
                html.Strong("UN WFP CHAD",
                            style={"color": T_BLUE}),
                html.Span(" — Tableau de bord distribution encours",
                          style={"color": GRAY_TEXT}),
            ]),
            html.Div(id="footer-ts"),
        ], className="page-footer"),

    ], className="page"),
])

# ── CALLBACKS ────────────────────────────────────────────────────────────────

@app.callback(
    Output("store",   "data"),
    Output("form-msg","children"),
    Output("f-vch",   "value"),
    Output("f-amt",   "value"),
    Output("f-ben",   "value"),
    Input("btn-add",  "n_clicks"),
    State("f-date",   "date"),
    State("f-ben",    "value"),
    State("f-vch",    "value"),
    State("f-amt",    "value"),
    State("store",    "data"),
    prevent_initial_call=True,
)
def add_entry(_, fd, fb, fv, fm, data):
    errs = []
    if not fd:              errs.append("date manquante")
    if fb is None or fb<0:  errs.append("bénéficiaires invalides")
    if fv is None or fv<0:  errs.append("ménages invalides")
    if fm is None or fm<0:  errs.append("montant invalide")
    if errs:
        return (no_update,
                html.Div("⚠ " + " · ".join(errs).capitalize()+".",
                         className="msg-warn"),
                no_update, no_update, no_update)
    entries = list(data or [])
    entries.append({"id":str(datetime.now().timestamp()),
                    "date":fd,"b":int(fb),"v":int(fv),"m":float(fm)})
    save(entries)
    return (entries,
            html.Div("✓ Entrée ajoutée avec succès.", className="msg-ok"),
            None, None, None)


@app.callback(
    Output("confirm-del","displayed"),
    Output("del-id",     "data"),
    Input({"type":"btn-del","index":dash.ALL},"n_clicks"),
    prevent_initial_call=True,
)
def ask_del(nc):
    t = ctx.triggered_id
    if not t or not any(n for n in nc if n): return False, no_update
    return True, t["index"]


@app.callback(
    Output("store",   "data",    allow_duplicate=True),
    Output("form-msg","children", allow_duplicate=True),
    Input("confirm-del","submit_n_clicks"),
    State("del-id","data"),
    State("store","data"),
    prevent_initial_call=True,
)
def del_entry(sub, eid, data):
    if not sub or not eid: return no_update, no_update
    entries = [e for e in (data or []) if e["id"] != eid]
    save(entries)
    return entries, html.Div("🗑 Entrée supprimée.", className="msg-info")


@app.callback(
    Output("download","data"),
    Input("btn-csv","n_clicks"),
    State("store","data"),
    prevent_initial_call=True,
)
def export_csv(_, data):
    rows = [{"Date":f"{e['date'][8:]}/{e['date'][5:7]}/{e['date'][:4]}",
             "Bénéficiaires":e.get("b",0),
             "Ménages_Vouchers":e["v"],
             "Montant_XAF":e["m"]}
            for e in sorted(data or [], key=lambda x: x["date"])]
    return dcc.send_data_frame(
        pd.DataFrame(rows).to_csv,
        "wfp_distribution_encours.csv",
        index=False, sep=";", encoding="utf-8-sig",
    )


@app.callback(
    Output("kpi-benef",  "children"),
    Output("kpi-v",      "children"),
    Output("kpi-m",      "children"),
    Output("pie-chart",  "figure"),
    Output("trend-body", "children"),
    Output("main-chart", "figure"),
    Output("table-area", "children"),
    Output("row-count",  "children"),
    Output("hdr-taux",   "children"),
    Output("hdr-last",   "children"),
    Output("footer-ts",  "children"),
    Output("chart-badge","children"),
    Input("store","data"),
)
def update(data):
    entries = data or []
    t   = compute(entries)
    tr  = compute_trend(entries, t)
    now = datetime.now()

    # Bénéficiaires
    kpi_b = html.Span(fmt(t["tot_b"]))

    # Ménages tri-stat
    kpi_v = html.Div([
        stat_block("Planifié",  fmt(TARGET_V),   color=GRAY_TEXT),
        html.Div(className="stat-sep"),
        stat_block("Servis",    fmt(t["tot_v"]),
                   f"{t['pct_v']:.1f}% du planifié", color=T_BLUE),
        html.Div(className="stat-sep"),
        stat_block("Restant",   fmt(t["rst_v"]), color=T_ORANGE),
    ], className="stat-row")

    # Montant tri-stat
    kpi_m = html.Div([
        stat_block("Planifié",  fmt(TARGET_M)+" XAF", color=GRAY_TEXT),
        html.Div(className="stat-sep"),
        stat_block("Servi",     fmt(t["tot_m"])+" XAF",
                   f"{t['pct_m']:.1f}% du planifié", color=T_BLUE),
        html.Div(className="stat-sep"),
        stat_block("Restant",   fmt(t["rst_m"])+" XAF", color=T_ORANGE),
    ], className="stat-row")

    # Pie chart
    pie_fig   = build_pie_chart(t)
    trend_div = make_trend_card(tr, t)

    # Chart
    fig = build_chart(entries) if entries else EMPTY_FIG

    # Table
    if not entries:
        table = html.Div("Aucune saisie — utilisez le formulaire ci-dessus.",
                         className="empty-table")
    else:
        se = sorted(entries, key=lambda e: e["date"], reverse=True)
        cm: dict = {}; c = BASE_V
        for e in sorted(entries, key=lambda x: x["date"]):
            c += e["v"]; cm[e["id"]] = c

        rows = []
        for i, e in enumerate(se):
            d  = e["date"]
            pv = e["v"]/TARGET_V*100
            pm = e["m"]/TARGET_M*100
            rows.append(html.Tr([
                html.Td(f"{d[8:]}/{d[5:7]}/{d[:4]}", className="td-date"),
                html.Td(fmt(e.get("b",0)),            className="td-b"),
                html.Td(html.Strong(fmt(e["v"]))),
                html.Td(html.Span(f"{pv:.2f}%",       className="pill pill-blue")),
                html.Td(fmt(e["m"])+" XAF"),
                html.Td(html.Span(f"{pm:.2f}%",       className="pill pill-green")),
                html.Td(html.Strong(fmt(cm[e["id"]]), style={"color":T_NAVY})),
                html.Td(html.Button("✕",
                        id={"type":"btn-del","index":e["id"]},
                        className="btn-del")),
            ], className="tr-alt" if i%2 else ""))
        table = html.Table([
            html.Thead(html.Tr([
                html.Th("Date"),
                html.Th("Bénéficiaires"),
                html.Th("Ménages / Jour"),
                html.Th("% Cible Ménages"),
                html.Th("Montant / Jour"),
                html.Th("% Cible Montant"),
                html.Th("Cumul Ménages"),
                html.Th(""),
            ])),
            html.Tbody(rows),
        ], className="dist-table")

    ld        = sorted(entries,key=lambda e:e["date"])[-1]["date"] if entries else None
    hdr_last  = f"{ld[8:]}/{ld[5:7]}/{ld[:4]}" if ld else "—"
    footer_ts = f"Mise à jour : {now.strftime('%d/%m/%Y à %H:%M')}"

    return (kpi_b, kpi_v, kpi_m, pie_fig, trend_div, fig, table,
            f"{len(entries)} entrée{'s' if len(entries)>1 else ''}",
            f"{t['pct_v']:.1f}%", hdr_last, footer_ts,
            f"Au {now.strftime('%d/%m/%Y')}")


# ── CSS ──────────────────────────────────────────────────────────────────────
app.index_string = f"""<!DOCTYPE html>
<html>
<head>
  {{%metas%}}<title>{{%title%}}</title>{{%favicon%}}{{%css%}}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <style>
  :root {{
    --navy:    {T_NAVY};
    --blue:    {T_BLUE};
    --blue2:   {T_BLUE2};
    --teal:    {T_TEAL};
    --light:   {T_LIGHT};
    --green:   {T_GREEN};
    --orange:  {T_ORANGE};
    --gray-bg: {GRAY_BG};
    --gray-ln: {GRAY_LINE};
    --gray-txt:{GRAY_TEXT};
    --white:   {WHITE};
    --shadow-sm: 0 1px 4px rgba(0,73,153,.08), 0 1px 2px rgba(0,73,153,.04);
    --shadow:    0 2px 12px rgba(0,73,153,.10), 0 1px 4px rgba(0,73,153,.06);
    --shadow-lg: 0 6px 24px rgba(0,73,153,.13), 0 2px 8px rgba(0,73,153,.07);
    --radius:  8px;
  }}
  *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family: 'Open Sans','Segoe UI',Arial,sans-serif;
    background: var(--gray-bg);
    color: #1A3050;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  /* ══ HEADER — WFP/UN Official White Banner ════════════════════════════════ */
  header {{
    background: {WHITE};
    border-bottom: 3px solid {T_BLUE};
    box-shadow: 0 2px 12px rgba(0,105,181,.12);
    position: sticky; top: 0; z-index: 100;
  }}
  .hdr-body {{
    display: flex; align-items: center; gap: 0;
    padding: 0 40px; flex-wrap: wrap;
    max-width: 1440px; margin: 0 auto;
    min-height: 72px;
  }}
  .hdr-divider {{
    width: 1px; height: 44px;
    background: {GRAY_LINE};
    flex-shrink: 0; margin: 0 24px;
  }}
  .hdr-org {{
    font-size: 1rem; font-weight: 800; color: {T_BLUE};
    letter-spacing: .8px; text-transform: uppercase;
    line-height: 1; margin-bottom: 4px;
  }}
  .hdr-title {{
    font-size: .78rem; font-weight: 700; color: {T_NAVY};
    letter-spacing: .6px; text-transform: uppercase;
  }}
  .hdr-sub {{ font-size: .7rem; color: {GRAY_TEXT}; margin-top: 3px; font-weight: 400; letter-spacing: .2px; }}

  .hdr-meta {{
    margin-left: auto; display: flex; align-items: stretch; gap: 0;
  }}
  .meta-block {{
    padding: 14px 22px; text-align: center;
    border-left: 1px solid {GRAY_LINE};
    display: flex; flex-direction: column; justify-content: center;
  }}
  .meta-block:last-child {{ border-right: 1px solid {GRAY_LINE}; }}
  .meta-lbl {{
    font-size: .58rem; text-transform: uppercase; letter-spacing: 1.2px;
    color: {GRAY_TEXT}; font-weight: 700; margin-bottom: 4px;
  }}
  .meta-val {{
    font-size: .88rem; font-weight: 700; color: {T_NAVY};
  }}
  .accent {{
    font-size: 1.05rem !important; font-weight: 800 !important;
    color: {T_BLUE} !important;
  }}
  .meta-sep {{ display: none; }}

  /* ══ PAGE ════════════════════════════════════════════════════════════════ */
  .page {{ max-width: 1360px; margin: 0 auto; padding: 28px 28px 0; }}

  /* ══ KPI GRID ════════════════════════════════════════════════════════════ */
  .kpi-grid {{
    display: grid;
    grid-template-columns: 1fr 2.2fr 2.2fr;
    gap: 16px; margin-bottom: 20px;
  }}
  @media(max-width:860px){{.kpi-grid{{grid-template-columns:1fr 1fr;}}}}
  @media(max-width:540px){{.kpi-grid{{grid-template-columns:1fr;}}}}

  .mc {{
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border: none;
    transition: transform .15s, box-shadow .15s;
  }}
  .mc:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-lg); }}

  .mc-blue-light {{
    background: linear-gradient(145deg, {T_BLUE} 0%, {T_NAVY} 100%);
    border-left: 4px solid rgba(255,255,255,.3);
  }}
  .mc-white {{
    background: {WHITE};
    border-top: 3px solid {T_BLUE};
  }}
  .mc-white:nth-child(3) {{ border-top-color: {T_TEAL}; }}

  .mc-head {{
    display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
  }}
  .mc-lbl {{
    font-size: .65rem; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; font-family: 'Open Sans', sans-serif;
  }}
  .mc-blue-light .mc-lbl {{ color: rgba(219,235,245,.85); }}
  .mc-white      .mc-lbl {{ color: var(--gray-txt); }}

  .mc-big {{
    font-size: 2.8rem; font-weight: 800; color: {WHITE};
    line-height: 1; letter-spacing: -1.5px;
    font-family: 'Open Sans', sans-serif;
  }}
  .mc-note {{ font-size: .7rem; color: rgba(219,235,245,.65); margin-top: 8px; font-weight: 400; }}

  .stat-row {{
    display: flex; align-items: stretch; gap: 0;
    padding: 4px 0;
  }}
  .stat-block {{ flex: 1; padding: 0; }}
  .stat-lbl {{
    font-size: .62rem; text-transform: uppercase; letter-spacing: .8px;
    color: var(--gray-txt); font-weight: 700; margin-bottom: 5px;
  }}
  .stat-val {{
    font-size: 1.1rem; font-weight: 800; line-height: 1.2; color: {T_NAVY};
    font-family: 'Open Sans', sans-serif;
  }}
  .stat-sub {{ font-size: .72rem; font-weight: 600; margin-top: 2px; color: var(--gray-txt); }}
  .stat-sep {{
    width: 1px; background: var(--gray-ln);
    margin: 0 18px; flex-shrink: 0; align-self: stretch;
  }}

  /* ══ SECTION LABEL ═══════════════════════════════════════════════════════ */
  .section-lbl {{
    font-size: .68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.3px; color: var(--blue); margin-bottom: 2px;
  }}
  .card-sub {{ font-size: .75rem; color: var(--gray-txt); }}

  /* ══ CHART CARD ══════════════════════════════════════════════════════════ */
  .chart-card {{
    background: {WHITE};
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    overflow: hidden;
    border: none;
  }}
  .h-100 {{ height: calc(100% - 20px) !important; margin-bottom: 0 !important; }}
  .chart-hdr {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 22px 12px;
    border-bottom: 1px solid var(--gray-ln);
    background: {WHITE};
  }}
  .badge {{
    font-size: .7rem; font-weight: 700; color: var(--blue);
    background: var(--light); border: 1px solid #B3D7F0;
    padding: 3px 11px; border-radius: 20px;
    white-space: nowrap;
  }}

  /* ══ FORM CARD ═══════════════════════════════════════════════════════════ */
  .form-card {{
    background: {WHITE};
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    overflow: hidden;
  }}
  .form-hdr {{
    padding: 14px 22px 12px;
    border-bottom: 1px solid var(--gray-ln);
    background: {WHITE};
  }}
  .form-grid {{
    display: grid;
    grid-template-columns: 155px 1fr 1fr 1fr auto;
    gap: 14px; padding: 18px 22px; align-items: end;
  }}
  @media(max-width:840px){{.form-grid{{grid-template-columns:1fr 1fr;}}}}
  .fg {{ display: flex; flex-direction: column; }}
  .fg-btns {{ flex-direction: row; gap: 8px; align-items: flex-end; }}
  .field-lbl {{
    font-size: .65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .7px; color: var(--gray-txt); margin-bottom: 5px;
  }}
  .finput {{
    width: 100%; padding: 9px 12px;
    border: 1.5px solid var(--gray-ln); border-radius: 7px;
    font-size: .9rem; font-family: inherit; color: #1A2340;
    outline: none; transition: border-color .2s, box-shadow .2s;
    background: {WHITE};
  }}
  .finput:focus {{
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(0,105,181,.12);
  }}
  .btn-primary {{
    padding: 9px 22px;
    background: {T_BLUE}; color: {WHITE};
    border: none; border-radius: 6px;
    font-size: .85rem; font-weight: 700;
    cursor: pointer; white-space: nowrap;
    font-family: 'Open Sans', sans-serif;
    letter-spacing: .3px;
    transition: background .15s, transform .1s, box-shadow .15s;
    box-shadow: 0 2px 8px rgba(0,105,181,.28);
  }}
  .btn-primary:hover {{
    background: {T_NAVY};
    box-shadow: 0 4px 14px rgba(0,105,181,.38);
    transform: translateY(-1px);
  }}
  .btn-sec {{
    padding: 9px 14px; background: {WHITE}; color: var(--blue);
    border: 1.5px solid var(--gray-ln); border-radius: 7px;
    font-size: .85rem; font-weight: 600; cursor: pointer;
    font-family: inherit; transition: all .15s;
  }}
  .btn-sec:hover {{
    background: var(--light); border-color: var(--blue);
  }}
  .msg-ok   {{ font-size:.8rem; color:var(--green);   padding:7px 0; font-weight:700; }}
  .msg-warn {{ font-size:.8rem; color:var(--orange);  padding:7px 0; font-weight:700; }}
  .msg-info {{ font-size:.8rem; color:var(--gray-txt);padding:7px 0; }}

  /* ══ TABLE CARD ══════════════════════════════════════════════════════════ */
  .table-card {{
    background: {WHITE};
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    overflow: hidden;
  }}
  .table-hdr {{
    padding: 14px 22px 12px;
    border-bottom: 1px solid var(--gray-ln);
    background: {WHITE};
  }}
  .dist-table {{ width: 100%; border-collapse: collapse; font-size: .85rem; font-family: 'Open Sans', sans-serif; }}
  .dist-table thead {{
    background: linear-gradient(90deg, {T_BLUE} 0%, {T_NAVY} 100%);
  }}
  .dist-table thead th {{
    padding: 11px 16px; color: {WHITE}; text-align: left;
    font-size: .62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
  }}
  .dist-table tbody tr {{
    border-bottom: 1px solid {GRAY_LINE};
    transition: background .1s;
  }}
  .dist-table tbody tr:hover {{ background: #EEF5FB; }}
  .dist-table .tr-alt {{ background: #F7FAFE; }}
  .dist-table tbody td {{ padding: 10px 16px; vertical-align: middle; }}
  .td-date {{ color: var(--gray-txt); font-size: .8rem; }}
  .td-b    {{ font-weight: 700; color: {T_BLUE}; font-size: .9rem; }}
  .pill {{
    display: inline-block; padding: 2px 9px; border-radius: 20px;
    font-size: .7rem; font-weight: 700;
  }}
  .pill-blue  {{ background: {T_LIGHT}; color: {T_NAVY}; }}
  .pill-green {{ background: {T_GREEN_L}; color: {T_GREEN}; }}
  .btn-del {{
    background: none; border: none; color: #C0C8D6;
    cursor: pointer; padding: 3px 7px; border-radius: 4px; font-size: .85rem;
    transition: color .12s, background .12s;
  }}
  .btn-del:hover {{ color: {T_ORANGE}; background: {T_ORANGE_L}; }}
  .empty-table {{
    text-align: center; color: var(--gray-txt); padding: 44px;
    font-size: .9rem;
  }}

  /* ══ PROJECTION CARD ═════════════════════════════════════════════════════ */
  .tc-card {{
    padding: 18px 20px;
    display: flex; flex-direction: column; gap: 14px;
  }}
  .tc-row {{
    display: flex; align-items: center;
    background: #F7FAFD; border-radius: 8px; padding: 11px 14px;
    border: 1px solid var(--gray-ln);
  }}
  .tc-stat {{ flex: 1; }}
  .tc-sep {{
    width: 1px; background: var(--gray-ln);
    margin: 0 16px; align-self: stretch;
  }}
  .tc-lbl {{
    font-size: .62rem; text-transform: uppercase; letter-spacing: .8px;
    color: var(--gray-txt); font-weight: 700; margin-bottom: 3px;
  }}
  .tc-val  {{ font-size: 1.05rem; font-weight: 800; display: inline; }}
  .tc-unit {{ font-size: .7rem; color: var(--gray-txt); font-weight: 600; margin-left: 3px; }}

  .tc-result {{
    display: flex; align-items: center; gap: 16px; flex: 1;
    padding: 4px 0;
  }}
  .tc-days-block {{
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-width: 76px; height: 76px;
    border-radius: 12px; border: 2px solid; flex-shrink: 0;
    box-shadow: var(--shadow-sm);
  }}
  .tc-days     {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
  .tc-days-lbl {{ font-size: .65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; }}

  .trend-empty {{
    padding: 28px 20px; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px; flex: 1;
  }}

  /* ══ DATE PICKER ═════════════════════════════════════════════════════════ */
  .SingleDatePickerInput {{
    border: 1.5px solid var(--gray-ln) !important;
    border-radius: 7px !important;
    background: {WHITE} !important;
  }}
  .DateInput_input {{
    font-size: .9rem !important; padding: 8px 12px !important;
    font-family: inherit !important; color: #1A2340 !important;
  }}
  .DateInput_input:focus {{ border-bottom: 2px solid var(--blue) !important; }}
  .CalendarDay__selected {{
    background: var(--blue) !important; border-color: var(--blue) !important;
  }}
  .DayPickerNavigation_button:hover {{ border-color: var(--blue) !important; }}

  /* ══ FOOTER ══════════════════════════════════════════════════════════════ */
  .page-footer {{
    border-top: 2px solid {T_BLUE};
    padding: 16px 4px 28px;
    display: flex; align-items: center; justify-content: space-between;
    font-size: .73rem; color: var(--gray-txt);
    margin-top: 4px;
    font-family: 'Open Sans', sans-serif;
  }}
  </style>
</head>
<body>{{%app_entry%}}<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer></body>
</html>
"""

if __name__ == "__main__":
    print("\n" + "="*58)
    print("  UN WFP CHAD")
    print("  Dashboard Distribution Encours")
    print("  ➜  http://127.0.0.1:8050")
    print("="*58 + "\n")
    app.run(debug=False, port=8050)
