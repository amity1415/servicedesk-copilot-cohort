"""Content model for knowledge-base topics and the tickets they generate.

A Topic is one support subject. It becomes one article per operating system it
has steps for, or one article per region when `by_region` is set. Its TicketSpec
supplies the phrases the ticket generator combines into historical tickets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Ticket categories. "Security" is deliberately rare: session 2 uses it to show
# why accuracy hides poor recall on a minority class.
ACCESS = "Access & Identity"
NETWORK = "Network & VPN"
EMAIL = "Email & Collaboration"
HARDWARE = "Hardware & Devices"
SOFTWARE = "Software"
SECURITY = "Security"
ONBOARDING = "Onboarding & Offboarding"
GENERAL = "General Enquiry"

CATEGORIES = (ACCESS, NETWORK, EMAIL, HARDWARE, SOFTWARE, SECURITY, ONBOARDING, GENERAL)

# Assignment groups.
L1 = "Service Desk L1"
IAM = "Identity & Access"
NETOPS = "Network Operations"
WORKPLACE = "Workplace Engineering"
MESSAGING = "Messaging & Collaboration"
PACKAGING = "Software Packaging"
SECOPS = "Security Operations"
ONBOARD_TEAM = "Onboarding Team"

GROUPS = (L1, IAM, NETOPS, WORKPLACE, MESSAGING, PACKAGING, SECOPS, ONBOARD_TEAM)


@dataclass(frozen=True)
class TicketSpec:
    """Phrases for tickets about one topic.

    Placeholders filled by the generator: {os}, {model}, {code}, {office}.
    `priority` holds relative weights for P1, P2, P3 and P4.
    """

    shorts: tuple[str, ...]
    descs: tuple[str, ...]
    fixes: tuple[str, ...]
    weight: float = 1.0
    priority: tuple[int, int, int, int] = (0, 5, 60, 35)


@dataclass(frozen=True)
class Topic:
    key: str
    title: str
    system: str
    category: str
    subcategory: str
    kind: str  # how-to | troubleshooting | reference
    summary: str
    steps: dict[str, tuple[str, ...]]  # operating system (or "any") -> ordered steps
    symptoms: tuple[str, ...] = ()
    causes: tuple[str, ...] = ()
    codes: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    group: str = L1
    audience: str = "employee"  # employee | it-staff
    policy: str | None = None
    by_region: bool = False
    ticket: TicketSpec | None = None


@dataclass
class TopicRegistry:
    topics: list[Topic] = field(default_factory=list)

    def add(self, topic: Topic) -> Topic:
        if any(existing.key == topic.key for existing in self.topics):
            raise ValueError(f"duplicate topic key: {topic.key}")
        if topic.by_region and set(topic.steps) != {"any"}:
            raise ValueError(f"{topic.key}: a by_region topic must have only 'any' steps")
        self.topics.append(topic)
        return topic


REGISTRY = TopicRegistry()


def T(key: str, title: str, **fields) -> Topic:  # noqa: N802 - short name keeps content files readable
    """Register a topic. Lists are accepted and stored as tuples."""
    steps = {os_name: tuple(items) for os_name, items in fields.pop("steps").items()}
    for name in ("symptoms", "causes", "codes", "notes"):
        if name in fields:
            fields[name] = tuple(fields[name])
    return REGISTRY.add(Topic(key=key, title=title, steps=steps, **fields))


def K(shorts, descs, fixes, weight: float = 1.0, priority=(0, 5, 60, 35)) -> TicketSpec:  # noqa: N802
    return TicketSpec(tuple(shorts), tuple(descs), tuple(fixes), weight, tuple(priority))
