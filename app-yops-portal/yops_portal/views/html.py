from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from yops_portal.core.security import SessionUser


def e(value) -> str:
    return escape(str(value), quote=True)


def badge(value: str, kind: str = "neutral") -> str:
    return f'<span class="badge badge-{e(kind)}">{e(value)}</span>'


def severity_badge(severity: str) -> str:
    labels = {"critical": "Critique", "high": "Haute", "medium": "Moyenne", "low": "Faible"}
    return badge(labels.get(severity, severity), severity)


def status_badge(status: str) -> str:
    kind = {
        "ouverte": "critical",
        "en_cours": "high",
        "corrigee": "success",
        "acceptee": "neutral",
        "termine": "success",
        "ouvert": "critical",
        "bloque": "high",
        "planifie": "neutral",
    }.get(status, "neutral")
    return badge(status.replace("_", " "), kind)


def layout(title: str, user: SessionUser | None, content: str, active: str = "dashboard") -> bytes:
    nav = ""
    if user:
        if user.role == "client":
            links = [
                ("home", "/", "Accueil"),
                ("dashboard", "/dashboard", "Mon espace"),
                ("audits", "/audits", "Mes audits"),
                ("reports", "/reports", "Mes rapports"),
            ]
        else:
            links = [
                ("home", "/", "Accueil"),
                ("dashboard", "/dashboard", "Back-office"),
                ("clients", "/clients", "Clients"),
                ("audits", "/audits", "Audits"),
                ("vulnerabilities", "/vulnerabilities", "Vulnerabilites"),
                ("tickets", "/tickets", "Tickets"),
                ("reports", "/reports", "Rapports"),
            ]
        admin = '<a class="nav-link" href="/admin/users">Utilisateurs</a>' if user.role == "admin" else ""
        nav_links = "".join(
            f'<a class="nav-link {"is-active" if key == active else ""}" href="{href}">{label}</a>'
            for key, href, label in links
        )
        nav = f"""
        <aside class="sidebar" aria-label="Navigation principale">
            <a class="brand" href="/dashboard" aria-label="Retour dashboard">
                <span class="brand-mark">Y</span>
                <span><strong>YOps</strong><small>Portal</small></span>
            </a>
            <nav>{nav_links}{admin}</nav>
            <div class="session-card">
                <span class="eyebrow">Session</span>
                <strong>{e(user.name)}</strong>
                <small>{e(user.role)}</small>
                <form method="post" action="/logout">
                    <button class="ghost-button" type="submit">Deconnexion</button>
                </form>
            </div>
        </aside>
        """
    html = f"""<!doctype html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{e(title)} - YOps Portal</title>
        <link rel="stylesheet" href="/assets/styles.css">
        <script defer src="/assets/app.js"></script>
    </head>
    <body>
        <div class="grain" aria-hidden="true"></div>
        <main class="app-shell {'with-sidebar' if user else 'auth-shell'}">
            {nav}
            <section class="main-panel">
                {content}
            </section>
        </main>
    </body>
    </html>"""
    return html.encode("utf-8")


def public_shell(title: str, content: str) -> bytes:
    html = f"""<!doctype html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{e(title)} - YOps Cybersecurity</title>
        <link rel="stylesheet" href="/assets/styles.css">
        <script defer src="/assets/app.js"></script>
    </head>
    <body>
        <div class="grain" aria-hidden="true"></div>
        <main class="public-site">
            {content}
        </main>
    </body>
    </html>"""
    return html.encode("utf-8")


