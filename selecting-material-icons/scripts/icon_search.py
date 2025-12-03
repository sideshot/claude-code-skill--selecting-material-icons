#!/usr/bin/env python3
"""
Material Design Icons name search tool.

Generic helper to find icon NAMES from the official metadata JSON.
Useful for any platform that uses Material Icons or Material Symbols.

Examples:
    python icon_search.py "shopping cart"
    python icon_search.py --quick "email"
    python icon_search.py --collection "blog posts"
    python icon_search.py --field "email address"
"""

import argparse
import json
import os
import sys
import urllib.request
from typing import List, Dict, Tuple


ICONS_URL = "https://material-icons.github.io/material-icons/data.json"
# Always keep the cache JSON inside this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "icons-metadata.json")


# Common collection-style mappings (platform-agnostic)
COLLECTION_MAPPINGS = {
    "users": ["person", "account_circle", "people", "group"],
    "products": ["inventory", "shopping_bag", "store", "category"],
    "orders": ["shopping_cart", "receipt", "assignment"],
    "posts": ["article", "description", "note", "subject"],
    "pages": ["description", "article", "web"],
    "media": ["photo_library", "image", "perm_media", "collections"],
    "files": ["folder", "insert_drive_file", "attach_file"],
    "settings": ["settings", "tune", "build"],
    "events": ["event", "calendar_today", "schedule"],
    "messages": ["message", "chat", "forum", "mail"],
    "comments": ["comment", "chat_bubble", "forum"],
    "reviews": ["star", "rate_review", "feedback"],
    "categories": ["category", "dashboard", "widgets"],
    "tags": ["local_offer", "label", "bookmark"],
    "notifications": ["notifications", "notification_important"],
    "analytics": ["analytics", "assessment", "bar_chart"],
    "teams": ["groups", "group_work", "people_alt"],
    "projects": ["folder_special", "work", "business_center"],
    "tasks": ["check_box", "assignment_turned_in", "task_alt"],
    "locations": ["place", "location_on", "map", "room"],
    "invoices": ["receipt_long", "description", "request_quote"],
    "payments": ["payment", "credit_card", "account_balance"],
}


FIELD_MAPPINGS = {
    "name": ["badge", "text_fields", "person"],
    "title": ["title", "text_fields", "subject"],
    "description": ["description", "subject", "notes"],
    "email": ["email", "alternate_email", "mail_outline"],
    "phone": ["phone", "call", "contact_phone"],
    "password": ["lock", "vpn_key", "security"],
    "url": ["link", "insert_link", "language"],
    "date": ["calendar_today", "event", "date_range"],
    "time": ["access_time", "schedule", "alarm"],
    "status": ["info", "check_circle", "toggle_on"],
    "priority": ["flag", "priority_high", "low_priority"],
    "rating": ["star", "grade", "star_half"],
    "price": ["attach_money", "payments", "currency_exchange"],
    "quantity": ["pin", "tag", "dialpad"],
    "address": ["location_on", "place", "home"],
    "city": ["location_city", "place", "apartment"],
    "country": ["public", "language", "flag"],
    "image": ["image", "photo_camera", "add_photo_alternate"],
    "file": ["attach_file", "insert_drive_file", "upload_file"],
    "color": ["palette", "color_lens", "format_color_fill"],
    "boolean": ["toggle_on", "check_box", "radio_button_checked"],
}


def load_icons() -> Dict:
    """Load icons metadata from cache or download."""
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Downloading icons metadata...", file=sys.stderr)
        with urllib.request.urlopen(ICONS_URL) as response:
            data = json.loads(response.read().decode())
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f)
            return data


def search_icons(data: Dict, query: str) -> List[str]:
    """Search for icons and return list of matching names."""
    query_lower = query.lower()
    matches: List[Tuple[str, int]] = []

    for icon in data["icons"]:
        score = 0

        # Exact name match
        if icon["name"] == query_lower:
            return [icon["name"]]  # Perfect match

        # Name contains query
        if query_lower in icon["name"]:
            score += 10

        # Tags contain query
        if "tags" in icon:
            for tag in icon["tags"]:
                tag_lower = tag.lower()
                if query_lower == tag_lower:
                    score += 5
                elif query_lower in tag_lower:
                    score += 2

        if score > 0:
            matches.append((icon["name"], score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return [name for name, score in matches[:10]]


def suggest_for_collection(query: str) -> List[str] | None:
    """Suggest icons based on a collection-like label."""
    query_lower = query.lower()

    for key, icons in COLLECTION_MAPPINGS.items():
        if key in query_lower or query_lower in key:
            return icons

    if any(word in query_lower for word in ["user", "account", "profile", "member"]):
        return COLLECTION_MAPPINGS["users"]
    if any(word in query_lower for word in ["product", "item", "goods", "catalog"]):
        return COLLECTION_MAPPINGS["products"]
    if any(word in query_lower for word in ["order", "purchase", "sale"]):
        return COLLECTION_MAPPINGS["orders"]
    if any(word in query_lower for word in ["post", "blog", "article", "content"]):
        return COLLECTION_MAPPINGS["posts"]

    return None


def suggest_for_field(query: str) -> List[str] | None:
    """Suggest icons based on a field-like label."""
    query_lower = query.lower()

    for key, icons in FIELD_MAPPINGS.items():
        if key in query_lower or query_lower in key:
            return icons

    return None


def print_suggestions(suggestions: List[str], label: str) -> None:
    """Print icon suggestions."""
    if not suggestions:
        print("No suggestions found.")
        return

    print(f"\n{label}:")
    for i, icon in enumerate(suggestions, 1):
        print(f"  {i}. {icon}")

    print(f"\n✓ Top pick: {suggestions[0]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Material Design Icon names using the official metadata JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for any icon
  python icon_search.py "shopping cart"

  # Get suggestions for a collection-like label
  python icon_search.py --collection "blog posts"

  # Get suggestions for a field-like label
  python icon_search.py --field "email address"

  # Just get the top result (good for scripting)
  python icon_search.py --quick "user profile"
        """,
    )

    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument(
        "-c",
        "--collection",
        help="Suggest icon for a collection-like label (e.g., products, orders, posts)",
    )
    parser.add_argument(
        "-f",
        "--field",
        help="Suggest icon for a field-like label (e.g., email, phone, price)",
    )
    parser.add_argument(
        "-q",
        "--quick",
        help="Return only the top result for the given query",
        metavar="QUERY",
    )

    args = parser.parse_args()

    query = args.query or args.quick or args.collection or args.field
    if not query:
        parser.print_help()
        return

    data = load_icons()

    suggestions: List[str] | None = None
    label = "Search results"

    if args.collection:
        suggestions = suggest_for_collection(args.collection)
        label = f"Collection icons for '{args.collection}'"
        if not suggestions:
            suggestions = search_icons(data, args.collection)
    elif args.field:
        suggestions = suggest_for_field(args.field)
        label = f"Field icons for '{args.field}'"
        if not suggestions:
            suggestions = search_icons(data, args.field)
    else:
        suggestions = search_icons(data, query)
        label = f"Icons matching '{query}'"

    if args.quick:
        if suggestions:
            print(suggestions[0])
        else:
            print("No match found", file=sys.stderr)
            sys.exit(1)
    else:
        print_suggestions(suggestions or [], label)


if __name__ == "__main__":
    main()


