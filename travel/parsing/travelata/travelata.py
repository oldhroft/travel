import glob
from travel.parsing.travelata.utils import (
    load_process_html_cards,
    get_cards_travelata,
    parse_hotel_card_travelata,
    extract_attributes_travelata,
)
from travel.utils import dump_json, load_json


def parse_html(pattern_html, output_file, **kwargs):
    files = glob.glob(pattern_html)
    result = []
    for file in files:
        path_to_meta = file.split(".")[0] + ".json"
        result_file = load_process_html_cards(
            file, get_cards_travelata, parse_hotel_card_travelata, path_to_meta
        )
        result.extend(result_file)

    dump_json(result, output_file)


def create_attributes(input_file, output_file):
    data = load_json(input_file)
    result_extracted = list(map(extract_attributes_travelata, data))
    dump_json(result_extracted, output_file)