def landing_page(user: SessionUser | None = None) -> bytes:
    account_link = "/dashboard" if user else "/login"
    account_label = "Ouvrir mon espace" if user else "Connexion"
    content = f"""
    <nav class="public-nav reveal">
        <a class="brand public-brand" href="/">
            <span class="brand-mark">Y</span>
            <span><strong>YOps</strong><small>Cybersecurity</small></span>
        </a>
        <div>
            <a href="#services">Services</a>
            <a href="#method">Methode</a>
            <a href="#pricing">Offres</a>
            <a class="secondary-button" href="{account_link}">{account_label}</a>
        </div>
    </nav>
    <section class="hero-section reveal">
        <div class="hero-copy">
            <p class="eyebrow">Audit - SOC - Remediation</p>
            <h1>La securite cyber lisible pour les PME.</h1>
            <p>YOps aide les entreprises a identifier leurs risques, prioriser les corrections et suivre les actions sans jargon inutile.</p>
            <div class="hero-actions">
                <a class="primary-link" href="/register">Demander un audit</a>
                <a class="text-link" href="#services">Voir les services</a>
            </div>
        </div>
        <aside class="hero-board double-bezel">
            <div class="card-core">
                <span class="board-label">Synthese client</span>
                <strong>Risque expose</strong>
                <div class="board-score"><span>82</span><small>/100</small></div>
                <div class="board-bars">
                    <span style="--w: 82%"></span>
                    <span style="--w: 58%"></span>
                    <span style="--w: 34%"></span>
                </div>
                <p>Rapport clair, plan de correction, suivi des tickets.</p>
            </div>
        </aside>
    </section>
    <section id="services" class="service-strip reveal">
        <article><span>01</span><h2>Audit web</h2><p>Recherche de failles sur application, API et authentification.</p></article>
        <article><span>02</span><h2>Audit infrastructure</h2><p>Controle AD, serveurs, partages, sauvegardes et exposition reseau.</p></article>
        <article><span>03</span><h2>Supervision SOC</h2><p>Mise en place d'agents, alertes, tableaux de bord et suivi des incidents.</p></article>
    </section>
    <section id="method" class="method-section reveal">
        <div>
            <p class="eyebrow">Methode</p>
            <h2>Un parcours simple, du premier contact au rapport final.</h2>
        </div>
        <ol class="method-list">
            <li><strong>Cadrage</strong><span>On comprend le besoin, le perimetre et les contraintes.</span></li>
            <li><strong>Evaluation</strong><span>On teste les actifs et on qualifie les risques.</span></li>
            <li><strong>Remediation</strong><span>On priorise les corrections et on suit les tickets.</span></li>
            <li><strong>Restitution</strong><span>Vous recevez un rapport clair pour la technique et la direction.</span></li>
        </ol>
    </section>
    <section id="pricing" class="pricing-grid reveal">
        <article class="price-card">
            <span>Starter</span><h2>Audit express</h2><strong>Sur devis</strong>
            <p>Pour valider rapidement un site, une API ou un serveur expose.</p>
            <a href="/register">Choisir</a>
        </article>
        <article class="price-card is-featured">
            <span>Business</span><h2>Audit complet</h2><strong>Sur devis</strong>
            <p>Audit web + infrastructure + plan de remediation suivi.</p>
            <a href="/register">Demander une proposition</a>
        </article>
        <article class="price-card">
            <span>Managed</span><h2>Suivi SOC</h2><strong>Mensuel</strong>
            <p>Supervision, alertes, durcissement et reporting regulier.</p>
            <a href="/register">Echanger</a>
        </article>
    </section>
    <section class="final-cta reveal">
        <h2>Besoin d'une vision claire de votre exposition cyber ?</h2>
        <a class="primary-link" href="/register">Creer un espace client</a>
    </section>
    """
    return public_shell("Services cyber pour PME", content)


def login_page(error: str | None = None) -> bytes:
    error_html = f'<div class="notice error">{e(error)}</div>' if error else ""
    content = f"""
    <section class="login-wrap reveal">
        <div class="login-copy">
            <p class="eyebrow">YOps Cybersecurity</p>
            <h1>Connectez-vous a votre espace cyber.</h1>
            <p>Clients et equipe YOps retrouvent ici les audits, les risques, les tickets et les rapports de securite.</p>
            <div class="login-metrics">
                <span><strong>client</strong> espace dedie</span>
                <span><strong>admin</strong> back-office</span>
                <span><strong>local</strong> SQLite</span>
            </div>
            <figure class="login-visual">
                <img src="/assets/login-visual.svg" alt="Apercu graphique d'un rapport cyber YOps">
            </figure>
        </div>
        <form class="login-card double-bezel" method="post" action="/login">
            <div class="card-core">
                <h2>Connexion</h2>
                {error_html}
                <label>Email
                    <input name="email" type="email" value="admin@yops.local" required>
                </label>
                <label>Mot de passe
                    <input name="password" type="password" value="YOps-Admin-2026!" required>
                </label>
                <button class="primary-button" type="submit"><span>Entrer</span><span class="button-dot">↗</span></button>
                <p class="form-help">Pas encore client ? <a href="/register">Demander un audit</a></p>
                <p class="form-help">Comptes demo : admin@yops.local, sarah.diallo@yops.local, client@alphatech.local</p>
            </div>
        </form>
    </section>
    """
    return layout("Connexion", None, content)


