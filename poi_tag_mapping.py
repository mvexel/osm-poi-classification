#!/usr/bin/env python

# Load taginfo CSVs and generate mappings.json

import json
import httpx

TAGINFO_PRIMARY_KEYS_URL = "https://taginfo.openstreetmap.org/api/4/key/values?key={key}&filter=all&lang=en&sortname=count&sortorder=desc&rp=100&page=1"
TAGINFO_COMBINATIONS_URL = "https://taginfo.openstreetmap.org/api/4/tag/combinations?key={key}&value={value}&filter=all&sortname=to_count&sortorder=desc&rp=19&page=1"

# Thresholds for filtering tag values
THRESHOLD_USAGE_FRACTION = 0.001  # 0.1%
THRESHOLD_NAME_FRACTION = 0.25  # 25%
THRESHOLD_ABSOLUTE_COUNT = 10000  # 10000 named instances

import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


tag_keys = [
    "aeroway",
    "amenity",
    "building",
    "craft",
    "emergency",
    "healthcare",
    "historic",
    "leisure",
    "man_made",
    "military",
    "natural",
    "office",
    "place",
    "public_transport",
    "railway",
    "shop",
    "tourism",
    "waterway",
]


def construct_taginfo_url(tag_key: str) -> str:
    return TAGINFO_PRIMARY_KEYS_URL.format(key=tag_key)


def fetch_taginfo_data(url: str) -> dict:
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def get_top_values(data: dict) -> list:
    """
    Extract the values that have more than 0.1% usage fraction.

    :param data: The JSON data from taginfo.
    :return: List of tag values
    """
    return [
        item["value"]
        for item in data.get("data", [])
        if item.get("fraction", 0) > THRESHOLD_USAGE_FRACTION
    ]


def narrow_down_values(k: str, values: list) -> list:
    """
    Only keep values where more than half of the k/v pairs have a name tag
    Or an absolute count of more than 10,000 named instances.

    :param k: The tag key
    :param values: List of tag values to evaluate
    :return: Filtered list of tag values
    """
    narrowed = []
    for value in values:
        url = TAGINFO_COMBINATIONS_URL.format(key=k, value=value)
        data = fetch_taginfo_data(url)
        name_entry = next(
            (item for item in data.get("data", []) if item.get("other_key") == "name"),
            None,
        )
        if (
            name_entry and name_entry.get("to_fraction", 0) > THRESHOLD_NAME_FRACTION
        ) or (
            name_entry
            and name_entry.get("together_count", 0) > THRESHOLD_ABSOLUTE_COUNT
        ):
            narrowed.append(value)
    logging.info(f"Narrowed {k} values from {len(values)} to {len(narrowed)}")
    logging.info(f"Narrowed values: {narrowed}")
    return narrowed


def main():
    all_poi_kvs = {}
    for tag_key in tag_keys:
        # fetch primary taginfo data
        url = construct_taginfo_url(tag_key)
        data = fetch_taginfo_data(url)
        # extract top values (>0.1% of total)
        values = get_top_values(data)
        logging.info(f"Fetched {len(values)} values for key '{tag_key}'")
        logging.info(f"Values: {values}")
        # narrow down values based on secondary taginfo data
        narrowed_values = narrow_down_values(tag_key, values)
        logging.info(
            f"Narrowed down to {len(narrowed_values)} values for key '{tag_key}'"
        )
        if narrowed_values:
            all_poi_kvs[tag_key] = narrowed_values

    # write these out
    with open("poi_kvs.json", "w") as f:
        json.dump(all_poi_kvs, f, indent=2)
    logging.info("Wrote poi_kvs.json")


if __name__ == "__main__":
    main()
