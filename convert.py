"""
GPX converter for vpohid.com.ua JSON exports.

Features:
- Reads data either from a local JSON file or from a URL.
- Supports three input JSON shapes: a plain list of items, an object with "items",
  or an object with "response.items".
- Produces GPX 1.1; optionally adds OsmAnd extensions (icon, color, background).
- Supports grouping: single group name or by item kind.

Configuration is provided via CLI flags only (with built-in defaults).
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# --- CONSTANTS ---

BASE_URL = "https://vpohid.com.ua"

# Mapping of types ('kind') to OsmAnd icons.
KIND_TO_OSMAND_ICON: Dict[str, str] = {
    "dangerplace": "hazard",
    "guide": "tourism_information",
    "kampplace": "tourism_camp_site",
    "lake": "water",
    "mount": "natural",
    "parking": "parking",
    "pasture": "grassland",
    "photo": "special_photo_camera",
    "placeofinterest": "special_star",
    "rescuepost": "mountain_rescue",
    "usefulbuilding": "special_house",
    "watersource": "natural_spring",
}

# Default icon if the type is not found in the dictionary.
DEFAULT_ICON = "special_star"

# Mapping of types ('kind') to icon colors.
KIND_TO_COLOR: Dict[str, str] = {
    "dangerplace": "#FF0000",
    "guide": "#0000FF",
    "kampplace": "#964B00",
    "lake": "#00FFFF",
    "mount": "#8B0000",
    "parking": "#0000FF",
    "pasture": "#008000",
    "photo": "#FFA500",
    "placeofinterest": "#FFD700",
    "rescuepost": "#FF0000",
    "usefulbuilding": "#808080",
    "watersource": "#00FFFF",
}
# Default color.
DEFAULT_COLOR = "#4A4A4A"


def build_config_from_env_and_args() -> Dict[str, Any]:
    """Build runtime config from CLI only (with defaults).

    Returns a dict with keys: use_osmand_tags, use_single_group_name,
    group_name, input_json, input_url, output_gpx.
    If neither input_json nor input_url is provided, defaults to my_places.json.
    If output_gpx is empty, generates a name based on OsmAnd flag.
    """
    defaults = {"use_osmand_tags": True}

    parser = argparse.ArgumentParser(
        description=(
            "Конвертує список локацій з JSON у GPX 1.1. "
            "Підтримує розширення OsmAnd (іконки, кольори) та групування."
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_json",
        help=(
            "Вхідний JSON-файл (за замовчуванням: my_places.json)"
        ),
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="input_url",
        help=(
            "URL з JSON-відповіддю (поля у response.items)"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_gpx",
        help=(
            "Шлях до вихідного GPX-файлу (за замовчуванням генерується автоматично)"
        ),
    )

    # OsmAnd extensions: default is enabled; provide only the disabling flag.
    parser.add_argument(
        "--no-osmand-tags",
        dest="use_osmand_tags",
        action="store_false",
        help="Вимкнути розширення OsmAnd",
    )
    parser.set_defaults(use_osmand_tags=defaults["use_osmand_tags"])

    # Grouping: only --group-name. If provided => single group with this name;
    # otherwise group by kind.
    parser.add_argument(
        "--group-name",
        dest="group_name",
        default=None,
        help=(
            "Назва єдиної групи. Якщо не вказано — групування за типом (kind)"
        ),
    )

    args = parser.parse_args()

    use_single = args.group_name is not None and args.group_name.strip() != ""
    cfg: Dict[str, Any] = {
        "use_osmand_tags": args.use_osmand_tags,
        "use_single_group_name": use_single,
        "group_name": (args.group_name.strip() if use_single else ""),
        "input_json": args.input_json or "",
        "input_url": args.input_url or "",
        "output_gpx": args.output_gpx or "",
    }

    # If no source provided — use default file
    if not cfg.get("input_json") and not cfg.get("input_url"):
        cfg["input_json"] = "my_places.json"

    # If output file is not set — generate the name automatically
    if not cfg["output_gpx"]:
        cfg["output_gpx"] = (
            "converted_places_"
            f"{'osmand' if cfg['use_osmand_tags'] else 'standard'}.gpx"
        )

    return cfg


def _extract_items(ob: Any) -> List[Dict[str, Any]]:
    """Return a list of items from possible JSON shapes.

    - If it's an array — return it as a list of dicts.
    - If it's an object with response.items — return that list.
    - If it's an object with items — return that list.
    Otherwise, raise ValueError.
    """
    if isinstance(ob, list):
        return ob  # type: ignore[return-value]
    if isinstance(ob, dict):
        if isinstance(ob.get("response"), dict) and isinstance(
            ob["response"].get("items"), list
        ):
            return ob["response"]["items"]  # type: ignore[return-value]
        if isinstance(ob.get("items"), list):
            return ob["items"]  # type: ignore[return-value]
    raise ValueError(
        "Непідтримуваний формат JSON: очікується масив або об'єкт з 'response.items'."
    )


def _make_gpx_header(use_osmand_tags: bool) -> str:
    """Return the GPX header; adds OsmAnd namespace if enabled."""
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    if use_osmand_tags:
        header += (
            '<gpx version="1.1" creator="https://github.com/gekich/vpohid-gpx-converter" '
            'xmlns="http://www.topografix.com/GPX/1/1" '
            'xmlns:osmand="https://osmand.net">'
        )
    else:
        header += (
            '<gpx version="1.1" creator="https://github.com/gekich/vpohid-gpx-converter" '
            'xmlns="http://www.topografix.com/GPX/1/1">'
        )
    return header


def _load_data(input_json_file: str, input_url: str) -> List[Dict[str, Any]]:
    """Loads data from a file or URL and returns a list of items."""
    data_obj: Any
    if input_url:
        try:
            with urlopen(input_url, timeout=20) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                text = resp.read().decode(charset, errors="replace")
                data_obj = json.loads(text)
        except HTTPError as e:
            raise RuntimeError(
                f"HTTP помилка {e.code} при завантаженні URL: {input_url}"
            ) from e
        except URLError as e:
            raise RuntimeError(
                f"Помилка мережі при завантаженні URL: {e.reason}"
            ) from e
    else:
        with open(input_json_file, "r", encoding="utf-8") as f:
            data_obj = json.load(f)
    return _extract_items(data_obj)


def _make_wpt(place: Dict[str, Any], cfg: Dict[str, Any], base_url: str) -> str:
    """Build a GPX <wpt> element for a single place.

    Uses fields: latitude, longitude (required), sealevel-><ele>, whenadded-><time>,
    title-><name>, description-><desc>, kind-><type> (or a single group name from cfg),
    viewurl to append a link (with base_url). When OsmAnd is enabled, adds icon/color/background
    and a clickable link inside <extensions>.
    Returns an empty string if lat/lon are missing.
    """
    lat, lon = place.get("latitude"), place.get("longitude")
    if lat is None or lon is None:
        return ""

    parts: List[str] = [f'  <wpt lat="{lat}" lon="{lon}">']

    if place.get("sealevel"):
        parts.append(f'    <ele>{place["sealevel"]}</ele>')
    if place.get("whenadded"):
        parts.append(
            f'    <time>{place["whenadded"].replace(" ", "T")}Z</time>'
        )
    if place.get("title"):
        parts.append(f'    <name>{html.escape(place["title"])}</name>')

    description_content = place.get("description", "")
    if place.get("viewurl"):
        full_url = f"{base_url}{place['viewurl']}"
        description_content += (
            f'<br/><br/><a href="{full_url}">Детальніше</a>'
        )
    if description_content:
        parts.append(f"    <desc>{html.escape(description_content)}</desc>")

    if cfg["use_single_group_name"] and cfg["group_name"]:
        parts.append(f"    <type>{html.escape(cfg['group_name'])}</type>")
    elif place.get("kind"):
        parts.append(f"    <type>{html.escape(place['kind'])}</type>")

    if place.get("viewurl"):
        parts.append(
            f'    <link href="{base_url}{place["viewurl"]}"><text>Детальніше</text></link>'
        )
    if cfg["use_osmand_tags"]:
        parts.append("    <extensions>")
        kind = place.get("kind", "")
        icon_name = KIND_TO_OSMAND_ICON.get(kind, DEFAULT_ICON)
        color_hex = KIND_TO_COLOR.get(kind, DEFAULT_COLOR)
        parts.append(f"      <osmand:icon>{icon_name}</osmand:icon>")
        parts.append(f"      <osmand:color>{color_hex}</osmand:color>")
        parts.append("      <osmand:background>circle</osmand:background>")
        parts.append("    </extensions>")

    parts.append("  </wpt>")
    return "\n".join(parts)


def convert_places_to_gpx(cfg: Dict[str, Any]) -> int:
    """Converts data from a file or URL to GPX. Returns the number of converted points."""
    input_json_file = cfg.get("input_json") or ""
    input_url = cfg.get("input_url") or ""
    output_gpx_file = cfg["output_gpx"]
    base_url = BASE_URL.rstrip("/")

    gpx_parts: List[str] = [_make_gpx_header(cfg["use_osmand_tags"])]

    data = _load_data(input_json_file, input_url)

    converted = 0
    for place in data:
        wpt_xml = _make_wpt(place, cfg, base_url)
        if wpt_xml:
            gpx_parts.append(wpt_xml)
            converted += 1

    gpx_parts.append("</gpx>")

    with open(output_gpx_file, "w", encoding="utf-8") as f:
        f.write("\n".join(gpx_parts))

    return converted


def main() -> int:
    """Entry point: validates inputs, runs conversion, prints result.

    Exit codes: 0 success, 1 handled error, 2 invalid input configuration.
    """
    try:
        cfg = build_config_from_env_and_args()

        # Validate data source: file or URL
        if bool(cfg.get("input_json")) and bool(cfg.get("input_url")):
            print(
                "🚨 Помилка: виберіть лише одне джерело — файл (-i/--input) АБО URL (-u/--url).",
                file=sys.stderr,
            )
            return 2

        # Informational message about the selected data source
        if cfg.get("input_url"):
            print(f"Джерело: URL -> {cfg['input_url']}")
        else:
            print(f"Джерело: файл -> {cfg['input_json']}")

        count = convert_places_to_gpx(cfg)
        print(f"✅ Успішно! Створено файл: {cfg['output_gpx']}")
        print(f"Конвертовано {count} точок.")
        return 0
    except FileNotFoundError as e:
        missing = getattr(e, "filename", "") or "вхідний файл"
        print(f"🚨 Помилка: файл '{missing}' не знайдено.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(
            f"🚨 Помилка: Неправильний формат JSON у файлі: {e}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"🚨 Сталася невідома помилка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
