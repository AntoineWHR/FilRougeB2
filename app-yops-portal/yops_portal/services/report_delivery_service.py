from __future__ import annotations

import re
import uuid
from datetime import date
from pathlib import Path

from yops_portal.repositories.audit_repository import AuditRepository
from yops_portal.repositories.base import BaseRepository
from yops_portal.repositories.client_repository import ClientRepository
from yops_portal.repositories.report_delivery_repository import ReportDeliveryRepository
from yops_portal.repositories.vulnerability_repository import VulnerabilityRepository
from yops_portal.services.pdf_report import build_remediation_report, build_verification_report


VERDICT_TO_STATUS = {"validated": "corrigee", "rejected": "en_cours", "bypass": "ouverte"}


OPEN_STATUSES = ("ouverte", "en_cours")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "client"


class ReportDeliveryService:
    def __init__(
        self,
        vulnerabilities: VulnerabilityRepository,
        clients: ClientRepository,
        audits: AuditRepository,
        deliveries: ReportDeliveryRepository,
        base: BaseRepository,
        storage_dir: Path,
    ) -> None:
        self.vulnerabilities = vulnerabilities
        self.clients = clients
        self.audits = audits
        self.deliveries = deliveries
        self.base = base
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def deliver(self, client_id: int, sent_by_id: int, sent_by_name: str) -> int | None:
        client = self.clients.find(client_id)
        if client is None:
            return None
        vulns = [v for v in self.vulnerabilities.list_for_client(client_id) if v.status in OPEN_STATUSES]
        return self._persist(client_id, sent_by_id, sent_by_name, vulns, scope=client.name, slug=slugify(client.name))

    def close_audit_and_deliver(self, audit_id: int, sent_by_id: int, sent_by_name: str) -> int | None:
        audit = self.audits.find(audit_id)
        if audit is None:
            return None
        if audit.status != "termine":
            self.base.execute("UPDATE audits SET status = 'termine', ends_at = COALESCE(ends_at, date('now')) WHERE id = ?", (audit_id,))
        vulns = self.vulnerabilities.list_for_audit(audit_id)
        scope = f"{audit.client_name} · {audit.title}"
        slug = f"{slugify(audit.client_name)}-{slugify(audit.title)}"
        return self._persist(audit.client_id, sent_by_id, sent_by_name, vulns, scope=scope, slug=slug, audit_id=audit_id)

    def verify_and_deliver(self, vuln_id: int, verdict: str, admin_message: str, admin_id: int, admin_name: str) -> int | None:
        if verdict not in VERDICT_TO_STATUS:
            return None
        rows = self.vulnerabilities.fetch_all(
            """
            SELECT vulnerabilities.*, audits.title AS audit_title, clients.name AS client_name, clients.id AS client_id
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            WHERE vulnerabilities.id = ?
            """,
            (vuln_id,),
        )
        if not rows:
            return None
        row = rows[0]
        client_id = row["client_id"]
        client_name = row["client_name"]
        from yops_portal.models.entities import Vulnerability
        vuln = Vulnerability(
            id=row["id"], audit_id=row["audit_id"], client_name=client_name,
            audit_title=row["audit_title"], title=row["title"], description=row["description"],
            severity=row["severity"], cvss_score=row["cvss_score"], asset=row["asset"],
            evidence=row["evidence"], recommendation=row["recommendation"],
            status=row["status"], discovered_at=row["discovered_at"],
        )
        new_status = VERDICT_TO_STATUS[verdict]
        self.vulnerabilities.update_status(vuln_id, new_status)
        summary = self._client_status_summary(client_id)
        pdf_bytes = build_verification_report(vuln, verdict, admin_message, admin_name, client_name, summary)
        filename = f"yops-verification-{slugify(client_name)}-{vuln_id}-{date.today().isoformat()}.pdf"
        stored_name = f"{uuid.uuid4().hex}.pdf"
        (self.storage_dir / stored_name).write_bytes(pdf_bytes)
        return self.deliveries.create(
            client_id=client_id,
            sent_by=admin_id,
            filename=filename,
            file_path=stored_name,
            vuln_count=1,
            critical_count=1 if vuln.severity == "critical" else 0,
            vulnerability_id=vuln_id,
            kind="verification",
            verdict=verdict,
            admin_message=admin_message,
        )

    def _client_status_summary(self, client_id: int) -> dict:
        rows = self.base.fetch_all(
            """
            SELECT vulnerabilities.status AS status, COUNT(*) AS n
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            WHERE audits.client_id = ?
            GROUP BY vulnerabilities.status
            """,
            (client_id,),
        )
        return {row["status"]: row["n"] for row in rows}

    def _persist(self, client_id: int, sent_by_id: int, sent_by_name: str, vulns, scope: str, slug: str, audit_id: int | None = None) -> int:
        vulns = sorted(vulns, key=lambda v: -float(v.cvss_score or 0))
        pdf_bytes = build_remediation_report(vulns, generated_by=sent_by_name, scope=scope)
        filename = f"yops-{slug}-{date.today().isoformat()}.pdf"
        stored_name = f"{uuid.uuid4().hex}.pdf"
        (self.storage_dir / stored_name).write_bytes(pdf_bytes)
        critical = sum(1 for v in vulns if v.severity == "critical")
        return self.deliveries.create(
            client_id=client_id,
            sent_by=sent_by_id,
            filename=filename,
            file_path=stored_name,
            vuln_count=len(vulns),
            critical_count=critical,
            audit_id=audit_id,
        )

    def read_file(self, relative_path: str) -> bytes | None:
        target = (self.storage_dir / relative_path).resolve()
        if not str(target).startswith(str(self.storage_dir.resolve())):
            return None
        if not target.exists():
            return None
        return target.read_bytes()
