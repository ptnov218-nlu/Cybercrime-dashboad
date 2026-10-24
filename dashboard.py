"""
Hidden in plain sight: cyberbullying of adolescents, from the world to India, 2020-2026.
Run:  pip install streamlit pandas plotly
      streamlit run dashboard.py

Reads evidence_ledger.csv (same folder) and nothing else. Every number on screen is pulled
from a row of that file at runtime; every row carries a clickable source link, its location
in the source and the exact quote or data line it was checked against. Under each chart the
sources are linked; the evidence rows behind each chart are in the annexure. Figures
calculated here are labelled "computed" and their formulas are listed in the annexure.

Story: the world (44 countries) -> US and UK spotlight -> outliers -> how the question changes
the answer -> why it matters -> bridge to India -> what children say vs what is recorded ->
where complaints go -> records and courts -> what it adds up to -> annexure.
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
BLUE, ORANGE, AQUA, GREY = PALETTE[0], PALETTE[1], PALETTE[2], "#a3a29c"
# Full-width charts/tables: newer Streamlit (incl. the stlite build on GitHub Pages) uses width="stretch".
_ST = tuple(int(p) for p in st.__version__.split(".")[:2])
FULL = {"width": "stretch"} if _ST >= (1, 50) else {"use_container_width": True}
CSV = Path(__file__).with_name("evidence_ledger.csv")
YEARS = range(2020, 2027)
UK_NATIONS = ["England", "Scotland", "Wales"]
# The source lists supplied for this dashboard; anything else in the ledger was added from own research.
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
    "https://coalitionforgoodschools.org/wp-content/uploads/2025/09/India_Country-Report_Final.pdf",
    "https://www.mdpi.com/2673-995X/5/3/95",
    "https://bullyingsinfronteras.blogspot.com/2022/03/bullying-statistics-in-india-110000.html",
    "https://timesofindia.indiatimes.com/city/lucknow/one-case-of-cyberbullying-in-up-in-every-8-minutes/articleshow/120289739.cms",
    "https://www.indiatoday.in/health/story/online-bullying-in-teens-fuels-fear-and-anxiety-survey-finds-1-in-2-parents-worried-2866011-2026-02-10",
    "https://frontline.thehindu.com/social-issues/cyberbullying-teenagers-india-law-mental-health-ugc-social-media/article69905344.ece",
    "https://www.thehindu.com/news/national/uttar-pradesh/uttar-pradesh-police-warn-of-growing-hybrid-cybercrime-threat-stress-public-awareness/article71042340.ece",
    "https://timesofindia.indiatimes.com/city/mysuru/karnataka-saw-315-cyberbullying-cases-between-jan-2022-and-july-2025/articleshow/123682349.cms",
}

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 1.6rem;}
h2 {letter-spacing: -.01em;}
.hero {padding: 2.4rem 2.2rem 2rem; border-radius: 20px; margin-bottom: 1rem; color: #fff;
       background: linear-gradient(135deg, #0d366b 0%, #1c5cab 55%, #2a78d6 100%);}
.hero .kicker {text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; opacity: .85;}
.hero h1 {font-size: 2.7rem; line-height: 1.08; margin: .5rem 0 .6rem; padding: 0; color: #fff;}
.hero p {font-size: 1.15rem; line-height: 1.5; max-width: 46rem; margin: 0; opacity: .95;}
.kpi {border-radius: 16px; padding: 1rem 1.1rem .9rem; border: 1px solid rgba(128,128,128,.25); height: 100%;}
.kpi .big {font-size: 2.3rem; font-weight: 800; line-height: 1.05; letter-spacing: -.02em;}
.kpi .lbl {font-size: .92rem; line-height: 1.35; margin-top: .3rem;}
.kpi .who {font-size: .75rem; opacity: .65; margin-top: .35rem; text-transform: uppercase; letter-spacing: .05em;}
.kpi.accent .big {color: #eb6834;}
.chap {display: flex; align-items: baseline; gap: .7rem; margin-top: 3.2rem; border-top: 2px solid rgba(128,128,128,.18); padding-top: .9rem;}
.chap .num {font-size: 2.1rem; font-weight: 800; color: #2a78d6; line-height: 1;}
.chap .kick {text-transform: uppercase; letter-spacing: .12em; font-size: .8rem; font-weight: 700; opacity: .7;}
.lede {font-size: 1.05rem; line-height: 1.5; opacity: .85; margin: -.4rem 0 .6rem; max-width: 50rem;}
.src {font-size: .76rem; line-height: 1.5; opacity: .85; margin: -.2rem 0 1.4rem; padding-left: .6rem;
      border-left: 3px solid rgba(128,128,128,.35);}
.src a {color: #2a78d6; text-decoration: underline; text-underline-offset: 2px;}
.src .h {font-weight: 700; text-transform: uppercase; letter-spacing: .06em; font-size: .68rem; margin-right: .3rem;}
.src .warn {display: block; margin-top: .15rem;}
.bridge {margin: 3.5rem 0 1rem; padding: 2.4rem 2.2rem; border-radius: 20px; color: #fff;
         background: linear-gradient(135deg, #7a2e0e 0%, #c4521f 50%, #eb6834 100%);}
.bridge .kicker {text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; opacity: .85;}
.bridge h2 {color: #fff; font-size: 2.3rem; margin: .4rem 0 .6rem; padding: 0;}
.bridge p {font-size: 1.08rem; line-height: 1.55; max-width: 48rem; margin: 0 0 1rem;}
.steps {display: flex; gap: .6rem; flex-wrap: wrap; align-items: center;}
.steps span {background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.35); border-radius: 999px;
             padding: .35rem .9rem; font-weight: 600;}
.steps b {opacity: .8;}
.card {border-radius: 16px; padding: 1rem 1.15rem; border: 1px solid rgba(128,128,128,.25); margin-bottom: .6rem; height: 100%;}
.card .t {font-weight: 700; font-size: 1.02rem; margin-bottom: .25rem;}
.card .b {font-size: .9rem; line-height: 1.45; opacity: .9;}
.card.hot {border-color: rgba(235,104,52,.5); background: rgba(235,104,52,.06);}
.vs {display: flex; align-items: center; justify-content: center; font-size: 1.05rem; font-weight: 700; opacity: .7; height: 100%;
     text-align: center; line-height: 1.35;}
.close {border-radius: 20px; padding: 1.6rem 1.8rem; background: rgba(42,120,214,.07); border: 1px solid rgba(42,120,214,.25);}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data + lookups
def _check(v):
    if "PDF text" in v:
        return "✔ PDF-matched"
    if "web page text" in v:
        return "✔ web-page-matched"
    if "data file" in v:
        return "✔ data-file-matched"
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
EVIDENCE = []          # (title, frame, computed, note) for every evidence line; rendered in the annexure
_TITLE = ["Overview"]  # the current chart title, set by head()


def head(title, lede=None):
    _TITLE[0] = title
    st.subheader(title)
    if lede:
        st.markdown(f'<p class="lede">{lede}</p>', unsafe_allow_html=True)


def ev(frame, computed=(), note=None, related=(), warn=None):
    """Compact, clickable source line under a chart; the evidence rows go to the annexure.
    `related` names extra 2025-26 sources (by name prefix); `warn` is a one-line caveat shown inline."""
    frame = frame.drop_duplicates("id").sort_values("id")
    EVIDENCE.append((_TITLE[0], frame, list(computed), note))
    n = len(EVIDENCE)
    parts = []
    for name, g in frame.groupby("source", sort=False):
        yrs = ", ".join(str(int(y)) for y in sorted(g.data_year.dropna().unique()))
        locs = "; ".join(sorted(g.location.unique()))
        parts.append(f"{link(name, g.source_url.iloc[0])} <span style='opacity:.7'>({escape(locs)}{', ' + yrs if yrs else ''})</span>")
    rel = ""
    if related:
        rel = " · <span class='h'>Related 2025–26</span>" + " · ".join(link(s.source, s.url) for s in (src(p) for p in related))
    extra = f" · {len(computed)} computed" if computed else ""
    w = f"<span class='warn'>⚠ {escape(warn)}</span>" if warn else ""
    st.markdown(f'<div class="src"><span class="h">Sources</span>{" · ".join(parts)}{rel}<br>'
                f'<span style="opacity:.7">{len(frame)} evidence rows{extra} · '
                f'<a href="#ev-{n}">see rows in annexure</a></span>{w}</div>', unsafe_allow_html=True)


def chapter(num, kicker, anchor, title, lede=None):
    st.markdown(f'<div class="chap"><span class="num">{num}</span><span class="kick">{kicker}</span></div>', unsafe_allow_html=True)
    st.header(title, anchor=anchor)
    if lede:
        st.markdown(f'<p class="lede">{lede}</p>', unsafe_allow_html=True)


def kpi(big, label, who="", accent=False):
    st.markdown(f'<div class="kpi{" accent" if accent else ""}"><div class="big">{big}</div><div class="lbl">{label}</div>'
                f'<div class="who">{who}</div></div>', unsafe_allow_html=True)


def card(title, body, hot=False):
    st.markdown(f'<div class="card{" hot" if hot else ""}"><div class="t">{title}</div><div class="b">{body}</div></div>',
                unsafe_allow_html=True)


def style(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=50, t=30, b=10), legend_title_text="",
                      bargap=0.3, bargroupgap=0.08, font=dict(size=13),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    fig.update_traces(marker_line_width=0, cliponaxis=False, selector=dict(type="bar"))
    return fig


def plot(fig, height=360, top=None):
    fig = style(fig, height)
    if top:  # extra room above facet titles so the legend never overlaps them
        fig.update_layout(margin_t=top, legend_y=1 + top / height)
    st.plotly_chart(fig, **FULL, config={"displayModeBar": False})


def hbar(frame, x, y, color, cmap, height, fmt="%{text:,.0f}", order=None, xlabel=""):
    fig = px.bar(frame, x=x, y=y, orientation="h", text=x, color=color, color_discrete_map=cmap,
                 category_orders={y: order} if order else None, labels={x: xlabel, y: ""}, hover_data={"id": True})
    fig.update_traces(texttemplate=fmt, textposition="outside")
    fig.update_layout(showlegend=bool(frame[color].nunique() > 1))
    plot(fig, height)


# ---------------------------------------------------------------- every number used in the story
# Global: HBSC 2021/22
HB16 = row("Cyberbullied (victim), all, body text")
HB15 = row("Cyberbullied (victim), all, key-findings text")
vb, vg = v("Cyberbullied (victim), boys", 2022), v("Cyberbullied (victim), girls", 2022)
BASE18 = rows("Cyberbullied (victim), boys", "Cyberbullied (victim), girls", year=2018, frame=ledger)
vb18, vg18 = (BASE18.set_index("metric").value[m] for m in ("Cyberbullied (victim), boys", "Cyberbullied (victim), girls"))
GEND22 = rows("Cyberbullied (victim), boys", "Cyberbullied (victim), girls", year=2022)
LT_PERP = row("Cyberbullying others, highest cell")
HB_N = row("Young people surveyed (HBSC 2021/22)")
CTRY = df[df.metric.str.startswith("Cyberbullied, age") & df.metric.str.endswith("combined")].copy()
CTRY["age"] = CTRY.metric.str.extract(r"age (\d+)")[0]
G15 = df[df.metric.isin(["Cyberbullied, age 15, girls", "Cyberbullied, age 15, boys"])].copy()
G15["sex"] = G15.metric.str.extract(r"(girls|boys)")[0]
SCAT = G15.pivot_table(index="geography", columns="sex", values="value").reset_index()


def rank_of(age, country):
    a = CTRY[CTRY.age == age].sort_values("value", ascending=False).reset_index(drop=True)
    return int(a.index[a.geography == country][0]) + 1, len(a)


lt_first = all(rank_of(a, "Lithuania")[0] == 1 for a in ("11", "13", "15"))
eng11_rank, n_ctry_hbsc = rank_of("11", "England")
LOW15 = CTRY[CTRY.age == "15"].sort_values("value").iloc[0]
LT15 = SCAT[SCAT.geography == "Lithuania"].iloc[0]

# Global: PISA 2025, UNICEF Disrupting Harm, WeProtect
PISA3 = row("Cyberbullied a few times a month or more (upsetting information published online without consent)")
PISA59 = row("Science score gap, cyberbullied vs other students")
OUTCOMES = {"anxiety": "Anxiety", "self-harm": "Self-harm", "suicidal thoughts/behaviours": "Suicidal thoughts"}
IMPACT = df[df.metric.str.startswith("Online bullying ->") & df.metric.str.contains("std. SEM")].copy()
IMPACT["outcome"] = IMPACT.metric.str.extract(r"-> (.+?), std")[0].map(OUTCOMES)
IMPACT["result"] = IMPACT.metric.str.contains("not significant").map({True: "Could be chance", False: "Solid link (p<.001)"})
SIG = IMPACT[IMPACT.result.str.startswith("Solid")].groupby("outcome").size()
n_anx, n_sh, n_su = (int(SIG.get(o, 0)) for o in OUTCOMES.values())
n_ctry = int(IMPACT.groupby("outcome").size().max())
DH_N = row("Children aged 12-17 surveyed (Disrupting Harm)")
ANX_NS = IMPACT[(IMPACT.outcome == "Anxiety") & IMPACT.result.str.startswith("Could")]
SX0, SX1 = row("Sextortion reports, 2021 baseline"), row("Sextortion reports, 2022")
GROOM19 = row("Time for gaming-platform chats to escalate to high-risk grooming")

# United States: CDC YRBS 2023, Pew 2022
YR = {k: row(f"Electronically bullied in past year, high school students, {k}") for k in
      ("all", "female", "male", "LGBTQ+", "cisgender and heterosexual")}
PEW46 = row("Teens who ever experienced at least one of six cyberbullying behaviours")
PEW54 = row("Girls aged 15-17 who experienced at least one behaviour")
PEW_SM = row("Teens saying social media sites do a good job addressing cyberbullying")

# United Kingdom: ONS (England and Wales), HBSC UK nations
ONS19 = row("Children aged 10-15 who experienced an online bullying behaviour", 2023)
ONS_N = row("Children aged 10-15 who experienced an online bullying behaviour (number)")
ONS_TOLD = row("Children bullied online who told no one")
ONS_NAME = row("Children bullied online who would not describe it as bullying")
UKN = CTRY[CTRY.geography.isin(UK_NATIONS)].copy()

# India: Himachal Pradesh survey vs records; UP complaints; parents; records; courts
IA, HP, UP = "India (all)", "Himachal Pradesh", "Uttar Pradesh"
HPV = row("Cyberbullying victimization, % of all respondents", 2023, HP)
HP_CNT, HP_N = row("Students reporting cyberbullying victimization (count)", 2023, HP), row("School students surveyed, ages 13-17", 2023, HP)
HP_REC23, HP_REC24 = row("Cyber crimes against children: TOTAL", 2023, HP), row("Cyber crimes against children: TOTAL", 2024, HP)
UPC = row("Cyberbullying complaints received (UP Police WCSO / 1090)", 2024, UP)
UP16 = row("Cyberbullying complaints filed by people aged 16-25", 2024, UP)
UPW = row("Complaints resolved at first stage (counsellor warning call)", 2024, UP)
UPF = row("Complaints resolved via Friends, Family and Relatives cell", 2024, UP)
up_rest = UPC.value - UPW.value - UPF.value
up_settled = (UPW.value + UPF.value) / UPC.value
SB_ALL24 = row("Cyber stalking/bullying of women & children (combined)", 2024)
LC = df[df.category == "Parent survey (online, self-selected)"]
LC_REP = LC[LC.metric.str.startswith("Reporting online bullying/harmful content:")].copy()
LC82 = row("Parents saying reporting is difficult, slow or unclear")
LC_UNAWARE = row("Reporting online bullying/harmful content: not aware of any clear reporting mechanism")
LC_N = row("Parents answering the reporting question (LocalCircles)")
TOT = "Cyber crimes against children: TOTAL"
CHILD = df[df.metric.str.startswith("Cyber crimes against children:") & (df.geography == IA)].copy()
CHILD["type"] = CHILD.metric.str.replace("Cyber crimes against children: ", "", regex=False)
CHILD_TOT = CHILD[CHILD.type == "TOTAL"].sort_values("data_year")
c20, c23, tot24 = (v(TOT, y, IA) for y in (2020, 2023, 2024))
T24 = row(TOT, 2024, IA)
SB24 = row("Cyber crimes against children: Cyber stalking/bullying", 2024, IA)
CSAM24 = row("Cyber crimes against children: Sexually explicit material depicting children (CSAM)", 2024, IA)
sb24, csam24 = SB24.value, CSAM24.value
SBK = "Cyber stalking/bullying of women/children"
JUST = {k: row(f"{SBK}: {k}", 2024) for k in ("cases for trial", "trials completed", "cases convicted", "pending trial at year end",
                                              "conviction rate", "court pendency", "charge-sheeting rate")}
ALL_TOT = df[df.metric == "TOTAL cyber crime cases (all ages, all types)"].sort_values("data_year")
b0, b4 = ALL_TOT.value.iloc[0], ALL_TOT.value.iloc[-1]
KA_REPLY = df[df.metric == "Cyberbullying cases against children registered (Karnataka govt reply)"].sort_values("data_year")
KA_NCRB = df[(df.metric == TOT) & (df.geography == "Karnataka")].sort_values("data_year")
EST_LO = row("Cyberbullying prevalence among Indian adolescents, lowest study estimate", frame=ledger)
EST_HI = row("Cyberbullying prevalence among Indian adolescents, highest study estimate", frame=ledger)
CGS37 = row("Children aged 10-17 who experienced cyberbullying (key finding, source not cited)", frame=ledger)
CGS1614 = row("Cyberstalking cases in 2020 (as stated by the report)", frame=ledger)
SB_ALL20 = row("Cyber stalking/bullying of women & children (combined)", 2020)
POLICY = ledger[ledger.category == "Policy framework"]
NOLAW = POLICY[POLICY.metric.str.startswith("No Indian law")].iloc[0]
EXCLUDED = ledger[ledger.category == "Excluded source"]
HYGIENE = row("Students given cyber hygiene training by I4C (NCC, NSS, NYKS)")
SH_MED = row("Online bullying -> self-harm, median std. estimate across countries")
n_ok = int(ledger.checked.str.startswith("✔").sum())

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### The story")
    st.markdown("[01 · The world](#world)  \n[02 · US & UK](#usuk)  \n[03 · Outliers](#outliers)  \n"
                "[04 · How you ask](#measure)  \n[05 · Why it matters](#matters)  \n**→ India**  \n"
                "[06 · Said vs recorded](#said)  \n[07 · Where complaints go](#complaints)  \n"
                "[08 · Records & courts](#records)  \n[What it adds up to](#close)  \n[Annexure](#annexure)")
    st.divider()
    st.markdown(f"**{len(ledger)}** evidence rows · **{len(SOURCES)}** sources · every row linked.  \n"
                f"✔ {n_ok} checked word-for-word against the source.")
    with st.expander("Words used here"):
        st.markdown("**Cyberbullying**: being repeatedly hurt, threatened or humiliated online.  \n"
                    "**HBSC**: WHO survey of 11–15-year-olds in 44 countries.  \n**YRBS**: CDC's US high-school survey.  \n"
                    "**ONS**: UK statistics office (Crime Survey, England & Wales).  \n**PISA**: OECD test of 15-year-olds.  \n"
                    "**NCRB**: India's crime records bureau.  \n**CSAM**: child sexual abuse material.  \n"
                    "**Charge-sheet**: police report sending a case to court.")

# ================================================================ HERO
st.markdown(f"""
<div class="hero">
  <div class="kicker">Data story · adolescents online · 2020–2026</div>
  <h1>One in six children is bullied online.<br>In India, most of it is never counted.</h1>
  <p>What surveys find around the world, what the US and UK measure, where the pattern breaks, and what happens
  to the same harm in India, where there is no national survey and the trail runs through police records.</p>