def register_page(errors: list[str] | None = None, data: dict[str, str] | None = None) -> bytes:
    data = data or {}
    error_html = "".join(f'<div class="notice error">{e(error)}</div>' for error in (errors or []))
    content = f"""
    <section class="login-wrap register-wrap reveal">
        <div class="login-copy">
            <p class="eyebrow">Demande client</p>
            <h1>Demandez un audit YOps.</h1>
            <p>Creer un espace client permet de centraliser les echanges, les audits, les vulnerabilites et les rapports.</p>
            <div class="login-metrics">
                <span><strong>48h</strong> premier retour</span>
                <span><strong>PME</strong> cible</span>
                <span><strong>rapport</strong> clair</span>
            </div>
        </div>
        <form class="login-card double-bezel" method="post" action="/register">
            <div class="card-core">
                <h2>Creation de l'espace client</h2>
                {error_html}
                <label>Entreprise<input name="company" value="{e(data.get('company', ''))}" required></label>
                <label>Secteur<input name="sector" value="{e(data.get('sector', ''))}" required></label>
                <label>Nom du contact<input name="name" value="{e(data.get('name', ''))}" required></label>
                <label>Email professionnel<input name="email" type="email" value="{e(data.get('email', ''))}" required></label>
                <label>Telephone<input name="phone" value="{e(data.get('phone', ''))}" required></label>
                <label>Mot de passe<input name="password" type="password" required></label>
                <button class="primary-button" type="submit"><span>Creer ma demande</span><span class="button-dot">↗</span></button>
                <p class="form-help"><a href="/">Retour au site</a> - deja inscrit ? <a href="/login">Connexion</a></p>
            </div>
        </form>
    </section>
    """
    return public_shell("Demande d'audit", content)


def page_header(title: str, subtitle: str, action: str = "") -> str:
    return f"""
    <header class="page-header reveal">
        <div>
            <p class="eyebrow">YOps Portal</p>
            <h1>{e(title)}</h1>
            <p>{e(subtitle)}</p>
        </div>
        {action}
    </header>
    """


def dashboard_page(user: SessionUser, data: dict) -> bytes:
    stats = data["stats"]
    severity_rows = "".join(
        f'<div class="severity-row"><span>{severity_badge(row["severity"])}</span><strong>{row["total"]}</strong></div>'
        for row in data["severity"]
    )
    recent = "".join(
        f"""
        <tr>
            <td>{e(v["title"])}</td>
            <td>{e(v["client_name"])}</td>
            <td>{severity_badge(v["severity"])}</td>
            <td>{status_badge(v["status"])}</td>
            <td>{e(v["cvss_score"])}</td>
        </tr>
        """
        for v in data["recent_vulnerabilities"]
    )
    risk_cards = "".join(
        f"""
        <article class="risk-card">
            <span>{e(risk.client_name)}</span>
            <strong>{risk.score}</strong>
            <small>Risque {e(risk.level)} · C:{risk.critical} H:{risk.high} M:{risk.medium}</small>
        </article>
        """
        for risk in data["client_risks"]
    )
    content = page_header(
        "Pilotage cyber local",
        "Vue metier des clients, audits, vulnerabilites et remediations.",
    )
    content += f"""
    <section class="kpi-grid reveal">
        <article class="kpi-card"><span>Clients actifs</span><strong>{stats["active_clients"]}</strong></article>
        <article class="kpi-card"><span>Audits en cours</span><strong>{stats["active_audits"]}</strong></article>
        <article class="kpi-card danger"><span>Critiques ouvertes</span><strong>{stats["critical_open"]}</strong></article>
        <article class="kpi-card"><span>Remediation</span><strong>{stats["remediation_rate"]}%</strong></article>
    </section>
    <section class="bento-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Dernieres vulnerabilites</h2><a href="/vulnerabilities">Tout voir</a></div>
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Client</th><th>Criticite</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{recent}</tbody></table></div>
        </article>
        <article class="panel">
            <div class="panel-head"><h2>Criticites</h2></div>
            <div class="severity-list">{severity_rows}</div>
        </article>
        <article class="panel panel-tall">
            <div class="panel-head"><h2>Risque client</h2></div>
            <div class="risk-list">{risk_cards}</div>
        </article>
    </section>
    """
    return layout("Dashboard", user, content, "dashboard")


