from __future__ import annotations

from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from yops_portal.core.database import initialize_database
from yops_portal.core.security import SessionStore, SessionUser
from yops_portal.repositories.audit_repository import AuditRepository
from yops_portal.repositories.audit_request_repository import AuditRequestRepository
from yops_portal.repositories.base import BaseRepository
from yops_portal.repositories.client_note_repository import ClientNoteRepository
from yops_portal.repositories.client_repository import ClientRepository
from yops_portal.repositories.report_delivery_repository import ReportDeliveryRepository
from yops_portal.repositories.report_repository import ReportRepository
from yops_portal.repositories.ticket_repository import TicketRepository
from yops_portal.repositories.user_repository import UserRepository
from yops_portal.repositories.vulnerability_repository import VulnerabilityRepository
from yops_portal.services.auth_service import AuthService
from yops_portal.services.client_risk_service import ClientRiskService
from yops_portal.services.cvss import parse_cvss
from yops_portal.services.dashboard_service import DashboardService
from yops_portal.services.pdf_report import build_remediation_report
from yops_portal.services.registration_service import RegistrationService
from yops_portal.services.report_delivery_service import ReportDeliveryService
from yops_portal.services.validation import ValidationError, require_fields
from yops_portal.views import html


ROOT_DIR = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT_DIR / "public"
PDF_STORAGE_DIR = ROOT_DIR / "storage" / "reports" / "pdf"


class Services:
    def __init__(self) -> None:
        self.base = BaseRepository()
        self.users = UserRepository()
        self.clients = ClientRepository()
        self.notes = ClientNoteRepository()
        self.audits = AuditRepository()
        self.audit_requests = AuditRequestRepository()
        self.vulnerabilities = VulnerabilityRepository()
        self.tickets = TicketRepository()
        self.reports = ReportRepository()
        self.deliveries = ReportDeliveryRepository()
        self.auth = AuthService(self.users)
        self.registration = RegistrationService(self.clients, self.users)
        self.risk = ClientRiskService(self.base)
        self.dashboard = DashboardService(self.base, self.risk)
        self.report_delivery = ReportDeliveryService(self.vulnerabilities, self.clients, self.deliveries, PDF_STORAGE_DIR)


