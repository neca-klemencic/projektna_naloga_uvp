import re
import os
import csv
from datetime import date
import urllib.request
import urllib.error


def download_url_to_string(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            page_content = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f'Napaka pri prenosu strani {url} : {e}')
        return None
    except (TypeError, ValueError) as e:
        print(f'Napaka pri prenosu strani {url} : {e}')
        return None
    return page_content


def save_string_to_file(text, directory, filename):
    if text is not None:
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        with open(path, 'w', encoding='utf-8') as file_out:
            file_out.write(text)
    return None


def download_url_to_file(url, directory, filename):
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        text = download_url_to_string(url)
        # Dodano za kasnejše popravke:
        save_string_to_file(text, directory, filename)


def download_top_rated_shows():
    """Naloži seznam najbolj ocenjenih serij in ga shrani v datoteko 
    shows/shows.html"""
    top_rated_url = "https://seriesgraph.com/api/top-rated"
    download_url_to_file(top_rated_url, "shows", "shows.html")


def shows_to_array():
    serija_re = re.compile(r'"imdbId".*?"firstAirDate"')
    with open('shows/shows.html', 'r', encoding='utf-8') as f:
        vsebina = f.read()
    return serija_re.findall(vsebina)


def convert_community_ratings(seznam):
    """"Funkcija sprejme seznam nizov, ki predstavljajo posamezne serije in vrne 
    seznam slovarjev, ki vsebujejo podatke o posameznih serijah. Za vsako serijo 
    prenese tudi podatke o ocenah skupnosti in jih shrani v datoteko."""
    oblika_serije_re = re.compile(
        r'"title":"([^"]*)",'
        r'"averageEpisodeRating":([\d\.]*).*?'
        r'"totalEpisodes":([\d]*).*?'
        r'"totalEpisodeVotes":([\d]*).*?'
        r'"numVotes":([\d]*).*?'
        r'"showRating":([\d\.]*).*?'
        r'"minEpisodeRating":([\d\.]*).*?'
        r'"maxEpisodeRating":([\d\.]*).*?'
        r'"rank":([\d]*).*?'
        r'"tmdbId":(\d+),.*?'
    )
    serije_slovarji = []

    zaporedna = 1
    stevilo_serij = len(seznam)
    for serija in seznam:
        iskanje = oblika_serije_re.search(serija)
        if iskanje:
            ena_serija = iskanje.groups()
            id = ena_serija[9]
            print(f"Serija {zaporedna}/{stevilo_serij}")
            serije_slovarji.append(ena_serija)

            url = f"https://seriesgraph.com/api/community-ratings/{id}/season-ratings"
            download_url_to_file(url, "shows", f"{id}_community.json")
            zaporedna += 1
    return serije_slovarji


def write_shows_to_csv(serije_slovarji):
    """Funkcija sprejme seznam slovarjev, ki vsebujejo podatke o posameznih 
    serijah in jih shrani v datoteko shows/shows.csv; izbrane podatke tudi 
    formatira na dve decimalni mesti."""
    with open('shows/shows.csv', 'w', newline='', encoding='utf-8') as d:
        writer = csv.writer(d)
        writer.writerow([
            'Naslov', 
            'Povprecna_ocena_epizode', 
            'Stevilo_epizod', 
            'Stevilo_ocen_epizod', 
            'Stevilo_ocen_serije',
            'Povprecna_ocena_serije', 
            'Minimalna_ocena', 
            'Maksimalna_ocena', 
            'Pozicija', 
            'ID'
        ])
        vrstice = []
        for vrstica in serije_slovarji:
            nova_vrstica = list(vrstica)
            for indeks in (1, 4, 5, 6, 7):
                try:
                    nova_vrstica[indeks] = f"{float(nova_vrstica[indeks]):.2f}"
                except (TypeError, ValueError):
                    pass
            vrstice.append(nova_vrstica)
        writer.writerows(vrstice)


def community_to_seasons(vsebina):
    """Funkcija vsebino celotne serije razdeli na posamezne sezone in 
    vrne seznam nizov, kjer vsak niz predstavlja eno sezono."""
    community_re = re.compile(r'"episodes":')
    # prvi element predstavlja vsebino pred prvo sezono, zato ga preskočimo
    return community_re.split(vsebina)[1:]