def client_dashboard_page(user: SessionUser, client, audits, vulnerabilities, tickets, reports) -> bytes:
    audit_rows = "".join(
        f"""
        <tr>
            <td><a href="/audits/{audit.id}">{e(audit.title)}</a></td>
            <td>{e(audit.audit_type)}</td>
            <td>{status_badge(audit.status)}</td>
            <td>{e(audit.starts_at)}</td>
        </tr>
        """
        for audit in audits
    )
    vuln_rows = "".join(
        f"""
        <tr>
            <td>{e(vuln.title)}<small>{e(vuln.asset)}</small></td>
            <td>{severity_badge(vuln.severity)}</td>
            <td>{status_badge(vuln.status)}</td>
        </tr>
        """
        for vuln in vulnerabilities[:6]
    )
    ticket_rows = "".join(
        f"""
        <tr>
            <td>{e(ticket.vulnerability_title)}</td>
            <td>{badge(ticket.priority, 'high' if ticket.priority == 'P1' else 'neutral')}</td>
            <td>{e(ticket.due_date)}</td>
            <td>{status_badge(ticket.status)}</td>
        </tr>
        """
        for ticket in tickets[:6]
    )
    report_cards = "".join(
        f"""
        <article class="report-card">
            <span>{e(report.generated_at)}</span>
            <h2>{e(report.title)}</h2>
            <p>{e(report.executive_summary)}</p>
            <small>{e(report.audit_title)}</small>
        </article>
        """
        for report in reports
    )
    open_vulns = sum(1 for vuln in vulnerabilities if vuln.status != "corrigee")
    critical_vulns = sum(1 for vuln in vulnerabilities if vuln.severity == "critical" and vuln.status != "corrigee")
    open_tickets = sum(1 for ticket in tickets if ticket.status != "termine")
    content = page_header(
        f"Espace {client.name}",
        "Suivi client : audits, risques, tickets et rapports visibles uniquement pour votre entreprise.",
    )
    content += f"""
    <section class="kpi-grid reveal">
        <article class="kpi-card"><span>Audits</span><strong>{len(audits)}</strong></article>
        <article class="kpi-card danger"><span>Critiques ouvertes</span><strong>{critical_vulns}</strong></article>
        <article class="kpi-card"><span>Vulnerabilites ouvertes</span><strong>{open_vulns}</strong></article>
        <article class="kpi-card"><span>Tickets ouverts</span><strong>{open_tickets}</strong></article>
    </section>
    <section class="bento-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Mes audits</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Audit</th><th>Type</th><th>Statut</th><th>Debut</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
        </article>
        <article class="panel">
            <div class="panel-head"><h2>Mes tickets</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Faille</th><th>Priorite</th><th>Echeance</th><th>Statut</th></tr></thead><tbody>{ticket_rows}</tbody></table></div>
        </article>
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Vulnerabilites principales</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Criticite</th><th>Statut</th></tr></thead><tbody>{vuln_rows}</tbody></table></div>
        </article>
    </section>
    <section class="report-grid reveal">{report_cards}</section>
    """
    return layout("Espace client", user, content, "dashboard")


def clients_page(user: SessionUser, clients, errors: list[str] | None = None) -> bytes:
    error_html = "".join(f'<div class="notice error">{e(error)}</div>' for error in (errors or []))
    rows = "".join(
        f"""
        <tr>
            <td><a href="/clients/{client.id}">{e(client.name)}</a></td>
            <td>{e(client.sector)}</td>
            <td>{e(client.contact_name)}</td>
            <td>{e(client.email)}</td>
            <td>{status_badge(client.status)}</td>
        </tr>
        """
        for client in clients
    )
    content = page_header("Clients", "Portefeuille clients suivi par YOps.")
    content += f"""
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="table-wrap"><table><thead><tr><th>Client</th><th>Secteur</th><th>Contact</th><th>Email</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table></div>
        </article>
        <form class="panel form-panel" method="post" action="/clients">
            <h2>Nouveau client</h2>
            {error_html}
            <label>Nom<input name="name" required></label>
            <label>Secteur<input name="sector" required></label>
            <label>Contact<input name="contact_name" required></label>
            <label>Email<input name="email" type="email" required></label>
            <label>Telephone<input name="phone" required></label>
            <input type="hidden" name="status" value="active">
            <button class="primary-button" type="submit"><span>Creer</span><span class="button-dot">↗</span></button>
        </form>
    </section>
    """
    return layout("Clients", user, content, "clients")