class YOpsApplication:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sessions = SessionStore()
        self.services = Services()

    def run(self) -> None:
        initialize_database()
        handler = self._handler()
        httpd = ThreadingHTTPServer((self.host, self.port), handler)
        print(f"YOps Portal running on http://{self.host}:{self.port}")
        httpd.serve_forever()

    def _handler(self):
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                app.dispatch_get(self)

            def do_POST(self) -> None:
                app.dispatch_post(self)

            def log_message(self, format: str, *args) -> None:
                return

        return Handler

    def dispatch_get(self, request: BaseHTTPRequestHandler) -> None:
        parsed = urlparse(request.path)
        path = parsed.path
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        if path.startswith("/assets/"):
            return self.serve_asset(request, path)
        user = self.current_user(request)
        if path == "/":
            return self.respond(request, html.landing_page(user))
        if path == "/login":
            return self.respond(request, html.login_page())
        if path == "/register":
            return self.respond(request, html.register_page())
        if user is None:
            return self.redirect(request, "/login")
        if path == "/dashboard":
            if user.role == "client":
                return self.respond(request, self.client_dashboard(user))
            data = self.services.dashboard.get_dashboard()
            data["pending_requests"] = self.services.audit_requests.list_pending()
            data["clients"] = self.services.clients.list_clients()
            data["recent_deliveries"] = self.services.deliveries.list_recent(5)
            return self.respond(request, html.dashboard_page(user, data))
        if path == "/audit-requests":
            if user.role == "client":
                return self.redirect(request, "/dashboard")
            return self.respond(request, html.audit_requests_page(user, self.services.audit_requests.list_all()))
        if path == "/clients":
            if user.role == "client":
                return self.redirect(request, "/dashboard")
            return self.respond(request, html.clients_page(user, self.services.clients.list_clients()))
        if path.startswith("/clients/"):
            client_id = self._int_path_id(path)
            if user.role == "client" and user.client_id != client_id:
                return self.redirect(request, "/dashboard")
            client = self.services.clients.find(client_id) if client_id else None
            if client is None:
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            audits = self.services.audits.list_for_client(client.id)
            vulnerabilities = self.services.vulnerabilities.list_for_client(client.id)
            risk = next(
                (item for item in self.services.risk.calculate() if item.client_name == client.name),
                None,
            )
            if risk is None:
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            notes = self.services.notes.list_for_client(client.id) if user.role != "client" else []
            return self.respond(request, html.client_detail_page(user, client, audits, vulnerabilities, risk, notes))
        if path == "/audits":
            if user.role == "client":
                return self.respond(request, html.audits_page(user, self.services.audits.list_for_client(user.client_id or 0)))
            return self.respond(request, html.audits_page(user, self.services.audits.list_audits()))
        if path.startswith("/audits/"):
            audit_id = self._int_path_id(path)
            audit = self.services.audits.find(audit_id) if audit_id else None
            if audit is None:
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            if user.role == "client" and audit.client_id != user.client_id:
                return self.redirect(request, "/dashboard")
            vulnerabilities = self.services.vulnerabilities.list_for_audit(audit.id)
            return self.respond(request, html.audit_detail_page(user, audit, vulnerabilities))
        if path == "/vulnerabilities":
            if user.role == "client":
                return self.redirect(request, "/dashboard")
            return self.respond(
                request,
                html.vulnerabilities_page(
                    user,
                    self.services.vulnerabilities.list_vulnerabilities(query.get("severity"), query.get("status")),
                    self.services.audits.list_audits(),
                    self.services.clients.list_clients(),
                    query,
                ),
            )
        if path == "/tickets":
            if user.role == "client":
                return self.redirect(request, "/dashboard")
            return self.respond(request, html.tickets_page(user, self.services.tickets.list_tickets()))
        if path == "/reports":
            if user.role == "client":
                return self.respond(request, html.reports_page(user, self.services.reports.list_for_client(user.client_id or 0)))
            return self.respond(request, html.reports_page(user, self.services.reports.list_reports()))
        if path == "/admin/users":
            if user.role != "admin":
                return self.redirect(request, "/dashboard")
            return self.respond(request, html.users_page(user, self.services.users.list_users()))
        if path == "/reports/vulnerabilities.pdf":
            if user.role == "client":
                return self.redirect(request, "/dashboard")
            open_statuses = ("ouverte", "en_cours")
            vulns = [
                v for v in self.services.vulnerabilities.list_vulnerabilities()
                if v.status in open_statuses
            ]
            vulns.sort(key=lambda v: (-float(v.cvss_score or 0), v.client_name))
            body = build_remediation_report(vulns, generated_by=user.name)
            filename = f"yops-vulnerabilites-{date.today().isoformat()}.pdf"
            return self.respond_binary(request, body, "application/pdf", filename)
        if path.startswith("/reports/delivered/") and path.endswith(".pdf"):
            try:
                delivery_id = int(path.split("/")[3].removesuffix(".pdf"))
            except (ValueError, IndexError):
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            delivery = self.services.deliveries.find(delivery_id)
            if delivery is None:
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            if user.role == "client" and delivery.client_id != user.client_id:
                return self.redirect(request, "/dashboard")
            body = self.services.report_delivery.read_file(delivery.file_path)
            if body is None:
                return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)
            if user.role == "client":
                self.services.deliveries.mark_read(delivery.id)
            return self.respond_binary(request, body, "application/pdf", delivery.filename)
        return self.respond(request, html.not_found_page(user), HTTPStatus.NOT_FOUND)

    def dispatch_post(self, request: BaseHTTPRequestHandler) -> None:
        parsed = urlparse(request.path)
        path = parsed.path
        data = self.read_form(request)
        user = self.current_user(request)
        if path == "/login":
            auth_user = self.services.auth.authenticate(data.get("email", ""), data.get("password", ""))
            if auth_user is None:
                return self.respond(request, html.login_page("Identifiants invalides."), HTTPStatus.UNAUTHORIZED)
            token = self.sessions.create(auth_user)
            return self.redirect(request, "/dashboard", cookie=f"yops_session={token}; HttpOnly; SameSite=Lax; Path=/")
        if path == "/register":
            try:
                self.services.registration.register_client(data)
                return self.redirect(request, "/login")
            except ValidationError as exc:
                return self.respond(request, html.register_page(exc.errors, data), HTTPStatus.BAD_REQUEST)
        if path == "/logout":
            self.sessions.delete(self.cookie_value(request, "yops_session"))
            return self.redirect(request, "/login", cookie="yops_session=deleted; Max-Age=0; Path=/")
        if user is None:
            return self.redirect(request, "/login")
        if path == "/audit-requests" and user.role == "client":
            if user.client_id is None:
                return self.redirect(request, "/dashboard")
            try:
                require_fields(data, ["audit_type", "scope"])
                self.services.audit_requests.create({
                    "client_id": user.client_id,
                    "requested_by": user.id,
                    "audit_type": data.get("audit_type", "web"),
                    "scope": data.get("scope", "").strip(),
                    "rules": data.get("rules", "").strip(),
                    "urgency": data.get("urgency", "normal"),
                    "target_date": data.get("target_date", "").strip() or None,
                })
                return self.redirect(request, "/dashboard#requests")
            except ValidationError as exc:
                client = self.services.clients.find(user.client_id)
                if client is None:
                    return self.redirect(request, "/dashboard")
                return self.respond(
                    request,
                    html.client_dashboard_page(
                        user,
                        client,
                        self.services.audits.list_for_client(client.id),
                        self.services.vulnerabilities.list_for_client(client.id),
                        self.services.tickets.list_for_client(client.id),
                        self.services.reports.list_for_client(client.id),
                        self.services.audit_requests.list_for_client(client.id),
                        request_errors=exc.errors,
                        request_form=data,
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        if user.role == "client":
            return self.redirect(request, "/dashboard")
        if path == "/reports/deliver":
            try:
                client_id = int(data.get("client_id", "0"))
            except ValueError:
                return self.redirect(request, "/dashboard")
            self.services.report_delivery.deliver(client_id, user.id, user.name)
            return self.redirect(request, "/dashboard#deliver")
        if path.startswith("/audit-requests/") and path.endswith("/respond"):
            try:
                req_id = int(path.split("/")[2])
            except ValueError:
                return self.redirect(request, "/dashboard")
            req = self.services.audit_requests.find(req_id)
            if req is None or req.status != "pending":
                return self.redirect(request, "/audit-requests")
            decision = data.get("decision", "")
            message = data.get("message", "").strip()
            if decision == "accept":
                title = data.get("title", "").strip() or f"Audit {req.audit_type} - {req.client_name}"
                starts_at = data.get("starts_at", "").strip() or req.target_date or date.today().isoformat()
                audit_id = self.services.audits.create(
                    client_id=req.client_id,
                    owner_id=user.id,
                    title=title,
                    audit_type=req.audit_type,
                    starts_at=starts_at,
                    ends_at=None,
                    status="planifie",
                )
                self.services.audit_requests.respond(req.id, "accepted", user.id, message or "Demande acceptée.", audit_id)
            elif decision == "reject":
                self.services.audit_requests.respond(req.id, "rejected", user.id, message or "Demande refusée.", None)
            return self.redirect(request, "/audit-requests")
        if path == "/clients":
            try:
                require_fields(data, ["name", "sector", "contact_name", "email", "phone"])
                self.services.clients.create(data)
                return self.redirect(request, "/clients")
            except ValidationError as exc:
                return self.respond(request, html.clients_page(user, self.services.clients.list_clients(), exc.errors), HTTPStatus.BAD_REQUEST)
        if path.startswith("/clients/") and path.endswith("/notes"):
            try:
                client_id = int(path.split("/")[2])
            except ValueError:
                return self.redirect(request, "/clients")
            client = self.services.clients.find(client_id)
            if client is None:
                return self.redirect(request, "/clients")
            body = (data.get("body") or "").strip()
            kind = data.get("kind", "note")
            if kind not in ("note", "contact", "alert", "meeting"):
                kind = "note"
            if body:
                self.services.notes.create(client.id, user.id, kind, body)
            return self.redirect(request, f"/clients/{client.id}#notes")
        if path.startswith("/vulnerabilities/") and path.endswith("/status"):
            try:
                vuln_id = int(path.split("/")[2])
            except ValueError:
                return self.redirect(request, "/vulnerabilities")
            vuln = self.services.vulnerabilities.find(vuln_id)
            status = data.get("status", "")
            if vuln is not None and status in ("ouverte", "en_cours", "corrigee", "acceptee"):
                self.services.vulnerabilities.update_status(vuln_id, status)
            return_to = data.get("return_to") or "/vulnerabilities"
            return self.redirect(request, self._safe_return_to(return_to))
        if path.startswith("/vulnerabilities/") and path.endswith("/score"):
            try:
                vuln_id = int(path.split("/")[2])
            except ValueError:
                return self.redirect(request, "/vulnerabilities")
            vuln = self.services.vulnerabilities.find(vuln_id)
            try:
                score = parse_cvss(data.get("cvss_score", ""))
            except ValueError:
                score = None
            if vuln is not None and score is not None:
                self.services.vulnerabilities.update_score(vuln_id, score)
            return_to = data.get("return_to") or "/vulnerabilities"
            return self.redirect(request, self._safe_return_to(return_to))
        if path == "/vulnerabilities":
            query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
            try:
                require_fields(data, ["audit_id", "title", "description", "cvss_score", "asset", "evidence", "recommendation"])
                try:
                    data["cvss_score"] = parse_cvss(data["cvss_score"])
                except ValueError:
                    raise ValidationError(["Le score CVSS doit etre un nombre entre 0 et 10."])
                self.services.vulnerabilities.create(data)
                return self.redirect(request, self._safe_return_to(query.get("return_to", "/vulnerabilities")))
            except ValidationError as exc:
                return self.respond(
                    request,
                    html.vulnerabilities_page(
                        user,
                        self.services.vulnerabilities.list_vulnerabilities(query.get("severity"), query.get("status")),
                        self.services.audits.list_audits(),
                        self.services.clients.list_clients(),
                        query,
                        exc.errors,
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        return self.redirect(request, "/dashboard")

    def client_dashboard(self, user: SessionUser) -> bytes:
        if user.client_id is None:
            return html.not_found_page(user)
        client = self.services.clients.find(user.client_id)
        if client is None:
            return html.not_found_page(user)
        return html.client_dashboard_page(
            user,
            client,
            self.services.audits.list_for_client(client.id),
            self.services.vulnerabilities.list_for_client(client.id),
            self.services.tickets.list_for_client(client.id),
            self.services.reports.list_for_client(client.id),
            self.services.audit_requests.list_for_client(client.id),
            deliveries=self.services.deliveries.list_for_client(client.id),
        )

    def serve_asset(self, request: BaseHTTPRequestHandler, path: str) -> None:
        safe_name = unquote(path.removeprefix("/assets/"))
        asset_path = (PUBLIC_DIR / "assets" / safe_name).resolve()
        if not str(asset_path).startswith(str((PUBLIC_DIR / "assets").resolve())) or not asset_path.exists():
            request.send_error(404)
            return
        content_types = {
            ".css": "text/css",
            ".js": "text/javascript",
            ".png": "image/png",
        }
        content_type = content_types.get(asset_path.suffix, "application/octet-stream")
        body = asset_path.read_bytes()
        request.send_response(HTTPStatus.OK)
        request.send_header("Content-Type", content_type)
        request.send_header("Content-Length", str(len(body)))
        request.end_headers()
        request.wfile.write(body)

    def respond(self, request: BaseHTTPRequestHandler, body: bytes, status: HTTPStatus = HTTPStatus.OK) -> None:
        request.send_response(status)
        request.send_header("Content-Type", "text/html; charset=utf-8")
        request.send_header("Content-Length", str(len(body)))
        request.end_headers()
        request.wfile.write(body)

    def respond_binary(self, request: BaseHTTPRequestHandler, body: bytes, content_type: str, filename: str) -> None:
        request.send_response(HTTPStatus.OK)
        request.send_header("Content-Type", content_type)
        request.send_header("Content-Length", str(len(body)))
        request.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        request.end_headers()
        request.wfile.write(body)

    def redirect(self, request: BaseHTTPRequestHandler, location: str, cookie: str | None = None) -> None:
        request.send_response(HTTPStatus.SEE_OTHER)
        request.send_header("Location", location)
        if cookie:
            request.send_header("Set-Cookie", cookie)
        request.end_headers()

    def read_form(self, request: BaseHTTPRequestHandler) -> dict[str, str]:
        length = int(request.headers.get("Content-Length", "0"))
        raw = request.rfile.read(length).decode("utf-8")
        return {key: values[-1] for key, values in parse_qs(raw).items()}

    def current_user(self, request: BaseHTTPRequestHandler) -> SessionUser | None:
        return self.sessions.get(self.cookie_value(request, "yops_session"))

    def cookie_value(self, request: BaseHTTPRequestHandler, name: str) -> str | None:
        raw_cookie = request.headers.get("Cookie", "")
        for item in raw_cookie.split(";"):
            key, _, value = item.strip().partition("=")
            if key == name:
                return value
        return None

    def _int_path_id(self, path: str) -> int | None:
        try:
            return int(path.rstrip("/").split("/")[-1])
        except ValueError:
            return None

    def _safe_return_to(self, target: str) -> str:
        if not target.startswith("/") or target.startswith("//"):
            return "/vulnerabilities"
        return target
