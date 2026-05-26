from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from yops_portal.core.database import initialize_database
from yops_portal.core.security import SessionStore, SessionUser
from yops_portal.repositories.audit_repository import AuditRepository
from yops_portal.repositories.base import BaseRepository
from yops_portal.repositories.client_repository import ClientRepository
from yops_portal.repositories.report_repository import ReportRepository
from yops_portal.repositories.ticket_repository import TicketRepository
from yops_portal.repositories.user_repository import UserRepository
from yops_portal.repositories.vulnerability_repository import VulnerabilityRepository
from yops_portal.services.auth_service import AuthService
from yops_portal.services.client_risk_service import ClientRiskService
from yops_portal.services.dashboard_service import DashboardService
from yops_portal.services.registration_service import RegistrationService
from yops_portal.services.validation import ValidationError, require_fields
from yops_portal.views import html


ROOT_DIR = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT_DIR / "public"


class Services:
    def __init__(self) -> None:
        self.base = BaseRepository()
        self.users = UserRepository()
        self.clients = ClientRepository()
        self.audits = AuditRepository()
        self.vulnerabilities = VulnerabilityRepository()
        self.tickets = TicketRepository()
        self.reports = ReportRepository()
        self.auth = AuthService(self.users)
        self.registration = RegistrationService(self.clients, self.users)
        self.risk = ClientRiskService(self.base)
        self.dashboard = DashboardService(self.base, self.risk)


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
            return self.respond(request, html.dashboard_page(user, self.services.dashboard.get_dashboard()))
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
            return self.respond(request, html.client_detail_page(user, client, audits, vulnerabilities, risk))
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
        if user.role == "client":
            return self.redirect(request, "/dashboard")
        if path == "/clients":
            try:
                require_fields(data, ["name", "sector", "contact_name", "email", "phone"])
                self.services.clients.create(data)
                return self.redirect(request, "/clients")
            except ValidationError as exc:
                return self.respond(request, html.clients_page(user, self.services.clients.list_clients(), exc.errors), HTTPStatus.BAD_REQUEST)
        if path == "/vulnerabilities":
            try:
                require_fields(data, ["audit_id", "title", "description", "severity", "cvss_score", "asset", "evidence", "recommendation"])
                self.services.vulnerabilities.create(data)
                return self.redirect(request, "/vulnerabilities")
            except ValidationError as exc:
                query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
                return self.respond(
                    request,
                    html.vulnerabilities_page(
                        user,
                        self.services.vulnerabilities.list_vulnerabilities(query.get("severity"), query.get("status")),
                        self.services.audits.list_audits(),
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
        )

    def serve_asset(self, request: BaseHTTPRequestHandler, path: str) -> None:
        safe_name = unquote(path.removeprefix("/assets/"))
        asset_path = (PUBLIC_DIR / "assets" / safe_name).resolve()
        if not str(asset_path).startswith(str((PUBLIC_DIR / "assets").resolve())) or not asset_path.exists():
            request.send_error(404)
            return
        content_type = "text/css" if asset_path.suffix == ".css" else "text/javascript" if asset_path.suffix == ".js" else "application/octet-stream"
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