</div>""", unsafe_allow_html=True)
k = st.columns(4)
with k[0]:
    kpi(f"{HB16.value:.0f}%", "of 11–15-year-olds cyberbullied in the past couple of months", "44 countries · HBSC 2022")
with k[1]:
    kpi(f"{YR['all'].value:.0f}%", "of US high-school students bullied online in a year", "United States · CDC 2023")
with k[2]:
    kpi(f"{ONS_N.value / 1000:,.0f}k", "children aged 10–15 bullied online in a year", "England & Wales · ONS 2023")
with k[3]:
    kpi(f"{JUST['cases convicted'].value:,.0f}", f"convictions from {JUST['cases for trial'].value:,.0f} cyber stalking/bullying cases on trial",
        "India · NCRB 2024", accent=True)
_TITLE[0] = "Headline numbers"
ev(as_frame(HB16, YR["all"], ONS_N, JUST["cases convicted"], JUST["cases for trial"]))

# ================================================================ 01 THE WORLD
chapter("01", "The world", "world", "Online bullying is common everywhere, but not equally")
age = st.radio("Age group", ["11", "13", "15"], index=1, horizontal=True, format_func=lambda a: f"{a}-year-olds")
w = CTRY[CTRY.age == age].sort_values("value", ascending=False).copy()
w["group"] = w.geography.map(lambda c: "Lithuania (outlier)" if c == "Lithuania" else "UK nations" if c in UK_NATIONS
                             else "Canada" if c == "Canada" else "Other countries")
lo, hi = w.iloc[-1], w.iloc[0]
head(f"{hi.value:.0f}% in {hi.geography}, {lo.value:.0f}% in {lo.geography}: a {hi.value / lo.value:.0f}-fold gap among {age}-year-olds",
     f"Share of {age}-year-olds cyberbullied at least once or twice in the past couple of months, {len(w)} countries and regions.")
fig = px.bar(w, x="geography", y="value", color="group", text="value",
             color_discrete_map={"Lithuania (outlier)": ORANGE, "UK nations": BLUE, "Canada": AQUA, "Other countries": GREY},
             category_orders={"geography": w.geography.tolist(), "group": ["Lithuania (outlier)", "UK nations", "Canada", "Other countries"]},
             labels={"value": "% cyberbullied", "geography": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:.0f}", textposition="outside", textfont_size=10)
fig.update_xaxes(tickangle=-60, tickfont_size=11)
fig.add_hline(y=HB16.value, line_width=1, line_color="rgba(128,128,128,.7)",
              annotation_text=f"HBSC average, all ages: {HB16.value:.0f}%", annotation_position="top right")
plot(fig, 420)
ev(as_frame(w, HB16), computed=[("Fold gap", f"{hi.value:.1f} ÷ {lo.value:.1f} = {hi.value / lo.value:.1f}")],
   related=["OECD, PISA 2025"])

t = st.columns(3)
with t[0]:
    kpi(f"{vg18:.0f}→{vg:.0f}%", "girls cyberbullied, 2018 → 2022", "HBSC average")
with t[1]:
    kpi(f"{vb18:.0f}→{vb:.0f}%", "boys cyberbullied, 2018 → 2022", "HBSC average")
with t[2]:
    kpi(f"{HB_N.value / 1000:,.0f}k", "young people asked directly, in 44 countries", "HBSC 2021/22")
_TITLE[0] = "Trend 2018–2022 and sample"
ev(as_frame(BASE18, GEND22, HB_N), warn="2018 values are a pre-window baseline, used only to show the change.")

# ================================================================ 02 US & UK
chapter("02", "Spotlight", "usuk", "The US and the UK: the same story, measured at home")
us, uk = st.columns(2)
with us:
    head(f"US: 1 in 6 high-schoolers, 1 in 4 LGBTQ+ students")
    u = pd.DataFrame([(lab, YR[key].value, YR[key].id) for lab, key in [
        ("All students", "all"), ("Girls", "female"), ("Boys", "male"), ("Cisgender & heterosexual", "cisgender and heterosexual"),
        ("LGBTQ+", "LGBTQ+")]], columns=["group", "value", "id"])
    u["hl"] = u.group.map(lambda g: "Highest" if g == "LGBTQ+" else "Students")
    hbar(u, "value", "group", "hl", {"Students": BLUE, "Highest": ORANGE}, 270, fmt="%{text:.0f}%",
         order=u.group.tolist(), xlabel="% electronically bullied in the past year (2023)")
    ev(as_frame(*YR.values()))
    kpi(f"{PEW46.value:.0f}%", f"of US teens have ever faced at least one of six forms of online abuse; {PEW54.value:.0f}% of girls aged 15–17",
        "Pew Research · 2022")
    _TITLE[0] = "US: Pew 2022"
    ev(as_frame(PEW46, PEW54))
with uk:
    head(f"UK: England's 11-year-olds rank #{eng11_rank} of {n_ctry_hbsc}")
    fig = px.bar(UKN, x="age", y="value", color="geography", barmode="group", text="value",
                 color_discrete_sequence=PALETTE, category_orders={"geography": UK_NATIONS, "age": ["11", "13", "15"]},
                 labels={"value": "% cyberbullied (HBSC 2022)", "age": "age"}, hover_data={"id": True})
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    plot(fig, 270)
    ev(UKN, computed=[("England's rank at age 11", f"{eng11_rank} of {n_ctry_hbsc}, by combined value")])
    kpi(f"{ONS19.value:.1f}%", f"of children aged 10–15 in England & Wales bullied online in a year; "
        f"{ONS_TOLD.value:.0f}% of them told no one", "ONS · year to March 2023")
    _TITLE[0] = "UK: ONS 2023"
    ev(as_frame(ONS19, ONS_N, ONS_TOLD))

# ================================================================ 03 OUTLIERS
chapter("03", "Outliers", "outliers", "Where the pattern breaks")
left, right = st.columns([3, 2])
with left:
    head(f"In Lithuania, {LT15.boys:.0f}% of 15-year-old boys are cyberbullied: twice the rate for girls",
         "Each dot is a country. Above the line, boys are cyberbullied more than girls; below it, girls are.")
    sc = SCAT.copy()
    sc["group"] = sc.geography.map(lambda c: "Lithuania" if c == "Lithuania" else "UK nations" if c in UK_NATIONS
                                   else "Lowest" if c == LOW15.geography else "Other countries")
    labels = {"Lithuania", LOW15.geography, *UK_NATIONS, "Bulgaria"}
    sc["label"] = sc.geography.where(sc.geography.isin(labels), "")
    fig = px.scatter(sc, x="girls", y="boys", color="group", text="label",
                     color_discrete_map={"Lithuania": ORANGE, "UK nations": BLUE, "Lowest": AQUA, "Other countries": GREY},
                     labels={"girls": "girls cyberbullied, age 15 (%)", "boys": "boys cyberbullied, age 15 (%)"},
                     hover_data={"geography": True, "label": False})
    mx = float(max(sc.girls.max(), sc.boys.max())) + 3
    fig.add_shape(type="line", x0=0, y0=0, x1=mx, y1=mx, line=dict(color="rgba(128,128,128,.6)", width=1))
    fig.update_traces(marker_size=10, textposition="top center", textfont_size=11, selector=dict(type="scatter"))
    fig.update_xaxes(range=[0, mx]); fig.update_yaxes(range=[0, mx])
    plot(fig, 400)
    ev(G15)
with right:
    card("Lithuania: top of the table, every time",
         f"{'#1 of 44 at ages 11, 13 and 15' if lt_first else 'Near the top at every age'}. {LT_PERP.value:.0f}% of its "
         f"15-year-old boys say they cyberbully others, the highest figure anywhere.", hot=True)
    card(f"England's youngest", f"{UKN[(UKN.geography == 'England') & (UKN.age == '11')].value.iloc[0]:.0f}% of 11-year-olds "
         f"cyberbullied: #{eng11_rank} of {n_ctry_hbsc}. By 15 England falls back to mid-table.")
    card(f"{LOW15.geography}: the low point", f"{LOW15.value:.0f}% of 15-year-olds, the lowest of {n_ctry_hbsc}.")
    _TITLE[0] = "Outlier cards"
    ev(as_frame(CTRY[CTRY.geography.isin(["Lithuania", "England", LOW15.geography])], LT_PERP),
       computed=[("Ranks", "position by combined value among 44 countries and regions, per age")])

# ================================================================ 04 HOW YOU ASK
chapter("04", "How you ask", "measure", "Ask a different question, get a different number: 3% to 46%")
m = pd.DataFrame([
    ("PISA · 15-year-olds, OECD · a few times a month+", PISA3.value, PISA3.id),
    (f"HBSC · 11–15, 44 countries · past couple of months", HB16.value, HB16.id),
    ("CDC YRBS · US high school · past year", YR["all"].value, YR["all"].id),
    ("ONS · 10–15, England & Wales · past year", ONS19.value, ONS19.id),
    ("Pew · US teens 13–17 · ever, 6 behaviours", PEW46.value, PEW46.id)], columns=["measure", "value", "id"])
m["kind"] = "Survey"
hbar(m, "value", "measure", "kind", {"Survey": BLUE}, 300, fmt="%{text:.0f}%", order=m.measure.tolist(), xlabel="% of young people")
_TITLE[0] = "How you ask changes the answer"
ev(as_frame(PISA3, HB16, YR["all"], ONS19, PEW46),
   warn="Different questions, ages and countries: these are not comparable with each other, and that is the point.")

# ================================================================ 05 WHY IT MATTERS
chapter("05", "Why it matters", "matters", f"It travels with self-harm and suicidal thoughts in all {n_ctry} countries studied")
st.markdown(f'<p class="lede">Strength of the link between being bullied online and each outcome (0 = none). '
            f'Survey of {DH_N.value:,.0f} children aged 12–17. A link, not proof of cause.</p>', unsafe_allow_html=True)
_TITLE[0] = "Online bullying and mental health"
order = IMPACT[IMPACT.outcome == "Self-harm"].sort_values("value").geography.tolist()
fig = px.bar(IMPACT, x="value", y="geography", orientation="h", color="result", facet_col="outcome",
             category_orders={"geography": order, "outcome": list(OUTCOMES.values())},
             color_discrete_map={"Solid link (p<.001)": BLUE, "Could be chance": GREY},
             labels={"value": "strength of link", "geography": ""}, hover_data={"id": True})
fig.for_each_annotation(lambda an: an.update(text=f"<b>{an.text.split('=')[-1]}</b>"))
plot(fig, 440, top=70)
ev(as_frame(IMPACT, DH_N), related=["UNICEF Innocenti, Childhood in a Digital World (2025): report"],
   warn=f"Anxiety link not significant in {len(ANX_NS)} countries ({', '.join(ANX_NS.geography)}).")
t = st.columns(3)
with t[0]:
    kpi(f"−{PISA59.value:.0f}", "PISA science points for cyberbullied 15-year-olds", "OECD · PISA 2025")
with t[1]:
    kpi(f"{GROOM19.value:.0f} sec", "for a gaming-platform chat to turn into high-risk grooming", "WeProtect · 2023")
with t[2]:
    kpi(f"{SX0.value:,.0f}→{SX1.value / 1000:,.0f}k+", "sextortion reports, 2021 → 2022", "WeProtect · 2023")
_TITLE[0] = "Harm indicators"
ev(as_frame(PISA59, GROOM19, SX0, SX1))

# ================================================================ BRIDGE TO INDIA
st.markdown(f"""
<div class="bridge">
  <div class="kicker">Now, India</div>
  <h2>Everything above came from asking children. India has never asked them nationally.</h2>
  <p>The US, the UK and 44 HBSC countries survey young people directly, {HB_N.value / 1000:,.0f}k in HBSC alone. India has no
  national survey of cyberbullying. So the trail changes: from what children tell one state survey, to what reaches
  the police, to what reaches a verdict.</p>
  <div class="steps"><span>What children say</span><b>→</b><span>What police record</span><b>→</b><span>What courts decide</span></div>
