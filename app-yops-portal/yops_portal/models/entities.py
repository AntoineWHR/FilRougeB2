from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    id: int
    name: str
    label: str


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    role: str
    client_id: int | None


@dataclass(frozen=True)
class Client:
    id: int
    name: str
    sector: str
    contact_name: str
    email: str
    phone: str
    status: str


@dataclass(frozen=True)
class Audit:
    id: int
    client_id: int
    client_name: str
    owner_name: str
    title: str
    audit_type: str
    starts_at: str
    ends_at: str | None
    status: str


@dataclass(frozen=True)
class Vulnerability:
    id: int
    audit_id: int
    client_name: str
    audit_title: str
    title: str
    description: str
    severity: str
    cvss_score: float
    asset: str
    evidence: str
    recommendation: str
    status: str
    discovered_at: str


@dataclass(frozen=True)
class Ticket:
    id: int
    vulnerability_title: str
    client_name: str
    assignee_name: str
    priority: str
    due_date: str
    status: str
    comment: str


@dataclass(frozen=True)
class Report:
    id: int
    audit_title: str
    client_name: str
    title: str
    executive_summary: str
    generated_at: str


@dataclass(frozen=True)
class ClientNote:
    id: int
    client_id: int
    client_name: str
    author_name: str
    kind: str
    body: str
    created_at: str


@dataclass(frozen=True)
class ReportDelivery:
    id: int
    client_id: int
    client_name: str
    sent_by_name: str
    filename: str
    file_path: str
    vuln_count: int
    critical_count: int
    delivered_at: str
    read_at: str | None


@dataclass(frozen=True)
class AuditRequest:
    id: int
    client_id: int
    client_name: str
    requested_by_name: str
    audit_type: str
    scope: str
    rules: str
    urgency: str
    target_date: str | None
    status: str
    admin_response: str
    responded_by_name: str | None
    responded_at: str | None
    audit_id: int | None
    created_at: str

