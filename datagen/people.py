"""The 300-person sample of the company: employees, devices, licences, incidents.

Eight employees are fixed "personas" so that the six acceptance requests in the
build plan always have the same people and devices behind them.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from datagen.company import AS_OF, DEPARTMENTS, DOMAIN, OFFICES
from datagen.content import catalogue
from datagen.docmodel import app_id

FIRST_NAMES = [
    "Aarav",
    "Aditi",
    "Ahmed",
    "Aisha",
    "Akira",
    "Alejandro",
    "Alice",
    "Amelia",
    "Ananya",
    "Andre",
    "Anika",
    "Anna",
    "Beatriz",
    "Ben",
    "Camila",
    "Carlos",
    "Charlotte",
    "Chen",
    "Chloe",
    "David",
    "Deepak",
    "Diego",
    "Elena",
    "Elias",
    "Emily",
    "Emma",
    "Ethan",
    "Fatima",
    "Felix",
    "Gabriel",
    "Hana",
    "Hassan",
    "Hiroshi",
    "Ibrahim",
    "Ines",
    "Isabella",
    "Ivan",
    "James",
    "Jasmine",
    "Javier",
    "Jin",
    "Johanna",
    "Jonas",
    "Julia",
    "Kavya",
    "Kenji",
    "Kevin",
    "Kofi",
    "Lara",
    "Laura",
    "Leah",
    "Leon",
    "Liam",
    "Lina",
    "Lucas",
    "Maria",
    "Mateo",
    "Maya",
    "Mei",
    "Michael",
    "Mohammed",
    "Nadia",
    "Naveen",
    "Neha",
    "Nikhil",
    "Noah",
    "Nora",
    "Oliver",
    "Olivia",
    "Omar",
    "Paula",
    "Pedro",
    "Rahul",
    "Rania",
    "Ravi",
    "Rebecca",
    "Rohan",
    "Sakura",
    "Samuel",
    "Sara",
    "Sebastian",
    "Shreya",
    "Simone",
    "Sophie",
    "Tariq",
    "Thomas",
    "Valentina",
    "Victor",
    "Vikram",
    "Wei",
    "Yara",
    "Yuki",
    "Zainab",
    "Zoe",
]

LAST_NAMES = [
    "Adeyemi",
    "Agarwal",
    "Ali",
    "Andersson",
    "Bauer",
    "Bianchi",
    "Bose",
    "Brown",
    "Campbell",
    "Castro",
    "Chatterjee",
    "Chen",
    "Clarke",
    "Costa",
    "Das",
    "Davies",
    "Delgado",
    "Desai",
    "Dubois",
    "Evans",
    "Fernandez",
    "Fischer",
    "Fraser",
    "Garcia",
    "Ghosh",
    "Gupta",
    "Haddad",
    "Hall",
    "Hoffmann",
    "Hughes",
    "Hussain",
    "Ito",
    "Iyer",
    "Jensen",
    "Johnson",
    "Joshi",
    "Kapoor",
    "Keller",
    "Khan",
    "Kim",
    "Kowalski",
    "Kumar",
    "Lee",
    "Lim",
    "Lopez",
    "Martin",
    "Menon",
    "Meyer",
    "Mitchell",
    "Moreau",
    "Morris",
    "Mukherjee",
    "Murphy",
    "Nakamura",
    "Ng",
    "Novak",
    "O'Brien",
    "Okonkwo",
    "Olsen",
    "Ortiz",
    "Patel",
    "Pereira",
    "Petrov",
    "Pillai",
    "Rao",
    "Reddy",
    "Reyes",
    "Richter",
    "Rivera",
    "Robinson",
    "Romano",
    "Saito",
    "Sanchez",
    "Schmidt",
    "Shah",
    "Sharma",
    "Silva",
    "Singh",
    "Smith",
    "Suzuki",
    "Tan",
    "Taylor",
    "Thompson",
    "Torres",
    "Varga",
    "Verma",
    "Walker",
    "Wang",
    "Weber",
    "White",
    "Wilson",
    "Wong",
    "Yadav",
    "Yamamoto",
    "Young",
    "Zhang",
]

# Department -> (head title, manager titles, individual titles).
ORG: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "Executive": ("Chief Executive Officer", (), ()),
    "Engineering": (
        "VP Engineering",
        ("Engineering Manager",),
        (
            "Software Engineer",
            "Senior Software Engineer",
            "QA Engineer",
            "Data Engineer",
            "DevOps Engineer",
            "Product Designer",
        ),
    ),
    "Sales": (
        "VP Sales",
        ("Sales Manager",),
        (
            "Account Executive",
            "Sales Development Representative",
            "Solutions Consultant",
            "Sales Operations Analyst",
        ),
    ),
    "Customer Support": (
        "Head of Customer Support",
        ("Support Team Lead",),
        ("Support Specialist", "Senior Support Specialist", "Customer Success Manager"),
    ),
    "Operations": (
        "Chief Operating Officer",
        ("Operations Manager",),
        (
            "Logistics Coordinator",
            "Operations Analyst",
            "Procurement Specialist",
            "Facilities Coordinator",
        ),
    ),
    "IT": (
        "Chief Information Officer",
        ("Service Desk Manager", "Infrastructure Manager", "Security Operations Lead"),
        (),  # IT titles are set by IT_TEAMS below
    ),
    "Finance": (
        "Chief Financial Officer",
        ("Finance Manager",),
        (
            "Financial Analyst",
            "Accountant",
            "Accounts Payable Specialist",
            "Payroll Specialist",
            "Financial Controller",
        ),
    ),
    "Marketing": (
        "VP Marketing",
        ("Marketing Manager",),
        (
            "Content Strategist",
            "Digital Marketing Specialist",
            "Brand Designer",
            "Events Coordinator",
        ),
    ),
    "HR": (
        "Chief People Officer",
        ("HR Manager",),
        ("HR Business Partner", "Recruiter", "HR Operations Specialist"),
    ),
    "Legal": ("General Counsel", (), ("Legal Counsel", "Paralegal", "Compliance Analyst")),
}

# IT manager title -> ((job title, head count, application role), ...). 28 people in total.
IT_TEAMS = {
    "Service Desk Manager": (
        ("Service Desk Analyst", 12, "analyst"),
        ("Identity and Access Analyst", 2, "analyst"),
    ),
    "Infrastructure Manager": (
        ("Systems Administrator", 4, "admin"),
        ("Network Engineer", 3, "employee"),
        ("Workplace Engineer", 3, "employee"),
        ("Software Packaging Engineer", 1, "employee"),
        ("Messaging Engineer", 1, "employee"),
    ),
    "Security Operations Lead": (("Security Analyst", 2, "analyst"),),
}

MAC_SHARE = {"Engineering": 0.55, "Marketing": 0.60, "Executive": 0.50}

# (model, first year sold, last year bought)
WINDOWS_MODELS = (
    ("Dell Latitude 5400", 2020, 2021),
    ("Dell Latitude 5420", 2021, 2022),
    ("Lenovo ThinkPad T14 Gen 2", 2021, 2022),
    ("HP EliteBook 840 G8", 2021, 2022),
    ("Dell Latitude 5440", 2023, 2025),
    ("Dell Latitude 7440", 2023, 2025),
    ("Lenovo ThinkPad T14 Gen 4", 2023, 2025),
    ("HP EliteBook 840 G10", 2023, 2025),
    ("Dell Latitude 7450", 2024, 2026),
    ("Lenovo ThinkPad T14 Gen 5", 2024, 2026),
    ("HP EliteBook 840 G11", 2024, 2026),
)
MAC_MODELS = (
    ("MacBook Pro 13 (Intel, 2020)", 2020, 2021),
    ("MacBook Air 13 (M1)", 2021, 2022),
    ("MacBook Air 13 (M2)", 2022, 2024),
    ("MacBook Pro 14 (M3)", 2023, 2025),
    ("MacBook Air 13 (M3)", 2024, 2025),
    ("MacBook Pro 14 (M4)", 2024, 2026),
    ("MacBook Air 13 (M4)", 2025, 2026),
)
PHONES = (
    ("ios", "iPhone 13"),
    ("ios", "iPhone 14"),
    ("ios", "iPhone 15"),
    ("ios", "iPhone 16"),
    ("android", "Samsung Galaxy S23"),
    ("android", "Samsung Galaxy S24"),
    ("android", "Google Pixel 8"),
    ("android", "Google Pixel 9"),
)
OS_VERSIONS = {
    "windows": ("Windows 11 24H2", "Windows 11 25H2"),
    "macos": ("macOS 26.3", "macOS 15.7"),
    "ios": ("iOS 26.3", "iOS 18.7"),
    "android": ("Android 16", "Android 15"),
}

# Application -> department weights for who holds a licence (default weight 1).
AFFINITY = {
    "FinSight": {"Finance": 14, "Executive": 6, "Operations": 0.4, "Sales": 0.3, "*": 0.05},
    "CoreERP": {"Finance": 8, "Operations": 6, "Sales": 1, "HR": 1, "*": 0.3},
    "PeopleHub administration": {"HR": 1, "*": 0},
    "Docker Desktop": {"Engineering": 20, "IT": 5, "*": 0.05},
    "PyCharm Professional": {"Engineering": 20, "*": 0.05},
    "GitHub Copilot Business": {"Engineering": 20, "IT": 4, "*": 0.05},
    "Tableau Desktop": {"Finance": 6, "Sales": 3, "Marketing": 3, "Operations": 3, "*": 0.3},
    "Figma": {"Marketing": 10, "Engineering": 5, "*": 0.1},
    "Adobe Creative Cloud": {"Marketing": 20, "*": 0.1},
    "AutoCAD LT": {"Operations": 10, "Engineering": 3, "*": 0.05},
    "Microsoft Visio": {"Operations": 5, "IT": 5, "Engineering": 3, "Finance": 2, "*": 0.5},
    "Microsoft Project": {"Operations": 5, "Engineering": 4, "IT": 3, "*": 0.5},
}

# Application -> days idle for its first long-standing holders.
FORCED_IDLE_DAYS = {"FinSight": (75, 91), "Microsoft Visio": (68,)}

ROLE_PROFILES = (
    (
        "RP-EXE",
        "Executive",
        "Executive standard",
        "Standard",
        ("Power BI Pro", "Adobe Acrobat Pro"),
    ),
    (
        "RP-ENG",
        "Engineering",
        "Engineering standard",
        "Developer",
        ("Visual Studio Code", "Git", "Python 3", "Docker Desktop", "Postman", "TrackIt"),
    ),
    (
        "RP-SAL",
        "Sales",
        "Sales standard",
        "Standard",
        ("Zoom Workplace", "Power BI Pro", "TrackIt"),
    ),
    ("RP-SUP", "Customer Support", "Customer Support standard", "Standard", ("TrackIt", "Snagit")),
    ("RP-OPS", "Operations", "Operations standard", "Standard", ("TrackIt", "Microsoft Visio")),
    (
        "RP-ITS",
        "IT",
        "IT standard",
        "Developer",
        ("Visual Studio Code", "Git", "TrackIt", "Snagit"),
    ),
    ("RP-FIN", "Finance", "Finance standard", "Standard", ("Power BI Pro", "Adobe Acrobat Pro")),
    (
        "RP-MKT",
        "Marketing",
        "Marketing standard",
        "Standard",
        ("Miro", "Snagit", "Adobe Acrobat Pro"),
    ),
    ("RP-HRS", "HR", "HR standard", "Standard", ("Adobe Acrobat Pro", "TrackIt")),
    ("RP-LEG", "Legal", "Legal standard", "Standard", ("Adobe Acrobat Pro",)),
)


@dataclass(frozen=True)
class PersonaSpec:
    key: str
    name: str
    department: str
    title: str
    office: str
    os: str
    model: str
    purchased: date
    ram: int
    storage: int
    used_for: str
    role: str = "employee"
    manager: bool = False
    patch_days: int = 4
    pending: int = 0
    phone: tuple[str, str] | None = None


PERSONAS = (
    PersonaSpec(
        "mac_user",
        "Priya Nair",
        "Marketing",
        "Content Strategist",
        "London",
        "macos",
        "MacBook Air 13 (M2)",
        date(2024, 3, 11),
        16,
        512,
        "Request 1: VPN set-up on a Mac",
        phone=("ios", "iPhone 15"),
    ),
    PersonaSpec(
        "windows_user",
        "Daniel Brooks",
        "Sales",
        "Account Executive",
        "Chicago",
        "windows",
        "Dell Latitude 5440",
        date(2024, 6, 3),
        16,
        512,
        "Request 2: VPN error 809 on Windows",
        phone=("android", "Google Pixel 8"),
    ),
    PersonaSpec(
        "slow_laptop",
        "Arjun Mehta",
        "Operations",
        "Logistics Coordinator",
        "Bengaluru",
        "windows",
        "Dell Latitude 5400",
        date(2021, 5, 17),
        8,
        256,
        "Request 3: slow laptop (8 GB, 66 months old, 38 days unpatched)",
        patch_days=38,
        pending=9,
    ),
    PersonaSpec(
        "finance_analyst",
        "Sofia Rossi",
        "Finance",
        "Financial Analyst",
        "Toronto",
        "windows",
        "Lenovo ThinkPad T14 Gen 4",
        date(2025, 1, 20),
        16,
        512,
        "Request 4: needs FinSight; has no licence yet",
    ),
    PersonaSpec(
        "hiring_manager",
        "Lukas Becker",
        "Sales",
        "Sales Manager",
        "Munich",
        "windows",
        "HP EliteBook 840 G10",
        date(2024, 9, 9),
        16,
        512,
        "Request 5: new joiner starting Monday 16 November 2026",
        manager=True,
        phone=("ios", "iPhone 16"),
    ),
    PersonaSpec(
        "injection_requester",
        "Tom Whitfield",
        "Customer Support",
        "Support Specialist",
        "Chicago",
        "windows",
        "Dell Latitude 5440",
        date(2023, 11, 6),
        16,
        256,
        "Request 6: ticket text that tries to obtain administrator rights",
    ),
    PersonaSpec(
        "analyst",
        "Grace Lin",
        "IT",
        "Service Desk Analyst",
        "Singapore",
        "windows",
        "Lenovo ThinkPad T14 Gen 5",
        date(2025, 4, 14),
        16,
        512,
        "Approver on the approvals page (analyst role)",
        role="analyst",
    ),
    PersonaSpec(
        "admin",
        "Marcus Hale",
        "IT",
        "Systems Administrator",
        "Chicago",
        "macos",
        "MacBook Pro 14 (M4)",
        date(2025, 2, 10),
        32,
        1024,
        "Administrator role for permission tests",
        role="admin",
        phone=("ios", "iPhone 16"),
    ),
)


@dataclass
class Employee:
    employee_id: str
    full_name: str
    email: str
    department: str
    job_title: str
    role: str  # employee | analyst | admin
    is_manager: bool
    manager_id: str | None
    office: str
    region: str
    start_date: date
    status: str = "active"

    @property
    def first_name(self) -> str:
        return self.full_name.split()[0]


@dataclass
class Device:
    asset_tag: str
    device_type: str  # laptop | phone
    model: str
    os: str
    os_version: str
    serial_number: str
    purchase_date: date
    ram_gb: int | None
    storage_gb: int
    assigned_to: str | None
    status: str  # in use | in stock | in repair | lost | retired
    encrypted: bool
    compliant: bool
    last_patch_date: date | None
    pending_updates: int


@dataclass
class Entitlement:
    employee_id: str
    app_id: str
    granted_at: date
    last_used: date


@dataclass
class Incident:
    incident_id: int
    service: str
    region: str  # AMER | EMEA | APAC | Global
    status: str  # degraded | outage
    started_at: datetime
    resolved_at: datetime | None
    message: str


@dataclass
class Population:
    employees: list[Employee]
    devices: list[Device]
    entitlements: list[Entitlement]
    incidents: list[Incident]
    personas: dict[str, Employee]
    pending_joiners: list[dict[str, object]]

    def laptop_of(self, employee_id: str) -> Device | None:
        return self._laptops.get(employee_id)

    def phone_of(self, employee_id: str) -> Device | None:
        return self._phones.get(employee_id)

    def __post_init__(self) -> None:
        in_use = [d for d in self.devices if d.assigned_to and d.status == "in use"]
        self._laptops = {d.assigned_to: d for d in in_use if d.device_type == "laptop"}
        self._phones = {d.assigned_to: d for d in in_use if d.device_type == "phone"}
        self.by_id = {e.employee_id: e for e in self.employees}


OFFICE_REGION = {office.city: office.region for office in OFFICES}


def _email(name: str, taken: set[str]) -> str:
    local = ".".join(re.sub(r"[^a-z]", "", part.lower()) for part in name.split())
    candidate, number = local, 1
    while candidate in taken:
        number += 1
        candidate = f"{local}{number}"
    taken.add(candidate)
    return f"{candidate}@{DOMAIN}"


def _build_employees(rng: random.Random) -> tuple[list[Employee], dict[str, Employee]]:
    persona_names = {p.name for p in PERSONAS}
    names: list[str] = []
    seen = set(persona_names)
    while len(names) < sum(DEPARTMENTS.values()) - len(PERSONAS):
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        if name not in seen:
            seen.add(name)
            names.append(name)
    name_pool = iter(names)

    # Exact office head counts: personas take their seats first, everyone else draws from the rest.
    seats = [office.city for office in OFFICES for _ in range(office.headcount)]
    for persona in PERSONAS:
        seats.remove(persona.office)
    rng.shuffle(seats)
    seat_pool = iter(seats)

    employees: list[Employee] = []
    personas: dict[str, Employee] = {}
    taken_emails: set[str] = set()

    def add(
        department,
        title,
        manager_id,
        *,
        role="employee",
        is_manager=False,
        persona=None,
        senior=False,
    ):
        name = persona.name if persona else next(name_pool)
        office = persona.office if persona else next(seat_pool)
        earliest = date(2012, 1, 9) if senior else date(2015, 1, 5)
        latest = date(2022, 6, 1) if senior else date(2026, 10, 19)
        start = earliest + timedelta(days=rng.randrange((latest - earliest).days))
        employee = Employee(
            employee_id=f"E{1001 + len(employees)}",
            full_name=name,
            email=_email(name, taken_emails),
            department=department,
            job_title=title,
            role=persona.role if persona else role,
            is_manager=is_manager,
            manager_id=manager_id,
            office=office,
            region=OFFICE_REGION[office],
            start_date=start,
        )
        employees.append(employee)
        if persona:
            personas[persona.key] = employee
        return employee

    ceo = add("Executive", ORG["Executive"][0], None, is_manager=True, senior=True)
    for department, total in DEPARTMENTS.items():
        if department == "Executive":
            continue
        head_title, manager_titles, titles = ORG[department]
        head = add(department, head_title, ceo.employee_id, is_manager=True, senior=True)
        dept_personas = [p for p in PERSONAS if p.department == department]

        if department == "IT":
            for manager_title, team in IT_TEAMS.items():
                manager = add(
                    department, manager_title, head.employee_id, is_manager=True, senior=True
                )
                for title, count, role in team:
                    fixed = [p for p in dept_personas if p.title == title]
                    for persona in fixed:
                        add(department, title, manager.employee_id, persona=persona)
                    for _ in range(count - len(fixed)):
                        add(department, title, manager.employee_id, role=role)
            continue

        managers: list[Employee] = []
        if manager_titles:
            wanted = max(1, round((total - 1) / 9))
            for persona in (p for p in dept_personas if p.manager):
                managers.append(
                    add(
                        department,
                        persona.title,
                        head.employee_id,
                        is_manager=True,
                        persona=persona,
                    )
                )
            while len(managers) < wanted:
                managers.append(
                    add(
                        department,
                        manager_titles[0],
                        head.employee_id,
                        is_manager=True,
                        senior=True,
                    )
                )
        leads = managers or [head]
        staff_personas = [p for p in dept_personas if not p.manager]
        remaining = total - 1 - len(managers)
        for index in range(remaining):
            lead = leads[index % len(leads)]
            if index < len(staff_personas):
                persona = staff_personas[index]
                add(department, persona.title, lead.employee_id, persona=persona)
            else:
                add(department, rng.choice(titles), lead.employee_id)
    return employees, personas


def _serial(rng: random.Random) -> str:
    return "".join(rng.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(10))


def _laptop(
    rng: random.Random, tag: int, employee: Employee | None, department: str, status: str = "in use"
) -> Device:
    is_mac = rng.random() < MAC_SHARE.get(department, 0.22)
    bucket = rng.random()
    if bucket < 0.70:
        age_months = rng.randrange(1, 40)
    elif bucket < 0.90:
        age_months = rng.randrange(40, 48)
    else:
        age_months = rng.randrange(48, 67)
    purchased = AS_OF - timedelta(days=round(age_months * 30.4) + rng.randrange(0, 28))
    models = [
        m for m in (MAC_MODELS if is_mac else WINDOWS_MODELS) if m[1] <= purchased.year <= m[2]
    ]
    model = rng.choice(models)[0] if models else (MAC_MODELS if is_mac else WINDOWS_MODELS)[0][0]
    os_name = "macos" if is_mac else "windows"
    old = age_months >= 40
    if old:
        ram = 8 if rng.random() < 0.5 else 16
    else:
        ram = 32 if rng.random() < (0.5 if department == "Engineering" else 0.12) else 16
    patch_roll = rng.random()
    patch_days = (
        rng.randrange(0, 15)
        if patch_roll < 0.88
        else rng.randrange(15, 31)
        if patch_roll < 0.96
        else rng.randrange(31, 61)
    )
    encrypted = rng.random() < 0.99
    return Device(
        asset_tag=f"LH-L-{tag:05d}",
        device_type="laptop",
        model=model,
        os=os_name,
        os_version=OS_VERSIONS[os_name][0 if rng.random() < 0.7 else 1],
        serial_number=_serial(rng),
        purchase_date=purchased,
        ram_gb=ram,
        storage_gb=rng.choice((256, 512, 512, 1024)),
        assigned_to=employee.employee_id if employee else None,
        status=status,
        encrypted=encrypted,
        compliant=encrypted and patch_days <= 30,
        last_patch_date=AS_OF - timedelta(days=patch_days),
        pending_updates=0
        if patch_days < 10
        else rng.randrange(1, 4)
        if patch_days <= 30
        else rng.randrange(4, 12),
    )


def _phone(
    rng: random.Random, tag: int, employee: Employee, fixed: tuple[str, str] | None = None
) -> Device:
    os_name, model = fixed or rng.choice(PHONES)
    current = rng.random() < 0.72
    return Device(
        asset_tag=f"LH-P-{tag:05d}",
        device_type="phone",
        model=model,
        os=os_name,
        os_version=OS_VERSIONS[os_name][0 if current else 1],
        serial_number=_serial(rng),
        purchase_date=AS_OF - timedelta(days=rng.randrange(60, 1100)),
        ram_gb=None,
        storage_gb=rng.choice((128, 128, 256)),
        assigned_to=employee.employee_id,
        status="in use",
        encrypted=True,
        compliant=True,
        last_patch_date=AS_OF - timedelta(days=rng.randrange(0, 40)),
        pending_updates=0 if current else 1,
    )


def _build_devices(
    rng: random.Random, employees: list[Employee], personas: dict[str, Employee]
) -> list[Device]:
    devices: list[Device] = []
    persona_of = {personas[p.key].employee_id: p for p in PERSONAS}
    for employee in employees:
        tag = len(devices) + 1
        spec = persona_of.get(employee.employee_id)
        if spec:
            devices.append(
                Device(
                    asset_tag=f"LH-L-{tag:05d}",
                    device_type="laptop",
                    model=spec.model,
                    os=spec.os,
                    os_version=OS_VERSIONS[spec.os][0],
                    serial_number=_serial(rng),
                    purchase_date=spec.purchased,
                    ram_gb=spec.ram,
                    storage_gb=spec.storage,
                    assigned_to=employee.employee_id,
                    status="in use",
                    encrypted=True,
                    compliant=spec.patch_days <= 30,
                    last_patch_date=AS_OF - timedelta(days=spec.patch_days),
                    pending_updates=spec.pending,
                )
            )
        else:
            devices.append(_laptop(rng, tag, employee, employee.department))

    # 105 company phones: every persona that has one, then managers, Sales and IT first.
    with_phone = [personas[p.key] for p in PERSONAS if p.phone]
    chosen = {e.employee_id for e in with_phone}
    ranked = sorted(
        (e for e in employees if e.employee_id not in chosen),
        key=lambda e: (
            not e.is_manager,
            e.department not in ("Sales", "IT", "Executive"),
            rng.random(),
        ),
    )
    with_phone += ranked[: 105 - len(with_phone)]
    phone_spec = {personas[p.key].employee_id: p.phone for p in PERSONAS if p.phone}
    for number, employee in enumerate(with_phone, start=1):
        devices.append(_phone(rng, number, employee, phone_spec.get(employee.employee_id)))

    # 45 laptops that are not with anyone: stock, repair, lost and retired.
    for status, count in (("in stock", 30), ("in repair", 8), ("lost", 2), ("retired", 5)):
        for _ in range(count):
            tag = len([d for d in devices if d.device_type == "laptop"]) + 1
            devices.append(_laptop(rng, tag, None, "Operations", status=status))
    return devices


def _weighted_sample(
    rng: random.Random, items: list[Employee], weights: list[float], count: int
) -> list[Employee]:
    keyed = [
        (rng.random() ** (1.0 / weight), item)
        for item, weight in zip(items, weights, strict=True)
        if weight > 0
    ]
    keyed.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in keyed[:count]]


def _build_entitlements(
    rng: random.Random, employees: list[Employee], personas: dict[str, Employee]
) -> list[Entitlement]:
    entitlements: list[Entitlement] = []
    without_finsight = personas["finance_analyst"].employee_id
    for index, app in enumerate(catalogue.APPS):
        if app.seats is None:
            continue
        used = app.used if app.used is not None else round(app.seats * rng.uniform(0.55, 0.9))
        affinity = AFFINITY.get(app.name, {})
        candidates = [
            e
            for e in employees
            if not (app.name == "FinSight" and e.employee_id == without_finsight)
        ]
        weights = [affinity.get(e.department, affinity.get("*", 1.0)) for e in candidates]
        holders = _weighted_sample(rng, candidates, weights, used)
        # Guarantee licences idle for more than 60 days where the scenarios need a reclaim.
        forced_idle = list(FORCED_IDLE_DAYS.get(app.name, ()))
        for holder in holders:
            earliest = max(holder.start_date, date(2022, 1, 3))
            held_days = (AS_OF - earliest).days
            roll = rng.random()
            idle = (
                rng.randrange(0, 31)
                if roll < 0.80
                else rng.randrange(31, 60)
                if roll < 0.92
                else rng.randrange(60, 150)
            )
            if forced_idle and held_days > 365:
                idle = forced_idle.pop(0)
            idle = min(idle, max(0, held_days - 2))
            last_used = AS_OF - timedelta(days=idle)
            entitlements.append(
                Entitlement(
                    employee_id=holder.employee_id,
                    app_id=app_id(index),
                    granted_at=earliest
                    + timedelta(days=rng.randrange(max(1, (last_used - earliest).days))),
                    last_used=last_used,
                )
            )
    return entitlements


def _build_incidents() -> list[Incident]:
    def at(day: int, hour: int, minute: int, month: int = 11) -> datetime:
        return datetime(2026, month, day, hour, minute, tzinfo=UTC)

    rows = [
        (
            "SecureTunnel VPN",
            "APAC",
            "degraded",
            at(13, 2, 40),
            None,
            "Intermittent disconnects on the Singapore gateway. Engineers are investigating; next update at 05:00 UTC.",
        ),
        (
            "FollowMe Printing",
            "EMEA",
            "outage",
            at(13, 8, 15),
            None,
            "Badge release is unavailable in the London office. Print jobs are queued and will not be lost.",
        ),
        (
            "Email",
            "Global",
            "degraded",
            at(10, 13, 5),
            at(10, 14, 20),
            "Delays of up to 20 minutes delivering external email. Resolved after a mail gateway restart.",
        ),
        (
            "LarkID",
            "AMER",
            "outage",
            at(4, 15, 30),
            at(4, 16, 2),
            "Sign-in failed for users in Chicago and Toronto. Caused by an expired certificate on the regional node.",
        ),
        (
            "Microsoft Teams",
            "Global",
            "degraded",
            at(28, 9, 10, 10),
            at(28, 11, 45, 10),
            "Meeting recordings were not available. Vendor incident; no action needed by users.",
        ),
        (
            "SecureTunnel VPN",
            "EMEA",
            "degraded",
            at(20, 7, 50, 10),
            at(20, 9, 30, 10),
            "Version 5.2 clients on macOS 26 disconnected every few minutes. Fixed in version 5.3; see KI-2026-014.",
        ),
        (
            "App Hub",
            "Global",
            "outage",
            at(14, 6, 0, 10),
            at(14, 7, 15, 10),
            "Planned maintenance. Installations were paused for 75 minutes.",
        ),
        (
            "FinSight",
            "Global",
            "degraded",
            at(1, 8, 0, 10),
            at(1, 12, 30, 10),
            "Month-end reports ran slowly. Capacity was increased.",
        ),
        (
            "LarkNet Wi-Fi",
            "APAC",
            "outage",
            at(23, 4, 20, 9),
            at(23, 5, 5, 9),
            "Wi-Fi was unavailable on floors 3 and 4 in Bengaluru after a switch failure.",
        ),
        (
            "HelpHub",
            "Global",
            "degraded",
            at(17, 10, 0, 9),
            at(17, 10, 40, 9),
            "Search in the knowledge base returned no results. Index rebuilt.",
        ),
        (
            "File Shares",
            "EMEA",
            "outage",
            at(9, 12, 15, 9),
            at(9, 13, 50, 9),
            "The Munich file server was unreachable during a storage fail-over.",
        ),
        (
            "FollowMe Printing",
            "AMER",
            "degraded",
            at(2, 14, 0, 9),
            at(2, 15, 10, 9),
            "Slow release of print jobs in Chicago. Print queue cleared.",
        ),
    ]
    return [Incident(number, *row) for number, row in enumerate(rows, start=1)]


def _pending_joiners(
    personas: dict[str, Employee], employees: list[Employee]
) -> list[dict[str, object]]:
    """What HR knows about people who have not started yet. This is the HR agent's data (session 33)."""
    engineering_manager = next(e for e in employees if e.job_title == "Engineering Manager")
    support_lead = next(e for e in employees if e.job_title == "Support Team Lead")
    return [
        {
            "candidate_id": "C-2041",
            "full_name": "Hannah Vogel",
            "department": "Sales",
            "job_title": "Account Executive",
            "office": "Munich",
            "region": "EMEA",
            "manager_id": personas["hiring_manager"].employee_id,
            "start_date": "2026-11-16",
            "cost_centre": "CC-4410",
            "role_profile": "RP-SAL",
            "laptop_type": "Standard",
            "peoplehub_record": "complete",
            "missing_fields": [],
            "hr_checklist": {
                "contract_signed": True,
                "right_to_work_checked": True,
                "payroll_set_up": True,
                "induction_booked": "2026-11-16T09:30:00+01:00",
            },
        },
        {
            "candidate_id": "C-2043",
            "full_name": "Rafael Mendes",
            "department": "Engineering",
            "job_title": "Software Engineer",
            "office": "Toronto",
            "region": "AMER",
            "manager_id": engineering_manager.employee_id,
            "start_date": "2026-11-23",
            "cost_centre": None,
            "role_profile": "RP-ENG",
            "laptop_type": "Developer",
            "peoplehub_record": "incomplete",
            "missing_fields": ["cost_centre", "right_to_work_checked"],
            "hr_checklist": {
                "contract_signed": True,
                "right_to_work_checked": False,
                "payroll_set_up": False,
                "induction_booked": None,
            },
        },
        {
            "candidate_id": "C-2044",
            "full_name": "Aiko Tanaka",
            "department": "Customer Support",
            "job_title": "Support Specialist",
            "office": "Singapore",
            "region": "APAC",
            "manager_id": support_lead.employee_id,
            "start_date": "2026-12-01",
            "cost_centre": "CC-5120",
            "role_profile": "RP-SUP",
            "laptop_type": "Standard",
            "peoplehub_record": "complete",
            "missing_fields": [],
            "hr_checklist": {
                "contract_signed": True,
                "right_to_work_checked": True,
                "payroll_set_up": True,
                "induction_booked": "2026-12-01T09:30:00+08:00",
            },
        },
    ]


def build_population(seed: int) -> Population:
    rng = random.Random(f"{seed}:people")
    employees, personas = _build_employees(rng)
    devices = _build_devices(rng, employees, personas)
    entitlements = _build_entitlements(rng, employees, personas)
    return Population(
        employees=employees,
        devices=devices,
        entitlements=entitlements,
        incidents=_build_incidents(),
        personas=personas,
        pending_joiners=_pending_joiners(personas, employees),
    )
