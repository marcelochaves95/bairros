import json
import os
from pyproj import Proj, Transformer
from xml.dom import minidom
import xml.etree.ElementTree as ET

url = "https://geoservicos.pbh.gov.br/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=ide_bhgeo:BAIRRO_POPULAR&srsName=EPSG:31983&outputFormat=application%2Fjson"

utm_proj = Proj(proj='utm', zone=23, south=True, datum='WGS84')
latlon_proj = Proj(proj='latlong', datum='WGS84')

transformer = Transformer.from_proj(utm_proj, latlon_proj)

def convert_utm_to_latlon(x, y):
    latitude, longitude = transformer.transform(x, y)
    return latitude, longitude

def save_bairros_to_json(data, file_path="bairros.json"):
    if os.path.exists(file_path):
        response = input(f"O arquivo {file_path} já existe. Deseja substituir? (s/n): ")
        if response.lower() != 's':
            print("Arquivo não foi substituído.")
            return

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Arquivo {file_path} salvo com sucesso!")


def fetch_neighborhoods():    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        response = driver.find_element(By.TAG_NAME, "pre").text
        driver.quit()
        
        data = json.loads(response)
        
        neighborhoods = {
            feature["properties"].get("NOME", "Nome não disponível"): feature["geometry"]["coordinates"]
            for feature in data.get("features", [])
        }

        neighborhoods = dict(sorted(neighborhoods.items()))

        return neighborhoods
    except Exception as e:
        driver.quit()
        raise RuntimeError(f"Erro ao buscar os dados: {e}")

def generate_gpx(selected_neighborhood, coordinates, elevation=1045.55):
    gpx = ET.Element("gpx", version="1.1", creator="BairrosBH", xmlns="http://www.topografix.com/GPX/1/1")

    trk = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = selected_neighborhood

    trkseg = ET.SubElement(trk, "trkseg")

    for polygon in coordinates:
        for coord in polygon:
            for point in coord:
                longitude, latitude = convert_utm_to_latlon(point[0], point[1])

                trkpt = ET.SubElement(trkseg, "trkpt", lat=str(latitude), lon=str(longitude))

                ET.SubElement(trkpt, "ele").text = str(elevation)

                ET.SubElement(trkpt, "name").text = selected_neighborhood

    tree = ET.ElementTree(gpx)

    rough_string = ET.tostring(gpx, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)

    with open(f"{selected_neighborhood.replace(' ', '_')}.gpx", "w", encoding="UTF-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    return f"{selected_neighborhood} GPX gerado com sucesso!"