def client_detail_page(user: SessionUser, client, audits, vulnerabilities, risk) -> bytes:
    audit_rows = "".join(
        f"""
        <tr>
            <td><a href="/audits/{audit.id}">{e(audit.title)}</a></td>
            <td>{e(audit.audit_type)}</td>
            <td>{status_badge(audit.status)}</td>
            <td>{e(audit.starts_at)}</td>
            <td>{e(audit.ends_at or '-')}</td>
        </tr>
        """
        for audit in audits
    )
    vulnerability_rows = "".join(
        f"""
        <tr>
            <td>{e(vuln.title)}<small>{e(vuln.asset)}</small></td>
            <td>{severity_badge(vuln.severity)}</td>
            <td>{status_badge(vuln.status)}</td>
            <td>{e(vuln.cvss_score)}</td>
        </tr>
        """
        for vuln in vulnerabilities[:8]
    )
    content = page_header(
        client.name,
        f"{client.sector} - contact {client.contact_name} - {client.email}",
        '<a class="secondary-button" href="/clients">Retour clients</a>',
    )
    content += f"""
    <section class="kpi-grid reveal">
        <article class="kpi-card"><span>Score risque</span><strong>{risk.score}</strong></article>
        <article class="kpi-card danger"><span>Critiques</span><strong>{risk.critical}</strong></article>
        <article class="kpi-card"><span>Hautes</span><strong>{risk.high}</strong></article>
        <article class="kpi-card"><span>Niveau</span><strong>{e(risk.level)}</strong></article>
    </section>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Audits</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Mission</th><th>Type</th><th>Statut</th><th>Debut</th><th>Fin</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
        </article>
        <article class="panel">
            <h2>Fiche client</h2>
            <dl class="detail-list">
                <dt>Secteur</dt><dd>{e(client.sector)}</dd>
                <dt>Contact</dt><dd>{e(client.contact_name)}</dd>
                <dt>Email</dt><dd>{e(client.email)}</dd>
                <dt>Telephone</dt><dd>{e(client.phone)}</dd>
            </dl>
        </article>
    </section>
    <article class="panel reveal">
        <div class="panel-head"><h2>Vulnerabilites principales</h2><a href="/vulnerabilities">Registre complet</a></div>
        <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Criticite</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{vulnerability_rows}</tbody></table></div>
    </article>
    """
    return layout(client.name, user, content, "clients")


def audits_page(user: SessionUser, audits) -> bytes:
    rows = "".join(
        f"""
        <tr>
            <td><a href="/audits/{audit.id}">{e(audit.title)}</a></td>
            <td>{e(audit.client_name)}</td>
            <td>{e(audit.audit_type)}</td>
            <td>{status_badge(audit.status)}</td>
            <td>{e(audit.owner_name)}</td>
        </tr>
        """
        for audit in audits
    )
    content = page_header("Audits", "Missions cyber et avancement par client.")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Audit</th><th>Client</th><th>Type</th><th>Statut</th><th>Responsable</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Audits", user, content, "audits")


def audit_detail_page(user: SessionUser, audit, vulnerabilities) -> bytes:
    rows = "".join(
        f"""
        <tr>
            <td>{e(v.title)}</td><td>{severity_badge(v.severity)}</td><td>{e(v.asset)}</td><td>{status_badge(v.status)}</td><td>{e(v.cvss_score)}</td>
        </tr>
        """
        for v in vulnerabilities
    )
    content = page_header(audit.title, f"{audit.client_name} · {audit.audit_type} · responsable {audit.owner_name}")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Vulnerabilite</th><th>Criticite</th><th>Actif</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Audit", user, content, "audits")


