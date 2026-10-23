"""
Hidden in plain sight: cyberbullying of adolescents, global -> India, 2020-2026.
Run:  pip install streamlit pandas plotly
      streamlit run dashboard.py

Reads evidence_ledger.csv (same folder) and nothing else. Every number on screen is
pulled from a row of that file at runtime. Nothing is estimated. Figures calculated
here (differences, ratios, shares, roundings) are labelled "computed" and their
formula and input rows are shown in the evidence block beneath them.

The page follows the Stanford d.school design-thinking modes as a story:
Empathize -> Define -> Ideate -> Prototype -> Test, then a close and an appendix.
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
FULL = {"use_container_width": True}
VERIFIED = "programmatically matched in source PDF text"
CSV = Path(__file__).with_name("evidence_ledger.csv")
YEARS = range(2020, 2027)

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
.ev {font-size: .8rem; line-height: 1.5; opacity: .88; border-left: 3px solid rgba(128,128,128,.45);
     padding: .35rem .75rem; margin: .1rem 0 .25rem;}
.ev .h {font-weight: 700; text-transform: uppercase; letter-spacing: .07em; font-size: .7rem; margin-right: .35rem;}
.callout {border-radius: 14px; padding: 1.1rem 1.35rem; margin: .6rem 0 .3rem; font-size: 1.05rem; line-height: 1.6;
          background: rgba(235,104,52,.08); border: 1px solid rgba(235,104,52,.38);}
.callout .kicker {color: #c4521f; margin-bottom: .3rem;}
.heard {border-radius: 14px; padding: 1rem 1.3rem; margin: .8rem 0 .3rem; line-height: 1.6;
        background: rgba(42,120,214,.07); border: 1px solid rgba(42,120,214,.25);}
.hmw {border: 1px solid rgba(128,128,128,.28); border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: .8rem;}
.hmw .q {font-size: 1.08rem; font-weight: 650; line-height: 1.4; margin-bottom: .45rem;}
.hmw .b {font-size: .9rem; opacity: .85; line-height: 1.45;}
.hmw .r {font-size: .75rem; opacity: .65; margin-top: .35rem;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data + lookups
@st.cache_data
def load(mtime):
    d = pd.read_csv(CSV)
    d = d[d.data_year.between(2020, 2026)].copy()      # strict window: data-collection year
    d["metric"] = d.metric.str.strip()
    for c in ("scope", "geography", "category", "source", "unit", "location", "verification", "anchor"):
        d[c] = d[c].fillna("").astype(str)
    d["checked"] = d.verification.eq(VERIFIED).map({True: "✔ PDF-matched", False: "◐ web-read"})
    return d


df = load(CSV.stat().st_mtime)  # reloads when the CSV changes


def rows(*metrics, year=None, geo=None):
    """All ledger rows for these exact metric names. Fails loudly if any is missing."""
    q = df[df.metric.isin(metrics)]
    if year is not None:
        q = q[q.data_year == year]
    if geo is not None:
        q = q[q.geography == geo]
    missing = set(metrics) - set(q.metric)
    if missing:
        st.error(f"Ledger has no row for: {sorted(missing)} / {year} / {geo}")
        st.stop()
    return q


def row(metric, year=None, geo=None):
    q = rows(metric, year=year, geo=geo)
    if len(q) != 1:
        st.error(f"Ledger lookup returned {len(q)} rows for: {metric} / {year} / {geo}")
        st.stop()
    return q.iloc[0]


def v(metric, year=None, geo=None):
    return row(metric, year, geo).value


def rid(*keys):
    """Ledger IDs for (metric[, year[, geo]]) tuples or bare metric names, joined for display."""
    return ", ".join(row(*(k if isinstance(k, tuple) else (k,))).id for k in keys)


def as_frame(*items):
    """Combine rows (Series) and frames into one evidence frame."""
    parts = [i.to_frame().T if isinstance(i, pd.Series) else i for i in items]
    return pd.concat(parts).drop_duplicates("id")


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


# ---------------------------------------------------------------- presentation helpers
def ev(frame, computed=(), note=None):
    """Evidence block under a chart: a visible summary line, then every row and quote on demand."""
    frame = frame.drop_duplicates("id").sort_values("id")
    lines = []
    for src, g in frame.groupby("source", sort=False):
        locs = "; ".join(sorted(g.location.unique()))
        yrs = ", ".join(str(int(y)) for y in sorted(g.data_year.unique()))
        lines.append(f"<b>{escape(src)}</b> · {escape(locs)} · data year {yrs}")
    n_ok = int((frame.checked == "✔ PDF-matched").sum())
    checks = []
    if n_ok:
        checks.append(f"✔ {n_ok} matched word-for-word in the source PDF")
    if len(frame) - n_ok:
        checks.append(f"◐ {len(frame) - n_ok} read on the source web page")
    if computed:
        checks.append(f"{len(computed)} computed here (formula in drop-down)")
    st.markdown(f'<div class="ev"><span class="h">Evidence</span>{len(frame)} ledger row'
                f'{"s" if len(frame) != 1 else ""} ({id_ranges(frame.id)})<br>' + "<br>".join(lines)
                + "<br>" + " · ".join(checks) + "</div>", unsafe_allow_html=True)
    with st.expander("Open the evidence: each number, where it sits in the source, and the exact quote"):
        t = frame[["id", "metric", "value", "unit", "geography", "data_year", "source", "location", "checked", "anchor"]]
        t = t.rename(columns={"id": "Row", "metric": "What it measures", "value": "Value", "unit": "Unit",
                              "geography": "Where", "data_year": "Data year", "source": "Source",
                              "location": "Location in source", "checked": "Check",
                              "anchor": "Exact quote matched in source PDF"})
        st.dataframe(t, hide_index=True, **FULL)
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


def plot(fig, height=380):
    st.plotly_chart(style(fig, height), **FULL, config={"displayModeBar": False})


# ---------------------------------------------------------------- every number used in the story
HB16 = row("Cyberbullied (victim), all, body text")
HB15 = row("Cyberbullied (victim), all, key-findings text")
HB_GENDER = rows("Cyberbullied (victim), all, body text", "Cyberbullied (victim), boys", "Cyberbullied (victim), girls",
                 "Cyberbullying others, all", "Cyberbullying others, boys", "Cyberbullying others, girls")
vb, vg = v("Cyberbullied (victim), boys"), v("Cyberbullied (victim), girls")
pa, pb, pg = v("Cyberbullying others, all"), v("Cyberbullying others, boys"), v("Cyberbullying others, girls")
AGE_LABELS = {"Cyberbullying others, all 13y": "Age 13, all", "Cyberbullying others, 15y girls": "Age 15, girls",
              "Cyberbullying others, 15y boys": "Age 15, boys",
              "Cyberbullying others, highest cell": "Highest anywhere: Lithuania, boys age 15"}
HB_AGE = rows(*AGE_LABELS)
p13, p15g, p15b = v("Cyberbullying others, all 13y"), v("Cyberbullying others, 15y girls"), v("Cyberbullying others, 15y boys")
LT = row("Cyberbullying others, highest cell")

ANX = df[df.metric.str.startswith("Online bullying -> anxiety")].copy()
ANX["result"] = ANX.metric.str.contains("not significant").map({True: "Could be chance (not significant)",
                                                                 False: "Solid link (significant, p<.001)"})
ANX_NS = ANX[ANX.metric.str.contains("not significant")]
ANX_TOP = ANX.loc[ANX.value.idxmax()]
n_sig, n_anx = len(ANX) - len(ANX_NS), len(ANX)
DH_N = row("Children aged 12-17 surveyed (Disrupting Harm)")

HP = "Himachal Pradesh"
HP_ROWS = rows("Cyberbullying victimization, % of all respondents", "Cyberbullying perpetration, % of all respondents",
               "Any bullying victimization (physical or cyber), % of all respondents", year=2023, geo=HP)
HPV = row("Cyberbullying victimization, % of all respondents", 2023, HP)
hpv, hpp = HPV.value, v("Cyberbullying perpetration, % of all respondents", 2023, HP)
hpa = v("Any bullying victimization (physical or cyber), % of all respondents", 2023, HP)

NCRB_TOT = row("Cyber crimes against children, total cases", 2023)
NCRB_SPLIT = df[(df.data_year == 2023) & df.metric.str.startswith("of which")].copy()
NCRB_SB = row("of which: Cyber stalking/bullying of children", 2023)
sb23, tot23 = NCRB_SB.value, NCRB_TOT.value
csam23 = v("of which: Sec 67B IT Act (child sexual abuse material)", 2023)

CHILD = df[df.metric.str.startswith("Child victims (<18)")].copy()
CHILD_TOT = CHILD[CHILD.metric.str.contains("TOTAL")]
c20, c21, c22 = (v("Child victims (<18): TOTAL cyber crime, child victims", y) for y in (2020, 2021, 2022))
sb20c, sb22c = (v("Child victims (<18): Cyber stalking/bullying", y) for y in (2020, 2022))
CHILD_SB = rows("Child victims (<18): Cyber stalking/bullying")

ALLAGE = df[df.source.str.contains("PIB 2026")]
ALL_TOT = ALLAGE[ALLAGE.metric == "TOTAL cyber crime cases (all ages, all types)"]
b0, b4 = (v("TOTAL cyber crime cases (all ages, all types)", y) for y in (2020, 2024))

SX0, SX1 = row("Sextortion reports, 2021 baseline"), row("Sextortion reports, 2022")
IMG = row("Rise in self-generated imagery of 7-10 year olds, 2020-2022")
CSAMR = row("CSAM reports rise since 2019")
WP = as_frame(SX0, SX1, IMG, CSAMR)
UG = row("Countries where bullying rose >=2 pp for girls, 2018-2022 (of 66)")
UB = row("Countries where bullying rose >=2 pp for boys, 2018-2022 (of 66)")
UN = as_frame(UG, UB)
PISA = df[df.source.str.contains("PISA 2025")]
PISA_R = PISA.iloc[0]

class30 = 30 * HB16.value / 100
dots_hb, dots_hp = round(HB16.value), round(hpv)


def plus(r):
    return "+" if "+" in r.unit else ""


# ---------------------------------------------------------------- sidebar: the map of the story
with st.sidebar:
    st.markdown("### The story")
    st.markdown("[Start: the gap](#start)  \n[1 · Empathize](#empathize)  \n[2 · Define](#define)  \n"
                "[3 · Ideate](#ideate)  \n[4 · Prototype](#prototype)  \n[5 · Test](#test)  \n"
                "[The story in one breath](#close)  \n[Appendix: all evidence](#appendix)")
    st.divider()
    st.markdown("### The evidence base")
    n_ok = int((df.checked == "✔ PDF-matched").sum())
    st.markdown(f"**{len(df)}** numbers from **{df.source.nunique()}** sources, data years "
                f"{int(df.data_year.min())}–{int(df.data_year.max())}.  \n"
                f"✔ **{n_ok}** matched word-for-word in the source PDF  \n"
                f"◐ **{len(df) - n_ok}** read on the source web page")
    st.divider()
    st.markdown("### Words used here")
    st.markdown(
        "**Cyberbullying**: being repeatedly hurt, threatened or humiliated through phones, apps or the internet.  \n"
        "**Perpetration**: doing the bullying.  \n"
        "**CSAM**: child sexual abuse material (images or videos).  \n"
        "**Sextortion**: threatening to share someone's intimate images unless they comply.  \n"
        "**HBSC**: WHO's Health Behaviour in School-aged Children survey.  \n"
        "**NCRB**: India's National Crime Records Bureau, which counts crimes police register.  \n"
        "**PIB**: Press Information Bureau; publishes government replies in Parliament.  \n"
        "**PISA**: OECD's international student assessment.")

# ---------------------------------------------------------------- HERO: the hook
st.markdown(f"""
<div class="hero">
  <div class="kicker">Evidence dashboard · 2020–2026 · from the world to India</div>
  <h1>Hidden in plain sight: cyberbullying of adolescents</h1>
  <p>Across 44 countries, <b>{HB16.value:.0f} in every 100</b> adolescents say they have been cyberbullied, and in
  {n_sig} of {n_anx} countries studied, being bullied online goes hand in hand with anxiety. Yet in India, police
  records for all of 2023 show just <b>{sb23:,.0f}</b> cases of cyber stalking or bullying against children.
  This page follows that gap step by step: who is hurt, what the real problem is, what could be done, how to
  track it, and how far the evidence can be trusted.</p>
