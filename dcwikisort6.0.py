import requests
from bs4 import BeautifulSoup
import re
import os
import time
from tqdm import tqdm

def get_publication_year(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    pattern = re.compile(r'.{0,0}\(Publication\)[^"]*"[^"]*"')
    match = pattern.search(str(soup))

    if match:
        index = match.start()
        date_string = match.string[index-18:index]
        year = re.findall(r'\d{4}', date_string)
        if year:
            return year[0]

    return None

start_time = time.time()

url = input('Link with the character appearances (e.g., https://dc.fandom.com/wiki/Character_Appearances): ')

try:

    response = requests.get(url)
    response.raise_for_status()     
    html = response.text   
    target_string = '<p class="category-page__total-number">'   
    lines = html.split('\n')
    numeric_value = None     
    for i, line in enumerate(lines):
        if target_string in line:
            
            match = re.search(r'\d+', lines[i + 1])
            if match:
                numeric_value = match.group()
                break  


except requests.exceptions.RequestException as e:
    print("Error al hacer la solicitud HTTP:", e)
except Exception as e:
    print("Error:", e)

if numeric_value is not None:  
    if int(numeric_value) <= 200:

        output_file_path = input('Save List as: ')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                links.append(href)

        start_link_index = 0
        for i, link in enumerate(links):
            if link.endswith("/Gallery"):
                start_link_index = i
                break

        start_link_index = start_link_index+1
        end_link_index = links.index("/wiki/Special:Categories")-1
        filtered_links = links[start_link_index:end_link_index+1]
        unique_links = list(set(filtered_links))
        unique_links = [link for link in unique_links if link.startswith('/wiki')]

        for i in range(len(unique_links)):
            unique_links[i] = "https://dc.fandom.com" + unique_links[i]

        links_with_years = []
        for link in tqdm(unique_links, desc="Scraping and Processing"):
            year = get_publication_year(link)
            links_with_years.append((link, year or 'N/A'))

        sorted_links = sorted(links_with_years, key=lambda x: (int(x[1][-4:]) if x[1][-4:].isdigit() else 9999, x[0]))

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write("Sorted by year of publication:\n")
            for i, (link, year) in enumerate(sorted_links):
                result_line = f"{i+1}. {link} - Publication Year: {year}\n"
                output_file.write(result_line)
       
    else:

        base_url = url
        output_file_path = input('Save List as: ')
        unique_links_with_years = set()

        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            
            url = f'{base_url}?from={letter}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    links.append(href)

            start_link_index = 0
            for i, link in enumerate(links):
                if link.endswith("/Gallery"):
                    start_link_index = i
                    break

            start_link_index = start_link_index + 1
            end_link_index = links.index("/wiki/Special:Categories") - 1

            filtered_links = links[start_link_index:end_link_index + 1]
            unique_links = list(set(filtered_links))
            unique_links = [link for link in unique_links if link.startswith('/wiki')]

            for i in range(len(unique_links)):
                unique_links[i] = "https://dc.fandom.com" + unique_links[i]

            links_with_years = []
            for link in tqdm(unique_links, desc="Scraping and Processing"):
                year = get_publication_year(link)
                links_with_years.append((link, year or 'N/A'))

            unique_links_with_years.update(links_with_years)
            time.sleep(1)

        all_links_with_years = list(unique_links_with_years)
        sorted_all_links = sorted(all_links_with_years, key=lambda x: (int(x[1][-4:]) if x[1][-4:].isdigit() else 9999, x[0]))

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write("Sorted by year of publication:\n")
            for i, (link, year) in enumerate(sorted_all_links):
                result_line = f"{i+1}. {link} - Publication Year: {year}\n"
                output_file.write(result_line)
else:
    print("El valor numérico no se encontró o es None.")

end_time = time.time()
elapsed_time = end_time - start_time
print("El proceso tardó", elapsed_time, "segundos en completarse.")
os.system("pause")