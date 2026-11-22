"""Request and response models, and the fixed vocabularies of the ticketing system."""

from __future__ import annotations

from typing import Annotated, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field

Category = Literal[
    "Access & Identity",
    "Network & VPN",
    "Email & Collaboration",
    "Hardware & Devices",
    "Software",
    "Security",
    "Onboarding & Offboarding",
    "General Enquiry",
]
Group = Literal[
    "Service Desk L1",
    "Identity & Access",
    "Network Operations",
    "Workplace Engineering",
    "Messaging & Collaboration",
    "Software Packaging",
    "Security Operations",
    "Onboarding Team",
]
Priority = Literal["P1", "P2", "P3", "P4"]
Status = Literal["New", "In Progress", "Awaiting User", "On Hold", "Resolved", "Closed"]

CATEGORIES: tuple[str, ...] = get_args(Category)
GROUPS: tuple[str, ...] = get_args(Group)
OPEN_STATUSES = ("New", "In Progress", "Awaiting User", "On Hold")

EmployeeId = Annotated[
    str, Field(pattern=r"^E\d{4}$", description="Employee ID, for example E1166")
]


class Comment(BaseModel):
    comment_id: int
    ticket_id: str
    author_id: str
    created_at: str
    body: str
    internal: bool


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author_id: EmployeeId
    body: str = Field(min_length=1, max_length=4000)
    internal: bool = Field(
        default=False, description="Internal notes are hidden from the requester"
    )


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requester_id: EmployeeId
    short_description: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=1, max_length=8000)
    category: Category
    subcategory: str | None = Field(default=None, max_length=80)
    priority: Priority = "P3"
    assignment_group: Group = "Service Desk L1"


class TicketUpdate(BaseModel):
    """Partial update: send only the fields that change."""

    model_config = ConfigDict(extra="forbid")

    short_description: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, min_length=1, max_length=8000)
    category: Category | None = None
    subcategory: str | None = Field(default=None, max_length=80)
    priority: Priority | None = None
    assignment_group: Group | None = None
    status: Status | None = None
    resolution_notes: str | None = Field(default=None, max_length=4000)


class Ticket(BaseModel):
    ticket_id: str
    created_at: str
    updated_at: str
    requester_id: str
    short_description: str
    description: str
    category: str
    subcategory: str | None = None
    priority: str
    assignment_group: str
    status: str
    resolution_notes: str | None = None
    comments: list[Comment] = []


class TicketPage(BaseModel):
    items: list[Ticket]
    total: int
    limit: int
    offset: int


class FaultSettings(BaseModel):
    """How the mock misbehaves. All zeros means it behaves perfectly."""

    model_config = ConfigDict(extra="forbid")

    error_rate: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Share of requests answered 503 before any work is done",
    )
    timeout_rate: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Share of requests that are processed and then answered late",
    )
    timeout_seconds: float = Field(
        default=30.0, ge=0, le=120, description="Delay before a late answer"
    )
    rate_limit_per_minute: int = Field(
        default=0, ge=0, description="Requests allowed per API key per minute; 0 means no limit"
    )
    latency_ms: int = Field(default=0, ge=0, le=10_000, description="Delay added to every request")
    seed: int | None = Field(
        default=None, description="Seed for the random faults, for repeatable runs"
    )
