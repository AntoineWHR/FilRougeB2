from __future__ import annotations

import re
import uuid
from datetime import date
from pathlib import Path

from yops_portal.repositories.client_repository import ClientRepository
from yops_portal.repositories.report_delivery_repository import ReportDeliveryRepository
from yops_portal.repositories.vulnerability_repository import VulnerabilityRepository
from yops_portal.services.pdf_report import build_remediation_report


OPEN_STATUSES = ("ouverte", "en_cours")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "client"


class ReportDeliveryService:
    def __init__(
        self,
        vulnerabilities: VulnerabilityRepository,
        clients: ClientRepository,
        deliveries: ReportDeliveryRepository,
        storage_dir: Path,
    ) -> None:
        self.vulnerabilities = vulnerabilities
        self.clients = clients
        self.deliveries = deliveries
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def deliver(self, client_id: int, sent_by_id: int, sent_by_name: str) -> int | None:
        client = self.clients.find(client_id)
        if client is None:
            return None
        vulns = [v for v in self.vulnerabilities.list_for_client(client_id) if v.status in OPEN_STATUSES]
        vulns.sort(key=lambda v: -float(v.cvss_score or 0))
        pdf_bytes = build_remediation_report(vulns, generated_by=sent_by_name, scope=client.name)
        filename = f"yops-{slugify(client.name)}-{date.today().isoformat()}.pdf"
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
        )

    def read_file(self, relative_path: str) -> bytes | None:
        target = (self.storage_dir / relative_path).resolve()
        if not str(target).startswith(str(self.storage_dir.resolve())):
            return None
        if not target.exists():
            return None
        return target.read_bytes()
