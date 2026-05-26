from yops_portal.models.entities import Ticket
from yops_portal.repositories.base import BaseRepository


class TicketRepository(BaseRepository):
    def list_tickets(self) -> list[Ticket]:
        rows = self.fetch_all(
            """
            SELECT remediation_tickets.*, vulnerabilities.title AS vulnerability_title,
                   users.name AS assignee_name, clients.name AS client_name
            FROM remediation_tickets
            JOIN vulnerabilities ON vulnerabilities.id = remediation_tickets.vulnerability_id
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            JOIN users ON users.id = remediation_tickets.assignee_id
            ORDER BY remediation_tickets.due_date ASC
            """
        )
        return [
            Ticket(
                row["id"],
                row["vulnerability_title"],
                row["client_name"],
                row["assignee_name"],
                row["priority"],
                row["due_date"],
                row["status"],
                row["comment"],
            )
            for row in rows
        ]

    def list_for_client(self, client_id: int) -> list[Ticket]:
        rows = self.fetch_all(
            """
            SELECT remediation_tickets.*, vulnerabilities.title AS vulnerability_title,
                   users.name AS assignee_name, clients.name AS client_name
            FROM remediation_tickets
            JOIN vulnerabilities ON vulnerabilities.id = remediation_tickets.vulnerability_id
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            JOIN users ON users.id = remediation_tickets.assignee_id
            WHERE clients.id = ?
            ORDER BY remediation_tickets.due_date ASC
            """,
            (client_id,),
        )
        return [
            Ticket(
                row["id"],
                row["vulnerability_title"],
                row["client_name"],
                row["assignee_name"],
                row["priority"],
                row["due_date"],
                row["status"],
                row["comment"],
            )
            for row in rows
        ]
