import urllib.request
import urllib.error
import os

top_rated_url = "https://seriesgraph.com/api/top-rated"
#top_rated_url = "https://www.wine-searcher.com/discover?t=w"


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
    return page_content

def save_string_to_file(text, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None

def main(redownload=True, reparse=True):
    top_rated_html = download_url_to_string(top_rated_url)
    save_string_to_file(top_rated_html, "shows", "shows.html")
#    subprocess.run(["curl.exe", top_rated_url, "-o", "testp.html"], capture_output=True, text=True)



if __name__ == '__main__':
    main()