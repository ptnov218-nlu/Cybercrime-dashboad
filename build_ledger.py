"""
Builds evidence_ledger.csv: one row per number used by the dashboard, each with a
clickable source URL, its location in the source, and an exact quote ("anchor").

Verification: download every source in SOURCES, convert it to plain text, and save it as
<text-dir>/<file> (PDFs: any PDF-to-text tool; web pages: HTML with tags stripped). Then run
    python build_ledger.py --text-dir path/to/sources_text
Each anchor is searched for in its source's text (whitespace, table bars, quote and dash
styles normalised). Rows whose anchor is found are marked as matched; any miss is reported
and marked "ANCHOR NOT FOUND". Rows with no number (policy documents) are marked as reviewed.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

# key: (short source name, url, landing page, published, text file, kind)
SOURCES = {
    "HBSC": ("WHO/Europe HBSC Vol. 2: A focus on adolescent peer violence and bullying (2024), survey 2021/22",
             "https://iris.who.int/server/api/core/bitstreams/1d8d101a-e414-4635-a1dc-5cb50ed2b5da/content",
             "https://www.who.int/europe/publications/i/item/9789289060929", "2024-03-27", "hbsc_vol2.txt", "pdf"),
    "WHO_PR": ("WHO/Europe press release: One in six school-aged children experiences cyberbullying (27 Mar 2024)",
               "https://www.who.int/europe/news/item/27-03-2024-one-in-six-school-aged-children-experiences-cyberbullying--finds-new-who-europe-study",
               "https://www.who.int/europe/news/item/27-03-2024-one-in-six-school-aged-children-experiences-cyberbullying--finds-new-who-europe-study",
               "2024-03-27", "who_pr.txt", "web"),
    "CDW_STATS": ("UNICEF Innocenti, Childhood in a Digital World (2025): statistical analysis background paper",
                  "https://www.unicef.org/innocenti/media/11321/file/UNICEF-Innocenti-Childhood-Digital-World-Statistical-Analysis-2025.pdf",
                  "https://www.unicef.org/innocenti/reports/childhood-digital-world", "2025-06", "unicef_cdw_stats.txt", "pdf"),
    "CDW_REPORT": ("UNICEF Innocenti, Childhood in a Digital World (2025): report",
                   "https://www.unicef.org/innocenti/media/11296/file/UNICEF-Innocenti-Childhood-in-a-Digital%20World-report-2025.pdf",
                   "https://www.unicef.org/innocenti/reports/childhood-digital-world", "2025-06", "unicef_cdw_report.txt", "pdf"),
    "NCRB23": ("NCRB, Crime in India 2023, Vol. II",
               "https://www.ncrb.mha.gov.in/uploads/files/2CrimeinIndia2023PartII2.pdf",
               "https://www.ncrb.mha.gov.in/uploads/files/2CrimeinIndia2023PartII2.pdf", "not stated in PDF", "ncrb2023_p2.txt", "pdf"),
    "NCRB24": ("NCRB, Crime in India 2024, Vol. II",
               "https://www.ncrb.mha.gov.in/uploads/files/2CrimeinIndia2024-VolumeII.pdf",
               "https://www.ncrb.mha.gov.in/uploads/files/2CrimeinIndia2024-VolumeII.pdf", "not stated in PDF", "ncrb2024_v2.txt", "pdf"),
    "PIB25": ("PIB, MHA Lok Sabha reply: Cyber-crime targeting children (29 Jul 2025)",
              "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2149788&reg=48&lang=2",
              "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2149788&reg=48&lang=2", "2025-07-29", "pib_2149788.txt", "web"),
    "PIB26": ("PIB, MHA Lok Sabha reply: National cyber crime data (21 Jul 2026)",
              "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287039&lang=1&reg=1",
              "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287039&lang=1&reg=1", "2026-07-21", "pib_2287039.txt", "web"),
    "WEP": ("WeProtect Global Alliance, Global Threat Assessment 2023: press release (17 Oct 2023)",
            "https://www.weprotect.org/wp-content/uploads/Global-Threat-Asssesment-2023-Press-Release.pdf",
            "https://www.weprotect.org/wp-content/uploads/Global-Threat-Asssesment-2023-Press-Release.pdf", "2023-10-17", "weprotect_pr.txt", "pdf"),
    "GEM": ("UNESCO GEM Report 2024/5: Monitoring SDG 4",
            "https://www.unesco.org/reports/gem-report/en/2024-monitoringsdg4",
            "https://www.unesco.org/reports/gem-report/en/2024-monitoringsdg4", "2024", "unesco_gem.txt", "web"),
    "PLOS": ("Bahl et al., PLOS ONE 21(4): e0345468 (2 Apr 2026), Himachal Pradesh school survey, ages 13-17",
             "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345468",
             "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345468", "2026-04-02", "plos_hp.txt", "web"),
    "PISA": ("OECD, PISA 2025 Results (Volume I) (Sep 2026)",
             "https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/09/pisa-2025-results-volume-i_5265bfb1/73451bc5-en.pdf",
             "https://www.oecd.org/en/publications/pisa-2025-results-volume-i_73451bc5-en/full-report/executive-summary_3701b0ef.html",
             "2026-09", "pisa2025_v1.txt", "pdf"),
    "BIO": ("Kharadi et al., Bioinformation 21(6): 1380-1384 (30 Jun 2025), video-assisted teaching, Mehsana (Gujarat) schools",
            "https://www.bioinformation.net/021/973206300211380.pdf",
            "https://www.bioinformation.net/021/973206300211380.pdf", "2025-06-30", "bioinfo.txt", "pdf"),
    "GKO": ("UNICEF Innocenti, Global Kids Online: Growing up in a connected world, comparative report (Nov 2019)",
            "https://www.unicef.org/innocenti/media/7011/file/GKO-Comparative-Report-2019.pdf",
            "https://www.unicef.org/innocenti/reports/global-kids-online-growing-connected-world", "2019-11", "gko2019.txt", "pdf"),
    "GKO_PAGE": ("UNICEF Innocenti, Global Kids Online: Growing up in a connected world (report page, Nov 2019)",
                 "https://www.unicef.org/innocenti/reports/global-kids-online-growing-connected-world",
                 "https://www.unicef.org/innocenti/reports/global-kids-online-growing-connected-world", "2019-11", "gko_page.txt", "web"),
    "POCSO": ("NCPCR, An Easy Guide to the POCSO Act and Rules, 2012",
              "https://ncpcr.gov.in/public/viewPdf/17833306256a4b774107204_175576490268a6d8a6c5bdf_posco2012.pdf",
              "https://ncpcr.gov.in/public/viewPdf/17833306256a4b774107204_175576490268a6d8a6c5bdf_posco2012.pdf", "n.d.", None, "scan"),
    "NCPCR_HB": ("NCPCR, User Handbook for Implementation of the POCSO Act",
                 "https://ncpcr.gov.in/public/viewPdf/17834007756a4c8947aee09_175585670368a83f3faec2c_userhandbook.pdf",
                 "https://ncpcr.gov.in/public/viewPdf/17834007756a4c8947aee09_175585670368a83f3faec2c_userhandbook.pdf", "n.d.", "ncpcr_handbook.txt", "pdf"),
    "NCPCR_SCH": ("NCPCR, Manual on Safety and Security of Children in Schools (2021)",
                  "https://ncpcr.gov.in/public/viewPdf/17834954586a4dfb2284359_a.pdf",
                  "https://ncpcr.gov.in/public/viewPdf/17834954586a4dfb2284359_a.pdf", "2021", "ncpcr_a.txt", "pdf"),
    "NCPCR_SAI": ("NCPCR / SAI, Guidelines for protection of children in SAI Training Centres",
                  "https://ncpcr.gov.in/public/viewPdf/17835058926a4e23e4473f2_b.pdf",
                  "https://ncpcr.gov.in/public/viewPdf/17835058926a4e23e4473f2_b.pdf", "n.d.", "ncpcr_b.txt", "pdf"),
    "NCPCR_PLAY": ("NCPCR, Regulatory guidelines for private play schools",
                   "https://ncpcr.gov.in/public/viewPdf/17835062196a4e252b6e7ad_c.pdf",
                   "https://ncpcr.gov.in/public/viewPdf/17835062196a4e252b6e7ad_c.pdf", "n.d.", "ncpcr_c.txt", "pdf"),
    "TOI_UP": ("Times of India: One case of cyberbullying in UP in every 8 minutes (15 Apr 2025), data from UP Police WCSO",
               "https://timesofindia.indiatimes.com/city/lucknow/one-case-of-cyberbullying-in-up-in-every-8-minutes/articleshow/120289739.cms",
               "https://timesofindia.indiatimes.com/city/lucknow/one-case-of-cyberbullying-in-up-in-every-8-minutes/articleshow/120289739.cms",
               "2025-04-15", "toi_up.txt", "web"),
    "TOI_KA": ("Times of India: Karnataka saw 315 cyberbullying cases between Jan 2022 and July 2025 (4 Sep 2025), Legislative Council reply",
               "https://timesofindia.indiatimes.com/city/mysuru/karnataka-saw-315-cyberbullying-cases-between-jan-2022-and-july-2025/articleshow/123682349.cms",
               "https://timesofindia.indiatimes.com/city/mysuru/karnataka-saw-315-cyberbullying-cases-between-jan-2022-and-july-2025/articleshow/123682349.cms",
               "2025-09-04", "toi_ka.txt", "web"),
    "LC": ("India Today: LocalCircles Safer Internet Day survey of urban parents (10 Feb 2026)",
           "https://www.indiatoday.in/health/story/online-bullying-in-teens-fuels-fear-and-anxiety-survey-finds-1-in-2-parents-worried-2866011-2026-02-10",
           "https://www.indiatoday.in/health/story/online-bullying-in-teens-fuels-fear-and-anxiety-survey-finds-1-in-2-parents-worried-2866011-2026-02-10",
           "2026-02-10", "indiatoday.txt", "web"),
    "MDPI": ("Mehari et al., Youth 5(3): 95 (10 Sep 2025), US and India (Delhi) cyberbullying cohort before and during COVID-19",
             "https://www.mdpi.com/2673-995X/5/3/95", "https://doi.org/10.3390/youth5030095", "2025-09-10", "mdpi.txt", "web"),
    "CGS": ("Coalition for Good Schools, Towards Safer Schools for Children: India country report (2025)",
            "https://coalitionforgoodschools.org/wp-content/uploads/2025/09/India_Country-Report_Final.pdf",
            "https://coalitionforgoodschools.org/wp-content/uploads/2025/09/India_Country-Report_Final.pdf", "2025-09", "cgs_india.txt", "pdf"),
    "FRONTLINE": ("Frontline: cyberbullying, teenagers, law and mental health in India (8 Aug 2025)",
                  "https://frontline.thehindu.com/social-issues/cyberbullying-teenagers-india-law-mental-health-ugc-social-media/article69905344.ece",
                  "https://frontline.thehindu.com/social-issues/cyberbullying-teenagers-india-law-mental-health-ugc-social-media/article69905344.ece",
                  "2025-08-08", "frontline.txt", "web"),
    "HINDU_UP": ("The Hindu: UP police warn of growing hybrid cybercrime threat (31 May 2026)",
                 "https://www.thehindu.com/news/national/uttar-pradesh/uttar-pradesh-police-warn-of-growing-hybrid-cybercrime-threat-stress-public-awareness/article71042340.ece",
                 "https://www.thehindu.com/news/national/uttar-pradesh/uttar-pradesh-police-warn-of-growing-hybrid-cybercrime-threat-stress-public-awareness/article71042340.ece",
                 "2026-05-31", "hindu_up.txt", "web"),
    "BLOG": ("Bullying Sin Fronteras blog: Bullying statistics in India",
             "https://bullyingsinfronteras.blogspot.com/2022/03/bullying-statistics-in-india-110000.html",
             "https://bullyingsinfronteras.blogspot.com/2022/03/bullying-statistics-in-india-110000.html", "2022-03 (updated Oct 2025)", "blog.txt", "web"),
}
HBSC_DB = "https://data-browser.hbsc.org/measure/cyberbullying-bullying-others/#chart"

R = []  # (src, scope, geography, data_year, category, metric, value, unit, location, anchor, note)


def add(src, scope, geo, year, cat, metric, value, unit, loc, anchor, note=""):
    R.append((src, scope, geo, year, cat, metric, value, unit, loc, anchor, note))


# ---- WHO/HBSC 2021/22 (44 countries/regions, ages 11/13/15) ----
G, H = "Global", "HBSC avg (44 countries/regions)"
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullied (victim), all, key-findings text", 15, "% of adolescents", "Key findings, PDF p.8",
    "Overall, 15% of adolescents reported being cyberbullied")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullied (victim), all, body text", 16, "% of adolescents", "Being cyberbullied, PDF p.17",
    "Overall, 16% of adolescents reported that they had been cyberbullied")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullied (victim), boys", 15, "% of adolescents", "Being cyberbullied, PDF p.17", "(15% of boys and 16% of girls)")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullied (victim), girls", 16, "% of adolescents", "Being cyberbullied, PDF p.17", "(15% of boys and 16% of girls)")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullying others, all", 12, "% of adolescents", "Cyberbullying others, PDF p.13",
    "12% of adolescents reported that they")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullying others, boys", 14, "% of adolescents", "Key findings, PDF p.8", "(14% of boys and 9% of girls)")
add("HBSC", G, H, 2022, "Prevalence", "Cyberbullying others, girls", 9, "% of adolescents", "Key findings, PDF p.8", "(14% of boys and 9% of girls)")
add("HBSC", G, "HBSC avg, age 15", 2022, "Prevalence", "Cyberbullying others, 15y girls", 8, "% of adolescents", "Annex, PDF p.27",
    "8% of 15-year-old girls and 15% of 15-year-old boys")
add("HBSC", G, "HBSC avg, age 15", 2022, "Prevalence", "Cyberbullying others, 15y boys", 15, "% of adolescents", "Annex, PDF p.27",
    "8% of 15-year-old girls and 15% of 15-year-old boys")
add("HBSC", G, "HBSC avg, age 13", 2022, "Prevalence", "Cyberbullying others, all 13y", 13, "% of adolescents", "Annex, PDF p.27",
    "highest at age 13 (13%)")
add("HBSC", G, "Lithuania, boys 15y", 2022, "Prevalence", "Cyberbullying others, highest cell", 40, "% of adolescents", "Annex, PDF p.27",
    "Fifteen-year-old boys in Lithuania report the highest prevalence of cyberbullying others (40%)")
add("HBSC", G, "Romania, girls 13y", 2022, "Prevalence", "Cyberbullying others, highest cell among girls", 24, "% of adolescents", "Annex, PDF p.27",
    "Among girls, 13-year-olds in Romania report the highest prevalence of cyberbullying others (24%)")
# 2018 baselines (outside the 2020-2026 window; context for the 2022 change)
add("WHO_PR", G, H, 2018, "Prevalence", "Cyberbullied (victim), boys", 12, "% of adolescents", "Press release text",
    "from 12% to 15% for boys and 13% to 16% for girls", "2018 baseline, outside 2020-2026 window")
add("WHO_PR", G, H, 2018, "Prevalence", "Cyberbullied (victim), girls", 13, "% of adolescents", "Press release text",
    "from 12% to 15% for boys and 13% to 16% for girls", "2018 baseline, outside 2020-2026 window")
add("WHO_PR", G, H, 2018, "Prevalence", "Cyberbullying others, boys", 11, "% of adolescents", "Press release text",
    "boys up from 11% and girls from 7%", "2018 baseline, outside 2020-2026 window")
add("WHO_PR", G, H, 2018, "Prevalence", "Cyberbullying others, girls", 7, "% of adolescents", "Press release text",
    "boys up from 11% and girls from 7%", "2018 baseline, outside 2020-2026 window")
add("WHO_PR", G, H, 2022, "Sample", "Young people surveyed (HBSC 2021/22)", 279000, "young people (over 279,000)", "Press release text", "279 000")

# ---- UNICEF Innocenti 2025: Disrupting Harm, online bullying and mental health ----
for outcome, table, page, rows in [
    ("anxiety", "Table A30", 50, [("Ethiopia", "0.32***", "0.27***"), ("Kenya", "0.18***", "0.16***"), ("Mozambique", "0.11", "0.16***"),
                                  ("Namibia", "0.25***", "0.33***"), ("Tanzania", "0.09", "0.31***"), ("Uganda", "0.08", "0.21***"),
                                  ("Cambodia", "0.27***", "0.26***"), ("Indonesia", "0.31***", "0.24***"), ("Malaysia", "0.43***", "0.29***"),
                                  ("Philippines", "0.32***", "0.21***"), ("Thailand", "0.08", "-0.03"), ("Vietnam", "0.38***", "-0.04")]),
    ("self-harm", "Table A31", 51, [("Ethiopia", "0.26***", "0.26**"), ("Kenya", "0.45***", "0.38***"), ("Mozambique", "0.52***", "0.39***"),
                                    ("Namibia", "0.33***", "0.36***"), ("Tanzania", "0.4***", "0.29***"), ("Uganda", "0.34***", "0.28***"),
                                    ("Cambodia", "0.27***", "0.36***"), ("Indonesia", "0.65***", "0.39***"), ("Malaysia", "0.37***", "0.64***"),
                                    ("Philippines", "0.24***", "0.4***"), ("Thailand", "0.73***", "0.77***"), ("Vietnam", "0.43***", "0.45***")]),
    ("suicidal thoughts/behaviours", "Table A32", 52, [("Ethiopia", "0.44***", "0.48***"), ("Kenya", "0.5***", "0.56***"), ("Mozambique", "0.53***", "0.54***"),
                                                       ("Namibia", "0.47***", "0.39***"), ("Tanzania", "0.44***", "0.55***"), ("Uganda", "0.4***", "0.3***"),
                                                       ("Cambodia", "0.54***", "0.59***"), ("Indonesia", "0.52***", "0.54***"), ("Malaysia", "0.62***", "0.67***"),
                                                       ("Philippines", "0.41***", "0.52***"), ("Thailand", "0.78***", "0.74***"), ("Vietnam", "0.45***", "0.52***")]),
]:
    for country, b, sexab in rows:
        sig = "significant (p<.001)" if b.endswith("***") else "not significant"
        add("CDW_STATS", G, country, 2021, "Association", f"Online bullying -> {outcome}, std. SEM estimate ({sig})",
            float(b.rstrip("*")), "standardised estimate", f"{table}, PDF p.{page}", f"{country} {b} {sexab}",
            "Disrupting Harm fieldwork; 2021 used as data year")
for outcome, med in [("anxiety", 0.31), ("suicidal thoughts/behaviours", 0.50), ("self-harm", 0.45)]:
    add("CDW_REPORT", G, "Disrupting Harm, 21 countries", 2021, "Association", f"Online bullying -> {outcome}, median std. estimate across countries",
        med, "standardised estimate (median)", "Appendix B, Table 1, PDF p.35",
        "Online bullying β median = 0.31 β range = 0.08 to 1.02 β median = 0.50 β range = 0.32 to 0.78 β median = 0.45")
add("CDW_REPORT", G, "Disrupting Harm, 21 countries", 2021, "Sample", "Children aged 12-17 surveyed (Disrupting Harm)", 21000, "children",
    "Data and methods box, PDF p.22", "the responses of 21,000 internet-using children aged 12–17")

# ---- India: recorded cyber crimes against children (cases), one NCRB series 2018-2024 ----
I, IA = "India", "India (all)"
CATS = ["Cyber blackmailing/threatening/harassment", "Fake profile", "Sexually explicit material depicting children (CSAM)",
        "Cyber stalking/bullying", "Online games/gaming apps", "Other cyber crimes against children", "TOTAL"]
PIB25_ANCH = ["Cyber Blackmailing/Threatening/Harassment 4 3 3 23 74", "Fake Profile 3 2 1 9 2",
              "Cyber Pornography/ Hosting or Publishing Obscene Sexual Materials depicting children 44 103 738 969 1171",
              "Cyber Stalking/Bullying 40 44 140 123 158", "Internet Crimes through Online Games etc 0 1 0 0 2",
              "Other Crimes against Children 141 153 220 252 416", "Total Cyber crimes against Children 232 306 1102 1376 1823"]
PIB25_VALS = [(4, 3, 3, 23, 74), (3, 2, 1, 9, 2), (44, 103, 738, 969, 1171), (40, 44, 140, 123, 158), (0, 1, 0, 0, 2),
              (141, 153, 220, 252, 416), (232, 306, 1102, 1376, 1823)]
for cat, anc, vals in zip(CATS, PIB25_ANCH, PIB25_VALS):
    for yr, val in zip(range(2018, 2023), vals):
        add("PIB25", I, IA, yr, "Recorded crime", f"Cyber crimes against children: {cat}", val, "cases", "Annexure table", anc,
            "outside 2020-2026 window" if yr < 2020 else "NCRB data via PIB")
for src, yr, loc, anc, vals in [
    ("NCRB23", 2023, "Table 9A.11, p.832", "TOTAL ALL INDIA 2 0 1499 28 0 373 1902", (2, 0, 1499, 28, 0, 373, 1902)),
    ("NCRB24", 2024, "Table 9A.11, p.967", "TOTAL ALL INDIA 19 0 1099 105 1 529 1753", (19, 0, 1099, 105, 1, 529, 1753)),
]:
    for cat, val in zip(CATS, vals):
        add(src, I, IA, yr, "Recorded crime", f"Cyber crimes against children: {cat}", val, "cases", loc, anc)
for src, yr, loc, rows in [
    ("NCRB23", 2023, "Table 9A.11, p.832", [("Himachal Pradesh", "9 Himachal Pradesh 0 0 2 0 0 2 4", 4), ("Kerala", "12 Kerala 0 0 342 3 0 98 443", 443),
                                           ("Karnataka", "11 Karnataka 0 0 341 0 0 22 363", 363), ("Rajasthan", "21 Rajasthan 0 0 254 6 0 46 306", 306),
                                           ("Chhattisgarh", "5 Chhattisgarh 2 0 187 0 0 4 193", 193)]),
    ("NCRB24", 2024, "Table 9A.11, p.967", [("Himachal Pradesh", "9 Himachal Pradesh 0 0 1 0 0 4 5", 5), ("Chhattisgarh", "5 Chhattisgarh 0 0 265 3 0 6 274", 274),
                                           ("Rajasthan", "21 Rajasthan 1 0 171 3 0 22 197", 197), ("Uttar Pradesh", "26 Uttar Pradesh 0 0 59 3 0 124 186", 186),
                                           ("Kerala", "12 Kerala 0 0 90 13 0 63 166", 166), ("Delhi", "32 Delhi 1 0 149 0 0 2 152", 152),
                                           ("Karnataka", "11 Karnataka 0 0 77 0 0 19 96", 96)]),
]:
    for geo, anc, val in rows:
        add(src, I, geo, yr, "Recorded crime", "Cyber crimes against children: TOTAL", val, "cases", loc, anc)

# ---- India: what happens to recorded cyber stalking/bullying cases (women and children combined) ----
SB = "Cyber stalking/bullying of women/children"
for src, yr, pol, crt in [
    ("NCRB23", 2023,
     ("Table 9A.4, pp.803-806", "Cyber Stalking/Bullying of Women/Children 1710 1305 0 3015 0", "Cyber Stalking/Bullying of Women/Children 191 3 257 287 539 826",
      "Cyber Stalking/Bullying of Women/Children 1101 7 3 1907 75.0 63.3", 3015, 826, 1907, 75.0, 63.3),
     ("Table 9A.6, pp.815-818", "Cyber Stalking/Bullying of Women/Children 2885 826 3711 2 0", "Cyber Stalking/Bullying of Women/Children 27 2 29 9 80",
      "Cyber Stalking/Bullying of Women/Children 118 149 3562 24.6 96.0", 3711, 29, 118, 3562, 24.6, 96.0)),
    ("NCRB24", 2024,
     ("Table 9A.4, pp.938-941", "Cyber Stalking/Bullying of Women/Children 1907 1240 3 3150 0", "Cyber Stalking/Bullying of Women/Children 141 3 194 315 471 786",
      "Cyber Stalking/Bullying of Women/Children 980 1 0 2169 80.2 68.9", 3150, 786, 2169, 80.2, 68.9),
     ("Table 9A.6, pp.950-953", "Cyber Stalking/Bullying of Women/Children 3562 786 4348 3 0", "Cyber Stalking/Bullying of Women/Children 29 4 33 2 110",
      "Cyber Stalking/Bullying of Women/Children 145 203 4145 22.8 95.3", 4348, 33, 145, 4145, 22.8, 95.3)),
]:
    loc, a1, a2, a3, inv, cs, pend, csr, pp = pol
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: cases for police investigation", inv, "cases", loc, a1)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: cases charge-sheeted", cs, "cases", loc, a2)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: pending investigation at year end", pend, "cases", loc, a3)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: charge-sheeting rate", csr, "%", loc, a3)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: police pendency", pp, "%", loc, a3)
    loc, a1, a2, a3, trial, conv, done, pend, cr, cp = crt
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: cases for trial", trial, "cases", loc, a1)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: cases convicted", conv, "cases", loc, a2)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: trials completed", done, "cases", loc, a3)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: pending trial at year end", pend, "cases", loc, a3)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: conviction rate", cr, "%", loc, a3)
    add(src, I, IA, yr, "Police & court disposal", f"{SB}: court pendency", cp, "%", loc, a3)
for src, yr, csr, a_csr, cr, a_cr, lp, lc in [
    ("NCRB23", 2023, 33.9, "Total Cyber Crimes 60618 47 13 100621 33.9 62.4", 27.6, "Total Cyber Crimes 3210 5968 74638 27.6 92.6", "Table 9A.4, p.806", "Table 9A.6, p.818"),
    ("NCRB24", 2024, 31.9, "Total Cyber Crimes 77975 45 24 124988 31.9 61.6", 56.8, "Total Cyber Crimes 4567 9063 90630 56.8 90.9", "Table 9A.4, p.941", "Table 9A.6, p.953"),
]:
    add(src, I, IA, yr, "Police & court disposal", "All cyber crimes: charge-sheeting rate", csr, "%", lp, a_csr)
    add(src, I, IA, yr, "Police & court disposal", "All cyber crimes: conviction rate", cr, "%", lc, a_cr)

# ---- India: all-age NCRB series 2020-2024 (PIB 2026 reply) ----
for lab, anc, vals in [
    ("Cyber stalking/bullying of women & children (combined)", "Cyber Stalking/Bullying of Women/Children 872 1176 1471 1305 1240", (872, 1176, 1471, 1305, 1240)),
    ("Cyber blackmailing/threatening", "Cyber Blackmailing/Threatening 303 689 696 689 601", (303, 689, 696, 689, 601)),
    ("Cyber fake profile", "Fake Profile 149 123 157 225 266", (149, 123, 157, 225, 266)),
    ("Abetment to suicide (online)", "Abetment of Suicide (Online) 10 10 24 30 12", (10, 10, 24, 30, 12)),
    ("Obscene/sexually explicit content in electronic form (IT Act)",
     "Publication/transmission of obscene / sexually explicit act in electronic form 6308 6598 6896 7893 6990", (6308, 6598, 6896, 7893, 6990)),
    ("TOTAL cyber crime cases (all ages, all types)", "Total Cyber Crimes (A+B+C) 50035 52974 65893 86420 101928", (50035, 52974, 65893, 86420, 101928)),
]:
    for yr, val in zip(range(2020, 2025), vals):
        add("PIB26", I, IA, yr, "Recorded crime", lab, val, "cases", "Annexure-II (crime head-wise)", anc)

# ---- India: response measures stated in the PIB replies ----
add("PIB26", I, IA, 2026, "Response", "CCPWC scheme funds released to States/UTs", 132.93, "Rs crore", "Reply text",
    "financial assistance to the tune of Rs. 132.93 crores under the ‘Cyber Crime Prevention against Women and Children (CCPWC)’ Scheme",
    "cumulative, as stated in Jul 2026 reply")
add("PIB26", I, IA, 2026, "Response", "States/UTs with cyber forensic-cum-training labs (CCPWC)", 33, "States/UTs", "Reply text",
    "Cyber forensic-cum-training laboratories have been commissioned in 33 States/UTs", "as stated in Jul 2026 reply")
add("PIB26", I, IA, 2026, "Response", "Police, judicial officers and prosecutors trained (CCPWC)", 24600, "people (24,600+)", "Reply text",
    "more than 24,600 LEA personnel, judicial officers and prosecutors have been provided training", "as stated in Jul 2026 reply")
add("PIB25", I, IA, 2025, "Response", "Students given cyber hygiene training by I4C (NCC, NSS, NYKS)", 200000, "students (2 lakh+)", "Reply text",
    "Cyber Hygiene training to more than 2 lakh NCC, NSS & NYKS Students", "as stated in Jul 2025 reply")

# ---- India: survey prevalence, Himachal Pradesh (fieldwork Nov-Dec 2023) ----
HP = "Himachal Pradesh"
for metric, val, anc in [
    ("Cyberbullying victimization, % of all respondents", 7.88, "596 (7.88%) reporting cyberbullying"),
    ("Cyberbullying perpetration, % of all respondents", 9.64, "729 (9.64%) in cyberbullying"),
    ("Any bullying victimization (physical or cyber), % of all respondents", 15.60, "1180 adolescents (15.60%) reported being victims of either form of bullying"),
    ("Physical bullying victimization, % of all respondents", 11.40, "862 (11.40%) experiencing physical bullying"),
    ("Any bullying perpetration (physical or cyber), % of all respondents", 18.41, "1392(18.41%) reported engaging in both form of bullying"),
]:
    add("PLOS", I, HP, 2023, "Prevalence", metric, val, "% of students", "Results, prevalence of bullying", anc, "fieldwork Nov-Dec 2023")
add("PLOS", I, HP, 2023, "Prevalence", "Students reporting cyberbullying victimization (count)", 596, "students", "Results, prevalence of bullying",
    "596 (7.88%) reporting cyberbullying", "fieldwork Nov-Dec 2023")
add("PLOS", I, HP, 2023, "Sample", "School students surveyed, ages 13-17", 7563, "students", "Results, participants",
    "A total of 7,563 school-going adolescents participated in the survey", "fieldwork Nov-Dec 2023")

# ---- India: school awareness intervention (small study) ----
add("BIO", I, "Mehsana district, Gujarat", 2025, "Intervention", "Students with poor cyberbullying knowledge, before video teaching", 48, "% of students",
    "Abstract", "48% of students had poor knowledge", "publication year; fieldwork year not stated; abstract says 60 students, methods say 100")
add("BIO", I, "Mehsana district, Gujarat", 2025, "Intervention", "Students with poor cyberbullying knowledge, after video teaching", 10, "% of students",
    "Abstract", "which dropped to 10% post-intervention", "publication year; fieldwork year not stated")
add("BIO", I, "Mehsana district, Gujarat", 2025, "Intervention", "Students with good cyberbullying knowledge, after video teaching", 60, "% of students",
    "Abstract", "knowledge rising to 60%", "publication year; fieldwork year not stated")

# ---- Global: OECD PISA 2025 (15-year-olds; India did not take part) ----
P = "OECD average (PISA 2025)"
add("PISA", G, P, 2025, "Prevalence", "Cyberbullied a few times a month or more (upsetting information published online without consent)", 3,
    "% of 15-year-old students", "Ch. on school climate, PDF p.265",
    "only 3% of students reported that information about them that was upsetting was published online without their consent at least a few times per month")
add("PISA", G, P, 2025, "Impact", "Science score gap, cyberbullied vs other students", 59, "PISA points", "PDF p.221",
    "victims scored 59 points lower in science than their peers on average")
add("PISA", G, P, 2025, "Impact", "Science score gap after socio-economic adjustment", 48, "PISA points", "PDF p.221",
    "and 48 points lower after accounting for socio-economic profile")
add("PISA", G, P, 2025, "Prevalence", "Cyberbullied students also bullied in other ways at least monthly", 90, "% (stated 'nine out of ten')", "PDF p.268",
    "of students who reported being cyberbullied, nine out of ten also reported that they experience other forms of bullying")
add("PISA", G, "86 PISA countries/economies", 2025, "Impact", "Systems where cyberbullying victims scored lower in science (of 86)", 82, "countries/economies",
    "PDF p.268", "In the 82 out of 86 countries and economies with available data")

# ---- Global: severe online harms (WeProtect GTA 2023) ----
W = "Global (WeProtect)"
add("WEP", G, W, 2022, "Online child sexual exploitation", "Child sexual abuse reports worldwide (NCMEC)", 32000000, "reports (32 million+)", "PDF p.1",
    "with over 32 million reports globally (NCMEC)")
add("WEP", G, W, 2022, "Online child sexual exploitation", "CSAM reports rise since 2019", 87, "% increase", "PDF p.1",
    "87% increase in reported child sexual abuse material cases since 2019")
add("WEP", G, W, 2022, "Online child sexual exploitation", "Rise in self-generated imagery of 7-10 year olds, 2020-2022", 360, "% increase", "PDF p.1",
    "360% increase in self-generated sexual imagery of 7-10-year-olds from 2020 to 2022")
add("WEP", G, W, 2021, "Online child sexual exploitation", "Sextortion reports, 2021 baseline", 139, "reports", "PDF p.1",
    "jumping from 139 in 2021 to over 10,000 reports in 2022")
add("WEP", G, W, 2022, "Online child sexual exploitation", "Sextortion reports, 2022", 10000, "reports (10,000+)", "PDF p.1",
    "jumping from 139 in 2021 to over 10,000 reports in 2022")
add("WEP", G, W, 2023, "Online child sexual exploitation", "Time for gaming-platform chats to escalate to high-risk grooming", 19, "seconds", "PDF p.1",
    "high-risk grooming situations within 19 seconds", "data year not stated; publication year used")
add("WEP", G, W, 2023, "Online child sexual exploitation", "Average grooming time on social gaming platforms", 45, "minutes", "PDF p.1",
    "with an average grooming time of just 45 minutes", "data year not stated; publication year used")
add("WEP", G, W, 2023, "Online child sexual exploitation", "Online abuse cases where the perpetrator was likely known to the child (Disrupting Harm)", 60,
    "% of cases", "PDF p.8", "in 60% of all cases of online abuse, the perpetrator was likely to be known to the child",
    "data year not stated; publication year used")

# ---- Global: UNESCO GEM 2024/5 ----
U = "66 countries (UNESCO GEM)"
add("GEM", G, U, 2022, "Trend", "Countries where bullying rose >=2 pp for girls, 2018-2022 (of 66)", 34, "countries", "Target 4.a section",
    "In 34 of the 66 countries with available data, bullying increased by at least 2 percentage points for girls")
add("GEM", G, U, 2022, "Trend", "Countries where bullying rose >=2 pp for boys, 2018-2022 (of 66)", 22, "countries", "Target 4.a section",
    "The same was true for boys in only 22 countries")
add("GEM", G, "Türkiye", 2022, "Trend", "Rise in share of 15-year-old girls bullied", 18, "percentage points", "Target 4.a section",
    "the share of 15-year-old girls who experienced bullying increased by 18 percentage points")
add("GEM", G, "Türkiye", 2022, "Trend", "Rise in share of 15-year-old boys bullied", 7, "percentage points", "Target 4.a section",
    "compared to 7 percentage points for boys")

# ---- Pre-2020 baseline (outside window; annexure only) ----
add("GKO", G, "11 countries (Global Kids Online)", 2019, "Prevalence", "Children treated in a hurtful or nasty way in the past year, low end of country range", 10,
    "% of internet-using children", "Comparative report, PDF p.56", "between around 10 and 30 per cent of children report being treated in this way in the past year",
    "fieldwork 2016-2019, outside 2020-2026 window")
add("GKO", G, "11 countries (Global Kids Online)", 2019, "Prevalence", "Children treated in a hurtful or nasty way in the past year, high end of country range", 30,
    "% of internet-using children", "Comparative report, PDF p.56", "between around 10 and 30 per cent of children report being treated in this way in the past year",
    "fieldwork 2016-2019, outside 2020-2026 window")
add("GKO_PAGE", G, "11 countries (Global Kids Online)", 2019, "Sample", "Internet-using children surveyed (Global Kids Online)", 14000, "children (14,000+)",
    "Report page", "more than 14,000 internet-using children across 11 countries", "fieldwork 2016-2019, outside 2020-2026 window")

# ---- India: legal and policy framework (no statistic) ----
for src, year, metric, loc, anc in [
    ("POCSO", None, "POCSO Act 2012 guide: child-friendly reporting via NCPCR POCSO e-box and helpline 9868235077", "Page 1 (scanned)", ""),
    ("NCPCR_HB", None, "POCSO user handbook: defines online abuse, including cyber bullying and grooming", "Ch. I, PDF p.13",
     "Children and young people may experience cyber bullying, grooming, sexual abuse, sexual exploitation or emotional abuse"),
    ("NCPCR_SCH", 2021, "School safety manual: chapter on cyber safety and security; POCSO e-box reporting route", "Contents p.6; PDF p.58",
     "POCSO e-box is a major initiative by NCPCR to help children seek help and report such crimes directly to the Commission"),
    ("NCPCR_SAI", None, "SAI child-protection guidelines: online portal/help desk for trainees to report grievances", "PDF p.3",
     "An online portal/ designated help desk/phonefor trainees to report their grievances"),
    ("NCPCR_PLAY", None, "Play-school guidelines: cyber safety checklist, incl. handling cyber-bullying", "Checklist items 54-60, PDF p.24",
     "Cyber-bullying or harassment is handled with utmost care"),
]:
    add(src, I, IA, year, "Policy framework", metric, None, "", loc, anc, "policy document; no statistic")


# ---- India: state-level complaint and case data reported in the news ----
UP = "Uttar Pradesh"
for metric, val, unit, anc in [
    ("Cyberbullying complaints received (UP Police WCSO / 1090)", 66854, "complaints",
     "Uttar Pradesh reported a staggering 66,854 cases of cyberbullying in 2024"),
    ("Cyberbullying complaints filed by people aged 16-25", 45000, "complaints (45,000+)",
     "more than 45,000—were filed by individuals aged 16 to 25"),
    ("Complaints resolved at first stage (counsellor warning call)", 59771, "complaints", "59,771 cases were resolved at the first stage"),
    ("Complaints resolved via Friends, Family and Relatives cell", 5166, "complaints", "Around 5,166 cases were resolved at this stage alone"),
    ("Cyberbullying complaints from Lucknow", 9839, "complaints", "The maximum 9,839 cases were received from Lucknow"),
]:
    add("TOI_UP", I, UP, 2024, "Helpline complaints", metric, val, unit, "Article text", anc,
        "news report of data accessed from UP Police Women and Child Security Organisation; complaints, not FIRs")
for yr, val in [(2022, 105), (2023, 117), (2024, 66), (2025, 27)]:
    add("TOI_KA", I, "Karnataka", yr, "Recorded crime (state reply)", "Cyberbullying cases against children registered (Karnataka govt reply)",
        val, "cases", "Year-wise table in article", "2022: 105 2023: 117 2024: 66 2025 till July: 27",
        ("Jan-Jul 2025 only; " if yr == 2025 else "") + "registered under IT Act s.67B per the article; does not match NCRB definitions")
add("TOI_KA", I, "Karnataka", 2025, "Recorded crime (state reply)", "Cyberbullying cases against children, Jan 2022-Jul 2025 total (Karnataka)",
    315, "cases", "Article text", "Karnataka recorded as many as 315 cyberbullying cases between Jan 2022 and July 2025",
    "period total; Legislative Council reply quoted by the article")

# ---- India: parents' experience of reporting (online, self-selected poll) ----
LCN = "LocalCircles poll (urban India)"
for metric, val, anc in [
    ("Parents saying children aged 9-17 were exposed to inappropriate content or bullying online", 50,
     "50 per cent of urban parents confirmed their children had been exposed to inappropriate material or bullying online"),
    ("Reporting online bullying/harmful content: very easy and effective", 8,
     'Out of 18,151 who responded to the question 8% indicated that it is "very easy and effective"'),
    ("Reporting online bullying/harmful content: somewhat easy but slow or unclear", 7,
     '7 per cent of respondents indicated that it is "Somewhat easy but slow or unclear"'),
    ("Reporting online bullying/harmful content: difficult and time-consuming", 17,
     '17 per cent of respondents indicated that reporting is "difficult and time-consuming"'),
    ("Reporting online bullying/harmful content: very difficult, complaints usually unresolved", 29,
     '29 per cent of respondents indicated that it is in fact "verydifficult; complaints usually go unresolved"'),
    ("Reporting online bullying/harmful content: not aware of any clear reporting mechanism", 29,
     '29 per cent of respondents indicated that they are "not aware of any clear reporting mechanism"'),
    ("Reporting online bullying/harmful content: no clear answer", 10, "10 per cent of respondents did not give a clear answer"),
    ("Parents saying reporting is difficult, slow or unclear", 82,
     "82 per cent parents of children between ages 9-17 surveyed say reporting online bullying"),
]:
    add("LC", I, LCN, 2026, "Parent survey (online, self-selected)", metric, val, "% of responding parents", "Article text", anc,
        "online poll, not a representative sample; fieldwork dates not stated, publication year used")
add("LC", I, LCN, 2026, "Sample", "Parents answering the reporting question (LocalCircles)", 18151, "parents", "Article text",
    "Out of 18,151 who responded to the question", "online poll, not a representative sample")

# ---- India: small Delhi cohort and the spread of Indian estimates ----
DL = "Delhi NCR schools (cohort)"
add("MDPI", I, DL, 2019, "Survey (small cohort)", "Cybervictimization, past 30 days, before COVID-19 (T1)", 35.1, "% of youth aged 9-15",
    "Results 4.2", "at T1, 33.9% of youth reported engaging in cyberbullying, and 35.1% reported experiencing cybervictimization",
    "fieldwork Oct 2019-Jan 2020, outside 2020-2026 window; n=178")
add("MDPI", I, DL, 2019, "Survey (small cohort)", "Cyberbullying perpetration, past 30 days, before COVID-19 (T1)", 33.9, "% of youth aged 9-15",
    "Results 4.2", "at T1, 33.9% of youth reported engaging in cyberbullying", "fieldwork Oct 2019-Jan 2020, outside 2020-2026 window; n=178")
add("MDPI", I, DL, 2019, "Sample", "Delhi youth surveyed before COVID-19, ages 9-15", 178, "youth", "Methods",
    "The India participants were 178 youth aged 9–15 years", "fieldwork Oct 2019-Jan 2020")
add("MDPI", I, DL, 2020, "Sample", "Delhi cohort retained after COVID-19 onset", 21.3, "% retained (n = 38)", "Results 4.1",
    "the retention rate was 21.3% (n = 38)", "lower-income youth significantly less likely to remain")
add("MDPI", I, "India (studies reviewed)", None, "Secondary compilation", "Cyberbullying prevalence among Indian adolescents, lowest study estimate", 3.3,
    "%", "Introduction (citing Vijayarani et al., 2024)", "from 3.3 to 60.56%", "range across studies, cited by the paper; no single data year")
add("MDPI", I, "India (studies reviewed)", None, "Secondary compilation", "Cyberbullying prevalence among Indian adolescents, highest study estimate", 60.56,
    "%", "Introduction (citing Vijayarani et al., 2024)", "from 3.3 to 60.56%", "range across studies, cited by the paper; no single data year")

# ---- Secondary compilation (figures without cited sources; annexure only) ----
for metric, val, anc, note in [
    ("Children aged 10-17 who experienced cyberbullying (key finding, source not cited)", 37,
     "37% of children (10-17 years) having experienced cyberbullying", "no source or data year given for this key finding"),
    ("Children aged 10-17 exposed to online sexual exploitation (key finding, source not cited)", 14,
     "14% exposed to online sexual exploitation", "no source or data year given for this key finding"),
    ("Students in grades 6-12 reporting being bullied (key finding, source not cited)", 34,
     "34% of students (Grades 6-12) report being bullied", "no source or data year given for this key finding"),
    ("Cyberstalking cases in 2020 (as stated by the report)", 1614, "Among these, 1614 cases of cyberstalking",
     "conflicts with NCRB via PIB 2026: 872 cyber stalking/bullying cases of women/children in 2020"),
]:
    add("CGS", I, IA, None, "Secondary compilation", metric, val, "% / cases as stated", "Key findings p.4; p.8", anc, note)

# ---- Policy and context from news reporting (no statistic) ----
for src, year, metric, loc, anc in [
    ("FRONTLINE", 2025, "UGC directive (9 Jul 2025): colleges to monitor student WhatsApp groups; online harassment of juniors treated as ragging",
     "Article text", "On July 9, the University Grants Commission (UGC) issued a directive"),
    ("FRONTLINE", 2023, "Telangana police Cyber Ambassadors Platform (Jan 2023): students and teachers trained as peer cyber-safety officers",
     "Article text", "launched the Cyber Ambassadors Platform in January 2023"),
    ("FRONTLINE", None, "No Indian law (IT Act, BNS, JJ Act) treats cyberbullying as a distinct offence", "Article text",
     "none of these laws address cyberbullying as a distinct offence"),
    ("CGS", None, "No specific law against bullying in India", "p.9", "There is no specific law against bullying in India"),
    ("HINDU_UP", 2026, "UP Police expanded the 1930 cyber helpline with a dedicated call centre in Lucknow; minors named as vulnerable to blackmail, "
     "morphing and sextortion", "Article text", "U.P. Police has expanded its 1930 cyber helpline capacity with a dedicated call-centre setup in Lucknow"),
]:
    add(src, I, IA, year, "Policy framework", metric, None, "", loc, anc, "context from news reporting; no statistic")
add("BLOG", I, IA, None, "Excluded source", "Blog compilation of bullying statistics (not used: unsourced, implausible global claims)", None, "",
    "Blog text", "200,000 children and adolescents die each year worldwide as a result of bullying and cyberbullying",
    "excluded from the dashboard story; kept here for transparency")


def norm(s):
    s = s.replace("|", " ").replace(" ", " ")
    for a, b in (("‐", "-"), ("–", "-"), ("—", "-"), ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-dir", required=True, help="folder with the plain-text copies of each source")
    ap.add_argument("--out", default=str(Path(__file__).with_name("evidence_ledger.csv")))
    args = ap.parse_args()
    cache, ok, bad = {}, 0, 0
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "scope", "geography", "data_year", "category", "metric", "value", "unit", "source", "source_url",
                    "landing_url", "published", "location", "verification", "anchor", "note"])
        for i, (src, scope, geo, yr, cat, metric, val, unit, loc, anc, note) in enumerate(R, 1):
            name, url, landing, pub, txt, kind = SOURCES[src]
            if src == "HBSC" and metric.startswith("Cyberbullying others"):
                landing = HBSC_DB
            if kind == "scan":
                ver = "scanned PDF; page viewed (no machine-readable text)"
            else:
                if txt not in cache:
                    cache[txt] = norm((Path(args.text_dir) / txt).read_text(errors="ignore"))
                if norm(anc) in cache[txt]:
                    ver = f"matched in source {'PDF' if kind == 'pdf' else 'web page'} text"
                    ok += 1
                else:
                    ver = "ANCHOR NOT FOUND"
                    bad += 1
                    print("MISS", f"E{i:03d}", src, metric, "|", anc, file=sys.stderr)
            w.writerow([f"E{i:03d}", scope, geo, "" if yr is None else yr, cat, metric, "" if val is None else val, unit,
                        name, url, landing, pub, loc, ver, anc, note])
    print(len(R), "rows; matched", ok, "missing", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
