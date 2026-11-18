"""Reference tables: software catalogue, service level targets and glossary.

Charges are invented internal figures. They are not vendor prices.
"""

from datagen.docmodel import App

NONE = "None"
MGR = "Manager"
MGR_CC = "Manager + cost-centre owner"
MGR_OWNER = "Manager + data owner"

BOTH = "Windows, macOS"
WIN = "Windows"
MOBILE = "iOS, Android"
WEB = "Web"

HUB = "App Hub"
REQUEST = "HelpHub request, then App Hub"
WEB_SSO = "LarkID portal"

APPS = (
    App("Microsoft 365 Apps", "Microsoft", "Productivity", "Site", 0, NONE, BOTH, "Preinstalled"),
    App("Microsoft Teams", "Microsoft", "Collaboration", "Site", 0, NONE, BOTH, "Preinstalled"),
    App("OneDrive", "Microsoft", "Storage", "Site", 0, NONE, BOTH, "Preinstalled"),
    App("Google Chrome", "Google", "Browser", "Free", 0, NONE, BOTH, HUB),
    App("Microsoft Edge", "Microsoft", "Browser", "Free", 0, NONE, BOTH, "Preinstalled"),
    App("SecureTunnel VPN", "Larkhaven IT", "Network", "Site", 0, NONE, BOTH, HUB),
    App("EndpointShield", "Larkhaven IT", "Security", "Site", 0, NONE, BOTH, "Preinstalled"),
    App("VaultKey", "Larkhaven IT", "Security", "Site", 0, NONE, BOTH, HUB),
    App("LarkID Authenticator", "Larkhaven IT", "Security", "Free", 0, NONE, MOBILE, "App store"),
    App("DeviceCare", "Larkhaven IT", "Device management", "Site", 0, NONE, MOBILE, "App store"),
    App("SendSafe", "Larkhaven IT", "File transfer", "Site", 0, NONE, WEB, WEB_SSO),
    App("Adobe Acrobat Reader", "Adobe", "Documents", "Free", 0, NONE, BOTH, HUB),
    App("Adobe Acrobat Pro", "Adobe", "Documents", "Named", 240, MGR, BOTH, REQUEST, seats=120),
    App(
        "Microsoft Visio",
        "Microsoft",
        "Diagrams",
        "Named",
        180,
        MGR,
        WIN,
        REQUEST,
        seats=25,
        used=25,
    ),
    App("Microsoft Project", "Microsoft", "Planning", "Named", 360, MGR_CC, WIN, REQUEST, seats=30),
    App("Power BI Desktop", "Microsoft", "Analytics", "Free", 0, NONE, WIN, HUB),
    App("Power BI Pro", "Microsoft", "Analytics", "Named", 168, MGR, WEB, REQUEST, seats=80),
    App(
        "Tableau Desktop", "Salesforce", "Analytics", "Named", 840, MGR_CC, BOTH, REQUEST, seats=20
    ),
    App("Tableau Viewer", "Salesforce", "Analytics", "Named", 180, MGR, WEB, REQUEST, seats=90),
    App(
        "FinSight",
        "Larkhaven Finance Systems",
        "Finance",
        "Named",
        600,
        MGR_OWNER,
        WEB,
        WEB_SSO,
        restricted=True,
        seats=60,
        used=58,
    ),
    App(
        "CoreERP",
        "Larkhaven Finance Systems",
        "Finance",
        "Named",
        0,
        MGR_OWNER,
        WEB,
        WEB_SSO,
        restricted=True,
        seats=200,
    ),
    App(
        "PeopleHub administration",
        "Larkhaven HR Systems",
        "HR",
        "Named",
        0,
        MGR_OWNER,
        WEB,
        WEB_SSO,
        restricted=True,
        seats=15,
    ),
    App("TrackIt", "Larkhaven IT", "Project tracking", "Site", 0, MGR, WEB, WEB_SSO),
    App("Zoom Workplace", "Zoom", "Collaboration", "Named", 150, MGR, BOTH, REQUEST, seats=60),
    App("Miro", "Miro", "Collaboration", "Named", 120, MGR, WEB, REQUEST, seats=70),
    App("Figma", "Figma", "Design", "Named", 540, MGR_CC, WEB, REQUEST, seats=25),
    App("Adobe Creative Cloud", "Adobe", "Design", "Named", 960, MGR_CC, BOTH, REQUEST, seats=18),
    App("Snagit", "TechSmith", "Screen capture", "Named", 40, MGR, BOTH, REQUEST, seats=100),
    App("Camtasia", "TechSmith", "Video", "Named", 220, MGR, BOTH, REQUEST, seats=20),
    App("AutoCAD LT", "Autodesk", "Engineering", "Named", 480, MGR_CC, WIN, REQUEST, seats=12),
    App("Visual Studio Code", "Microsoft", "Development", "Free", 0, NONE, BOTH, HUB),
    App("Python 3", "Python Software Foundation", "Development", "Free", 0, NONE, BOTH, HUB),
    App("Git", "Software Freedom Conservancy", "Development", "Free", 0, NONE, BOTH, HUB),
    App("Docker Desktop", "Docker", "Development", "Named", 252, MGR, BOTH, REQUEST, seats=70),
    App(
        "PyCharm Professional",
        "JetBrains",
        "Development",
        "Named",
        249,
        MGR,
        BOTH,
        REQUEST,
        seats=40,
    ),
    App("Postman", "Postman", "Development", "Free", 0, NONE, BOTH, HUB),
    App("DBeaver Community", "DBeaver", "Development", "Free", 0, NONE, BOTH, HUB),
    App(
        "GitHub Copilot Business",
        "GitHub",
        "AI assistant",
        "Named",
        228,
        MGR,
        BOTH,
        REQUEST,
        seats=80,
    ),
    App("7-Zip", "Igor Pavlov", "Utilities", "Free", 0, NONE, WIN, HUB),
    App("Notepad++", "Notepad++ team", "Utilities", "Free", 0, NONE, WIN, HUB),
)

