"""
Hidden in plain sight: cyberbullying of adolescents, global -> India, 2020-2026.
Run:  pip install streamlit pandas plotly
      streamlit run dashboard.py

Reads evidence_ledger.csv (same folder) and nothing else. Every number on screen is
pulled from a row of that file at runtime; every row carries a clickable source link,
its location in the source and the exact quote it was checked against. Figures
calculated here (differences, ratios, shares, roundings) are labelled "computed" and
their formula and input rows are shown in the evidence block beneath them.

The page follows the Stanford d.school design-thinking modes as a story:
Empathize -> Define -> Ideate -> Prototype -> Test, then a close and an annexure.
"""
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hidden in plain sight", layout="wide")

# Fixed categorical order (validated CVD-safe on adjacent pairs); never cycled.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE, ORANGE, GREY = PALETTE[0], PALETTE[1], "#a3a29c"
# Full-width charts/tables: newer Streamlit (incl. the stlite build on GitHub Pages) uses width="stretch".
_ST = tuple(int(p) for p in st.__version__.split(".")[:2])
FULL = {"width": "stretch"} if _ST >= (1, 50) else {"use_container_width": True}
CSV = Path(__file__).with_name("evidence_ledger.csv")
YEARS = range(2020, 2027)
# The source list supplied for this dashboard; anything else in the ledger was added from own research.
PROVIDED = {
    "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287039&lang=1&reg=1",
    "https://ncpcr.gov.in/public/viewPdf/17833306256a4b774107204_175576490268a6d8a6c5bdf_posco2012.pdf",
    "https://ncpcr.gov.in/public/viewPdf/17834007756a4c8947aee09_175585670368a83f3faec2c_userhandbook.pdf",
    "https://ncpcr.gov.in/public/viewPdf/17834954586a4dfb2284359_a.pdf",
    "https://ncpcr.gov.in/public/viewPdf/17835058926a4e23e4473f2_b.pdf",
    "https://ncpcr.gov.in/public/viewPdf/17835062196a4e252b6e7ad_c.pdf",
    "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2149788&reg=48&lang=2",
    "https://www.unicef.org/innocenti/reports/global-kids-online-growing-connected-world",
    "https://www.who.int/europe/publications/i/item/9789289060929",
    "https://www.ncrb.mha.gov.in/uploads/files/2CrimeinIndia2023PartII2.pdf",
    "https://www.unicef.org/innocenti/reports/childhood-digital-world",
    "https://www.unicef.org/innocenti/media/7011/file/GKO-Comparative-Report-2019.pdf",
    "https://data-browser.hbsc.org/measure/cyberbullying-bullying-others/#chart",
    "https://iris.who.int/server/api/core/bitstreams/1d8d101a-e414-4635-a1dc-5cb50ed2b5da/content",
    "https://www.unesco.org/reports/gem-report/en/2024-monitoringsdg4",
    "https://www.weprotect.org/wp-content/uploads/Global-Threat-Asssesment-2023-Press-Release.pdf",
    "https://www.bioinformation.net/021/973206300211380.pdf",
}

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {padding: 2.2rem 2.2rem 1.8rem; border-radius: 18px; margin-bottom: 1.2rem;
       background: linear-gradient(135deg, rgba(42,120,214,.14), rgba(42,120,214,.02));
       border: 1px solid rgba(42,120,214,.28);}
.kicker {text-transform: uppercase; letter-spacing: .09em; font-size: .78rem; font-weight: 700; opacity: .75;}
.hero h1 {font-size: 2.5rem; line-height: 1.12; margin: .35rem 0 .7rem; padding: 0;}
.hero p {font-size: 1.12rem; line-height: 1.55; max-width: 54rem; margin: 0;}
.modes {display: flex; gap: .6rem; flex-wrap: wrap; margin: .4rem 0 .6rem;}
.modes div {flex: 1 1 170px; border: 1px solid rgba(128,128,128,.28); border-radius: 12px;
            padding: .75rem .85rem; font-size: .9rem; line-height: 1.4;}