def season_to_episodes(vsebina):
    """Funkcija vsebino posamezne sezone razdeli na posamezne epizode in 
    vrne seznam nizov, kjer vsak niz predstavlja eno epizodo."""
    community_re = re.compile(r'"vote_average":')
    # prvi element predstavlja vsebino pred prvo epizodo, zato ga preskočimo
    return community_re.split(vsebina)[1:]


def add_community_data(vhodna, izhodna, epizode_izhodna):
    """Funkcija prebere podatke o serijah iz datoteke "vhodna", prenese 
    podatke o ocenah skupnosti za vsako serijo in jih shrani v datoteko 
    "izhodna" ter podatke o posameznih epizodah v datoteko "epizode_izhodna"."""
    oblika_epizode_re = re.compile(
        r'^([\d\.]*).*?'
        r'"community_count":([\d]*).*?'
        r'"episode_number":([\d]*).*'
        r'"season_number":([\d]*).*'
        r'"air_date":"(\d{4}-\d{2}-\d{2})",'
        r'"runtime":([\d]+)'
    )

    with open(vhodna, 'r', encoding='utf-8') as f:
        serije_slovarji = list(csv.reader(f))
        vse_epizode = []

        zaporedna = 1
        stevilo_serij = len(serije_slovarji)
        for serija in serije_slovarji[1:]:
            print(f"Serija {zaporedna}/{stevilo_serij - 1}")
            zaporedna += 1
            with open(f"shows/{serija[9]}_community.json", 'r', encoding='utf-8') as d:
                vsebina = d.read()

            stevilo_sezon = 0
            stevilo_epizod = 0
            first_date = None
            last_date = None
            average_runtime = 0.0
            for sezona in community_to_seasons(vsebina):
                stevilo_sezon += 1
                for epizoda in season_to_episodes(sezona):
                    stevilo_epizod += 1
                    epizoda_podatki = oblika_epizode_re.search(epizoda)
                    if epizoda_podatki:
                        groups = epizoda_podatki.groups()
                        vote = float(groups[0])
                        count = int(groups[1])
                        air_date = date.fromisoformat(groups[4])
                        runtime = int(groups[5])
                        if first_date is None or air_date < first_date:
                            first_date = air_date
                        if last_date is None or air_date > last_date:
                            last_date = air_date
                        average_runtime += runtime
                        vse_epizode.append({
                            'vote_average': vote,
                            'community_count': count,
                            'episode_number': int(groups[2]),
                            'season_number': int(groups[3]),
                            'air_date': air_date,
                            'runtime': runtime,
                            'id': serija[9],
                            'pozicija': serija[8],
                            'stevilo_epizod': serija[2],
                            'ocena_serije': serija[5]
                        })
            if stevilo_epizod > 0:
                average_runtime /= stevilo_epizod
            serija.append(str(first_date))
            serija.append(str(last_date))
            serija.append(f"{average_runtime:.2f}" if stevilo_epizod > 0 else "0.00")
            serija.append(str(stevilo_sezon))

        with open(izhodna, 'w', newline='', encoding='utf-8') as e:
            writer = csv.writer(e)
            writer.writerow([
                'Naslov', 
                'Povprecna_ocena_epizode', 
                'Stevilo_epizod', 
                'Stevilo_ocen_epizod', 
                'Stevilo_ocen_serije', 
                'Povprecna_ocena_serije', 
                'Minimalna_ocena', 
                'Maksimalna_ocena', 
                'Pozicija', 
                'ID', 
                'Prva_epizoda', 
                'Najnovejša_epizoda', 
                'Povprecna_dolzina_epizode', 
                'Stevilo_sezon'
            ])
            writer.writerows(serije_slovarji[1:])

        with open(epizode_izhodna, 'w', newline='', encoding='utf-8') as e:
            writer = csv.DictWriter(
                e, 
                fieldnames=[
                    'vote_average', 
                    'community_count', 
                    'episode_number', 
                    'season_number', 
                    'air_date', 
                    'runtime', 
                    'id', 
                    'pozicija', 
                    'stevilo_epizod', 
                    'ocena_serije' 
                ],
            )
            writer.writeheader()
            writer.writerows(vse_epizode)


download_top_rated_shows()
seznam = shows_to_array()
serije_slovarji = convert_community_ratings(seznam)
write_shows_to_csv(serije_slovarji)
add_community_data(
    'shows/shows.csv', 
    'shows/shows_community.csv', 
    'shows/epizode_community.csv'
    )