# Priority, definition, first response, resolution target, service hours, updates to requester.
SLA_PRIORITIES = (
    (
        "Priority 1",
        "A service is down for an office or region, or a security incident is in progress",
        "15 minutes",
        "4 hours",
        "24 hours, every day",
        "Every 30 minutes on the status page",
    ),
    (
        "Priority 2",
        "A team cannot work, an event is at risk within 2 hours, or a device is lost or stolen",
        "30 minutes",
        "8 hours",
        "Support hours; lost devices 24 hours",
        "Every 2 hours",
    ),
    (
        "Priority 3",
        "One person cannot do part of their work and has no workaround",
        "4 hours",
        "3 business days",
        "Support hours",
        "Daily",
    ),
    (
        "Priority 4",
        "A request, a question, or a fault with a workaround",
        "1 business day",
        "5 business days",
        "Support hours",
        "On change of status",
    ),
)

# Request, target, clock starts.
SLA_REQUESTS = (
    ("Access to a standard application", "60 minutes", "Final approval"),
    ("Access to a restricted application", "60 minutes", "Data owner's approval"),
    (
        "Licensed software from the catalogue",
        "60 minutes",
        "Final approval, when a licence is free",
    ),
    ("Software not in the catalogue", "10 business days", "Request submitted"),
    ("MFA reset", "4 hours", "Identity verified"),
    (
        "New joiner setup",
        "Ready 2 business days before start",
        "Form submitted 5 business days ahead",
    ),
    ("Replacement laptop", "5 business days", "Request approved"),
    ("Shared mailbox or distribution list", "2 business days", "Request approved"),
    ("Temporary administrator rights", "1 business day", "Both approvals recorded"),
    ("Guest Wi-Fi multi-day pass", "1 business day", "Request submitted"),
)

GLOSSARY = (
    (
        "A2A",
        "Agent-to-Agent protocol, used by the IT assistant to hand work to another team's assistant.",
    ),
    ("App Hub", "The self-service application on every laptop that installs approved software."),
    ("BYOD", "Bring your own device: a personal phone or tablet used for work."),
    ("DeviceCare", "The mobile device management application for phones and tablets."),
    ("FIDO2", "A standard for hardware security keys used as an MFA method."),
    ("FollowMe", "Badge-release printing: one queue, collected at any printer."),
    ("HelpHub", "The IT service portal for tickets and requests."),
    ("JML", "Joiner, mover, leaver: the processes for people starting, changing role and leaving."),
    ("KB", "Knowledge base."),
    ("KI", "Known issue: a fault with a documented cause and workaround."),
    ("LarkID", "The single sign-on and identity service."),
    ("LarkNet", "The office Wi-Fi network for company laptops."),
    ("MFA", "Multi-factor authentication."),
    ("P1 to P4", "Ticket priorities 1 (highest) to 4, set from impact and urgency."),
    ("SLA", "Service level agreement: the response and resolution targets."),
    ("SSO", "Single sign-on."),
    ("TAP", "Temporary access pass: a single-use code that lets a user sign in to register MFA."),
    ("Tech Bar", "The walk-up IT support desk in each office."),
    ("VPN", "Virtual private network; at Larkhaven, the SecureTunnel client."),
)
