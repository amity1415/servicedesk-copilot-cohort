"""Facts about the fictional company that every generated asset must agree on.

Larkhaven Group does not exist. Its domain uses the reserved .example
top-level domain, so no address in the data pack can resolve to a real site.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

COMPANY = "Larkhaven Group"
DOMAIN = "larkhaven.example"
HEADCOUNT_STATED = 10_000  # what the documents say; the database seed is a 300-person sample

# The data pack is written as if exported on this date.
AS_OF = date(2026, 11, 13)


@dataclass(frozen=True)
class Office:
    city: str
    code: str
    region: str
    headcount: int


@dataclass(frozen=True)
class Region:
    code: str
    name: str
    support_hours: str
    phone: str
    tech_bar: str
    guest_ssid: str
    printer_queue: str
    room_panel: str


REGIONS = {
    "AMER": Region(
        code="AMER",
        name="Americas",
        support_hours="07:00 to 19:00 Central Time, Monday to Friday",
        phone="extension 4357 or +1 312 555 0143",
        tech_bar="Chicago, floor 3, 09:00 to 16:00; Toronto, floor 2, 10:00 to 15:00",
        guest_ssid="LarkGuest-AMER",
        printer_queue="FollowMe-AMER",
        room_panel="RoomBoard Chicago and RoomBoard Toronto",
    ),
    "EMEA": Region(
        code="EMEA",
        name="Europe, Middle East and Africa",
        support_hours="07:00 to 19:00 UK time, Monday to Friday",
        phone="extension 4357 or +44 20 7946 0143",
        tech_bar="London, floor 5, 09:00 to 16:00; Munich, floor 1, 09:30 to 15:30",
        guest_ssid="LarkGuest-EMEA",
        printer_queue="FollowMe-EMEA",
        room_panel="RoomBoard London and RoomBoard Munich",
    ),
    "APAC": Region(
        code="APAC",
        name="Asia Pacific",
        support_hours="07:00 to 19:00 India Standard Time, Monday to Friday",
        phone="extension 4357 or +65 6555 0143",
        tech_bar="Bengaluru, floor 4, 09:30 to 17:00; Singapore, floor 9, 10:00 to 15:00",
        guest_ssid="LarkGuest-APAC",
        printer_queue="FollowMe-APAC",
        room_panel="RoomBoard Bengaluru and RoomBoard Singapore",
    ),
}

OFFICES = (
    Office("Chicago", "CHI", "AMER", 100),
    Office("Toronto", "TOR", "AMER", 35),
    Office("London", "LON", "EMEA", 55),
    Office("Munich", "MUC", "EMEA", 35),
    Office("Bengaluru", "BLR", "APAC", 50),
    Office("Singapore", "SIN", "APAC", 25),
)

# Department -> head count in the 300-person sample.
DEPARTMENTS = {
    "Executive": 1,
    "Engineering": 59,
    "Sales": 55,
    "Customer Support": 45,
    "Operations": 40,
    "IT": 32,
    "Finance": 25,
    "Marketing": 20,
    "HR": 15,
    "Legal": 8,
}

# Services whose status the diagnostics agent can check.
SERVICES = (
    ("LarkID", "Single sign-on and multi-factor authentication"),
    ("SecureTunnel VPN", "Remote access VPN gateways"),
    ("Email", "Mailboxes and calendars"),
    ("Microsoft Teams", "Chat, calls and meetings"),
    ("HelpHub", "IT service portal"),
    ("App Hub", "Self-service software installation"),
    ("FinSight", "Finance reporting"),
    ("FollowMe Printing", "Badge-release printing"),
    ("LarkNet Wi-Fi", "Office wireless network"),
    ("File Shares", "Departmental shared folders"),
)

OS_LABELS = {
    "windows": "Windows",
    "macos": "macOS",
    "ios": "iPhone and iPad",
    "android": "Android",
    "any": "Any",
}
