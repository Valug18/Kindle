import requests
import json
import re
import os

def create_notion_page(token, database_id, book, highlights, page, date, genre, author=None):
    url = 'https://api.notion.com/v1/pages'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Combina todos los highlights y la página en un solo string
    combined_highlight = f"{highlights} (Page: {page})"

    properties = {
        "Title": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": book
                    }
                }
            ]
        },
        "Author": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": author if author else "Desconocido"
                    }
                }
            ]
        },
        "Date": {
            "date": {
                "start": date
            }
        },
        "Page": {
            "number": page if page is not None else 0
        },
        "Highlight": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": combined_highlight
                    }
                }
            ]
        },
        "Genre": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": genre if genre else "Desconocido"
                    }
                }
            ]
        }
    }

    data = {
        "parent": {"database_id": database_id},
        "properties": properties
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")

def read_clippings(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    entries = content.split('==========')
    parsed_entries = []

    for entry in entries:
        lines = entry.strip().split('\n')
        if len(lines) >= 3:
            book = lines[0].strip()
            page_info = lines[1].strip()
            highlight_lines = lines[2:]
            date = "2024-08-03T00:00:00Z"  # Cambia esto si es necesario

            # Extraer el número de página usando expresión regular
            page_match = re.search(r'\b\d+\b', page_info)
            page = int(page_match.group(0)) if page_match else None

            # Extraer la fecha real si está presente en el archivo
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', entry)
            if date_match:
                date = date_match.group(0)
                # Convertir la fecha a formato ISO 8601
                date = f"{date[-4:]}-{date[3:5]}-{date[:2]}T00:00:00Z"

            highlights = " ".join([line.strip() for line in highlight_lines])
            parsed_entries.append((book, highlights, page, date, "Unknown"))  # Cambia "Unknown" si tienes el género disponible

    return parsed_entries

if __name__ == "__main__":
    # Utilizar los nombres correctos de las variables de entorno
    token = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('DATABASE_ID')
    file_path = 'My Clippings.txt'  # Cambié la ruta para que coincida con la ubicación del archivo
    
    clippings = read_clippings(file_path)
    
    for clipping in clippings:
        book, highlights, page, date, genre = clipping
        create_notion_page(token, database_id, book, highlights, page, date, genre)
