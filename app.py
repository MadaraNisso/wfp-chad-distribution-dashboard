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

# ── BRAND — 5 couleurs image (navy · blue · orange · green · white) ───────────
T_NAVY    = "#17375E"   # ① Navy foncé  — headers tableau, accents forts
T_BLUE    = "#0B72C0"   # ② WFP Blue    — labels, highlights, primaire
T_BLUE2   = "#1A85D6"   # variation blue
T_LIGHT   = "#EBF4FC"   # tint (dérivé)
T_TEAL    = "#0B72C0"
T_GREEN   = "#22A060"   # ③ Vert        — projection, objectif, succès
T_GREEN_L = "#E8F7EF"   # tint vert
T_ORANGE  = "#E07020"   # ④ Orange      — restant, tendance, alerte
T_ORANGE_L= "#FEF0E4"   # tint orange
T_RED     = "#E07020"
WHITE     = "#FFFFFF"   # ⑤ Blanc       — cartes, fonds
GRAY_BG   = "#F0F4F8"   # fond page (dérivé)
GRAY_LINE = "#D8E4EF"   # bordures
GRAY_TEXT = "#4A6070"   # texte secondaire
FONT      = "'Inter','system-ui',sans-serif"

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
        font_family=FONT, font_size=14,
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
        hoverlabel=dict(bgcolor=T_NAVY, font_size=14, font_family=FONT, font_color=WHITE, bordercolor=T_BLUE2),
        xaxis=dict(showgrid=False, tickfont=dict(size=13, color=GRAY_TEXT), linecolor=GRAY_LINE, tickangle=-30),
        yaxis=dict(
            title=dict(text="Bénéficiaires / Ménages · Jour", font=dict(color=GRAY_TEXT, size=13)),
            showgrid=True, gridcolor="#E8EFF5", gridwidth=1,
            tickfont=dict(size=13, color=GRAY_TEXT), zeroline=False,
        ),
        yaxis2=dict(
            title=dict(text="Cumul Ménages", font=dict(color=T_NAVY, size=13)),
            tickfont=dict(size=13, color=T_NAVY),
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
    is_highlight = (color == T_BLUE)
    return html.Div([
        html.Div(label,
                 className="text-[11px] font-semibold uppercase tracking-[1.2px] mb-2",
                 style={"color": GRAY_TEXT}),
        html.Div([
            html.Div(value,
                     className="text-[1.9rem] font-extrabold leading-none tracking-tight",
                     style={"color": color}),
            html.Div(className="h-[3px] mt-2 rounded-full",
                     style={"background": color, "width": "32px"}) if is_highlight else None,
        ]),
        html.Div(sub,
                 className="text-[12px] font-medium mt-2",
                 style={"color": GRAY_TEXT}) if sub else None,
    ], className="flex-1 min-w-0")

def make_trend_card(tr, t):
    if tr["days_remaining"] is None:
        return html.Div([
            html.Div("📊", className="text-4xl mb-2"),
            html.Div("Ajoutez des saisies pour calculer la projection.",
                     className="text-xs text-[#3A5070] text-center"),
        ], className="flex flex-col items-center justify-center p-6")

    color = T_GREEN if tr["days_remaining"] <= 14 else (T_BLUE if tr["days_remaining"] <= 30 else T_ORANGE)
    bg    = T_GREEN_L if tr["days_remaining"] <= 14 else (T_LIGHT if tr["days_remaining"] <= 30 else T_ORANGE_L)

    return html.Div([
        # Mini stats
        html.Div([
            html.Div([
                html.Div("RYTHME MOYEN",
                         className="text-[10px] font-semibold uppercase tracking-[1.2px] mb-1.5",
                         style={"color": GRAY_TEXT}),
                html.Div([
                    html.Span(fmt(tr["avg_daily"]),
                              className="text-[1.9rem] font-extrabold leading-none tracking-tight",
                              style={"color": T_BLUE}),
                    html.Span(" / jour",
                              className="text-[13px] font-medium ml-1.5",
                              style={"color": GRAY_TEXT}),
                ]),
            ], className="flex-1"),
            html.Div(className="w-px mx-4 self-stretch", style={"background": GRAY_LINE}),
            html.Div([
                html.Div("RESTANT",
                         className="text-[10px] font-semibold uppercase tracking-[1.2px] mb-1.5",
                         style={"color": GRAY_TEXT}),
                html.Div([
                    html.Span(fmt(t["rst_v"]),
                              className="text-[1.9rem] font-extrabold leading-none tracking-tight",
                              style={"color": T_ORANGE}),
                    html.Span(" ménages",
                              className="text-[13px] font-medium ml-1.5",
                              style={"color": GRAY_TEXT}),
                ]),
            ], className="flex-1"),
        ], className="flex items-center rounded-lg px-5 py-4",
           style={"background": "#F7FAFD", "border": f"1px solid {GRAY_LINE}"}),
        # Main result
        html.Div([
            html.Div([
                html.Div(str(tr["days_remaining"]),
                         className="text-[3.2rem] font-extrabold leading-none tracking-tighter",
                         style={"color": T_GREEN}),
                html.Div(f"JOUR{'S' if tr['days_remaining']>1 else ''}",
                         className="text-[9px] font-bold uppercase tracking-[2px] mt-1",
                         style={"color": T_GREEN}),
            ], className="flex flex-col items-center justify-center min-w-[90px] h-[90px] rounded-xl flex-shrink-0",
               style={"border": f"2px solid {T_GREEN}", "background": T_GREEN_L}),
            html.Div([
                html.Div("OBJECTIF ESTIMÉ ATTEINT DANS",
                         className="text-[10px] font-semibold uppercase tracking-[1px] mb-2",
                         style={"color": GRAY_TEXT}),
                html.Div(tr["est_date"].strftime("%d %b %Y").upper(),
                         className="text-[1.4rem] font-extrabold tracking-wide",
                         style={"color": T_GREEN}),
            ], className="ml-5"),
        ], className="flex items-center"),
    ], className="flex flex-col gap-4 p-5")

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
    dcc.ConfirmDialog(id="confirm-del", message="Confirmer la suppression de cette entrée ?"),

    # ── HEADER ──────────────────────────────────────────────────────────────
    html.Header([
        html.Div([
            LOGO_IMG,
            html.Div(className="w-px h-11 bg-[#D5E3EF] mx-6 flex-shrink-0"),
            html.Div([
                html.Div("UN WFP CHAD",
                         className="text-[#0069B5] font-extrabold text-[19px] uppercase tracking-[2px] leading-none mb-1.5"),
                html.Div("TABLEAU DE BORD — DISTRIBUTION ENCOURS",
                         className="text-[#004F87] font-bold text-[13px] uppercase tracking-[0.8px]"),
                html.Div("Suivi opérationnel · Ménages · Bénéficiaires · Montants XAF",
                         className="text-[#3A5070] text-[12px] mt-1"),
            ]),
            html.Div([
                html.Div([
                    html.Div("Rapport du",
                             className="text-[10px] font-bold uppercase tracking-[1.2px] text-[#3A5070] mb-1"),
                    html.Div(datetime.today().strftime("%d %b %Y").upper(),
                             className="text-[15px] font-bold text-[#004F87]"),
                ], className="px-6 py-4 border-l border-[#D5E3EF] text-center"),
                html.Div([
                    html.Div("Taux de réalisation",
                             className="text-[10px] font-bold uppercase tracking-[1.2px] text-[#3A5070] mb-1"),
                    html.Div(id="hdr-taux",
                             className="text-[22px] font-extrabold text-[#0069B5]"),
                ], className="px-6 py-4 border-l border-[#D5E3EF] text-center"),
                html.Div([
                    html.Div("Dernière saisie",
                             className="text-[10px] font-bold uppercase tracking-[1.2px] text-[#3A5070] mb-1"),
                    html.Div(id="hdr-last",
                             className="text-[15px] font-bold text-[#004F87]"),
                ], className="px-6 py-4 border-l border-r border-[#D5E3EF] text-center"),
            ], className="ml-auto flex items-stretch"),
        ], className="flex items-center px-10 max-w-[1440px] mx-auto min-h-[72px]"),
    ], className="bg-white border-b-[3px] border-[#0069B5] sticky top-0 z-50",
       style={"boxShadow": "0 2px 12px rgba(0,105,181,0.12)"}),

    # ── PAGE ────────────────────────────────────────────────────────────────
    html.Div([

        # KPI Grid
        html.Div([
            html.Div([
                html.Div([
                    html.Span("👥", className="text-3xl"),
                    html.Span("BÉNÉFICIAIRES SERVIS",
                              className="text-[12px] font-bold tracking-[1.5px] uppercase ml-3",
                              style={"color":"rgba(219,235,245,0.85)"}),
                ], className="flex items-center mb-4"),
                html.Div(id="kpi-benef",
                         className="text-[4.2rem] font-extrabold text-white leading-none tracking-[-3px]"),
                html.Div(className="h-[3px] w-14 rounded-full bg-white opacity-40 my-3"),
                html.Div("Total cumulé depuis le début",
                         className="text-[12.5px]",
                         style={"color":"rgba(255,255,255,0.65)"}),
            ], className="rounded-xl p-5 border-l-4 border-[rgba(255,255,255,0.25)]",
               style={"background": f"linear-gradient(145deg, {T_BLUE} 0%, {T_NAVY} 100%)",
                      "boxShadow": "0 4px 16px rgba(0,105,181,0.25)"}),

            html.Div([
                html.Div([
                    html.Span("🏠", className="text-3xl"),
                    html.Span("MÉNAGES — VOUCHERS",
                              className="text-[12px] font-bold tracking-[1.5px] uppercase text-[#3A5070] ml-3"),
                ], className="flex items-center mb-4"),
                html.Div(id="kpi-v"),
            ], className="bg-white rounded-xl p-5 border-t-[3px] border-[#0069B5]",
               style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),

            html.Div([
                html.Div([
                    html.Span("💰", className="text-3xl"),
                    html.Span("MONTANT XAF",
                              className="text-[12px] font-bold tracking-[1.5px] uppercase text-[#3A5070] ml-3"),
                ], className="flex items-center mb-4"),
                html.Div(id="kpi-m"),
            ], className="bg-white rounded-xl p-5 border-t-[3px] border-[#0095A8]",
               style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),

        ], className="grid gap-4 mb-5",
           style={"gridTemplateColumns": "1fr 2.2fr 2.2fr"}),

        # Graphique
        html.Div([
            html.Div([
                html.Div([
                    html.Div("ÉVOLUTION JOURNALIÈRE & TENDANCE VERS L'OBJECTIF",
                             className="text-[13px] font-bold uppercase tracking-[1.3px] text-[#0069B5]"),
                    html.Div("Bénéficiaires · Ménages · Cumul · Projection",
                             className="text-[13px] text-[#3A5070] mt-0.5"),
                ]),
                html.Div(id="chart-badge",
                         className="text-[12px] font-bold text-[#0069B5] bg-[#E8F2FB] border border-[#C0D8EE] px-3.5 py-1 rounded-full whitespace-nowrap"),
            ], className="flex items-center justify-between px-5 py-3.5 border-b border-[#D5E3EF]"),
            dcc.Graph(
                id="main-chart", figure=EMPTY_FIG,
                config={"displayModeBar": True,
                        "modeBarButtonsToRemove": ["select2d","lasso2d"],
                        "displaylogo": False,
                        "toImageButtonOptions": {"format":"png","filename":"wfp_distribution","width":1400,"height":520,"scale":2}},
                style={"height":"400px"},
            ),
        ], className="bg-white rounded-xl mb-5 overflow-hidden",
           style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),

        # Pie + Projection
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div("TAUX DE RÉALISATION",
                                 className="text-[13px] font-bold uppercase tracking-[1.3px] text-[#0069B5]"),
                        html.Div("Ménages & Montant XAF",
                                 className="text-[13px] text-[#3A5070] mt-0.5"),
                    ], className="px-5 py-3.5 border-b border-[#D5E3EF]"),
                    dcc.Graph(id="pie-chart", config={"displayModeBar": False},
                              style={"height":"240px"}),
                ], className="bg-white rounded-xl overflow-hidden h-full",
                   style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),
            ], md=7),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div("PROJECTION OBJECTIF",
                                 className="text-[13px] font-bold uppercase tracking-[1.3px] text-[#0069B5]"),
                    ], className="px-5 py-3.5 border-b border-[#D5E3EF]"),
                    html.Div(id="trend-body"),
                ], className="bg-white rounded-xl overflow-hidden h-full",
                   style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),
            ], md=5),
        ], className="g-3 mb-5"),

        # Tableau
        html.Div([
            html.Div([
                html.Div([
                    html.Div("DONNÉES JOURNALIÈRES",
                             className="text-[13px] font-bold uppercase tracking-[1.3px] text-[#0069B5]"),
                    html.Span(id="row-count",
                              className="text-[12px] font-bold text-[#0069B5] bg-[#E8F2FB] border border-[#C0D8EE] px-3.5 py-1 rounded-full ml-3"),
                ], className="flex items-center"),
            ], className="px-5 py-3.5 border-b border-[#D5E3EF]"),
            html.Div(id="table-area", className="overflow-x-auto"),
        ], className="bg-white rounded-xl mb-5 overflow-hidden",
           style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),

        # Formulaire
        html.Div([
            html.Div([
                html.Div("SAISIE JOURNALIÈRE",
                         className="text-[13px] font-bold uppercase tracking-[1.3px] text-[#0069B5]"),
                html.Div("Renseignez les données de distribution du jour",
                         className="text-[13px] text-[#3A5070] mt-0.5"),
            ], className="px-5 py-3.5 border-b border-[#D5E3EF]"),
            html.Div([
                html.Div([
                    html.Label("Date",
                               className="block text-[11px] font-bold uppercase tracking-[0.7px] text-[#3A5070] mb-2"),
                    dcc.DatePickerSingle(id="f-date", date=date.today().isoformat(),
                                        display_format="DD/MM/YYYY", style={"width":"100%"}),
                ], className="flex flex-col"),
                html.Div([
                    html.Label("Bénéficiaires servis",
                               className="block text-[11px] font-bold uppercase tracking-[0.7px] text-[#3A5070] mb-2"),
                    dcc.Input(id="f-ben", type="number", min=0,
                              placeholder="ex : 4 250", className="finput"),
                ], className="flex flex-col"),
                html.Div([
                    html.Label("Ménages (Vouchers)",
                               className="block text-[11px] font-bold uppercase tracking-[0.7px] text-[#3A5070] mb-2"),
                    dcc.Input(id="f-vch", type="number", min=0,
                              placeholder="ex : 850", className="finput"),
                ], className="flex flex-col"),
                html.Div([
                    html.Label("Montant XAF",
                               className="block text-[11px] font-bold uppercase tracking-[0.7px] text-[#3A5070] mb-2"),
                    dcc.Input(id="f-amt", type="number", min=0,
                              placeholder="ex : 20 450 000", className="finput"),
                ], className="flex flex-col"),
                html.Div([
                    html.Button("＋ Ajouter", id="btn-add", className="btn-primary"),
                    html.Button("⬇ CSV",     id="btn-csv", className="btn-sec"),
                    dcc.Download(id="download"),
                ], className="flex gap-2 items-end"),
            ], className="grid gap-4 p-5 items-end",
               style={"gridTemplateColumns": "155px 1fr 1fr 1fr auto"}),
            html.Div(id="form-msg", className="px-5 pb-3"),
        ], className="bg-white rounded-xl mb-5 overflow-hidden",
           style={"boxShadow": "0 2px 12px rgba(0,105,181,0.10)"}),

        # Footer
        html.Footer([
            html.Div([
                html.Strong("UN WFP CHAD", style={"color": T_BLUE}),
                html.Span(" — Tableau de bord distribution encours",
                          className="text-[#3A5070]"),
            ]),
            html.Div(id="footer-ts", className="text-[#3A5070]"),
        ], className="border-t-2 border-[#0069B5] pt-4 pb-7 flex items-center justify-between text-[12px]"),

    ], className="max-w-[1360px] mx-auto px-7 pt-7"),
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

    SEP = html.Div(className="w-px bg-[#D5E3EF] mx-4 self-stretch flex-shrink-0")

    # Ménages tri-stat
    kpi_v = html.Div([
        stat_block("Planifié",  fmt(TARGET_V),   color=GRAY_TEXT),
        SEP,
        stat_block("Servis",    fmt(t["tot_v"]),
                   f"{t['pct_v']:.1f}% du planifié", color=T_BLUE),
        SEP,
        stat_block("Restant",   fmt(t["rst_v"]), color="#E07020"),
    ], className="flex items-stretch py-1")

    # Montant tri-stat
    kpi_m = html.Div([
        stat_block("Planifié",  fmt(TARGET_M)+" XAF", color=GRAY_TEXT),
        SEP,
        stat_block("Servi",     fmt(t["tot_m"])+" XAF",
                   f"{t['pct_m']:.1f}% du planifié", color=T_BLUE),
        SEP,
        stat_block("Restant",   fmt(t["rst_m"])+" XAF", color="#E07020"),
    ], className="flex items-stretch py-1")

    # Pie chart
    pie_fig   = build_pie_chart(t)
    trend_div = make_trend_card(tr, t)

    # Chart
    fig = build_chart(entries) if entries else EMPTY_FIG

    # Table
    if not entries:
        table = html.Div("Aucune saisie — utilisez le formulaire ci-dessous.",
                         className="text-center text-[#3A5070] py-11 text-[.9rem]")
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
                html.Td(f"{d[8:]}/{d[5:7]}/{d[:4]}",
                        className="px-4 py-3.5 text-[#3A5070] text-[13px] whitespace-nowrap font-semibold"),
                html.Td(fmt(e.get("b",0)),
                        className="px-4 py-3.5 font-extrabold text-[15px]",
                        style={"color": T_BLUE}),
                html.Td(html.Strong(fmt(e["v"]), style={"fontSize":"15px","color":T_NAVY}),
                        className="px-4 py-3.5"),
                html.Td(html.Span(f"{pv:.2f}%",
                        className="inline-block px-3 py-1 rounded-full text-[12px] font-semibold bg-[#EBF4FC] text-[#0B72C0]"),
                        className="px-4 py-3.5"),
                html.Td(fmt(e["m"])+" XAF",
                        className="px-4 py-3.5 whitespace-nowrap text-[13px] font-semibold"),
                html.Td(html.Span(f"{pm:.2f}%",
                        className="inline-block px-3 py-1 rounded-full text-[12px] font-semibold bg-[#E8F7EF] text-[#22A060]"),
                        className="px-4 py-3.5"),
                html.Td(html.Strong(fmt(cm[e["id"]]), style={"color":"#17375E","fontSize":"15px"}),
                        className="px-4 py-3.5"),
                html.Td(html.Button("✕",
                        id={"type":"btn-del","index":e["id"]},
                        className="text-[#B0BFCE] hover:text-[#E07B2A] bg-transparent border-none cursor-pointer px-2 py-1 rounded text-[15px] transition-colors"),
                        className="px-2 py-3.5"),
            ], className=f"border-b border-[#D5E3EF] transition-colors {'bg-[#F7FAFE]' if i%2 else 'bg-white'}"))
        table = html.Table([
            html.Thead(html.Tr([
                html.Th(col, className="px-4 py-4 text-left text-[12px] font-bold uppercase tracking-[1px] text-white whitespace-nowrap")
                for col in ["Date","Bénéficiaires","Ménages / Jour","% Cible Ménages","Montant / Jour","% Cible Montant","Cumul Ménages",""]
            ]), style={"background": f"linear-gradient(90deg, {T_BLUE} 0%, {T_NAVY} 100%)"}),
            html.Tbody(rows),
        ], className="w-full border-collapse text-sm")

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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{ sans: ['"Inter"','"system-ui"','sans-serif'] }}
        }}
      }}
    }}
  </script>
  <style>
  body {{ font-family:'Open Sans','Segoe UI',Arial,sans-serif; background:{GRAY_BG}; color:#1A3050; -webkit-font-smoothing:antialiased; }}
  /* DatePicker */
  .SingleDatePickerInput {{ border:1.5px solid {GRAY_LINE} !important; border-radius:6px !important; background:white !important; }}
  .DateInput_input {{ font-size:.9rem !important; padding:8px 12px !important; font-family:'Open Sans',sans-serif !important; color:#1A3050 !important; }}
  .DateInput_input:focus {{ border-bottom:2px solid {T_BLUE} !important; }}
  .CalendarDay__selected {{ background:{T_BLUE} !important; border-color:{T_BLUE} !important; }}
  /* Inputs */
  .finput {{ width:100%; padding:9px 12px; border:1.5px solid {GRAY_LINE}; border-radius:6px; font-size:.9rem; font-family:'Open Sans',sans-serif; color:#1A3050; outline:none; transition:border-color .2s,box-shadow .2s; background:white; }}
  .finput:focus {{ border-color:{T_BLUE}; box-shadow:0 0 0 3px rgba(0,105,181,.10); }}
  /* Buttons */
  .btn-primary {{ padding:9px 22px; background:{T_BLUE}; color:white; border:none; border-radius:6px; font-size:.85rem; font-weight:700; cursor:pointer; white-space:nowrap; font-family:'Open Sans',sans-serif; letter-spacing:.3px; transition:background .15s,transform .1s,box-shadow .15s; box-shadow:0 2px 8px rgba(0,105,181,.28); }}
  .btn-primary:hover {{ background:{T_NAVY}; box-shadow:0 4px 14px rgba(0,105,181,.38); transform:translateY(-1px); }}
  .btn-sec {{ padding:9px 14px; background:white; color:{T_BLUE}; border:1.5px solid {GRAY_LINE}; border-radius:6px; font-size:.85rem; font-weight:600; cursor:pointer; font-family:'Open Sans',sans-serif; transition:all .15s; }}
  .btn-sec:hover {{ background:{T_LIGHT}; border-color:{T_BLUE}; }}
  /* Messages */
  .msg-ok   {{ font-size:.8rem; color:{T_GREEN};   padding:7px 0; font-weight:700; }}
  .msg-warn {{ font-size:.8rem; color:{T_ORANGE};  padding:7px 0; font-weight:700; }}
  .msg-info {{ font-size:.8rem; color:{GRAY_TEXT}; padding:7px 0; }}
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
