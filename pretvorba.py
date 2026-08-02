import re
import os
import csv
from datetime import date
import urllib.request
import urllib.error


def download_url_to_string(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "accept": "*/*"
        }

        # Create a Request object containing the URL and the headers
        req = urllib.request.Request(url, headers=headers)

        # Open the request and write the file content
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
        # dodano za kasnejše popravke 
        save_string_to_file(text, directory, filename)

def download_top_rated_shows():
    top_rated_url = "https://seriesgraph.com/api/top-rated"
    download_url_to_file(top_rated_url, "shows", "shows.html")

def shows_to_array():
    serija_re = re.compile(r'"imdbId".*?"firstAirDate"')
    with open('shows/shows.html', 'r', encoding='utf-8') as f:
        vsebina = f.read()
    return serija_re.findall(vsebina)

def convert_community_ratings(seznam):
    oblika_serije_re = re.compile(
        r'"title":"([^"]*)",'
        r'"averageEpisodeRating":([\d\.]*).*?'
        r'"totalEpisodes":([\d]*).*?'
        r'"totalEpisodeVotes":([\d]*).*?'
        r'"numVotes":([\d]*).*?'
        r'"showRating":([\d\.]*).*?'
        r'"minEpisodeRating":([\d\.]*).*?'
        r'"maxEpisodeRating":([\d\.]*).*?'
        #         "episodeScore": 8.55,
        #         "showScore": 9.45,
        #         "finalScore": 9.09,
        #         "lastUpdated": "2026-07-19T02:01:34.242Z",
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

            # Download the community ratings for the series and save it to a file
            url = f"https://seriesgraph.com/api/community-ratings/{id}/season-ratings"
            download_url_to_file(url, "shows", f"{id}_community.json")
            zaporedna += 1
    return serije_slovarji

def write_shows_to_csv(serije_slovarji):
    with open('shows/shows.csv', 'w', newline='', encoding='utf-8') as d:
        writer = csv.writer(d)
        writer.writerow([
            'Naslov', 'Povprecna_ocena_epizode', 'Stevilo_epizod', 'Stevilo_ocen_epizod', 'Stevilo_ocen_sezone',
            'Povprecna_ocena_sezone', 'Minimalna_ocena', 'Maksimalna_ocena', 'Pozicija', 'ID'
        ])
        writer.writerows(serije_slovarji)


def community_to_seasons(vsebina):
    community_re = re.compile(r'"episodes":')
    # prvi element predstavlja vsebino pred prvo sezono, zato ga preskočimo
    return community_re.split(vsebina)[1:]

def season_to_episodes(vsebina):
    community_re = re.compile(r'"vote_average":')
    # prvi element predstavlja vsebino pred prvo epizodo, zato ga preskočimo
    return community_re.split(vsebina)[1:]


def dodaj_community_podatke(vhodna, izhodna):
    oblika_epizode_re = re.compile(
        r'^([\d\.]*).*?'
        r'"community_count":([\d]*).*?'
        r'"episode_number":([\d]*).*'
        r'"season_number":([\d]*).*'
        r'"air_date":"(\d{4}-\d{2}-\d{2})",'
        r'"runtime":([\d]+)'
    )

    epizode_seznam = []
    with open(vhodna, 'r', encoding='utf-8') as f:
        serije_slovarji = list(csv.reader(f))

        zaporedna = 1
        stevilo_serij = len(serije_slovarji)
        for serija in serije_slovarji[1:]:
            print(f"Serija {zaporedna}/{stevilo_serij}")
            zaporedna += 1
            with open(f"shows/{serija[9]}_community.json", 'r', encoding='utf-8') as d:
                vsebina = d.read()

            stevilo_sezon = 0
            stevilo_epizod = 0
            #average_count = 0
            first_date = None
            last_date = None
            average_runtime = 0.0
            #average_vote = 0.0
            for sezona in community_to_seasons(vsebina):
                stevilo_sezon += 1
                for epizoda in season_to_episodes(sezona):
                    stevilo_epizod += 1
                    epizoda_podatki = oblika_epizode_re.search(epizoda)
                    if epizoda_podatki:
                        groups = epizoda_podatki.groups()
                        #vote = float(groups[0])
                        #count = int(groups[1])
                        air_date = date.fromisoformat(groups[4])
                        runtime = int(groups[5])
                        if first_date is None or air_date < first_date:
                            first_date = air_date
                        if last_date is None or air_date > last_date:
                            last_date = air_date
                        average_runtime += runtime
                        #average_count += count
                        #average_vote += vote
            if stevilo_epizod > 0:
                average_runtime /= stevilo_epizod
                #average_vote /= stevilo_epizod
                #average_count /= stevilo_epizod
            #serija[2] = str(stevilo_epizod)
            serija.append(str(first_date))
            serija.append(str(last_date))
            serija.append(str(average_runtime))
            serija.append(str(stevilo_sezon))
            date_difference = (last_date - first_date).days // 365 if first_date and last_date else 0
            serija.append(str(date_difference))

            


        with open(izhodna, 'w', newline='', encoding='utf-8') as e:
            writer = csv.writer(e)
            writer.writerow([
                'Naslov', 'Povprecna_ocena_epizode', 'Stevilo_epizod', 'Stevilo_ocen_epizod', 'Stevilo_ocen_sezone', 
                'Povprecna_ocena_sezone', 'Minimalna_ocena', 'Maksimalna_ocena', 'Pozicija', 'ID', 'Prva_epizoda', 
                'Najnovejša_epizoda', 'Povprecna_dolzina_epizode', 'Stevilo_sezon', "Leta"
            ])

            writer.writerows(serije_slovarji[1:])

download_top_rated_shows()
seznam = shows_to_array()
serije_slovarji = convert_community_ratings(seznam)
write_shows_to_csv(serije_slovarji)
dodaj_community_podatke('shows/shows.csv', 'shows/shows_community.csv')