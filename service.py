from selenium import webdriver
from selenium.webdriver.common.by import By
from pyproj import Proj, Transformer
from urllib.parse import urlencode, urlunparse
from xml.dom import minidom
import json
import os
import xml.etree.ElementTree as ET

def get_url():
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "ide_bhgeo:BAIRRO_POPULAR",
        "srsName": "EPSG:31983",
        "outputFormat": "application/json"
    }

    return urlunparse(("https", "geoservicos.pbh.gov.br", "/geoserver/wfs", "", urlencode(params), ""))

def convert_utm_to_latitude_and_longitude(x, y):
    utm_proj = Proj(proj='utm', zone=23, south=True, datum='WGS84')
    latlon_proj = Proj(proj='latlong', datum='WGS84')
    transformer = Transformer.from_proj(utm_proj, latlon_proj)
    return transformer.transform(x, y)

def save_neighborhoods_to_json(data, file_path="resources/neighborhoods.json"):
    if os.path.exists(file_path):
        response = input(f"The file {file_path} already exists. Do you want to overwrite? (y/n): ")
        if response.lower() != 'y':
            print("File was not overwritten.")
            return

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"File {file_path} saved successfully!")

def fetch_neighborhoods():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        url = get_url()
        driver.get(url)
        response = driver.find_element(By.TAG_NAME, "pre").text
        driver.quit()

        data = json.loads(response)

        neighborhoods = {
            feature["properties"].get("NOME", "Name not available"): feature["geometry"]["coordinates"]
            for feature in data.get("features", [])
        }

        neighborhoods = dict(sorted(neighborhoods.items()))

        return neighborhoods
    except Exception as e:
        driver.quit()
        raise RuntimeError(f"Error fetching the data: {e}")

def generate_gpx(selected_neighborhood, coordinates, file_path, elevation=1045.55):
    gpx = ET.Element("gpx", version="1.1", creator="BH Map", xmlns="http://www.topografix.com/GPX/1/1")
    trk = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = selected_neighborhood
    trkseg = ET.SubElement(trk, "trkseg")

    for polygon in coordinates:
        for coord in polygon:
            for point in coord:
                longitude, latitude = convert_utm_to_latitude_and_longitude(point[0], point[1])
                trkpt = ET.SubElement(trkseg, "trkpt", lat=str(latitude), lon=str(longitude))
                ET.SubElement(trkpt, "ele").text = str(elevation)
                ET.SubElement(trkpt, "name").text = selected_neighborhood

    tree = ET.ElementTree(gpx)

    rough_string = ET.tostring(gpx, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)

    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    return f"GPX file saved successfully at {file_path}."

