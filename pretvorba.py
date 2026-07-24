import re
import os
import csv
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

    #    Open the request and write the file content
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
    if text != None:
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        with open(path, 'w', encoding='utf-8') as file_out:
            file_out.write(text)
    return None


serija_re = re.compile(
    r'"imdbId".*?"genreIds"'
)

oblika_serije_re = re.compile(
    r'"title":"([^"]*)",'
    r'"averageEpisodeRating":([\d\.]*).*?'
    r'"totalEpisodes":([\d]*).*?'
    r'"totalEpisodeVotes":([\d]*).*?'
    # "numVotes": 2642930,
    # "showRating": 9.5,
    r'"minEpisodeRating":([\d\.]*).*?'
    r'"maxEpisodeRating":([\d\.]*).*?'
    #         "episodeScore": 8.55,
    #         "showScore": 9.45,
    #         "finalScore": 9.09,
    #         "lastUpdated": "2026-07-19T02:01:34.242Z",
    r'"rank":([\d]*).*?'
    r'"tmdbId":(\d+),.*?'
    r'"slug":"([^"]*)",.*?'
    #         "firstAirDate": "2008-01-20",
    #         "genreIds"
)

with open('shows/shows.html', 'r', encoding='utf-8') as f:
    vsebina = f.read()

seznam = serija_re.findall(vsebina)

serije_slovarji = []

for serija in seznam:
    iskanje = oblika_serije_re.search(serija)
    if iskanje:
        title, povpr_ocena, st_epizod, st_ocen_epizod, min_ocena, max_ocena, pozicija, id, slug = iskanje.groups()
        text_serija = download_url_to_string(f"https://seriesgraph.com/show/{id}")
        print(f"Serija: {slug}")
        save_string_to_file(text_serija, "shows", f"{id}.html")
        serije_slovarji.append([title, povpr_ocena, st_epizod, st_ocen_epizod, min_ocena, max_ocena, pozicija, id])


with open('shows/shows.csv', 'w', newline='', encoding='utf-8') as d:
    writer = csv.writer(d)

    writer.writerow([
        'Naslov', 'Povprecna_ocena_epizode', 'Stevilo_epizod', 'Stevilo_ocen_epizod', 'Minimalna_ocena', 'Maksimalna_ocena', 'Pozicija','ID'
    ])

    writer.writerows(serije_slovarji)