</div>""", unsafe_allow_html=True)
_TITLE[0] = "Bridge to India"
ev(as_frame(HB_N, HPV))

# ================================================================ 06 SAID VS RECORDED
chapter("06", "What children say", "said", "Same state, same year: 596 said it happened. Police recorded 4.")
a, mid, b = st.columns([5, 2, 5])
with a:
    kpi(f"{HP_CNT.value:,.0f}", f"of {HP_N.value:,.0f} surveyed school students said they were cyberbullied ({HPV.value:.2f}%)",
        "Himachal Pradesh · survey Nov–Dec 2023")
with mid:
    st.markdown('<div class="vs">vs</div>', unsafe_allow_html=True)
with b:
    kpi(f"{HP_REC23.value:,.0f}", f"cyber crimes against children recorded by police in the whole state ({HP_REC24.value:,.0f} in 2024)",
        "Himachal Pradesh · NCRB 2023", accent=True)
_TITLE[0] = "Said vs recorded: Himachal Pradesh"
ev(as_frame(HP_CNT, HP_N, HPV, HP_REC23, HP_REC24), warn="A survey sample and a police count measure different things; never divide one by the other.")

head(f"Parents: {LC82.value:.0f}% say reporting is hard, {LC_UNAWARE.value:.0f}% don't know how",
     f"How easy is it to report online harm to platforms or authorities? {LC_N.value:,.0f} urban parents.")
lr = LC_REP.copy()
lr["answer"] = lr.metric.str.replace("Reporting online bullying/harmful content: ", "", regex=False).str.capitalize()
lr["kind"] = lr.answer.map(lambda a: "Easy" if a.startswith("Very easy") else "No clear answer" if a.startswith("No clear") else "Hard, slow or unknown")
scale = ["Very easy and effective", "Somewhat easy but slow or unclear", "Difficult and time-consuming",
         "Very difficult, complaints usually unresolved", "Not aware of any clear reporting mechanism", "No clear answer"]
hbar(lr, "value", "answer", "kind", {"Easy": AQUA, "Hard, slow or unknown": ORANGE, "No clear answer": GREY}, 280,
     fmt="%{text:.0f}%", order=scale, xlabel="% of responding parents")
ev(as_frame(lr, LC82, LC_N), warn="Online, self-selected poll; not a representative sample.")

# ================================================================ 07 WHERE COMPLAINTS GO
chapter("07", "What police see", "complaints", f"{UPC.value:,.0f} complaints in one state. {up_settled:.0%} never became a case.")
st.markdown(f'<p class="lede">Uttar Pradesh police cyberbullying complaints, 2024 · {UP16.value:,.0f}+ from people aged 16–25. '
            f'For scale: NCRB recorded {SB_ALL24.value:,.0f} cyber stalking/bullying cases of women and children in all of India.</p>',
            unsafe_allow_html=True)
_TITLE[0] = "Where complaints go: Uttar Pradesh"
upf = pd.DataFrame([("Complaints received", UPC.value, "Received", UPC.id),
                    ("Settled by a counsellor's warning call", UPW.value, "Settled, no case", UPW.id),
                    ("Settled through the accused's family", UPF.value, "Settled, no case", UPF.id),
                    ("Left for district police (computed)", up_rest, "Escalated", "computed")], columns=["stage", "value", "kind", "id"])
hbar(upf, "value", "stage", "kind", {"Received": BLUE, "Settled, no case": GREY, "Escalated": ORANGE}, 260,
     order=upf.stage.tolist(), xlabel="complaints, Uttar Pradesh, 2024")
ev(as_frame(UPC, UP16, UPW, UPF, SB_ALL24),
   computed=[("Left for district police", f"{UPC.value:,.0f} − {UPW.value:,.0f} − {UPF.value:,.0f} = {up_rest:,.0f}"),
             ("Settled without a case", f"({UPW.value:,.0f} + {UPF.value:,.0f}) ÷ {UPC.value:,.0f} = {up_settled:.1%}")],
   warn="UP Police data as reported by the Times of India; complaints, not FIRs, and include adults.")

# ================================================================ 08 RECORDS & COURTS
chapter("08", "What courts decide", "records",
        f"What police record is mostly abuse imagery. What courts convict: {JUST['cases convicted'].value:,.0f}.")
left, right = st.columns(2)
with left:
    head(f"Cyber crimes against children: {c20:,.0f} (2020) → {tot24:,.0f} (2024)",
         f"Peak {c23:,.0f} in 2023. Bullying is {sb24 / tot24:.0%} of 2024 cases; abuse imagery {csam24 / tot24:.0%}.")
    c = CHILD[CHILD.type != "TOTAL"].copy()
    c["type"] = c.type.replace({"Sexually explicit material depicting children (CSAM)": "Abuse imagery (CSAM)"})
    tord = c.groupby("type").value.sum().sort_values(ascending=False).index.tolist()
    fig = px.bar(c, x="data_year", y="value", color="type", barmode="stack", category_orders={"type": tord},
                 color_discrete_sequence=PALETTE, labels={"value": "recorded cases", "data_year": ""}, hover_data={"id": True})
    fig.update_xaxes(dtick=1)
    fig.update_layout(legend=dict(font_size=10))
    for _, r in CHILD_TOT.iterrows():
        fig.add_annotation(x=r.data_year, y=r.value, text=f"<b>{r.value:,.0f}</b>", showarrow=False, yshift=12)
    plot(fig, 400)
    ev(CHILD, computed=[("Shares 2024", f"bullying {sb24:,.0f} ÷ {tot24:,.0f} = {sb24 / tot24:.1%}; CSAM {csam24:,.0f} ÷ {tot24:,.0f} = {csam24 / tot24:.1%}")])
with right:
    head(f"{JUST['cases convicted'].value:,.0f} convictions from {JUST['cases for trial'].value:,.0f} cases on trial",
         f"Cyber stalking/bullying of women & children, 2024 · {JUST['court pendency'].value:.1f}% still pending.")
    f = pd.DataFrame([(lab, JUST[key].value, JUST[key].id) for lab, key in [
        ("On trial during the year", "cases for trial"), ("Still pending at year end", "pending trial at year end"),
        ("Trials completed", "trials completed"), ("Convicted", "cases convicted")]], columns=["stage", "value", "id"])
    f["kind"] = f.stage.map(lambda s: "Conviction" if s == "Convicted" else "Court stage")
    hbar(f, "value", "stage", "kind", {"Court stage": BLUE, "Conviction": ORANGE}, 400, order=f.stage.tolist(),
         xlabel="cases, 2024")
    ev(as_frame(*JUST.values()), warn="NCRB reports this crime for women and children together.")

# ================================================================ CLOSE
st.markdown('<div class="chap"><span class="num">→</span><span class="kick">What it adds up to</span></div>', unsafe_allow_html=True)
st.header("Common everywhere. Counted elsewhere. Lost in India.", anchor="close")
c4 = st.columns(4)
with c4[0]:
    card("Common", f"{HB16.value:.0f}% across 44 countries; {YR['all'].value:.0f}% in the US; {ONS19.value:.0f}% in England & Wales.")
with c4[1]:
    card("Harmful", f"Linked to self-harm and suicidal thoughts in all {n_ctry} countries studied; −{PISA59.value:.0f} PISA points.")
with c4[2]:
    card("Uncounted", f"{HP_CNT.value:,.0f} students said it happened; police recorded {HP_REC23.value:,.0f}. "
         f"{up_settled:.0%} of UP complaints never became cases.", hot=True)
with c4[3]:
    card("Unresolved", f"{JUST['cases convicted'].value:,.0f} convictions from {JUST['cases for trial'].value:,.0f} cases on trial; "
         f"{LC_UNAWARE.value:.0f}% of parents don't know how to report.", hot=True)
st.markdown(f"""
<div class="close"><b>What would change the picture</b><br>
① A national survey that asks Indian children directly, as the US, UK and HBSC countries do.&nbsp;
② One clear, child-friendly way to report.&nbsp; ③ Count complaints settled outside the crime record.&nbsp;
④ Publish child-specific court outcomes.
</div>""", unsafe_allow_html=True)
_TITLE[0] = "What it adds up to"
ev(as_frame(HB16, YR["all"], ONS19, IMPACT[IMPACT.outcome != "Anxiety"], PISA59, HP_CNT, HP_REC23, UPC, UPW, UPF,
            JUST["cases convicted"], JUST["cases for trial"], LC_UNAWARE))

with st.expander("Read with care: what this evidence can and cannot carry"):
    st.markdown(f"""
