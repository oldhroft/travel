from typing import Optional, Callable
from bs4 import BeautifulSoup


def get_text(
    soup: BeautifulSoup,
    element: str,
    class_: str,
    raise_error: bool = True,
    attrs: Optional[list] = None,
) -> str:
    card = soup.find(element, class_=class_)

    if card is None and raise_error:
        raise ValueError(f"Element {element} with class {class_} not found")
    elif card is None:
        if attrs is None:
            return None
        else:
            return None, *(None for _ in range(len(attrs)))
    else:
        text = card.get_text(" ", strip=True)
        if attrs is None:
            return text
        else:
            attr_value = (card.attrs[a] for a in attrs)
            return text, *attr_value


from functools import wraps
import datetime
from urllib.parse import urljoin
from hashlib import md5


def parse_func_wrapper(website: str, time_fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> Callable:
    def dec_outer(fn):
        @wraps(fn)
        def somedec_inner(*args, **kwargs):
            result = fn(*args, **kwargs)
            result["created_dttm"] = datetime.datetime.now().strftime(time_fmt)
            result["website"] = website
            result["link"] = urljoin(website, result["href"])
            result["offer_hash"] = md5(result["link"].encode()).hexdigest()
            return result

        return somedec_inner

    return dec_outer


import os
from typing import List


def update_dicts(dicts: List[dict], **kwargs) -> List[dict]:
    return list(map(lambda x: {**x, **kwargs}, dicts))


def load_process_html_cards(
    path: str, get_cards: Callable, parse_card: Callable
) -> list:
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    soup = BeautifulSoup(content, "html.parser")
    cards = get_cards(soup)
    result = list(map(parse_card, cards))
    result_with_meta = update_dicts(result, path=path, filename=os.path.basename(path))
    return result_with_meta


def get_cards_travelata(soup: BeautifulSoup) -> List[dict]:
    return soup.find_all("div", class_="serpHotelCard")


@parse_func_wrapper("https://travelata.ru/")
def parse_hotel_card_travelata(card: BeautifulSoup) -> dict:
    title, href = get_text(card, "a", "serpHotelCard__title", attrs=["href"])
    location = get_text(card, "a", class_="serpHotelCard__resort")

    distances_card = card.find("div", class_="serpHotelCard__distances")
    if distances_card is not None:
        distances = list(
            map(
                lambda x: x.get_text(" ", strip=True),
                distances_card.find_all("div", class_="serpHotelCard__distance"),
            )
        )
    else:
        distances = []

    rating = get_text(card, "div", "serpHotelCard__rating")
    reviews = get_text(card, "a", "hotel-reviews", raise_error=False)
    less_places = get_text(
        card, "div", "serpHotelCard__tip__less-places", raise_error=False
    )
    num_stars = len(card.find_all("i", "icon-i16_star"))

    orders_count = get_text(
        card, "div", "serpHotelCard__ordersCount", raise_error=False
    )
    criteria = get_text(card, "div", "serpHotelCard__criteria")
    price = get_text(card, "span", "serpHotelCard__btn-price")
    oil_tax = get_text(card, "span", "serpHotelCard__btn-oilTax")

    # cashback = get_text(card, "div", "cashbackPartialPayment__banner")
    # partial_payment = get_text(card, "div", "partialPayment__banner")
    # free_cancel = get_text(card, "div", "freeCancellation__banner")
    attributes_cards = card.find_all("div", class_="serpHotelCard__attribute")
    attributes = list(map(lambda x: x.get_text(" ", strip=True), attributes_cards))

    return {
        "title": title,
        "href": href,
        "location": location,
        "distances": distances,
        "rating": rating,
        "reviews": reviews,
        "less_places": less_places,
        "num_stars": num_stars,
        "orders_count": orders_count,
        "criteria": criteria,
        "price": price,
        "oil_tax": oil_tax,
        # "cashback": cashback,
        # "partial_payment": partial_payment,
        # "free_cancel": free_cancel,
        "attributes": attributes,
    }


import datetime
import re

months_dict = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июлю": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def create_start_end_date(
    from_date_num: str, from_date_mnth: str, num_nights: str, fmt: str = "%Y-%m-%d"
):
    # TODO: make auto determination of a year
    start_date = datetime.date(2023, months_dict[from_date_mnth], int(from_date_num))
    end_date = start_date + datetime.timedelta(int(num_nights))
    return start_date.strftime(fmt), end_date.strftime(fmt)