def vulnerabilities_page(user: SessionUser, vulnerabilities, audits, query: dict, errors: list[str] | None = None) -> bytes:
    rows = "".join(
        f"""
        <tr>
            <td>{e(v.title)}<small>{e(v.asset)}</small></td>
            <td>{e(v.client_name)}</td>
            <td>{severity_badge(v.severity)}</td>
            <td>{status_badge(v.status)}</td>
            <td>{e(v.cvss_score)}</td>
        </tr>
        """
        for v in vulnerabilities
    )
    audit_options = "".join(f'<option value="{audit.id}">{e(audit.client_name)} - {e(audit.title)}</option>' for audit in audits)
    error_html = "".join(f'<div class="notice error">{e(error)}</div>' for error in (errors or []))
    filters = urlencode({key: value for key, value in query.items() if value})
    content = page_header("Vulnerabilites", "Registre technique classe par criticite.")
    content += f"""
    <section class="filter-bar reveal">
        <a class="chip" href="/vulnerabilities">Toutes</a>
        <a class="chip" href="/vulnerabilities?severity=critical">Critiques</a>
        <a class="chip" href="/vulnerabilities?severity=high">Hautes</a>
        <a class="chip" href="/vulnerabilities?status=ouverte">Ouvertes</a>
    </section>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Client</th><th>Criticite</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{rows}</tbody></table></div>
        </article>
        <form class="panel form-panel" method="post" action="/vulnerabilities?{filters}">
            <h2>Ajouter</h2>
            {error_html}
            <label>Audit<select name="audit_id">{audit_options}</select></label>
            <label>Titre<input name="title" required></label>
            <label>Description<textarea name="description" required></textarea></label>
            <label>Criticite<select name="severity"><option value="low">Faible</option><option value="medium">Moyenne</option><option value="high">Haute</option><option value="critical">Critique</option></select></label>
            <label>CVSS<input name="cvss_score" type="number" min="0" max="10" step="0.1" value="7.0" required></label>
            <label>Actif<input name="asset" required></label>
            <label>Preuve<textarea name="evidence" required></textarea></label>
            <label>Recommandation<textarea name="recommendation" required></textarea></label>
            <button class="primary-button" type="submit"><span>Enregistrer</span><span class="button-dot">↗</span></button>
        </form>
    </section>
    """
    return layout("Vulnerabilites", user, content, "vulnerabilities")


def tickets_page(user: SessionUser, tickets) -> bytes:
    rows = "".join(
        f"""
        <tr>
            <td>{e(ticket.vulnerability_title)}<small>{e(ticket.client_name)}</small></td>
            <td>{badge(ticket.priority, 'high' if ticket.priority == 'P1' else 'neutral')}</td>
            <td>{e(ticket.assignee_name)}</td>
            <td>{e(ticket.due_date)}</td>
            <td>{status_badge(ticket.status)}</td>
        </tr>
        """
        for ticket in tickets
    )
    content = page_header("Tickets", "Suivi operationnel des corrections.")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Vulnerabilite</th><th>Priorite</th><th>Assigne</th><th>Echeance</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Tickets", user, content, "tickets")


def reports_page(user: SessionUser, reports) -> bytes:
    cards = "".join(
        f"""
        <article class="report-card">
            <span>{e(report.client_name)}</span>
            <h2>{e(report.title)}</h2>
            <p>{e(report.executive_summary)}</p>
            <small>{e(report.generated_at)} · {e(report.audit_title)}</small>
        </article>
        """
        for report in reports
    )
    content = page_header("Rapports", "Syntheses exploitables pour le client et le management.")
    content += f'<section class="report-grid reveal">{cards}</section>'
    return layout("Rapports", user, content, "reports")


def users_page(user: SessionUser, users) -> bytes:
    rows = "".join(
        f"<tr><td>{e(item.name)}</td><td>{e(item.email)}</td><td>{badge(item.role)}</td><td>{e(item.client_id or '-')}</td></tr>"
        for item in users
    )
    content = page_header("Utilisateurs", "Comptes locaux de demonstration et roles applicatifs.")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Nom</th><th>Email</th><th>Role</th><th>Client</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Utilisateurs", user, content, "admin")


def not_found_page(user: SessionUser | None) -> bytes:
    content = page_header("Page introuvable", "La route demandee n'existe pas.")
    return layout("404", user, content)
