# Analiza spletne strani Series Graph
Za podatke sem uporabila spletno stran Series Graphs in sicer njihov seznam 250 najboljše ocenjenih serij na https://seriesgraph.com/top-rated ter še nadaljne podatke iz spletnih strani posamezne serije na https://seriesgraph.com/show/{show_id}. 
Koda analizira spletno stran 250 najboljše ocenjenih serij, v moji analizi pa je vključenih le 247, saj za tri serije spletna stran nima podatkov.

## 1. korak - Zaženi datoteko "pretvorba.py". 

Ta pobere podatke iz strani https://seriesgraph.com/top-rated in jih shrani v datoteko imenovano "shows.html" v mapo imenovano "shows". Te podatke preoblikuje in jih shrani v datoteko imenovano "shows.csv". 

S pomočjo podatkov v datoteki "shows.csv" z id številko serij pobere še podatke za vsako posamezno serijo s strani oblike https://seriesgraph.com/show/{show_id}. Te shrani v 247 datotek znotraj mape "shows" imenovane "{show_id}_community.json". Te preoblikuje in jih združi s podatki iz datoteke "shows.csv" v datoteki imenovani "shows_community.csv". V tej so podatki razporejeni po serijah (vsaka serija predstavlja eno vrstico). Koda poleg tega ustvari tudi novo datoteko imenovano "episode_community.csv", v katero podatke s posameznih strani razporedi po epizodah (vsaka epizoda predstavlja eno vrstico). Datoteko kasneje dopolni tudi s podatki o serijah.

## 2. korak - Zaženi datoteko "analiza.ipynb".

Ta datoteka podatke analizira in jih grafično predstavi. Ob skiciranju grafov sem si pomagala z dokumentacijo na https://pandas.pydata.org/docs/index.html ter https://matplotlib.org/stable/plot_types/index.html. 


