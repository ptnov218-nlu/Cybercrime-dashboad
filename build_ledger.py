import csv, re, sys, pathlib
UP = pathlib.Path("/tmp/claude-0/-home-claude/927f3a8d-6666-5f16-bd81-2185567067f1/scratchpad/up")
FILES = {"hbsc": "hbsc_raw.txt", "ncrb": "ncrb2023.txt", "stat": "stat.txt", "report": "report.txt"}
txt = {k: re.sub(r"\s+", " ", (UP/v).read_text(errors="ignore")) for k, v in FILES.items()}

# id, scope, geography, data_year, category, metric, value, unit, source, location, file_key, anchor
R = []
def add(*a): R.append(a)
H = "WHO/HBSC Vol.2 Peer violence & bullying (2024), survey 2021/22"
for gid, geo, m, v, anc in [
 ("Global","HBSC avg (44 countries/regions)","Cyberbullied (victim), all, key-findings text",15,"Overall, 15% of adolescents reported being cyberbullied"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullied (victim), all, body text",16,"Overall, 16% of adolescents reported that they had been cyberbullied"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullied (victim), boys",15,"(15% of boys and 16% of girls)"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullied (victim), girls",16,"(15% of boys and 16% of girls)"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullying others, all",12,"12% of adolescents reported that they had cyberbullied others"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullying others, boys",14,"(14% of boys and 9% of girls)"),
 ("Global","HBSC avg (44 countries/regions)","Cyberbullying others, girls",9,"(14% of boys and 9% of girls)"),
 ("Global","HBSC avg, age 15","Cyberbullying others, 15y girls",8,"8% of 15-year-old girls and 15% of 15-year-old boys"),
 ("Global","HBSC avg, age 15","Cyberbullying others, 15y boys",15,"8% of 15-year-old girls and 15% of 15-year-old boys"),
 ("Global","HBSC avg, age 13","Cyberbullying others, all 13y",13,"highest at age 13 (13%)"),
 ("Global","Lithuania, boys 15y","Cyberbullying others, highest cell",40,"Lithuania report the highest prevalence of cyberbullying others (40%)"),
 ]:
    add(gid,geo,2022,"Prevalence",m,v,"% of adolescents",H,"Key findings / Ch.2-3 / Annex","hbsc",anc)

D="UNICEF Innocenti Childhood in a Digital World (2025), Background paper Table A30"
for c,b in [("Ethiopia","0.32***"),("Kenya","0.18***"),("Namibia","0.25***"),("Cambodia","0.27***"),("Indonesia","0.31***"),
            ("Malaysia","0.43***"),("Philippines","0.32***"),("Vietnam","0.38***"),("Mozambique","0.11"),("Tanzania","0.09"),("Uganda","0.08"),("Thailand","0.08")]:
    anc = {"Ethiopia":"Ethiopia 0.32*** 0.27***","Kenya":"Kenya 0.18*** 0.16***","Namibia":"Namibia 0.25*** 0.33***","Cambodia":"Cambodia 0.27*** 0.26***",
           "Indonesia":"Indonesia 0.31*** 0.24***","Malaysia":"Malaysia 0.43*** 0.29***","Philippines":"Philippines 0.32*** 0.21***","Vietnam":"Vietnam 0.38*** -0.04",
           "Mozambique":"Mozambique 0.11 0.16***","Tanzania":"Tanzania 0.09 0.31***","Uganda":"Uganda 0.08 0.21***","Thailand":"Thailand 0.08 -0.03"}[c]
    sig = "significant (p<.001)" if b.endswith("***") else "not significant"
    add("Global",c,2021,"Association",f"Online bullying -> anxiety, std. SEM estimate ({sig})",float(b.rstrip('*')),"standardised estimate",D,"Table A30","stat",anc)

add("Global","Disrupting Harm, 21 countries",2021,"Sample","Children aged 12-17 surveyed (Disrupting Harm)",21000,"children","UNICEF Innocenti 2025 report","Methods box","report","the responses of 21,000")

# NCRB 2023 (uploaded PDF) 
N="NCRB Crime in India 2023, Table 9A.11 (child cyber crimes)"
add("India","India (all)",2023,"Recorded crime","Cyber crimes against children, total cases",1902,"cases",N,"Table 9A.11 (TOTAL ALL INDIA)","ncrb","TOTAL ALL INDIA 2 0 1499 28 0 373 1902")
add("India","India (all)",2023,"Recorded crime","  of which: Sec 67B IT Act (child sexual abuse material)",1499,"cases",N,"Table 9A.11","ncrb","TOTAL ALL INDIA 2 0 1499 28 0 373 1902")
add("India","India (all)",2023,"Recorded crime","  of which: Cyber stalking/bullying of children",28,"cases",N,"Table 9A.11","ncrb","TOTAL ALL INDIA 2 0 1499 28 0 373 1902")
add("India","India (all)",2023,"Recorded crime","  of which: Cyber blackmailing/threatening of children",2,"cases",N,"Table 9A.11","ncrb","TOTAL ALL INDIA 2 0 1499 28 0 373 1902")
add("India","India (all)",2023,"Recorded crime","  of which: Other cyber crimes against children",373,"cases",N,"Table 9A.11","ncrb","TOTAL ALL INDIA 2 0 1499 28 0 373 1902")

# Web-read (phase 1, not re-verifiable offline)
P25="PIB Lok Sabha reply 2025 (NCRB data, victims under 18)"
for yr,vals in {2020:(3,1,738,140,0,220,1102),2021:(23,9,969,123,0,252,1376),2022:(74,2,1171,158,2,416,1823)}.items():
    for lab,v in zip(["Cyber blackmailing/threatening/harassment","Cyber fake profile","Cyber pornography/obscene material depicting children","Cyber stalking/bullying","Online games","Other cyber crimes","TOTAL cyber crime, child victims"],vals):
        add("India","India (all)",yr,"Recorded crime",f"Child victims (<18): {lab}",v,"victims",P25,"Reply table","web","")
P26="PIB 2026 reply (NCRB 2020-2024, all victims)"
series = {"Cyber stalking/bullying of women & children (combined)":(872,1176,1471,1305,1240),
          "Cyber blackmailing/threatening":(303,689,696,689,601),
          "Cyber fake profile":(149,123,157,225,266),
          "Abetment to suicide (online)":(10,10,24,30,12),
          "TOTAL cyber crime cases (all ages, all types)":(50035,52974,65893,86420,101928)}
for lab,vals in series.items():
    for yr,v in zip(range(2020,2025),vals):
        add("India","India (all)",yr,"Recorded crime",lab,v,"cases",P26,"Reply table","web","")
add("Global","Global (WeProtect)",2022,"Online child sexual exploitation","Sextortion reports, 2021 baseline",139,"reports","WeProtect Global Threat Assessment 2023","Key findings","web","")
add("Global","Global (WeProtect)",2022,"Online child sexual exploitation","Sextortion reports, 2022",10000,"reports (10,000+)","WeProtect Global Threat Assessment 2023","Key findings","web","")
add("Global","Global (WeProtect)",2022,"Online child sexual exploitation","Rise in self-generated imagery of 7-10 year olds, 2020-2022",360,"% increase","WeProtect Global Threat Assessment 2023","Key findings","web","")
add("Global","Global (WeProtect)",2022,"Online child sexual exploitation","CSAM reports rise since 2019",87,"% increase","WeProtect Global Threat Assessment 2023","Key findings","web","")
add("Global","66 countries (UNESCO GEM)",2022,"Trend","Countries where bullying rose >=2 pp for girls, 2018-2022 (of 66)",34,"countries","UNESCO GEM Report 2024","Gender report","web","")
add("Global","66 countries (UNESCO GEM)",2022,"Trend","Countries where bullying rose >=2 pp for boys, 2018-2022 (of 66)",22,"countries","UNESCO GEM Report 2024","Gender report","web","")

HP="Bahl et al., PLOS One 21(4):e0345468 (published 2 Apr 2026), Himachal Pradesh school survey, 13-17 y, N=7,563, fieldwork Nov-Dec 2023"
for m,v in [("Cyberbullying perpetration, % of all respondents",9.64),("Cyberbullying victimization, % of all respondents",7.88),("Any bullying victimization (physical or cyber), % of all respondents",15.60)]:
    add("India","Himachal Pradesh",2023,"Prevalence",m,v,"% of students",HP,"Abstract/Results, Table 4","web","")
add("Global","OECD (PISA 2025)",2025,"Prevalence","Cyberbullying 'relatively rare' - OECD executive summary; exact item and base not stated on the page I could open",3,"% (as stated)","OECD PISA 2025 Results Vol. I, Executive Summary (8 Sep 2026)","Safe and fair learning environment","web","")

ok=bad=0
with open("evidence_ledger.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["id","scope","geography","data_year","category","metric","value","unit","source","location","verification","anchor"])
    for i,r in enumerate(R,1):
        scope,geo,yr,cat,m,v,u,src,loc,fk,anc=r
        if fk=="web": ver="read on source web page in phase 1 (not offline-checkable)"
        else:
            if anc and anc in txt[fk]: ver="programmatically matched in source PDF text"; ok+=1
            else: ver="ANCHOR NOT FOUND"; bad+=1; print("MISS",i,m,anc,file=sys.stderr)
        w.writerow([f"E{i:03d}",scope,geo,yr,cat,m,v,u,src,loc,ver,anc])
print(len(R),"rows; matched",ok,"missing",bad)