</div>""", unsafe_allow_html=True)
st.markdown('<a id="start"></a>', unsafe_allow_html=True)

h = st.columns(3)
with h[0]:
    stat(f"{HB16.value:.0f} in 100", "adolescents say they were cyberbullied",
         f"44 countries and regions, ages 11–15, survey year {int(HB16.data_year)}. "
         f"In a class of 30, that is about {class30:.0f} students.")
    ev(as_frame(HB16, HB15), computed=[("Students in a class of 30", f"30 × {HB16.value:.0f}% = {class30:.1f} ≈ {class30:.0f}")],
       note="The report's key findings say 15%; its body text says 16%. Both rows are kept, not reconciled.")
with h[1]:
    stat(f"{n_sig} of {n_anx}", "countries show a solid link between online bullying and anxiety",
         f"UNICEF Disrupting Harm survey of {DH_N.value:,.0f} children aged 12–17.")
    ev(as_frame(ANX, DH_N), computed=[("Countries with a significant link", f"count of significant rows = {n_sig} of {n_anx}")])
with h[2]:
    stat(f"{sb23:,.0f}", "recorded cases of cyber stalking or bullying of children, all India, 2023",
         f"Out of {tot23:,.0f} recorded cyber crimes against children that year.")
    ev(as_frame(NCRB_SB, NCRB_TOT))

st.markdown("#### How this page is built")
st.markdown("""
<div class="modes">
  <div><b><span>1</span>Empathize</b>Meet the young people: how often it happens, to whom, and what it does to them.</div>
  <div><b><span>2</span>Define</b>Pin down the real problem: what gets counted, and what slips through.</div>
  <div><b><span>3</span>Ideate</b>Turn each finding into a "How might we…?" question that invites solutions.</div>
  <div><b><span>4</span>Prototype</b>Draft a scorecard: what to track, and today's starting point.</div>
  <div><b><span>5</span>Test</b>Stress-test the evidence: how sure we are, and what is missing.</div>