- **Surveys vs records.** Surveys ask children; NCRB counts registered crimes. Shown side by side, never converted.
- **India has no national survey.** Indian studies range from {EST_LO.value:.1f}% to {EST_HI.value:.2f}% depending on method.
- **Measures differ.** PISA ({PISA3.value:.0f}%), HBSC ({HB16.value:.0f}%), YRBS ({YR['all'].value:.0f}%), ONS ({ONS19.value:.1f}%) and
  Pew ({PEW46.value:.0f}%) ask different questions of different ages.
- **HBSC gives two national averages** ({HB15.value:.0f}% and {HB16.value:.0f}%); this page uses {HB16.value:.0f}%.
- **Court figures cover women and children together.**
- **Secondary reports recycle unsourced numbers:** a 2025 NGO report's "{CGS37.value:.0f}% of Indian children" has no source, and its
  {CGS1614.value:,.0f} cyberstalking cases for 2020 contradict NCRB's {SB_ALL20.value:,.0f}. One unsourced blog was excluded.
- **No Indian law treats cyberbullying as a distinct offence.**
- **States count differently.** Karnataka's own figures and NCRB's differ:
""")
    kc = pd.concat([KA_REPLY.assign(series="State reply: 'cyberbullying' cases"), KA_NCRB.assign(series="NCRB: all cyber crimes against children")])
    kc["year"] = kc.data_year.astype(int).astype(str).replace({"2025": "2025 (Jan–Jul)"})
    fig = px.bar(kc, x="year", y="value", color="series", barmode="group", text="value",
                 category_orders={"year": ["2022", "2023", "2024", "2025 (Jan–Jul)"]},
                 color_discrete_sequence=[ORANGE, BLUE], labels={"value": "cases", "year": ""}, hover_data={"id": True})
    fig.update_xaxes(type="category")  # otherwise "2022".."2024" parse as numbers and the 2025 bar is dropped
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    plot(fig, 300)
    _TITLE[0] = "Read with care"
    ev(as_frame(EST_LO, EST_HI, PISA3, HB15, HB16, YR["all"], ONS19, PEW46, CGS37, CGS1614, SB_ALL20, EXCLUDED, NOLAW, kc))

# ================================================================ ANNEXURE
st.divider()
st.header("Annexure", anchor="annexure")
st.caption("Sources, the evidence rows behind every chart, the full ledger, computed figures and checks.")

st.subheader("A. Sources")
reg = SOURCES.copy()
reg["origin"] = reg.apply(lambda s: "Main source list" if s.url in PROVIDED else
                          "Linked from a main-list page" if s.landing in PROVIDED else "Added (own research)", axis=1)
st.dataframe(reg[["source", "published", "rows", "origin", "url", "landing"]], hide_index=True, **FULL, column_config={
    "source": "Source", "published": "Published", "rows": "Ledger rows", "origin": "Origin",
    "url": st.column_config.LinkColumn("Document link", display_text="open"),
    "landing": st.column_config.LinkColumn("Publisher page", display_text="open")})

st.subheader("B. Evidence behind each chart")
COLS = ["id", "metric", "value", "unit", "geography", "data_year", "source", "source_url", "location", "checked", "anchor", "note"]
for n, (title, frame, computed, note) in enumerate(EVIDENCE, 1):
    st.markdown(f'<a id="ev-{n}"></a>', unsafe_allow_html=True)
    with st.expander(f"#{n} · {title} · {len(frame)} rows"):
        st.dataframe(frame[COLS], hide_index=True, **FULL, column_config={
            "data_year": st.column_config.NumberColumn("data_year", format="%d"),
            "source_url": st.column_config.LinkColumn("link", display_text="open")})
        for label, formula in computed:
            st.markdown(f"- Computed · {label}: `{formula}`")
        if note:
            st.caption(note)

st.subheader("C. Full evidence ledger")
fl = st.columns(4)
sc_ = fl[0].multiselect("Scope", sorted(ledger.scope.unique()))
cat = fl[1].multiselect("Category", sorted(ledger.category.unique()))
chk = fl[2].multiselect("Check", sorted(ledger.checked.unique()))
win = fl[3].selectbox("Years", ["All rows", "2020–2026 window only", "Outside window / undated"])
view = ledger
if sc_: view = view[view.scope.isin(sc_)]
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

st.subheader("D. Indicator baselines")
BASE = pd.DataFrame([
    ["Share cyberbullied, 44 countries (HBSC)", f"{HB16.value:.0f}%", int(HB16.data_year), HB16.id],
    ["Share electronically bullied, US high school (CDC)", f"{YR['all'].value:.0f}%", int(YR["all"].data_year), YR["all"].id],
    ["Share bullied online, 10–15, England & Wales (ONS)", f"{ONS19.value:.1f}%", int(ONS19.data_year), ONS19.id],
    ["Share cyberbullied, India national", "No figure", "—", "—"],
    ["Share cyberbullied, Himachal Pradesh students", f"{HPV.value:.2f}%", int(HPV.data_year), HPV.id],
    ["Recorded cyber crimes against children, India", f"{tot24:,.0f}", 2024, T24.id],
    ["Recorded cyber stalking/bullying of children, India", f"{sb24:,.0f}", 2024, SB24.id],
    ["Conviction rate, cyber stalking/bullying (women & children)", f"{JUST['conviction rate'].value:.1f}%", 2024, JUST["conviction rate"].id],
    ["Parents saying reporting is hard (self-selected poll)", f"{LC82.value:.0f}%", int(LC82.data_year), LC82.id],
    ["Online bullying–self-harm link (median, 21 countries)", f"{SH_MED.value:.2f}", int(SH_MED.data_year), SH_MED.id],
    ["Students given cyber hygiene training (I4C)", f"{HYGIENE.value / 1e5:.0f} lakh+", int(HYGIENE.data_year), HYGIENE.id],
], columns=["Indicator", "Baseline", "Data year", "Evidence row"])
BASE["Data year"] = BASE["Data year"].astype(str)
st.dataframe(BASE, hide_index=True, **FULL)

st.subheader("E. Checks and coverage")
left, right = st.columns(2)
with left:
    vs = ledger.copy()
    vs["short"] = vs.source.str.split(r"[,:(]").str[0].str.strip()
    cnt = vs.groupby(["short", "checked"]).size().rename("rows").reset_index()
    fig = px.bar(cnt, x="rows", y="short", color="checked", orientation="h", barmode="stack",
                 color_discrete_map={"✔ PDF-matched": BLUE, "✔ web-page-matched": AQUA, "✔ data-file-matched": PALETTE[6], "◉ scan viewed": GREY},
                 labels={"rows": "ledger rows", "short": ""})
    plot(fig, 560)
with right:
    cov = df.groupby(["scope", "data_year"]).size().unstack(fill_value=0).reindex(columns=YEARS, fill_value=0)
    long = cov.stack().rename("rows").reset_index()
    fig = px.bar(long, x="data_year", y="rows", color="scope", barmode="group",
                 color_discrete_sequence=PALETTE, labels={"data_year": "data year", "rows": "ledger rows"})
    fig.update_xaxes(dtick=1)
    plot(fig, 360)
    st.caption("Rows per data year inside the 2020–2026 window. India's NCRB counts run to 2024; 2025 and 2026 are not yet "
               "published. Pre-2020 baselines, secondary compilations and policy documents stay in the ledger only.")
