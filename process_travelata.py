import glob
import os
import json
from process_trevalata_utils import (
    load_process_html_cards,
    get_cards_travelata,
    parse_hotel_card_travelata,
    extract_attributes_travelata
)

from pandas import DataFrame

def safe_mkdir(path: str):
    if not os.path.exists(path):
        os.mkdir(path)

def dump_json(data: list, path: str):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)

if __name__ == "__main__":
    files = glob.glob("./data_html/collected_hotels_*.html")
    result = []
    for file in files:
        result_file = load_process_html_cards(
            file, get_cards_travelata, parse_hotel_card_travelata
        )
        result.extend(result_file)
    
    safe_mkdir("./data/results")
    dump_json(result, "./data/results/result_travelata_raw.json")
    result_extracted = list(map(extract_attributes_travelata, result))
    dump_json(result_extracted, "./data/results/result_travelata.json")
    DataFrame(result_extracted).to_excel("hotels.xlsx")
    