</div>""", unsafe_allow_html=True)
st.caption("Under every chart is an Evidence line: source, table or page, data year and check status. Open its "
           "drop-down for every number and the exact quote. ✔ = matched word-for-word in the source PDF. "
           "◐ = read on the source web page. 'Computed' = calculated here from ledger rows; formula shown.")

# ================================================================ 1 EMPATHIZE
chapter(1, "Empathize", "empathize", "Meet the young people behind the numbers",
        "Before fixing anything, understand who is hurt, how often, and what it does to them. "
        "Picture each dot below as one student.")

st.subheader(f"{HB16.value:.0f} in every 100 adolescents across 44 countries say they have been cyberbullied")
left, right = st.columns(2)
with left:
    st.markdown(f"**International (HBSC, {int(HB16.data_year)})**: {dots_hb} of 100 dots filled")
    st.plotly_chart(icon_array(dots_hb), **FULL, config={"displayModeBar": False})
    ev(as_frame(HB16), computed=[("Dots filled", f"round({HB16.value:.0f}) = {dots_hb} of 100")])
with right:
    st.markdown(f"**India, Himachal Pradesh schools ({int(HPV.data_year)})**: {dots_hp} of 100 dots filled")
    st.plotly_chart(icon_array(dots_hp, color=ORANGE), **FULL, config={"displayModeBar": False})
    ev(as_frame(HPV), computed=[("Dots filled", f"round({hpv:.2f}) = {dots_hp} of 100")])
st.caption("Two different surveys with different questions, ages and places. Read each picture on its own, "
           "not as India versus the world.")

st.subheader(f"Girls and boys are bullied almost equally, but boys are more likely to do the bullying")
st.markdown(f"About {vb:.0f}% of boys and {vg:.0f}% of girls were cyberbullied. But {pb:.0f}% of boys said they "
            f"had cyberbullied someone, against {pg:.0f}% of girls.")
g = HB_GENDER.copy()
g["role"] = g.metric.str.startswith("Cyberbullied (victim)").map({True: "Was cyberbullied", False: "Cyberbullied others"})
g["group"] = g.metric.str.extract(r"(all|boys|girls)")[0].str.capitalize()
fig = px.bar(g, x="role", y="value", color="group", barmode="group", text="value",
             category_orders={"group": ["All", "Boys", "Girls"], "role": ["Was cyberbullied", "Cyberbullied others"]},
             color_discrete_sequence=PALETTE, labels={"value": "% of adolescents", "role": ""},
             hover_data={"id": True, "location": True})
fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
plot(fig, 360)
ev(g)

st.subheader(f"Bullying others peaks in the early teens, and can reach {LT.value:.0f}% in some places")
st.markdown(f"Across the survey, bullying others online is most common at age 13 ({p13:.0f}%). By 15, boys "
            f"({p15b:.0f}%) are almost twice as likely as girls ({p15g:.0f}%) to do it. The highest figure anywhere "
            f"is {LT.value:.0f}% among 15-year-old boys in Lithuania.")
a = HB_AGE.copy()
a["label"] = a.metric.map(AGE_LABELS)
a["highlight"] = a.metric.eq("Cyberbullying others, highest cell").map({True: "Highest cell", False: "Survey average"})
fig = px.bar(a.sort_values("value"), x="value", y="label", orientation="h", text="value", color="highlight",
             color_discrete_map={"Survey average": BLUE, "Highest cell": ORANGE},
             labels={"value": "% who cyberbullied others", "label": ""}, hover_data={"id": True, "anchor": True})
fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
plot(fig, 280)
ev(a, computed=[("'Almost twice'", f"{p15b:.0f} ÷ {p15g:.0f} = {p15b / p15g:.2f}")])

st.subheader("In India, the clearest view comes from one state's classrooms")
st.markdown(f"A 2023 survey of school students aged 13–17 in Himachal Pradesh found **{hpv:.2f}%** had been "
            f"cyberbullied and **{hpp:.2f}%** had cyberbullied someone else. Counting physical bullying too, "
            f"**{hpa:.1f}%** had been bullied in some way.")
hp = HP_ROWS.copy()
hp["label"] = hp.metric.str.replace(", % of all respondents", "", regex=False)
fig = px.bar(hp.sort_values("value"), x="value", y="label", orientation="h", text="value",
             color_discrete_sequence=[ORANGE], labels={"value": "% of students", "label": ""},
             hover_data={"id": True})
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
plot(fig, 240)
ev(hp, note="One state, school-going students only; not a national estimate.")

st.subheader("What it does to them: being bullied online goes hand in hand with anxiety")
st.markdown(f"Each bar shows how strongly being bullied online is connected to feeling anxious, on a standard "
            f"scale where 0 means no connection. **Blue** means the link is statistically solid; **grey** means it "
            f"could be chance. The link is solid in **{n_sig} of {n_anx}** countries, strongest in "
            f"{ANX_TOP.geography} ({ANX_TOP.value:.2f}). This shows the two go together; it does not prove one "
            f"causes the other.")
x = ANX.sort_values("value")
fig = px.bar(x, x="value", y="geography", orientation="h", text="value", color="result",
             color_discrete_map={"Solid link (significant, p<.001)": BLUE, "Could be chance (not significant)": GREY},
             labels={"value": "strength of link (standardised estimate)", "geography": ""},
             hover_data={"id": True, "anchor": True})
fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
plot(fig, 420)
ev(as_frame(ANX, DH_N))

st.markdown(f"""
<div class="heard"><div class="kicker">What we heard</div>
Cyberbullying is common: {HB16.value:.0f} in 100 adolescents internationally, about {class30:.0f} in a class of 30.
It touches girls and boys alike, while boys more often do it. It starts early, peaking at 13. And it is not
harmless: in most countries studied, it travels with anxiety.
</div>""", unsafe_allow_html=True)

# ================================================================ 2 DEFINE
chapter(2, "Define", "define", "Define the real problem",
        "What happens between a child being bullied online and anyone doing something about it? "
        "The evidence points to a gap between what young people go through and what gets counted.")

st.subheader("The reporting gap: what students say versus what police records show")
left, mid, right = st.columns([4, 5, 4])
with left:
    stat(f"{hpv:.2f}%", f"of surveyed students in one state said they had been cyberbullied",
         f"Himachal Pradesh school survey, {int(HPV.data_year)}. A self-report survey.")
    ev(as_frame(HPV))
with mid:
    st.markdown(f"""