def distance_to_airport_and_beach(distances: list):
    result = {"distance_to_beach": None, "distance_to_airport": None}

    pattern_airport = re.compile(r"(\d+) (\w+) до аэропорта")
    pattern_beach = re.compile(r"(\d+) (\w+) до пляжа")

    for text in distances:
        match_airport = pattern_airport.match(text)
        match_beach = pattern_beach.match(text)
        if match_airport is not None:
            distance, units = match_airport.groups()
            distance = int(distance)
            if units == "км":
                distance = 1000 * distance
            result["distance_to_airport"] = distance

        elif match_beach is not None:
            distance, units = match_beach.groups()
            distance = int(distance)
            if units == "км":
                distance = 1000 * distance
            result["distance_to_beach"] = distance

    return result


def parse_attributes(attributes):
    result = {
        "beach_line": None,
        "wifi": None,
        "conditioner": None,
        "beach_options": None,
        "beach_type": None,
    }

    for attribute in attributes:
        if "линия" in attribute and not "?" in attribute:
            result["beach_line"] = re.match("\d+", attribute).group()
        elif "wi-fi" in attribute:
            if "?" in attribute:
                result["wifi"] = attribute.split("?")[1].strip()
            else:
                result["wifi"] = "Бесплатно в номере?"
        elif "песок" in attribute:
            result["beach_type"] = "песок"
            if "?" in attribute:
                result["beach_options"] = attribute.split("?")[1].strip()
        elif "галька" in attribute:
            result["beach_type"] = "галька"
            if "?" in attribute:
                result["beach_options"] = attribute.split("?")[1].strip()
        elif "конди" in attribute:
            if "?" in attribute:
                result["conditioner"] = attribute.split("?")[1].strip()
            else:
                result["conditioner"] = "Бесплатно?"
    return result


def extract_attributes_travelata(data: dict) -> dict:
    location_splitted = data["location"].split(",")
    country = location_splitted[-1].strip()
    place = ",".join(location_splitted[:-1])

    pattern = r"(\d+) взро[cс]лых [cс] (\d+) (\w+) на (\d+) ноч\w{1,2}\, перелет (.+)"

    matched = re.match(pattern, data["criteria"], flags=re.DOTALL)
    if matched is not None:
        num_people, from_date_num, from_date_mnth, num_nights, flight = matched.groups()
    else:
        raise ValueError(f"Wrong criteria pattern for {data['criteria']}")

    start_date, end_date = create_start_end_date(
        from_date_num, from_date_mnth, num_nights
    )
    num_nights = int(num_nights)
    num_people = int(num_people)
    is_flight_included = flight == "включено"

    if data["reviews"] is not None:
        reviews = re.match("\d+", data["reviews"]).group(0)
    else:
        reviews = 0

    price = float(re.match("от (\d+)", data["price"]).groups()[0].replace(" ", ""))
    if data["orders_count"] is not None:
        orders_count = re.match(
            r"Забронировано (\d+) раз", data["orders_count"]
        ).groups()[0]
    else:
        orders_count = 0

    distances = distance_to_airport_and_beach(data["distances"])
    attributes = parse_attributes(data["attributes"])
    flag_less_places = data["less_places"] is not None

    rating = float(data["rating"]) if data["rating"] is not None else None

    oil_tax_included_match = re.match(
        "вкл\. топл\. сбор: ([\s\d]+) руб", data["oil_tax"]
    )
    if oil_tax_included_match is not None:
        oil_tax_included = float(oil_tax_included_match.groups()[0].replace(" ", ""))
    else:
        oil_tax_included = None

    return {
        "title": data["title"],
        "link": data["link"],
        "country": country,
        "place": place,
        "num_people": num_people,
        "start_date": start_date,
        "end_date": end_date,
        "num_nights": num_nights,
        "rating": rating,
        "reviews": reviews,
        "flag_less_places": flag_less_places,
        "num_stars": data["num_stars"],
        "orders_count": orders_count,
        "price": price,
        "is_flight_included": is_flight_included,
        "oil_tax_included": oil_tax_included,
        "website": data["website"],
        "offer_hash": data["offer_hash"],
        "path": data["path"],
        "filename": data["filename"],
        **attributes,
        **distances,
    }