.modes b {display: block; font-size: 1rem; margin-bottom: .15rem;}
.modes span {color: #2a78d6; font-weight: 700; margin-right: .3rem;}
.mode {display: inline-flex; align-items: center; gap: .55rem; margin-top: 3rem;
       text-transform: uppercase; letter-spacing: .09em; font-size: .8rem; font-weight: 700; color: #2a78d6;}
.mode i {font-style: normal; display: inline-grid; place-items: center; width: 1.7rem; height: 1.7rem;
         border-radius: 50%; background: #2a78d6; color: #fff;}
.lede {font-size: 1.15rem; line-height: 1.55; opacity: .88; margin: -.3rem 0 1rem; max-width: 52rem;}
.stat {border: 1px solid rgba(128,128,128,.28); border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: .3rem;}
.stat .big {font-size: 2.3rem; font-weight: 700; line-height: 1.1;}
.stat .lbl {font-weight: 600; margin: .3rem 0 .2rem; line-height: 1.35;}
.stat .mean {font-size: .9rem; opacity: .8; line-height: 1.45;}
.ev {font-size: .8rem; line-height: 1.55; border-left: 3px solid rgba(128,128,128,.45);
     padding: .35rem .75rem; margin: .1rem 0 .25rem;}
.ev .h {font-weight: 700; text-transform: uppercase; letter-spacing: .07em; font-size: .7rem; margin-right: .35rem;}
.ev a {color: #2a78d6; font-weight: 600; text-decoration: underline; text-underline-offset: 2px;}
.ev .rel {margin-top: .25rem;}
.ev .muted {opacity: .8;}
.callout {border-radius: 14px; padding: 1.1rem 1.35rem; margin: .6rem 0 .3rem; font-size: 1.05rem; line-height: 1.6;
          background: rgba(235,104,52,.08); border: 1px solid rgba(235,104,52,.38);}
.callout .kicker {color: #c4521f; margin-bottom: .3rem;}
.heard {border-radius: 14px; padding: 1rem 1.3rem; margin: .8rem 0 .3rem; line-height: 1.6;
        background: rgba(42,120,214,.07); border: 1px solid rgba(42,120,214,.25);}
.hmw {border: 1px solid rgba(128,128,128,.28); border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: .8rem;}
.hmw .q {font-size: 1.08rem; font-weight: 650; line-height: 1.4; margin-bottom: .45rem;}
.hmw .b {font-size: .9rem; opacity: .85; line-height: 1.45;}
.hmw .r {font-size: .78rem; margin-top: .4rem; line-height: 1.5;}
.hmw .r a {color: #2a78d6;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data + lookups
def _check(v):
    if "PDF text" in v:
        return "✔ PDF-matched"
    if "web page text" in v:
        return "✔ web-page-matched"
    if "scanned" in v:
        return "◉ scan viewed"
    return "✖ not verified"


@st.cache_data
def load(mtime):
    d = pd.read_csv(CSV)
    d["metric"] = d.metric.str.strip()
    for c in ("scope", "geography", "category", "source", "source_url", "landing_url", "published", "unit", "location",
              "verification", "anchor", "note"):
        d[c] = d[c].fillna("").astype(str)
    d["checked"] = d.verification.map(_check)
    d["in_window"] = d.data_year.between(2020, 2026)
    return d


ledger = load(CSV.stat().st_mtime)  # reloads when the CSV changes
df = ledger[ledger.in_window & ledger.value.notna()].copy()  # strict window: data-collection year 2020-2026
SOURCES = (ledger.groupby("source", sort=False)
           .agg(url=("source_url", "first"), landing=("landing_url", "first"), published=("published", "first"),
                rows=("id", "count"))
           .reset_index())


def src(prefix):
    """One source by the start of its name (for 'related evidence' links)."""
    s = SOURCES[SOURCES.source.str.startswith(prefix)]
    if len(s) != 1:
        st.error(f"Source lookup returned {len(s)} rows for: {prefix}")
        st.stop()
    return s.iloc[0]


def rows(*metrics, year=None, geo=None, frame=None):
    """All rows for these exact metric names. Fails loudly if any is missing."""
    q = (df if frame is None else frame)
    q = q[q.metric.isin(metrics)]
    if year is not None:
        q = q[q.data_year == year]
    if geo is not None:
        q = q[q.geography == geo]
    missing = set(metrics) - set(q.metric)
    if missing:
        st.error(f"Ledger has no row for: {sorted(missing)} / {year} / {geo}")
        st.stop()
    return q


def row(metric, year=None, geo=None, frame=None):
    q = rows(metric, year=year, geo=geo, frame=frame)
    if len(q) != 1:
        st.error(f"Ledger lookup returned {len(q)} rows for: {metric} / {year} / {geo}")
        st.stop()
    return q.iloc[0]


def v(metric, year=None, geo=None, frame=None):
    return row(metric, year, geo, frame).value


def rid(*keys):
    """Ledger IDs for (metric[, year[, geo]]) tuples or bare metric names, joined for display."""
    return ", ".join(row(*(k if isinstance(k, tuple) else (k,))).id for k in keys)


def as_frame(*items):
    """Combine rows (Series) and frames into one evidence frame, taken straight from the ledger."""
    ids = set()
    for i in items:
        ids.update([i.id] if isinstance(i, pd.Series) else i.id)
    return ledger[ledger.id.isin(ids)]


def id_ranges(ids):
    nums = sorted(int(i[1:]) for i in ids)
    out, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        out.append(f"E{start:03d}" if start == prev else f"E{start:03d}–E{prev:03d}")
        if n is not None:
            start = prev = n
    return ", ".join(out)


def link(text, url):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener">{escape(text)}</a>'


# ---------------------------------------------------------------- presentation helpers
def ev(frame, computed=(), note=None, related=()):
    """Evidence block under a chart: clickable sources, locations, data years and checks; every row on demand.
    `related` names extra 2025-26 sources (by name prefix) that give context for this chart."""
    frame = frame.drop_duplicates("id").sort_values("id")
    lines = []
    for name, g in frame.groupby("source", sort=False):
        locs = "; ".join(sorted(g.location.unique()))
        yrs = ", ".join(str(int(y)) for y in sorted(g.data_year.dropna().unique()))
        url, landing = g.source_url.iloc[0], g.landing_url.iloc[0]
        extra = f' · {link("publisher page", landing)}' if landing and landing != url else ""
        lines.append(f"{link(name, url)} · {escape(locs)}{' · data year ' + yrs if yrs else ''}{extra}")
    checks = [f"{k} {n}" for k, n in frame.checked.value_counts().items()]
    if computed:
        checks.append(f"{len(computed)} computed here (formula in drop-down)")
    rel = ""
    if related:
        items = [src(p) for p in related]
        rel = ('<div class="rel"><span class="h">Related 2025–26 evidence</span>'
               + " · ".join(f"{link(s.source, s.url)} <span class='muted'>({escape(s.published)})</span>" for s in items) + "</div>")
    st.markdown(f'<div class="ev"><span class="h">Evidence</span>{len(frame)} ledger row'
                f'{"s" if len(frame) != 1 else ""} ({id_ranges(frame.id)})<br>' + "<br>".join(lines)
                + '<br><span class="muted">' + " · ".join(checks) + "</span>" + rel + "</div>", unsafe_allow_html=True)
    with st.expander("Open the evidence: each number, its link, where it sits in the source, and the exact quote"):
        t = frame[["id", "metric", "value", "unit", "geography", "data_year", "source", "source_url", "location", "checked", "anchor", "note"]]
        st.dataframe(t, hide_index=True, **FULL, column_config={
            "id": "Row", "metric": "What it measures", "value": "Value", "unit": "Unit", "geography": "Where",
            "data_year": st.column_config.NumberColumn("Data year", format="%d"), "source": "Source",
            "source_url": st.column_config.LinkColumn("Link", display_text="open source"),
            "location": "Location in source", "checked": "Check", "anchor": "Exact quote matched in source", "note": "Note"})
        if computed:
            st.markdown("**Computed by this dashboard (not stated in any source):**")
            for label, formula in computed:
                st.markdown(f"- {label}: `{formula}`")
        if note:
            st.caption(note)


def chapter(n, mode, anchor, title, lede):
    st.markdown(f'<div class="mode"><i>{n}</i>{mode}</div>', unsafe_allow_html=True)
    st.header(title, anchor=anchor)
    st.markdown(f'<p class="lede">{lede}</p>', unsafe_allow_html=True)


def stat(big, label, meaning=""):
    st.markdown(f'<div class="stat"><div class="big">{big}</div><div class="lbl">{label}</div>'
                f'<div class="mean">{meaning}</div></div>', unsafe_allow_html=True)


def style(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=50, t=30, b=10), legend_title_text="",
                      bargap=0.3, bargroupgap=0.08, font=dict(size=13),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    fig.update_traces(marker_line_width=0, cliponaxis=False, selector=dict(type="bar"))
    return fig


def icon_array(k, total=100, color=BLUE):
    """100 dots, k filled: a whole classroom-style picture of a share."""
    cols = 10
    fig = go.Figure(go.Scatter(
        x=[i % cols for i in range(total)], y=[-(i // cols) for i in range(total)], mode="markers",
        marker=dict(size=20, color=[color if i < k else "rgba(128,128,128,0.28)" for i in range(total)]),
        hoverinfo="skip"))
    fig.update_layout(height=270, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, range=[-0.7, cols - 0.3])
    fig.update_yaxes(visible=False, scaleanchor="x", range=[-(total // cols) + 0.3, 0.7])
    return fig


def plot(fig, height=380, top=None):
    fig = style(fig, height)
    if top:  # extra room above facet titles so the legend never overlaps them
        fig.update_layout(margin_t=top, legend_y=1 + top / height)
    st.plotly_chart(fig, **FULL, config={"displayModeBar": False})


# ---------------------------------------------------------------- every number used in the story
# Global: HBSC 2021/22 (+ 2018 baselines, outside the window, from the WHO release)
HB16 = row("Cyberbullied (victim), all, body text")
HB15 = row("Cyberbullied (victim), all, key-findings text")
HB_GENDER = rows("Cyberbullied (victim), all, body text", "Cyberbullied (victim), boys", "Cyberbullied (victim), girls",
                 "Cyberbullying others, all", "Cyberbullying others, boys", "Cyberbullying others, girls", year=2022)
vb, vg = v("Cyberbullied (victim), boys", 2022), v("Cyberbullied (victim), girls", 2022)
pa, pb, pg = v("Cyberbullying others, all"), v("Cyberbullying others, boys", 2022), v("Cyberbullying others, girls", 2022)
BASE18 = rows("Cyberbullied (victim), boys", "Cyberbullied (victim), girls", "Cyberbullying others, boys",
              "Cyberbullying others, girls", year=2018, frame=ledger)
vb18, vg18, pb18, pg18 = (BASE18.set_index("metric").value[m] for m in
                          ("Cyberbullied (victim), boys", "Cyberbullied (victim), girls", "Cyberbullying others, boys", "Cyberbullying others, girls"))
AGE_LABELS = {"Cyberbullying others, all 13y": "Age 13, all", "Cyberbullying others, 15y girls": "Age 15, girls",
              "Cyberbullying others, 15y boys": "Age 15, boys",
              "Cyberbullying others, highest cell among girls": "Highest among girls: Romania, age 13",
              "Cyberbullying others, highest cell": "Highest anywhere: Lithuania, boys age 15"}
HB_AGE = rows(*AGE_LABELS)
p13, p15g, p15b = v("Cyberbullying others, all 13y"), v("Cyberbullying others, 15y girls"), v("Cyberbullying others, 15y boys")
LT, RO = row("Cyberbullying others, highest cell"), row("Cyberbullying others, highest cell among girls")
HB_N = row("Young people surveyed (HBSC 2021/22)")

# Global: PISA 2025
PISA3 = row("Cyberbullied a few times a month or more (upsetting information published online without consent)")
PISA59, PISA48 = row("Science score gap, cyberbullied vs other students"), row("Science score gap after socio-economic adjustment")
PISA90 = row("Cyberbullied students also bullied in other ways at least monthly")
PISA82 = row("Systems where cyberbullying victims scored lower in science (of 86)")

# Global: UNICEF Disrupting Harm (online bullying and mental health)
OUTCOMES = {"anxiety": "Anxiety", "self-harm": "Self-harm", "suicidal thoughts/behaviours": "Suicidal thoughts/behaviours"}
IMPACT = df[df.metric.str.startswith("Online bullying ->") & df.metric.str.contains("std. SEM")].copy()
IMPACT["outcome"] = IMPACT.metric.str.extract(r"-> (.+?), std")[0].map(OUTCOMES)
IMPACT["result"] = IMPACT.metric.str.contains("not significant").map({True: "Could be chance (not significant)",
                                                                      False: "Solid link (significant, p<.001)"})
SIG = IMPACT[IMPACT.result.str.startswith("Solid")].groupby("outcome").size()
N_CTRY = IMPACT.groupby("outcome").size()
n_anx, n_sh, n_su = (int(SIG.get(o, 0)) for o in ("Anxiety", "Self-harm", "Suicidal thoughts/behaviours"))
n_ctry = int(N_CTRY.max())
MED = {o: row(f"Online bullying -> {k}, median std. estimate across countries") for k, o in OUTCOMES.items()}
DH_N = row("Children aged 12-17 surveyed (Disrupting Harm)")
ANX_NS = IMPACT[(IMPACT.outcome == "Anxiety") & IMPACT.result.str.startswith("Could")]

# India: Himachal Pradesh survey (Nov-Dec 2023) vs recorded crime in the same state
HP = "Himachal Pradesh"
HP_ROWS = rows("Cyberbullying victimization, % of all respondents", "Cyberbullying perpetration, % of all respondents",
               "Any bullying victimization (physical or cyber), % of all respondents", year=2023, geo=HP)
HPV = row("Cyberbullying victimization, % of all respondents", 2023, HP)
hpv, hpp = HPV.value, v("Cyberbullying perpetration, % of all respondents", 2023, HP)
hpa = v("Any bullying victimization (physical or cyber), % of all respondents", 2023, HP)
HP_CNT, HP_N = row("Students reporting cyberbullying victimization (count)", 2023, HP), row("School students surveyed, ages 13-17", 2023, HP)
HP_REC23 = row("Cyber crimes against children: TOTAL", 2023, HP)
HP_REC24 = row("Cyber crimes against children: TOTAL", 2024, HP)

# India: recorded cyber crimes against children (cases), 2020-2024
IA = "India (all)"
CHILD = df[df.metric.str.startswith("Cyber crimes against children:") & (df.geography == IA)].copy()
CHILD["type"] = CHILD.metric.str.replace("Cyber crimes against children: ", "", regex=False)
CHILD_TOT = CHILD[CHILD.type == "TOTAL"].sort_values("data_year")
TOT = "Cyber crimes against children: TOTAL"
c20, c23, c24 = (v(TOT, y, IA) for y in (2020, 2023, 2024))
SB24 = row("Cyber crimes against children: Cyber stalking/bullying", 2024, IA)
SB23 = row("Cyber crimes against children: Cyber stalking/bullying", 2023, IA)
CSAM24 = row("Cyber crimes against children: Sexually explicit material depicting children (CSAM)", 2024, IA)
T24 = row(TOT, 2024, IA)
sb24, csam24, tot24 = SB24.value, CSAM24.value, T24.value
STATES24 = df[(df.metric == TOT) & (df.data_year == 2024) & (df.geography != IA)].copy()

# India: what happens to recorded cyber stalking/bullying cases (women and children combined)
SB = "Cyber stalking/bullying of women/children"
JUST = {k: row(f"{SB}: {k}", 2024) for k in ("cases for trial", "trials completed", "cases convicted", "pending trial at year end",
                                             "conviction rate", "court pendency", "cases for police investigation",
                                             "cases charge-sheeted", "charge-sheeting rate", "police pendency")}
JUST23 = {k: row(f"{SB}: {k}", 2023) for k in ("cases for trial", "cases convicted", "conviction rate", "court pendency")}

# India: all-age series and response measures
ALLAGE = df[df.source.str.startswith("PIB, MHA Lok Sabha reply: National") & (df.category == "Recorded crime")]
ALL_TOT = ALLAGE[ALLAGE.metric == "TOTAL cyber crime cases (all ages, all types)"].sort_values("data_year")
b0, b4 = ALL_TOT.value.iloc[0], ALL_TOT.value.iloc[-1]
CCPWC, LABS = row("CCPWC scheme funds released to States/UTs"), row("States/UTs with cyber forensic-cum-training labs (CCPWC)")
TRAINED, HYGIENE = row("Police, judicial officers and prosecutors trained (CCPWC)"), row("Students given cyber hygiene training by I4C (NCC, NSS, NYKS)")
BIO48 = row("Students with poor cyberbullying knowledge, before video teaching")
BIO10 = row("Students with poor cyberbullying knowledge, after video teaching")
BIO60 = row("Students with good cyberbullying knowledge, after video teaching")

# Global: severe online harms and bullying trends
SX0, SX1 = row("Sextortion reports, 2021 baseline"), row("Sextortion reports, 2022")
IMG, CSAMR = row("Rise in self-generated imagery of 7-10 year olds, 2020-2022"), row("CSAM reports rise since 2019")
NCMEC = row("Child sexual abuse reports worldwide (NCMEC)")
GROOM19, GROOM45 = row("Time for gaming-platform chats to escalate to high-risk grooming"), row("Average grooming time on social gaming platforms")
KNOWN = row("Online abuse cases where the perpetrator was likely known to the child (Disrupting Harm)")
UG = row("Countries where bullying rose >=2 pp for girls, 2018-2022 (of 66)")
UB = row("Countries where bullying rose >=2 pp for boys, 2018-2022 (of 66)")

class30 = 30 * HB16.value / 100
dots_hb, dots_hp = round(HB16.value), round(hpv)
n_ok = int(ledger.checked.str.startswith("✔").sum())


def plus(r):
    return "+" if "+" in r.unit else ""


# ---------------------------------------------------------------- sidebar: the map of the story
with st.sidebar:
    st.markdown("### The story")
    st.markdown("[Start: the gap](#start)  \n[1 · Empathize](#empathize)  \n[2 · Define](#define)  \n"
                "[3 · Ideate](#ideate)  \n[4 · Prototype](#prototype)  \n[5 · Test](#test)  \n"
                "[The story in one breath](#close)  \n[Annexure: evidence & sources](#annexure)")
    st.divider()
    st.markdown("### The evidence base")
    st.markdown(f"**{len(ledger)}** ledger rows from **{len(SOURCES)}** sources, each with a clickable link.  \n"
                f"✔ **{n_ok}** quotes matched word-for-word in the source PDF or web page  \n"
                f"**{len(df)}** numbers fall in the 2020–2026 window used for the charts.")
    st.divider()
    st.markdown("### Words used here")
    st.markdown(
        "**Cyberbullying**: being repeatedly hurt, threatened or humiliated through phones, apps or the internet.  \n"
        "**Perpetration**: doing the bullying.  \n"
        "**CSAM**: child sexual abuse material (images or videos).  \n"
        "**Sextortion**: threatening to share someone's intimate images unless they comply.  \n"
        "**Charge-sheet**: police report sending a case to court.  \n"
        "**Conviction rate**: convictions as a share of trials completed.  \n"
        "**Pendency**: cases still unresolved at year end.  \n"
        "**HBSC**: WHO's Health Behaviour in School-aged Children survey.  \n"
        "**NCRB**: India's National Crime Records Bureau, which counts crimes police register.  \n"
        "**PIB**: Press Information Bureau; publishes government replies in Parliament.  \n"
        "**I4C / CCPWC**: India's cyber crime coordination centre and its scheme against cyber crime on women and children.  \n"
        "**PISA**: OECD's international assessment of 15-year-olds.")

# ---------------------------------------------------------------- HERO: the hook
st.markdown(f"""
<div class="hero">
  <div class="kicker">Evidence dashboard · 2020–2026 · from the world to India</div>
  <h1>Hidden in plain sight: cyberbullying of adolescents</h1>
  <p>Across 44 countries, <b>{HB16.value:.0f} in every 100</b> adolescents say they have been cyberbullied, and in
  every one of {n_ctry} countries studied, being bullied online goes hand in hand with self-harm and suicidal thoughts.
  In India, one state's school survey found <b>{HP_CNT.value:,.0f}</b> students who said it happened to them; police in
  that state recorded <b>{HP_REC23.value:,.0f}</b> cyber crimes against children that year. Nationally, of
  <b>{JUST['cases for trial'].value:,.0f}</b> cyber stalking and bullying cases before the courts in 2024,
  <b>{JUST['cases convicted'].value:,.0f}</b> ended in conviction. This page follows that gap step by step.</p>
</div>""", unsafe_allow_html=True)
st.markdown('<a id="start"></a>', unsafe_allow_html=True)

h = st.columns(3)
with h[0]:
    stat(f"{HB16.value:.0f} in 100", "adolescents say they were cyberbullied",
         f"44 countries and regions, ages 11–15, survey year {int(HB16.data_year)}. In a class of 30, about {class30:.0f} students.")
    ev(as_frame(HB16, HB15), computed=[("Students in a class of 30", f"30 × {HB16.value:.0f}% = {class30:.1f} ≈ {class30:.0f}")],
       note="The report's key findings say 15%; its body text says 16%. Both rows are kept, not reconciled.",
       related=["OECD, PISA 2025"])
with h[1]:
    stat(f"{min(n_sh, n_su)} of {n_ctry}", "countries where online bullying is linked to both self-harm and suicidal thoughts",
         f"UNICEF Disrupting Harm survey of {DH_N.value:,.0f} children aged 12–17.")
    ev(as_frame(IMPACT[IMPACT.outcome != "Anxiety"], DH_N),
       computed=[("Countries with a significant link", f"self-harm {n_sh} of {n_ctry}; suicidal thoughts {n_su} of {n_ctry}")])
with h[2]:
    stat(f"{JUST['cases convicted'].value:,.0f} of {JUST['cases for trial'].value:,.0f}",
         "cyber stalking/bullying cases on trial in India ended in conviction in 2024",
         f"{JUST['court pendency'].value:.1f}% were still pending at year end. Covers women and children together.")
    ev(as_frame(JUST["cases convicted"], JUST["cases for trial"], JUST["court pendency"]))

st.markdown("#### How this page is built")
st.markdown("""
<div class="modes">
  <div><b><span>1</span>Empathize</b>Meet the young people: how often it happens, to whom, and what it does to them.</div>
  <div><b><span>2</span>Define</b>Pin down the real problem: what gets counted, what slips through, what reaches a verdict.</div>
  <div><b><span>3</span>Ideate</b>Turn each finding into a "How might we…?" question that invites solutions.</div>
  <div><b><span>4</span>Prototype</b>Draft a scorecard: what to track, and today's starting point.</div>
  <div><b><span>5</span>Test</b>Stress-test the evidence: how sure we are, and what is missing.</div>
</div>""", unsafe_allow_html=True)
st.caption("Under every chart is an Evidence line: clickable source links, the table or page, the data year and how each "
           "number was checked. Open its drop-down for every number, its link and the exact quote. ✔ = quote matched "
           "word-for-word in the source PDF or web page. 'Computed' = calculated here from ledger rows; formula shown. "
           "The full ledger and source list are in the annexure.")

# ================================================================ 1 EMPATHIZE
chapter(1, "Empathize", "empathize", "Meet the young people behind the numbers",
        "Before fixing anything, understand who is hurt, how often, and what it does to them. "
        "Picture each dot below as one student.")

st.subheader(f"{HB16.value:.0f} in every 100 adolescents across 44 countries say they have been cyberbullied")
left, right = st.columns(2)
with left:
    st.markdown(f"**International (HBSC, {int(HB16.data_year)})**: {dots_hb} of 100 dots filled")
    st.plotly_chart(icon_array(dots_hb), **FULL, config={"displayModeBar": False})
    ev(as_frame(HB16, HB_N), computed=[("Dots filled", f"round({HB16.value:.0f}) = {dots_hb} of 100")])
with right:
    st.markdown(f"**India, Himachal Pradesh schools ({int(HPV.data_year)})**: {dots_hp} of 100 dots filled")
    st.plotly_chart(icon_array(dots_hp, color=ORANGE), **FULL, config={"displayModeBar": False})
    ev(as_frame(HPV, HP_N), computed=[("Dots filled", f"round({hpv:.2f}) = {dots_hp} of 100")])
st.caption("Two different surveys with different questions, ages and places. Read each picture on its own, "
           "not as India versus the world.")

st.subheader("The newest global data: a stricter measure finds it rarer, but it costs students dearly")
st.markdown(f"PISA 2025 asked 15-year-olds a narrower question: had upsetting information about them been published "
            f"online without their consent, at least a few times a month? On that strict measure, {PISA3.value:.0f}% said "
            f"yes on average across OECD countries. Those students scored far lower, and most were bullied in other ways too.")
p = st.columns(3)
with p[0]:
    stat(f"{PISA3.value:.0f}%", "of 15-year-olds cyberbullied at least a few times a month", "OECD average, PISA 2025.")
with p[1]:
    stat(f"−{PISA59.value:.0f} pts", "lower science score for cyberbullied students",
         f"{PISA48.value:.0f} points lower after accounting for background; lower in {PISA82.value:.0f} of 86 systems.")
with p[2]:
    stat("9 in 10", "cyberbullied students were also bullied in other ways at least monthly")
ev(as_frame(PISA3, PISA59, PISA48, PISA82, PISA90), note="India did not take part in PISA 2025. The PISA item is stricter "
   "(a few times a month or more) than HBSC's (at least once or twice in the past couple of months), so the two are not compared.")

st.subheader("Girls and boys are bullied almost equally, boys more often do the bullying, and both have risen")
st.markdown(f"About {vb:.0f}% of boys and {vg:.0f}% of girls were cyberbullied in 2022, up from {vb18:.0f}% and "
            f"{vg18:.0f}% in 2018. {pb:.0f}% of boys said they had cyberbullied someone, against {pg:.0f}% of girls "
            f"(up from {pb18:.0f}% and {pg18:.0f}%).")
g = HB_GENDER.copy()
g["role"] = g.metric.str.startswith("Cyberbullied (victim)").map({True: "Was cyberbullied", False: "Cyberbullied others"})
g["group"] = g.metric.str.extract(r"(all|boys|girls)")[0].str.capitalize()
fig = px.bar(g, x="role", y="value", color="group", barmode="group", text="value",
             category_orders={"group": ["All", "Boys", "Girls"], "role": ["Was cyberbullied", "Cyberbullied others"]},
             color_discrete_sequence=PALETTE, labels={"value": "% of adolescents", "role": ""},
             hover_data={"id": True, "location": True})
fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
plot(fig, 360)
ev(as_frame(g, BASE18), note="2018 rows are a pre-window baseline from the WHO/Europe release, used only for the 'up from' comparison.",
   related=["OECD, PISA 2025"])

st.subheader(f"Bullying others peaks in the early teens, and can reach {LT.value:.0f}% in some places")
st.markdown(f"Across the survey, bullying others online is most common at age 13 ({p13:.0f}%). By 15, boys "
            f"({p15b:.0f}%) are almost twice as likely as girls ({p15g:.0f}%) to do it. The highest figures are "
            f"{LT.value:.0f}% among 15-year-old boys in Lithuania and {RO.value:.0f}% among 13-year-old girls in Romania.")
a = HB_AGE.copy()
a["label"] = a.metric.map(AGE_LABELS)
a["highlight"] = a.metric.str.contains("highest").map({True: "Highest cell", False: "Survey average"})
fig = px.bar(a.sort_values("value"), x="value", y="label", orientation="h", text="value", color="highlight",
             color_discrete_map={"Survey average": BLUE, "Highest cell": ORANGE},
             labels={"value": "% who cyberbullied others", "label": ""}, hover_data={"id": True, "anchor": True})
fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
plot(fig, 300)
ev(a, computed=[("'Almost twice'", f"{p15b:.0f} ÷ {p15g:.0f} = {p15b / p15g:.2f}")])

st.subheader("In India, the clearest view comes from one state's classrooms")
st.markdown(f"A survey of {HP_N.value:,.0f} school students aged 13–17 in Himachal Pradesh (Nov–Dec 2023) found "
            f"**{hpv:.2f}%** had been cyberbullied and **{hpp:.2f}%** had cyberbullied someone else. Counting physical "
            f"bullying too, **{hpa:.1f}%** had been bullied in some way.")
hp = HP_ROWS.copy()
hp["label"] = hp.metric.str.replace(", % of all respondents", "", regex=False)
fig = px.bar(hp.sort_values("value"), x="value", y="label", orientation="h", text="value",
             color_discrete_sequence=[ORANGE], labels={"value": "% of students", "label": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
plot(fig, 240)
ev(as_frame(hp, HP_N), note="One state, school-going students only; not a national estimate.")

st.subheader("What it does to them: online bullying travels with anxiety, self-harm and suicidal thoughts")
st.markdown(f"Each bar shows how strongly being bullied online is connected to a mental-health outcome, on a standard "
            f"scale where 0 means no connection. **Blue** means the link is statistically solid; **grey** means it could "
            f"be chance. The link with **self-harm** is solid in {n_sh} of {n_ctry} countries and with **suicidal thoughts** "
            f"in {n_su} of {n_ctry}; with **anxiety**, in {n_anx} of {n_ctry}. Across all 21 countries studied, the median "
            f"strength was {MED['Anxiety'].value:.2f} for anxiety, {MED['Self-harm'].value:.2f} for self-harm and "
            f"{MED['Suicidal thoughts/behaviours'].value:.2f} for suicidal thoughts. This shows the two go together; it does "
            f"not prove one causes the other.")
order = IMPACT[IMPACT.outcome == "Self-harm"].sort_values("value").geography.tolist()
fig = px.bar(IMPACT, x="value", y="geography", orientation="h", color="result", facet_col="outcome",
             category_orders={"geography": order, "outcome": list(OUTCOMES.values())},
             color_discrete_map={"Solid link (significant, p<.001)": BLUE, "Could be chance (not significant)": GREY},
             labels={"value": "strength of link", "geography": ""}, hover_data={"id": True, "anchor": True})
fig.for_each_annotation(lambda an: an.update(text=f"<b>{an.text.split('=')[-1]}</b>"))
plot(fig, 480, top=70)
ev(as_frame(IMPACT, *MED.values(), DH_N), related=["UNICEF Innocenti, Childhood in a Digital World (2025): report"],
   note="The report's text says the anxiety link held in all Disrupting Harm countries, but its own Table A30 shows "
        f"{len(ANX_NS)} countries as not significant ({', '.join(ANX_NS.geography)}). The chart follows the table.")

st.markdown(f"""
<div class="heard"><div class="kicker">What we heard</div>
Cyberbullying is common: {HB16.value:.0f} in 100 adolescents internationally, about {class30:.0f} in a class of 30, and it
rose between 2018 and 2022. It touches girls and boys alike, while boys more often do it. It peaks in the early teens.
And it is not harmless: it travels with self-harm and suicidal thoughts in every country studied, and with a
{PISA59.value:.0f}-point drop in science scores.
</div>""", unsafe_allow_html=True)

# ================================================================ 2 DEFINE
chapter(2, "Define", "define", "Define the real problem",
        "What happens between a child being bullied online and anyone doing something about it? The evidence points to "
        "a chain that breaks at every link: few incidents are recorded, and few recorded cases reach a verdict.")

st.subheader("The reporting gap, in one state: what students say versus what police recorded")
left, mid, right = st.columns([4, 5, 4])
with left:
    stat(f"{HP_CNT.value:,.0f}", f"of {HP_N.value:,.0f} surveyed students said they had been cyberbullied",
         f"Himachal Pradesh school survey, Nov–Dec {int(HPV.data_year)} ({hpv:.2f}%).")
    ev(as_frame(HP_CNT, HP_N, HPV))
with mid:
    st.markdown(f"""
<div class="callout" style="margin-top:0"><div class="kicker">Read with care</div>
These numbers measure different things: one is a survey of a sample of students, the other is every cyber crime against
a child that police registered in the state. One cannot be divided by the other. But in the same state and the same year,
{HP_CNT.value:,.0f} students in a single survey said they were cyberbullied, while police recorded {HP_REC23.value:,.0f}
cyber crimes against children of any kind ({HP_REC24.value:,.0f} in 2024).
</div>""", unsafe_allow_html=True)
with right:
    stat(f"{HP_REC23.value:,.0f}", "cyber crimes against children recorded by police in Himachal Pradesh, 2023",
         f"All types. NCRB, Table 9A.11. {HP_REC24.value:,.0f} in 2024.")
    ev(as_frame(HP_REC23, HP_REC24))

st.subheader(f"What the records capture is mostly abuse imagery: {csam24 / tot24:.0%} of child cyber crime cases in 2024")
st.markdown(f"Of {tot24:,.0f} cyber crimes against children recorded in India in 2024, {csam24:,.0f} involved sexually "
            f"explicit material depicting children. Cyber stalking or bullying made up {sb24:,.0f} cases ({sb24 / tot24:.1%}), "
            f"up from {SB23.value:,.0f} in 2023.")
n = CHILD[(CHILD.data_year == 2024) & (CHILD.type != "TOTAL")].copy()
n["highlight"] = n.type.eq("Cyber stalking/bullying").map({True: "Cyber stalking/bullying", False: "Other categories"})
fig = px.bar(n.sort_values("value"), x="value", y="type", orientation="h", text="value", color="highlight",
             color_discrete_map={"Cyber stalking/bullying": ORANGE, "Other categories": BLUE},
             labels={"value": "recorded cases, 2024", "type": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
plot(fig, 300)
ev(as_frame(n, T24, SB23), computed=[("CSAM share", f"{csam24:,.0f} ÷ {tot24:,.0f} = {csam24 / tot24:.1%}"),
                                     ("Stalking/bullying share", f"{sb24:,.0f} ÷ {tot24:,.0f} = {sb24 / tot24:.1%}")],
   related=["PIB, MHA Lok Sabha reply: National"])

st.subheader(f"Recorded cyber crimes against children: {c20:,.0f} in 2020, {tot24:,.0f} in 2024")
st.markdown(f"Cases rose every year to a peak of {c23:,.0f} in 2023, then dipped to {tot24:,.0f} in 2024. "
            f"Abuse imagery dominates every year; stalking and bullying stay a thin slice.")
c = CHILD[CHILD.type != "TOTAL"].copy()
type_order = c.groupby("type").value.sum().sort_values(ascending=False).index.tolist()
fig = px.bar(c, x="data_year", y="value", color="type", barmode="stack", category_orders={"type": type_order},
             color_discrete_sequence=PALETTE, labels={"value": "recorded cases", "data_year": "year"},
             hover_data={"id": True, "source": True})
fig.update_xaxes(dtick=1)
for _, r in CHILD_TOT.iterrows():
    fig.add_annotation(x=r.data_year, y=r.value, text=f"<b>{r.value:,.0f}</b>", showarrow=False, yshift=12)
plot(fig, 440)
ev(CHILD, computed=[("Growth 2020→2024", f"{tot24:,.0f} ÷ {c20:,.0f} = {tot24 / c20:.2f}x")],
   note="One NCRB series with the same six categories: 2020–2022 from the PIB 2025 reply, 2023 and 2024 from Crime in India "
        "Table 9A.11. All values are cases registered.")

st.subheader("Where cases are recorded: a handful of states, and almost none in Himachal Pradesh")
s24 = STATES24.sort_values("value")
s24["highlight"] = s24.geography.eq(HP).map({True: "Himachal Pradesh", False: "Top states"})
fig = px.bar(s24, x="value", y="geography", orientation="h", text="value", color="highlight",
             color_discrete_map={"Top states": BLUE, "Himachal Pradesh": ORANGE},
             labels={"value": "recorded cyber crimes against children, 2024", "geography": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
plot(fig, 300)
ev(s24, note="NCRB notes that states should not be compared purely on crime figures; differences reflect reporting and "
   "registration as well as incidence.")

st.subheader(f"Even recorded cases rarely reach a verdict: {JUST['cases convicted'].value:,.0f} convictions from "
             f"{JUST['cases for trial'].value:,.0f} cases on trial")
st.markdown(f"For cyber stalking and bullying of women and children, police sent {JUST['charge-sheeting rate'].value:.1f}% "
            f"of the cases they disposed of to court in 2024. But courts completed only {JUST['trials completed'].value:,.0f} "
            f"trials out of {JUST['cases for trial'].value:,.0f} cases on their books; {JUST['cases convicted'].value:,.0f} "
            f"ended in conviction ({JUST['conviction rate'].value:.1f}% of completed trials) and "
            f"{JUST['pending trial at year end'].value:,.0f} ({JUST['court pendency'].value:.1f}%) were still pending. "
            f"In 2023 it was {JUST23['cases convicted'].value:,.0f} convictions from {JUST23['cases for trial'].value:,.0f}.")
f = pd.DataFrame([(k, JUST[key].value, JUST[key].id) for k, key in [
    ("Cases on trial during the year", "cases for trial"), ("Still pending at year end", "pending trial at year end"),
    ("Trials completed", "trials completed"), ("Ended in conviction", "cases convicted")]], columns=["stage", "value", "id"])
f["highlight"] = f.stage.eq("Ended in conviction").map({True: "Conviction", False: "Court stage"})
fig = px.bar(f.iloc[::-1], x="value", y="stage", orientation="h", text="value", color="highlight",
             color_discrete_map={"Court stage": BLUE, "Conviction": ORANGE},
             labels={"value": "cases, cyber stalking/bullying of women & children, 2024", "stage": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
plot(fig, 280)
ev(as_frame(*JUST.values(), *JUST23.values()), note="NCRB reports this crime head for women and children together; a "
   "child-only figure is not published.", related=["PIB, MHA Lok Sabha reply: National"])

st.subheader(f"Meanwhile, all cyber crime in India grew {b4 / b0:.2f} times in five years")
st.markdown(f"Across all ages and crime types, recorded cyber crime cases went from {b0:,.0f} in 2020 to "
            f"{b4:,.0f} in 2024. These counts include adults; they show the wider online setting children are growing up in.")
fig = px.line(ALL_TOT, x="data_year", y="value", markers=True, color_discrete_sequence=[BLUE],
              labels={"value": "recorded cases, all ages", "data_year": "year"}, hover_data={"id": True})
fig.update_traces(line_width=2, marker_size=9)
fig.update_xaxes(dtick=1)
fig.update_yaxes(rangemode="tozero")
for _, r in ALL_TOT.iloc[[0, -1]].iterrows():
    fig.add_annotation(x=r.data_year, y=r.value, text=f"{r.value:,.0f}", showarrow=False, yshift=14)
plot(fig, 320)
ev(ALL_TOT, computed=[("Growth 2020→2024", f"{b4:,.0f} ÷ {b0:,.0f} = {b4 / b0:.2f}x")])

st.subheader("Worldwide, the most severe online harms to children are climbing fast")
w = st.columns(3)
with w[0]:
    stat(f"{SX0.value:,.0f} → {SX1.value:,.0f}{plus(SX1)}", "sextortion reports, 2021 → 2022",
         f"About {SX1.value / SX0.value:.0f} times more in one year (computed; 10,000 is a lower bound).")
with w[1]:
    stat(f"+{IMG.value:.0f}%", "rise in self-generated sexual imagery of 7–10 year olds, 2020–2022")
with w[2]:
    stat(f"{NCMEC.value / 1e6:.0f} million+", "child sexual abuse reports worldwide in a year",
         f"+{CSAMR.value:.0f}% since 2019.")
w = st.columns(2)
with w[0]:
    stat(f"{GROOM19.value:.0f} seconds", "for a chat on a social gaming platform to escalate into high-risk grooming",
         f"Average grooming time: {GROOM45.value:.0f} minutes.")
with w[1]:
    stat(f"{KNOWN.value:.0f}%", "of online abuse cases: the perpetrator was likely known to the child")
ev(as_frame(SX0, SX1, IMG, NCMEC, CSAMR, GROOM19, GROOM45, KNOWN),
   computed=[("Sextortion multiple", f"{SX1.value:,.0f} ÷ {SX0.value:,.0f} = {SX1.value / SX0.value:.1f}x (lower bound)")])
u = st.columns(2)
with u[0]:
    stat(f"{UG.value:.0f} of 66", "countries where bullying of girls rose by 2+ percentage points, 2018–2022")
with u[1]:
    stat(f"{UB.value:.0f} of 66", "countries where bullying of boys rose by 2+ percentage points, 2018–2022")
ev(as_frame(UG, UB), note="UNESCO counts all bullying, not only cyberbullying; it links girls' faster rise to cyberbullying.")

st.markdown(f"""
<div class="callout"><div class="kicker">Point of view: the problem, in one sentence</div>
Adolescents, {HB16.value:.0f} in 100 of whom say they have been cyberbullied, and for whom online bullying travels with
self-harm and suicidal thoughts, <b>need online harm to be noticed, reported, counted and resolved</b>, because in one
Indian state {HP_CNT.value:,.0f} surveyed students said it happened to them while police recorded {HP_REC23.value:,.0f}
cyber crimes against children, and nationally only {JUST['cases convicted'].value:,.0f} of
{JUST['cases for trial'].value:,.0f} cyber stalking and bullying cases on trial ended in conviction.
</div>""", unsafe_allow_html=True)
ev(as_frame(HB16, IMPACT[IMPACT.outcome != "Anxiety"], HP_CNT, HP_REC23, JUST["cases convicted"], JUST["cases for trial"]))

# ================================================================ 3 IDEATE
chapter(3, "Ideate", "ideate", "From evidence to “How might we…?”",
        "Design thinking turns a problem into open questions that invite many answers. Each question below "
        "grows straight out of a finding above. They are starting points for ideas, not conclusions.")

HMW = [
    ("make reporting online bullying as easy for a 13-year-old as sending a message?",
     f"In Himachal Pradesh, {HP_CNT.value:,.0f} surveyed students said they were cyberbullied; police in the state "
     f"recorded {HP_REC23.value:,.0f} cyber crimes against children that year.", as_frame(HP_CNT, HP_REC23)),
    ("make sure the cases that are reported actually reach a verdict?",
     f"Of {JUST['cases for trial'].value:,.0f} cyber stalking/bullying cases on trial in 2024, {JUST['cases convicted'].value:,.0f} "
     f"ended in conviction and {JUST['court pendency'].value:.1f}% were still pending.",
     as_frame(JUST["cases for trial"], JUST["cases convicted"], JUST["court pendency"])),
    ("connect online-safety help with mental-health support?",
     f"Online bullying is linked with self-harm in {n_sh} of {n_ctry} countries and with suicidal thoughts in {n_su} of {n_ctry}.",
     IMPACT[IMPACT.outcome != "Anxiety"]),
    ("reach boys before they start bullying others online?",
     f"{pb:.0f}% of boys versus {pg:.0f}% of girls cyberbullied others (HBSC); at age 15 it is {p15b:.0f}% versus {p15g:.0f}%.",
     as_frame(rows("Cyberbullying others, boys", "Cyberbullying others, girls", year=2022),
              rows("Cyberbullying others, 15y boys", "Cyberbullying others, 15y girls"))),
    ("step in around age 13, when bullying others peaks?",
     f"Cyberbullying others is highest at age 13 ({p13:.0f}%).", rows("Cyberbullying others, all 13y")),
    ("scale school awareness that measurably works?",
     f"In a small Gujarat study, video lessons cut 'poor knowledge' of cyberbullying from {BIO48.value:.0f}% to "
     f"{BIO10.value:.0f}% of students. India has given cyber hygiene training to {HYGIENE.value / 1e5:.0f} lakh+ students, "
     f"but no outcome data is published.", as_frame(BIO48, BIO10, HYGIENE)),
    ("protect children from sextortion and abuse imagery, the fastest-growing harms?",
     f"Sextortion reports went from {SX0.value:,.0f} to {SX1.value:,.0f}{plus(SX1)}; {csam24 / tot24:.0%} of India's recorded "
     f"child cyber crimes in 2024 involved abuse material.", as_frame(SX0, SX1, CSAM24, T24)),
    ("see what is happening across all of India, not only one state?",
     "The only Indian survey of cyberbullying prevalence in the evidence covers Himachal Pradesh.", HP_ROWS),
]
cols = st.columns(2)
for i, (q, because, frame) in enumerate(HMW):
    srcs = " · ".join(link(name, g.source_url.iloc[0]) for name, g in frame.groupby("source", sort=False))
    with cols[i % 2]:
        st.markdown(f'<div class="hmw"><div class="q">How might we {escape(q)}</div>'
                    f'<div class="b"><b>Because:</b> {escape(because)}</div>'
                    f'<div class="r">Evidence rows {id_ranges(frame.id)}: {srcs}</div></div>', unsafe_allow_html=True)
ev(as_frame(*[f for _, _, f in HMW]), computed=[("CSAM share 2024", f"{csam24:,.0f} ÷ {tot24:,.0f} = {csam24 / tot24:.1%}")],
   note="Every row cited by the questions above.", related=["Kharadi et al."])

# ================================================================ 4 PROTOTYPE
chapter(4, "Prototype", "prototype", "A first-draft scorecard for tracking progress",
        "A prototype is a rough first version you can try and improve. Here: a draft set of indicators anyone "
        "working on this could track, with today's starting point from the evidence, and where no starting point exists.")

sh_med = MED["Self-harm"]
SCORE = pd.DataFrame([
    ["How common is it? (international)", "Share of adolescents cyberbullied (HBSC)", f"{HB16.value:.0f}%", int(HB16.data_year), HB16.id, "✔ Baseline exists"],
    ["How common is it? (strict measure)", "Share of 15-year-olds cyberbullied monthly+ (PISA, OECD avg)", f"{PISA3.value:.0f}%", int(PISA3.data_year), PISA3.id, "✔ Baseline exists"],
    ["How common is it? (India, national)", "Share of Indian adolescents cyberbullied", "No figure", "—", "—", "✖ Gap: no national survey"],
    ["How common is it? (India, one state)", "Share of Himachal Pradesh students cyberbullied", f"{hpv:.2f}%", int(HPV.data_year), HPV.id, "◐ One state only"],
    ["Does it reach the system?", "Recorded cyber stalking/bullying cases against children, India", f"{sb24:,.0f}", 2024, SB24.id, "✔ Baseline exists"],
    ["Does it reach the system?", "Bullying share of recorded child cyber crimes, India", f"{sb24 / tot24:.1%} (computed)", 2024, f"{SB24.id}, {T24.id}", "✔ Baseline exists"],
    ["Is it resolved?", "Conviction rate, cyber stalking/bullying (women & children)", f"{JUST['conviction rate'].value:.1f}%", 2024, JUST["conviction rate"].id, "◐ Not child-specific"],
    ["Is it resolved?", "Court pendency, cyber stalking/bullying (women & children)", f"{JUST['court pendency'].value:.1f}%", 2024, JUST["court pendency"].id, "◐ Not child-specific"],
    ["How big is recorded harm?", "Recorded cyber crimes against children, India", f"{tot24:,.0f}", 2024, T24.id, "✔ Baseline exists"],
    ["What does it do?", "Online bullying–self-harm link (median, 21 countries)", f"{sh_med.value:.2f}", int(sh_med.data_year), sh_med.id, "✖ No India estimate"],
    ["Are we preventing it?", "Students given cyber hygiene training (I4C)", f"{HYGIENE.value / 1e5:.0f} lakh+", int(HYGIENE.data_year), HYGIENE.id, "◐ Reach only, no outcomes"],
], columns=["Question", "Indicator", "Starting point", "Data year", "Evidence row", "Status"])
SCORE["Data year"] = SCORE["Data year"].astype(str)
st.table(SCORE[["Question", "Indicator", "Starting point", "Status", "Data year", "Evidence row"]].set_index("Question"))
ev(as_frame(HB16, PISA3, HPV, SB24, T24, JUST["conviction rate"], JUST["court pendency"], sh_med, HYGIENE),
   computed=[("Bullying share", f"{sb24:,.0f} ÷ {tot24:,.0f} = {sb24 / tot24:.1%}")])

st.subheader("Try it yourself: explore India's recorded cyber crime trends")
st.markdown("Pick a series to see how it moved from 2020 to 2024. These are all-age counts, so they include adults.")
opts = sorted(ALLAGE.metric.unique())
metric = st.selectbox("Series", opts, index=opts.index("Cyber stalking/bullying of women & children (combined)"))
ss = ALLAGE[ALLAGE.metric == metric].sort_values("data_year")
fig = px.line(ss, x="data_year", y="value", markers=True, color_discrete_sequence=[BLUE],
              labels={"value": f"recorded {ss.unit.iloc[0]}", "data_year": "year"}, hover_data={"id": True})
fig.update_traces(line_width=2, marker_size=9)
fig.update_xaxes(dtick=1)
fig.update_yaxes(rangemode="tozero")
plot(fig, 320)
f0, f1 = ss.value.iloc[0], ss.value.iloc[-1]
ev(ss, computed=[("Change 2020→2024", f"{f1:,.0f} − {f0:,.0f} = {f1 - f0:+,.0f} ({f1 / f0:.2f}x)")])

st.subheader("What already exists to build on")
r = st.columns(3)
with r[0]:
    stat(f"₹{CCPWC.value:,.2f} cr", "released to States/UTs under the CCPWC scheme", "For cyber forensic labs, consultants and training.")
with r[1]:
    stat(f"{LABS.value:.0f}", "States/UTs with cyber forensic-cum-training labs")
with r[2]:
    stat(f"{TRAINED.value:,.0f}+", "police, judicial officers and prosecutors trained")
ev(as_frame(CCPWC, LABS, TRAINED), note="Reporting routes already in place: the National Cyber Crime Reporting Portal "
   "(cybercrime.gov.in), helpline 1930, and NCPCR's POCSO e-box. The NCPCR policy documents are in the annexure.")

# ================================================================ 5 TEST
chapter(5, "Test", "test", "How sure can we be?",
        "Testing means looking for where the story could break. Here is what this evidence can carry, "
        "and what it cannot.")

left, right = st.columns(2)
with left:
    st.subheader("How each number was checked")
    vs = ledger.copy()
    vs["short"] = vs.source.str.split(r"[,:(]").str[0].str.strip()
    cnt = vs.groupby(["short", "checked"]).size().rename("rows").reset_index()
    fig = px.bar(cnt, x="rows", y="short", color="checked", orientation="h", barmode="stack",
                 color_discrete_map={"✔ PDF-matched": BLUE, "✔ web-page-matched": PALETTE[2], "◉ scan viewed": GREY},
                 labels={"rows": "ledger rows", "short": ""})
    plot(fig, 440)
with right:
    st.subheader("Which years have evidence")
    cov = df.groupby(["scope", "data_year"]).size().unstack(fill_value=0).reindex(columns=YEARS, fill_value=0)
    long = cov.stack().rename("rows").reset_index()
    fig = px.bar(long, x="data_year", y="rows", color="scope", barmode="group",
                 color_discrete_sequence=PALETTE, labels={"data_year": "data year", "rows": "ledger rows"})
    fig.update_xaxes(dtick=1)
    plot(fig, 440)
    yrs25 = ", ".join(sorted(df[df.data_year == 2025].source.str.split(",").str[0].unique()))
    st.caption(f"Zero means no source with data for that year was found. Nothing is estimated. India: NCRB crime counts run "
               f"to 2024 (Crime in India 2024; July 2026 Lok Sabha reply); 2025 and 2026 not yet published. 2025 rows come "
               f"from: {yrs25}. 2026 rows are response measures stated in the July 2026 reply. Pre-2020 baselines and policy "
               f"documents are kept in the annexure, not in the charts.")
ev(ledger, note="Both charts above count ledger rows. The full ledger and source list are in the annexure.")

st.subheader("Where the story could break")
st.markdown(f"""
- **Surveys and police records measure different things.** A survey asks young people what happened; NCRB counts crimes
  that were reported and registered. This page puts them side by side but never converts one into the other.
- **India has no national survey here.** The {hpv:.2f}% figure covers school students in one state (Himachal Pradesh).
- **Court figures are not child-specific.** NCRB reports cyber stalking/bullying of women and children together.
- **Small numbers swing.** Recorded child cyber stalking/bullying went {v('Cyber crimes against children: Cyber stalking/bullying', 2022, IA):,.0f}
  (2022) → {SB23.value:,.0f} (2023) → {sb24:,.0f} (2024). Changes this size can reflect recording practice.
- **The international figure has two versions.** HBSC says {HB15.value:.0f}% in its key findings and {HB16.value:.0f}% in its
  body text. This page uses {HB16.value:.0f}% and shows both.
- **A source disagrees with itself.** UNICEF's report text says the anxiety link held in all countries; its Table A30 shows
  {len(ANX_NS)} not significant. The dashboard follows the table.
- **One study has an inconsistency.** The Gujarat awareness study gives 60 students in its abstract and 100 in its methods.
- **Different measures, different answers.** PISA's stricter monthly measure gives {PISA3.value:.0f}%; HBSC's broader one gives
  {HB16.value:.0f}%. Both are shown; neither is wrong.
- **A link is not a cause.** The mental-health figures show online bullying and harm go together, not that one causes the other.
- **Earlier version corrected.** The 2020–2022 India series counts cases registered, not victims, as the source table states.
""")
ev(as_frame(HB15, HB16, HPV, SB23, SB24, ANX_NS, BIO48, PISA3, JUST["conviction rate"],
            row("Cyber crimes against children: Cyber stalking/bullying", 2022, IA)))

st.markdown("""
<div class="heard"><div class="kicker">What would make this story stronger</div>
A national Indian survey of cyberbullying among adolescents. Child-specific court outcomes for cyber stalking and bullying.
NCRB figures for 2025 and 2026. Outcome data from India's school cyber hygiene programmes. Until then, treat the India
picture as a strong signal, not a full measurement.
</div>""", unsafe_allow_html=True)

# ================================================================ CLOSE
st.markdown('<div class="mode"><i>✓</i>The close</div>', unsafe_allow_html=True)
st.header("The story in one breath", anchor="close")
st.markdown(f"""
<div class="callout"><div class="kicker">Start to finish</div>
<b>Empathize:</b> {HB16.value:.0f} in 100 adolescents internationally say they have been cyberbullied, up since 2018, and it
travels with self-harm and suicidal thoughts in every country studied.<br>
<b>Define:</b> in one Indian state, {HP_CNT.value:,.0f} surveyed students said it happened to them while police recorded
{HP_REC23.value:,.0f} cyber crimes against children; nationally, {JUST['cases convicted'].value:,.0f} of
{JUST['cases for trial'].value:,.0f} cyber stalking/bullying cases on trial ended in conviction.<br>
<b>Ideate:</b> make reporting easy, get cases to a verdict, link safety with mental health, reach boys early, and measure all of India.<br>
<b>Prototype:</b> an eleven-line scorecard with today's starting points, and clear gaps where none exist.<br>
<b>Test:</b> every number links to its source and {n_ok} of {len(ledger)} quotes were matched word-for-word; the biggest
missing piece is a national Indian survey.<br><br>
<b>The ask:</b> count what children go through, not only what reaches a police station, and see that what is reported is resolved.
</div>""", unsafe_allow_html=True)
ev(as_frame(HB16, IMPACT[IMPACT.outcome != "Anxiety"], HP_CNT, HP_REC23, JUST["cases convicted"], JUST["cases for trial"]))

# ================================================================ ANNEXURE
st.divider()
st.header("Annexure: evidence ledger and sources", anchor="annexure")
st.markdown("Everything behind the page: every source with its link, every ledger row (including pre-2020 baselines and "
            "policy documents that are not charted), and every computed figure.")

st.subheader("A. Sources")
reg = SOURCES.copy()
reg["origin"] = reg.apply(lambda s: "Main source list" if s.url in PROVIDED else
                          "Linked from a main-list page" if s.landing in PROVIDED else "Added (own research)", axis=1)
reg = reg[["source", "published", "rows", "origin", "url", "landing"]]
st.dataframe(reg, hide_index=True, **FULL, column_config={
    "source": "Source", "published": "Published", "rows": "Ledger rows", "origin": "Origin",
    "url": st.column_config.LinkColumn("Document link", display_text="open"),
    "landing": st.column_config.LinkColumn("Publisher page", display_text="open")})

st.subheader("B. Full evidence ledger")
fl = st.columns(4)
sc = fl[0].multiselect("Scope", sorted(ledger.scope.unique()))
cat = fl[1].multiselect("Category", sorted(ledger.category.unique()))
chk = fl[2].multiselect("Check", sorted(ledger.checked.unique()))
win = fl[3].selectbox("Years", ["All rows", "2020–2026 window only", "Outside window / undated"])
view = ledger
if sc: view = view[view.scope.isin(sc)]
if cat: view = view[view.category.isin(cat)]
if chk: view = view[view.checked.isin(chk)]
if win != "All rows": view = view[view.in_window == (win == "2020–2026 window only")]
st.caption(f"{len(view)} of {len(ledger)} rows")
st.dataframe(view.drop(columns=["checked", "in_window"]), hide_index=True, **FULL, column_config={
    "data_year": st.column_config.NumberColumn("data_year", format="%d"),
    "source_url": st.column_config.LinkColumn("source_url"), "landing_url": st.column_config.LinkColumn("landing_url")})
st.download_button("Download filtered ledger CSV", view.drop(columns=["checked", "in_window"]).to_csv(index=False),
                   "evidence_ledger_filtered.csv", "text/csv")
st.caption("The complete ledger is also on GitHub: "
           "[evidence_ledger.csv](https://github.com/ptnov218-nlu/Cybercrime-dashboad/blob/main/evidence_ledger.csv). "
           "[build_ledger.py](https://github.com/ptnov218-nlu/Cybercrime-dashboad/blob/main/build_ledger.py) lists every "
           "source and quote and re-checks them against the source texts.")

st.subheader("C. Every computed figure on this page")
calc = pd.DataFrame([
    ["Students in a class of 30 (HBSC)", HB16.id, f"30 × {HB16.value:.0f}%", f"{class30:.1f}"],
    ["Recorded child cyber crimes, 2020 → 2024", f"{CHILD_TOT.id.iloc[0]}, {T24.id}", f"{tot24:,.0f} ÷ {c20:,.0f}", f"{tot24 / c20:.2f}x"],
    ["India all-age cyber cases, 2020 → 2024", ", ".join(ALL_TOT.id.iloc[[0, -1]]), f"{b4:,.0f} ÷ {b0:,.0f}", f"{b4 / b0:.2f}x"],
    ["CSAM share of child cyber crimes, 2024", f"{CSAM24.id}, {T24.id}", f"{csam24:,.0f} ÷ {tot24:,.0f}", f"{csam24 / tot24:.1%}"],
    ["Stalking/bullying share of child cyber crimes, 2024", f"{SB24.id}, {T24.id}", f"{sb24:,.0f} ÷ {tot24:,.0f}", f"{sb24 / tot24:.1%}"],
    ["HBSC perpetrator gap, boys − girls", rid(("Cyberbullying others, boys", 2022), ("Cyberbullying others, girls", 2022)),
     f"{pb:.0f} − {pg:.0f}", f"{pb - pg:+.0f} pp"],
    ["Age-15 perpetration ratio, boys ÷ girls", rid("Cyberbullying others, 15y boys", "Cyberbullying others, 15y girls"),
     f"{p15b:.0f} ÷ {p15g:.0f}", f"{p15b / p15g:.2f}"],
    ["Himachal Pradesh perpetration − victimization", rid(("Cyberbullying perpetration, % of all respondents", 2023, HP), (HPV.metric, 2023, HP)),
     f"{hpp:.2f} − {hpv:.2f}", f"{hpp - hpv:+.2f} pp"],
    ["Sextortion multiple (lower bound)", f"{SX0.id}, {SX1.id}", f"{SX1.value:,.0f} ÷ {SX0.value:,.0f}", f"{SX1.value / SX0.value:.1f}x"],
    ["Countries with significant online bullying links", id_ranges(IMPACT.id), "count of significant rows per outcome",
     f"anxiety {n_anx}, self-harm {n_sh}, suicidal {n_su} of {n_ctry}"],
], columns=["computed figure", "input rows", "formula", "result"])
st.dataframe(calc, hide_index=True, **FULL)

st.subheader("D. Rows per year and sources by year")
cov.columns = [str(c) for c in cov.columns]
st.dataframe(cov, **FULL)
by_year = (ledger.dropna(subset=["data_year"]).groupby(["scope", "source"]).data_year
           .agg(lambda s: ", ".join(str(int(y)) for y in sorted(s.unique()))).rename("data years").reset_index())
st.dataframe(by_year, hide_index=True, **FULL)