<div class="callout" style="margin-top:0"><div class="kicker">Read with care</div>
These two numbers measure different things, so one cannot be divided by the other. Put side by side, they still
raise the central question: in a country where {hpv:.2f}% of students in a single state report being cyberbullied,
only {sb23:,.0f} cases of cyber stalking or bullying of children were recorded nationwide.
</div>""", unsafe_allow_html=True)
with right:
    stat(f"{sb23:,.0f}", "recorded cases of cyber stalking or bullying of children, all of India",
         f"NCRB, {int(NCRB_SB.data_year)}. Crimes registered by police.")
    ev(as_frame(NCRB_SB))

st.subheader(f"What the records do capture is mostly abuse imagery: {csam23 / tot23:.0%} of child cyber crime cases")
st.markdown(f"Of {tot23:,.0f} cyber crimes against children recorded in India in 2023, {csam23:,.0f} were about child "
            f"sexual abuse material. Cyber stalking or bullying made up {sb23 / tot23:.1%}.")
n = NCRB_SPLIT.copy()
n["type"] = n.metric.str.replace("of which: ", "", regex=False)
n["highlight"] = n.type.str.contains("stalking/bullying").map({True: "Cyber stalking/bullying", False: "Other categories"})
fig = px.bar(n.sort_values("value"), x="value", y="type", orientation="h", text="value", color="highlight",
             color_discrete_map={"Cyber stalking/bullying": ORANGE, "Other categories": BLUE},
             labels={"value": "recorded cases, 2023", "type": ""}, hover_data={"id": True})
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
plot(fig, 280)
ev(as_frame(n, NCRB_TOT), computed=[("CSAM share", f"{csam23:,.0f} ÷ {tot23:,.0f} = {csam23 / tot23:.1%}"),
                                    ("Stalking/bullying share", f"{sb23:,.0f} ÷ {tot23:,.0f} = {sb23 / tot23:.1%}")])

st.subheader(f"Recorded child victims are rising: {c20:,.0f} → {c22:,.0f} in two years")
st.markdown(f"Children recorded as victims of cyber crime grew {c22 / c20:.2f} times between 2020 and 2022. "
            f"Stalking or bullying stayed a small slice: {sb22c:,.0f} of {c22:,.0f} victims in 2022 ({sb22c / c22:.1%}).")
c = CHILD[~CHILD.metric.str.contains("TOTAL")].copy()
c["type"] = c.metric.str.replace("Child victims (<18): ", "", regex=False)
order = c.groupby("type").value.sum().sort_values(ascending=False).index.tolist()
fig = px.bar(c, x="data_year", y="value", color="type", barmode="stack", category_orders={"type": order},
             color_discrete_sequence=PALETTE, labels={"value": "child victims", "data_year": "year"},
             hover_data={"id": True})
fig.update_xaxes(dtick=1)
for _, r in CHILD_TOT.iterrows():
    fig.add_annotation(x=r.data_year, y=r.value, text=f"<b>{r.value:,.0f}</b>", showarrow=False, yshift=12)
plot(fig, 420)
ev(CHILD, computed=[("Growth 2020→2022", f"{c22:,.0f} ÷ {c20:,.0f} = {c22 / c20:.2f}x"),
                    ("Stalking/bullying share 2022", f"{sb22c:,.0f} ÷ {c22:,.0f} = {sb22c / c22:.1%}")])

st.subheader(f"Meanwhile, all cyber crime in India grew {b4 / b0:.2f} times in five years")
st.markdown(f"Across all ages and crime types, recorded cyber crime cases went from {b0:,.0f} in 2020 to "
            f"{b4:,.0f} in 2024. These counts include adults; they show the wider online setting children "
            f"are growing up in.")
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
    stat(f"+{CSAMR.value:.0f}%", "rise in child sexual abuse material reports since 2019")
ev(WP, computed=[("Sextortion multiple", f"{SX1.value:,.0f} ÷ {SX0.value:,.0f} = {SX1.value / SX0.value:.1f}x (lower bound)")])
u = st.columns(2)
with u[0]:
    stat(f"{UG.value:.0f} of 66", "countries where bullying of girls rose by 2+ percentage points, 2018–2022")
with u[1]:
    stat(f"{UB.value:.0f} of 66", "countries where bullying of boys rose by 2+ percentage points, 2018–2022")
ev(UN, note="UNESCO counts all bullying, not only cyberbullying.")

st.markdown(f"""
<div class="callout"><div class="kicker">Point of view: the problem, in one sentence</div>
Adolescents, {HB16.value:.0f} in 100 of whom say they have been cyberbullied, and for whom online bullying travels
with anxiety in {n_sig} of {n_anx} countries studied, <b>need online harm to be noticed, reported and counted</b>,
because India's police records show just {sb23:,.0f} cases of cyber stalking or bullying of children in 2023, while
in one state alone {hpv:.2f}% of surveyed students say it happened to them.
</div>""", unsafe_allow_html=True)
ev(as_frame(HB16, ANX, NCRB_SB, HPV), computed=[("Countries with a significant link", f"{n_sig} of {n_anx}")])

# ================================================================ 3 IDEATE
chapter(3, "Ideate", "ideate", "From evidence to “How might we…?”",
        "Design thinking turns a problem into open questions that invite many answers. Each question below "
        "grows straight out of a finding above. They are starting points for ideas, not conclusions.")

HMW = [
    ("make reporting online bullying as easy for a 13-year-old as sending a message?",
     f"Only {sb23:,.0f} cases of cyber stalking or bullying of children were recorded in India in 2023, while "
     f"{hpv:.2f}% of students in one state say they were cyberbullied.", as_frame(NCRB_SB, HPV)),
    ("reach boys before they start bullying others online?",
     f"{pb:.0f}% of boys versus {pg:.0f}% of girls cyberbullied others (HBSC); at age 15 it is {p15b:.0f}% versus "
     f"{p15g:.0f}%.", rows("Cyberbullying others, boys", "Cyberbullying others, girls",
                           "Cyberbullying others, 15y boys", "Cyberbullying others, 15y girls")),
    ("connect online-safety help with mental-health support?",
     f"Being bullied online is linked with anxiety in {n_sig} of {n_anx} countries studied.", ANX),
    ("step in around age 13, when bullying others peaks?",
     f"Cyberbullying others is highest at age 13 ({p13:.0f}%).", rows("Cyberbullying others, all 13y")),
    ("protect children from sextortion and abuse imagery, the fastest-growing harms?",
     f"Sextortion reports went from {SX0.value:,.0f} to {SX1.value:,.0f}{plus(SX1)}; {csam23 / tot23:.0%} of India's "
     f"recorded child cyber crimes in 2023 involved abuse material.", as_frame(SX0, SX1, NCRB_TOT,
                                                                             row("of which: Sec 67B IT Act (child sexual abuse material)", 2023))),
    ("see what is happening across all of India, not only one state?",
     "The only Indian survey of cyberbullying in the evidence covers Himachal Pradesh.", HP_ROWS),
]
cols = st.columns(2)
for i, (q, because, frame) in enumerate(HMW):
    with cols[i % 2]:
        st.markdown(f'<div class="hmw"><div class="q">How might we {escape(q)}</div>'
                    f'<div class="b"><b>Because:</b> {escape(because)}</div>'
                    f'<div class="r">Evidence rows: {id_ranges(frame.id)}</div></div>', unsafe_allow_html=True)
ev(as_frame(*[f for _, _, f in HMW]), computed=[("CSAM share 2023", f"{csam23:,.0f} ÷ {tot23:,.0f} = {csam23 / tot23:.1%}")],
   note="Every row cited by the six questions above.")

# ================================================================ 4 PROTOTYPE
chapter(4, "Prototype", "prototype", "A first-draft scorecard for tracking progress",
        "A prototype is a rough first version you can try and improve. Here: a draft set of indicators anyone "
        "working on this could track, with today's starting point from the evidence, and where no starting point exists.")

anx_lo, anx_hi = ANX.value.min(), ANX.value.max()
TOT = "Child victims (<18): TOTAL cyber crime, child victims"
ID_PERP = rid("Cyberbullying others, boys", "Cyberbullying others, girls")
ID_C22 = rid((TOT, 2022))
SCORE = pd.DataFrame([
    ["How common is it? (international)", "Share of adolescents cyberbullied", f"{HB16.value:.0f}%", int(HB16.data_year), HB16.id, "✔ Baseline exists"],
    ["How common is it? (India, national)", "Share of Indian adolescents cyberbullied", "No figure", "—", "—", "✖ Gap: no national survey"],
    ["How common is it? (India, one state)", "Share of Himachal Pradesh students cyberbullied", f"{hpv:.2f}%", int(HPV.data_year), HPV.id, "◐ One state only"],
    ["Who does it?", "Gap between boys and girls who cyberbully others", f"{pb - pg:+.0f} points (computed)", int(HB16.data_year), ID_PERP, "✔ Baseline exists"],
    ["Does it reach the system?", "Recorded cyber stalking/bullying cases against children, India", f"{sb23:,.0f}", int(NCRB_SB.data_year), NCRB_SB.id, "✔ Baseline exists"],
    ["Does it reach the system?", "Bullying share of recorded child cyber crimes, India", f"{sb23 / tot23:.1%} (computed)", int(NCRB_SB.data_year), f"{NCRB_SB.id}, {NCRB_TOT.id}", "✔ Baseline exists"],
    ["How big is recorded harm?", "Recorded child victims of cyber crime, India", f"{c22:,.0f}", 2022, ID_C22, "◐ Latest year 2022"],
    ["What does it do?", "Strength of online bullying–anxiety link", f"{anx_lo:.2f} to {anx_hi:.2f}", int(ANX.data_year.iloc[0]), id_ranges(ANX.id), "✖ No India estimate"],
    ["How fast are severe harms growing?", "Sextortion reports worldwide", f"{SX1.value:,.0f}{plus(SX1)}", int(SX1.data_year), SX1.id, "◐ Web-read, global"],
], columns=["Question", "Indicator", "Starting point", "Data year", "Evidence row", "Status"])
SCORE["Data year"] = SCORE["Data year"].astype(str)
st.table(SCORE[["Question", "Indicator", "Starting point", "Status", "Data year", "Evidence row"]].set_index("Question"))
score_ids = [HB16.id, HPV.id, NCRB_SB.id, NCRB_TOT.id, SX1.id, *ID_PERP.split(", "), ID_C22, *ANX.id]
ev(df[df.id.isin(score_ids)],
   computed=[("Boys–girls gap", f"{pb:.0f} − {pg:.0f} = {pb - pg:+.0f} points"),
             ("Bullying share", f"{sb23:,.0f} ÷ {tot23:,.0f} = {sb23 / tot23:.1%}"),
             ("Anxiety link range", f"min {anx_lo:.2f}, max {anx_hi:.2f} across {n_anx} countries")])

st.subheader("Try it yourself: explore India's recorded cyber crime trends")
st.markdown("Pick a series to see how it moved from 2020 to 2024. These are all-age counts, so they include adults.")
opts = sorted(ALLAGE.metric.unique())
metric = st.selectbox("Series", opts, index=opts.index("Cyber stalking/bullying of women & children (combined)"))
ss = ALLAGE[ALLAGE.metric == metric]
fig = px.line(ss, x="data_year", y="value", markers=True, color_discrete_sequence=[BLUE],
              labels={"value": f"recorded {ss.unit.iloc[0]}", "data_year": "year"}, hover_data={"id": True})
fig.update_traces(line_width=2, marker_size=9)
fig.update_xaxes(dtick=1)
fig.update_yaxes(rangemode="tozero")
plot(fig, 320)
f0, f1 = ss.sort_values("data_year").value.iloc[[0, -1]]
ev(ss, computed=[("Change 2020→2024", f"{f1:,.0f} − {f0:,.0f} = {f1 - f0:+,.0f} ({f1 / f0:.2f}x)")])

# ================================================================ 5 TEST
chapter(5, "Test", "test", "How sure can we be?",
        "Testing means looking for where the story could break. Here is what this evidence can carry, "
        "and what it cannot.")

left, right = st.columns(2)
with left:
    st.subheader("How each number was checked")
    vs = df.copy()
    vs["short"] = vs.source.str.split(",").str[0]
    vs["short"] = vs.short.where(vs.short.str.count(r"\(") <= vs.short.str.count(r"\)"), vs.short + ")")
    cnt = vs.groupby(["short", "checked"]).size().rename("rows").reset_index()
    fig = px.bar(cnt, x="rows", y="short", color="checked", orientation="h", barmode="stack",
                 color_discrete_map={"✔ PDF-matched": BLUE, "◐ web-read": GREY},
                 category_orders={"checked": ["✔ PDF-matched", "◐ web-read"]},
                 labels={"rows": "ledger rows", "short": ""})
    plot(fig, 380)
with right:
    st.subheader("Which years have evidence")
    cov = df.groupby(["scope", "data_year"]).size().unstack(fill_value=0).reindex(columns=YEARS, fill_value=0)
    long = cov.stack().rename("rows").reset_index()
    fig = px.bar(long, x="data_year", y="rows", color="scope", barmode="group",
                 color_discrete_sequence=PALETTE, labels={"data_year": "data year", "rows": "ledger rows"})
    fig.update_xaxes(dtick=1)
    plot(fig, 380)
    st.caption("Zero means no source with data for that year was found. Nothing is estimated. India: NCRB crime "
               "counts run to 2024 (July 2026 Lok Sabha reply); 2025 and 2026 not yet published. Global: OECD PISA "
               "2025 (published 8 Sep 2026) is the only 2025 row.")
ev(df, note="Both charts above count every row in the ledger. The full ledger is also in the appendix.")

pisa_metric = PISA_R.metric
st.subheader("Where the story could break")
st.markdown(f"""
- **Surveys and police records measure different things.** A survey asks young people what happened; NCRB counts
  crimes that were reported and registered. This page puts them side by side but never converts one into the other.
