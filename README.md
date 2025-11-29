# OSM POI classification tool

I wrote a post about POI classification that uses this project. Read it here.

A tool to build a mapping between raw OSM k/v and common POI categories.

What it does:
1. Fetch the most frequently used values for selected keys (generously, any value that represents more than 0.1% of the total)
2. For each of those k/v pairs, consider those that have at least 25% coverage for the `name` tag, or at least 10,000 individual features with `name`.
3. Save as JSON

'Selected keys' are any OSM namespaces that contain what we could consider POI:

```python
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
```

The `name` tag is an important heuristic - if we loosely define a POI as 'a place you would visit', features without names are not likely to be useful.

A sample output JSON, based on a run done 2025-11-28, is [here](poi_kvs.json).

### Mapping to the Real World

I manually mapped the output k/v to [Google's top level POI classes](https://developers.google.com/maps/documentation/places/web-service/place-types#table-a). [Here's that table](mapping.csv).