- **India has no national survey here.** The {hpv:.2f}% figure covers school students in one state (Himachal Pradesh).
- **The international figure has two versions.** The HBSC report says {HB15.value:.0f}% in its key findings and
  {HB16.value:.0f}% in its body text. This page uses {HB16.value:.0f}% and shows both.
- **The newest global number is thin.** OECD PISA 2025 calls cyberbullying "relatively rare" ({PISA_R.value:.0f}%
  as stated), but the exact question and base were not stated on the page read, so it is not compared with anything.
- **Victims and cases are not the same unit.** The 2020–2022 series counts child victims; the 2023 table counts cases.
- **A link is not a cause.** The anxiety figures show online bullying and anxiety go together, not that one causes the other.
- **{len(df) - n_ok} of {len(df)} numbers were read on web pages** and could not be re-checked offline against a PDF.
""")
ev(as_frame(HB15, HB16, HPV, PISA, CHILD_TOT, NCRB_TOT))

st.markdown("""
<div class="heard"><div class="kicker">What would make this story stronger</div>
A national Indian survey of cyberbullying among adolescents. NCRB figures for 2025 and 2026. The exact question
and base behind the PISA 2025 figure. Until then, treat the India picture as a strong signal, not a full measurement.
</div>""", unsafe_allow_html=True)

# ================================================================ CLOSE
st.markdown('<div class="mode"><i>✓</i>The close</div>', unsafe_allow_html=True)
st.header("The story in one breath", anchor="close")
st.markdown(f"""
<div class="callout"><div class="kicker">Start to finish</div>
<b>Empathize:</b> {HB16.value:.0f} in 100 adolescents internationally say they have been cyberbullied, and in {n_sig}
of {n_anx} countries it travels with anxiety.<br>
<b>Define:</b> in India, {hpv:.2f}% of students in one state report it, but police recorded only {sb23:,.0f} cases
against children nationwide in 2023, while the records that do exist are {csam23 / tot23:.0%} abuse imagery.<br>
<b>Ideate:</b> make reporting easy, reach boys early, link safety with mental health, and measure all of India.<br>
<b>Prototype:</b> a nine-line scorecard with today's starting points, and clear gaps where none exist.<br>
<b>Test:</b> every number traces to a source ({n_ok} matched word-for-word in a PDF, {len(df) - n_ok} read on web
pages); the biggest missing piece is a national Indian survey.<br><br>
<b>The ask:</b> count what children go through, not only what reaches a police station.
</div>""", unsafe_allow_html=True)
ev(as_frame(HB16, ANX, HPV, NCRB_SB, NCRB_TOT, row("of which: Sec 67B IT Act (child sexual abuse material)", 2023)),
   computed=[("CSAM share 2023", f"{csam23:,.0f} ÷ {tot23:,.0f} = {csam23 / tot23:.1%}")])

# ================================================================ APPENDIX
st.divider()
st.header("Appendix: all evidence", anchor="appendix")
with st.expander("Every computed figure on this page, with inputs"):
    calc = pd.DataFrame([
        ["Students in a class of 30 (HBSC)", HB16.id, f"30 × {HB16.value:.0f}%", f"{class30:.1f}"],
        ["India child cyber victims, 2020 → 2022", rid((TOT, 2020), (TOT, 2022)), f"{c22:,.0f} ÷ {c20:,.0f}", f"{c22 / c20:.2f}x"],
        ["India all-age cyber cases, 2020 → 2024", ", ".join(ALL_TOT.id.iloc[[0, -1]]), f"{b4:,.0f} ÷ {b0:,.0f}", f"{b4 / b0:.2f}x"],
        ["Stalking/bullying share of child victims, 2020", rid(("Child victims (<18): Cyber stalking/bullying", 2020), (TOT, 2020)),
         f"{sb20c:,.0f} ÷ {c20:,.0f}", f"{sb20c / c20:.1%}"],
        ["Stalking/bullying share of child victims, 2022", rid(("Child victims (<18): Cyber stalking/bullying", 2022), (TOT, 2022)),
         f"{sb22c:,.0f} ÷ {c22:,.0f}", f"{sb22c / c22:.1%}"],
        ["Stalking/bullying share of child cyber cases, 2023", f"{NCRB_SB.id}, {NCRB_TOT.id}", f"{sb23:,.0f} ÷ {tot23:,.0f}", f"{sb23 / tot23:.1%}"],
        ["CSAM share of child cyber cases, 2023", rid(("of which: Sec 67B IT Act (child sexual abuse material)", 2023)) + f", {NCRB_TOT.id}",
         f"{csam23:,.0f} ÷ {tot23:,.0f}", f"{csam23 / tot23:.1%}"],
        ["HBSC victim gap, girls − boys", rid("Cyberbullied (victim), girls", "Cyberbullied (victim), boys"), f"{vg:.0f} − {vb:.0f}", f"{vg - vb:+.0f} pp"],
        ["HBSC perpetrator gap, boys − girls", ID_PERP, f"{pb:.0f} − {pg:.0f}", f"{pb - pg:+.0f} pp"],
        ["Himachal Pradesh perpetration − victimization", rid(("Cyberbullying perpetration, % of all respondents", 2023, HP), (HPV.metric, 2023, HP)),
         f"{hpp:.2f} − {hpv:.2f}", f"{hpp - hpv:+.2f} pp"],
        ["Sextortion multiple (lower bound)", f"{SX0.id}, {SX1.id}", f"{SX1.value:,.0f} ÷ {SX0.value:,.0f}", f"{SX1.value / SX0.value:.1f}x"],
    ], columns=["computed figure", "input rows", "formula", "result"])
    st.dataframe(calc, hide_index=True, **FULL)

with st.expander("Full evidence ledger: filter, read, download", expanded=False):
    f = st.columns(4)
    sc = f[0].multiselect("Scope", sorted(df.scope.unique()))
    cat = f[1].multiselect("Category", sorted(df.category.unique()))
    chk = f[2].multiselect("Check", sorted(df.checked.unique()))
    yr = f[3].slider("Data year", int(df.data_year.min()), int(df.data_year.max()),
                     (int(df.data_year.min()), int(df.data_year.max())))
    view = df[df.data_year.between(*yr)]
    if sc: view = view[view.scope.isin(sc)]
    if cat: view = view[view.category.isin(cat)]
    if chk: view = view[view.checked.isin(chk)]
    st.caption(f"{len(view)} of {len(df)} rows")
    st.dataframe(view, hide_index=True, **FULL)
    st.download_button("Download filtered ledger CSV", view.drop(columns="checked").to_csv(index=False),
                       "evidence_ledger_filtered.csv", "text/csv")

with st.expander("Rows per year and sources by year"):
    cov.columns = [str(c) for c in cov.columns]
    st.dataframe(cov, **FULL)
    src = (df.groupby(["scope", "source"]).data_year.agg(lambda s: ", ".join(str(int(y)) for y in sorted(s.unique())))
           .rename("data years").reset_index())
    st.dataframe(src, hide_index=True, **FULL)
