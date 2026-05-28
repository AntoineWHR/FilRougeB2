from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from yops_portal.core.security import SessionUser
from yops_portal.services.cvss import severity_from_cvss


def e(value) -> str:
    return escape(str(value), quote=True)


def badge(value: str, kind: str = "neutral") -> str:
    return f'<span class="badge badge-{e(kind)}">{e(value)}</span>'


def severity_badge(severity: str) -> str:
    labels = {"critical": "Critique", "high": "Haute", "medium": "Moyenne", "low": "Faible"}
    return badge(labels.get(severity, severity), severity)


def cvss_chip(score) -> str:
    try:
        value = float(score)
    except (TypeError, ValueError):
        value = 0.0
    return f'<span class="cvss-chip cvss-{severity_from_cvss(value)}">{value:.1f}</span>'


NEXT_STATUS = {"ouverte": "en_cours", "en_cours": "corrigee", "corrigee": "ouverte", "acceptee": "ouverte"}
NEXT_STATUS_LABEL = {"ouverte": "Démarrer", "en_cours": "Marquer corrigée", "corrigee": "Réouvrir", "acceptee": "Réouvrir"}


def status_action_form(vuln_id: int, status: str, return_to: str) -> str:
    return f"""
    <form method="post" action="/vulnerabilities/{vuln_id}/status">
        <input type="hidden" name="status" value="{NEXT_STATUS.get(status, 'en_cours')}">
        <input type="hidden" name="return_to" value="{e(return_to)}">
        <button class="inline-button" type="submit">{NEXT_STATUS_LABEL.get(status, 'Avancer')}</button>
    </form>
    """


def score_edit_form(vuln_id: int, score, return_to: str) -> str:
    try:
        value = float(score)
    except (TypeError, ValueError):
        value = 0.0
    return f"""
    <form class="cvss-edit" method="post" action="/vulnerabilities/{vuln_id}/score">
        <input type="number" name="cvss_score" min="0" max="10" step="0.1" value="{value:.1f}" aria-label="Nouveau score CVSS">
        <input type="hidden" name="return_to" value="{e(return_to)}">
        <button class="inline-button" type="submit">↻</button>
    </form>
    """


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
                ("requests", "/audit-requests", "Demandes"),
                ("clients", "/clients", "Clients"),
                ("audits", "/audits", "Audits"),
                ("vulnerabilities", "/vulnerabilities", "Vulnérabilités"),
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
                    <button class="ghost-button" type="submit">Déconnexion</button>
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
            <a href="#method">Méthode</a>
            <a href="#pricing">Offres</a>
            <a class="secondary-button" href="{account_link}">{account_label}</a>
        </div>
    </nav>
    <section class="hero-section reveal">
        <div class="hero-copy">
            <p class="eyebrow">Audit - SOC - Remédiation</p>
            <h1>La sécurité cyber <em>lisible</em> pour les PME.</h1>
            <p>YOps aide les entreprises à identifier leurs risques, prioriser les corrections et suivre les actions sans jargon inutile.</p>
            <div class="hero-actions">
                <a class="primary-link" href="/register">Demander un audit</a>
                <a class="text-link" href="#services">Voir les services</a>
            </div>
        </div>
        <aside class="hero-board double-bezel">
            <div class="card-core">
                <img src="/assets/yops-cyber-visual.png" alt="Visuels YOps Cybersecurity générés pour la landing page">
                <div class="hero-overlay top-right is-floating" style="--delay: 120ms; --float-delay: 0.4s">
                    <span class="live-dot" aria-hidden="true"></span>
                    <strong>SOC actif · 24/7</strong>
                </div>
                <div class="hero-overlay top-left is-floating alt" style="--delay: 220ms; --float-delay: 1.1s">
                    <span class="board-label">Synthèse client</span>
                    <strong>Risque exposé</strong>
                    <div class="board-score"><span>82</span><small>/100</small></div>
                    <div class="board-bars">
                        <span style="--w: 82%; --bar-delay: 400ms"></span>
                        <span style="--w: 58%; --bar-delay: 540ms"></span>
                        <span style="--w: 34%; --bar-delay: 680ms"></span>
                    </div>
                </div>
                <div class="hero-overlay bottom-right is-floating" style="--delay: 360ms; --float-delay: 1.8s">
                    <span class="board-label">Remédiation</span>
                    <strong>12 tickets traités cette semaine</strong>
                </div>
            </div>
        </aside>
    </section>
    <section class="trust-strip" aria-label="Stack et standards">
        <div class="trust-track">
            <span>OWASP Top 10</span>
            <span>ISO 27001</span>
            <span>ANSSI · PASSI</span>
            <span>Wazuh SIEM</span>
            <span>Active Directory</span>
            <span>pfSense</span>
            <span>NIST CSF</span>
            <span>CVSS 3.1</span>
            <span>OWASP Top 10</span>
            <span>ISO 27001</span>
            <span>ANSSI · PASSI</span>
            <span>Wazuh SIEM</span>
            <span>Active Directory</span>
            <span>pfSense</span>
            <span>NIST CSF</span>
            <span>CVSS 3.1</span>
        </div>
    </section>
    <section id="services" class="service-strip reveal">
        <article><span>01</span><h2>Audit web</h2><p>Recherche de failles sur application, API, authentification et parcours sensibles.</p><small>OWASP, API, comptes, sessions</small></article>
        <article><span>02</span><h2>Audit infrastructure</h2><p>Contrôle AD, serveurs, partages, sauvegardes et exposition réseau.</p><small>AD, Linux, Windows Server, pfSense</small></article>
        <article><span>03</span><h2>Supervision SOC</h2><p>Mise en place d'agents, alertes, tableaux de bord et suivi des incidents.</p><small>Wazuh, logs, endpoints, reporting</small></article>
    </section>
    <section id="method" class="method-section reveal">
        <div>
            <p class="eyebrow">Méthode</p>
            <h2>Un parcours simple, du premier contact au rapport final.</h2>
        </div>
        <ol class="method-list">
            <li><strong>Cadrage</strong><span>On comprend le besoin, le périmètre et les contraintes.</span></li>
            <li><strong>Évaluation</strong><span>On teste les actifs et on qualifie les risques.</span></li>
            <li><strong>Remédiation</strong><span>On priorise les corrections et on suit les tickets.</span></li>
            <li><strong>Restitution</strong><span>Vous recevez un rapport clair pour la technique et la direction.</span></li>
        </ol>
    </section>
    <section id="pricing" class="pricing-grid reveal">
        <article class="price-card">
            <span>Starter</span><h2>Audit express</h2><strong>Sur devis</strong>
            <p>Pour valider rapidement un site, une API ou un serveur exposé.</p>
            <a href="/register">Choisir</a>
        </article>
        <article class="price-card is-featured">
            <span>Business</span><h2>Audit complet</h2><strong>Sur devis</strong>
            <p>Audit web + infrastructure + plan de remédiation suivi.</p>
            <a href="/register">Demander une proposition</a>
        </article>
        <article class="price-card">
            <span>Managed</span><h2>Suivi SOC</h2><strong>Mensuel</strong>
            <p>Supervision, alertes, durcissement et reporting régulier.</p>
            <a href="/register">Échanger</a>
        </article>
    </section>
    <section class="final-cta reveal">
        <h2>Besoin d'une vision claire de votre exposition cyber ?</h2>
        <a class="primary-link" href="/register">Créer un espace client</a>
    </section>
    """
    return public_shell("Services cyber pour PME", content)


def login_page(error: str | None = None) -> bytes:
    error_html = f'<div class="notice error">{e(error)}</div>' if error else ""
    content = f"""
    <section class="login-wrap reveal">
        <div class="login-copy">
            <p class="eyebrow">YOps Cybersecurity</p>
            <h1>Connectez-vous à votre espace cyber.</h1>
            <p>Clients et équipe YOps retrouvent ici les audits, les risques, les tickets et les rapports de sécurité.</p>
            <div class="login-metrics">
                <span><strong>client</strong> espace dédié</span>
                <span><strong>admin</strong> back-office</span>
                <span><strong>local</strong> SQLite</span>
            </div>
            <figure class="login-visual">
                <img src="/assets/yops-login-visual.png" alt="Aperçu graphique d'un espace de connexion cyber YOps">
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
                <p class="form-help">Comptes démo : admin@yops.local, sarah.diallo@yops.local, client@alphatech.local</p>
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
            <p>Créer un espace client permet de centraliser les échanges, les audits, les vulnérabilités et les rapports.</p>
            <div class="login-metrics">
                <span><strong>48h</strong> premier retour</span>
                <span><strong>PME</strong> cible</span>
                <span><strong>rapport</strong> clair</span>
            </div>
        </div>
        <form class="login-card double-bezel" method="post" action="/register">
            <div class="card-core">
                <h2>Création de l'espace client</h2>
                {error_html}
                <label>Entreprise<input name="company" value="{e(data.get('company', ''))}" required></label>
                <label>Secteur<input name="sector" value="{e(data.get('sector', ''))}" required></label>
                <label>Nom du contact<input name="name" value="{e(data.get('name', ''))}" required></label>
                <label>Email professionnel<input name="email" type="email" value="{e(data.get('email', ''))}" required></label>
                <label>Téléphone<input name="phone" value="{e(data.get('phone', ''))}" required></label>
                <label>Mot de passe<input name="password" type="password" required></label>
                <button class="primary-button" type="submit"><span>Créer ma demande</span><span class="button-dot">↗</span></button>
                <p class="form-help"><a href="/">Retour au site</a> - déjà inscrit ? <a href="/login">Connexion</a></p>
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
            <td><a href="/vulnerabilities">{e(v["title"])}</a></td>
            <td>{e(v["client_name"])}</td>
            <td>{severity_badge(v["severity"])}</td>
            <td>{status_badge(v["status"])}</td>
            <td>{cvss_chip(v["cvss_score"])}</td>
            <td class="row-actions">{status_action_form(v["id"], v["status"], "/dashboard")}</td>
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
    top_assets = data.get("top_assets", [])
    audit_progress = data.get("audit_progress", [])
    activity = data.get("activity", [])

    asset_rows = "".join(
        f"""
        <li class="asset-row">
            <div>
                <strong>{e(asset["asset"])}</strong>
                <small>{e(asset["client_name"])}</small>
            </div>
            <div class="asset-meta">
                <span class="badge badge-{'critical' if asset['max_cvss'] >= 9 else 'high' if asset['max_cvss'] >= 7 else 'medium'}">CVSS {asset["max_cvss"]}</span>
                <strong>{asset["open_count"]}<small>/{asset["total"]}</small></strong>
            </div>
        </li>
        """
        for asset in top_assets
    )

    progress_rows = "".join(
        f"""
        <article class="progress-row">
            <div>
                <strong><a href="/audits/{ap["id"]}">{e(ap["title"])}</a></strong>
                <small>{e(ap["client_name"])} · {ap["fixed"]}/{ap["total"]} corrigées</small>
            </div>
            <div class="progress-bar" role="progressbar" aria-valuenow="{ap["percent"]}" aria-valuemin="0" aria-valuemax="100">
                <span style="--w: {ap["percent"]}%"></span>
            </div>
            <span class="progress-pct">{ap["percent"]}%</span>
        </article>
        """
        for ap in audit_progress
    )

    activity_rows = "".join(
        f"""
        <li class="activity-item kind-{e(item["kind"])}">
            <span class="activity-marker">{_activity_icon(item["kind"])}</span>
            <div>
                <strong>{e(item["label"])}</strong>
                <small>{e(item["client_name"])} · {_activity_label(item["kind"], item.get("detail", ""))} · {e(item["happened_at"])}</small>
            </div>
        </li>
        """
        for item in activity
    )

    pending_requests = data.get("pending_requests", [])
    pending_section = _pending_requests_block(pending_requests)

    content = page_header(
        "Pilotage cyber local",
        "Vue métier des clients, audits, vulnérabilités et remédiations.",
    )
    content += f"""
    <h2 class="section-title reveal"><span>Vue d'ensemble</span><small>{stats["active_clients"]} clients - {stats["active_audits"]} audits actifs</small></h2>
    <section class="kpi-grid reveal">
        <article class="kpi-card"><span>Clients actifs</span><strong data-count="{stats["active_clients"]}">{stats["active_clients"]}</strong></article>
        <article class="kpi-card"><span>Audits en cours</span><strong data-count="{stats["active_audits"]}">{stats["active_audits"]}</strong></article>
        <article class="kpi-card danger"><span>Critiques ouvertes</span><strong data-count="{stats["critical_open"]}">{stats["critical_open"]}</strong></article>
        <article class="kpi-card"><span>Remédiation</span><strong data-count="{stats["remediation_rate"]}" data-suffix="%">{stats["remediation_rate"]}%</strong></article>
    </section>
    <section class="quick-actions reveal">
        <a class="quick-action" href="/clients"><span class="qa-icon">＋</span><div><strong>Ajouter un client</strong><small>Créer un nouveau dossier</small></div></a>
        <a class="quick-action" href="/vulnerabilities"><span class="qa-icon">⚠</span><div><strong>Déclarer une faille</strong><small>Ajouter au registre</small></div></a>
        <a class="quick-action {'highlight' if pending_requests else ''}" href="/audit-requests"><span class="qa-icon">✉</span><div><strong>Demandes clients</strong><small>{len(pending_requests)} en attente</small></div></a>
        <a class="quick-action" href="/tickets"><span class="qa-icon">≡</span><div><strong>Tickets</strong><small>{stats["late_tickets"]} en retard</small></div></a>
        <a class="quick-action" href="/reports/vulnerabilities.pdf"><span class="qa-icon">▤</span><div><strong>Export global</strong><small>Toutes les vulns à corriger</small></div></a>
    </section>
    {_deliver_panel(data.get("clients", []), data.get("recent_deliveries", []))}
    {pending_section}
    <h2 class="section-title reveal"><span>Pilotage des audits</span><small>Avancement et actifs à risque</small></h2>
    <section class="split-grid reveal">
        <article class="panel">
            <div class="panel-head"><h2>Progression des audits actifs</h2><a href="/audits">Tout voir</a></div>
            <div class="progress-list">{progress_rows or '<p class="form-help">Aucun audit en cours.</p>'}</div>
        </article>
        <article class="panel">
            <div class="panel-head"><h2>Actifs à risque</h2></div>
            <ol class="asset-list">{asset_rows or '<li class="form-help">Aucun actif exposé.</li>'}</ol>
        </article>
    </section>
    <h2 class="section-title reveal"><span>Risque & vulnérabilités</span><small>Niveau d'exposition par client</small></h2>
    <section class="split-grid reveal">
        <article class="panel">
            <div class="panel-head"><h2>Dernières vulnérabilités</h2><a href="/vulnerabilities">Tout voir</a></div>
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Client</th><th>Criticité</th><th>Statut</th><th>CVSS</th><th></th></tr></thead><tbody>{recent}</tbody></table></div>
        </article>
        <article class="panel">
            <div class="panel-head"><h2>Criticités</h2></div>
            <div class="severity-list">{severity_rows}</div>
        </article>
    </section>
    <section class="reveal">
        <article class="panel">
            <div class="panel-head"><h2>Risque par client</h2><small>{len(data.get("client_risks", []))} clients analysés</small></div>
            <div class="risk-grid">{risk_cards}</div>
        </article>
    </section>
    <h2 class="section-title reveal"><span>Activité récente</span><small>Vulnérabilités, notes, rapports</small></h2>
    <section class="reveal">
        <article class="panel">
            <ol class="activity-list">{activity_rows}</ol>
        </article>
    </section>
    """
    return layout("Dashboard", user, content, "dashboard")


def _deliver_panel(clients, recent_deliveries) -> str:
    options = "".join(f'<option value="{c.id}">{e(c.name)}</option>' for c in clients)
    rows = "".join(
        f"""
        <li class="delivery-row">
            <div>
                <strong><a href="/reports/delivered/{d.id}.pdf">{e(d.filename)}</a></strong>
                <small>{e(d.client_name)} · {d.vuln_count} vulns ({d.critical_count} critiques) · envoyé par {e(d.sent_by_name)} · {e(d.delivered_at)}</small>
            </div>
            <span class="badge badge-{'success' if d.read_at else 'high'}">{'Lu' if d.read_at else 'Non lu'}</span>
        </li>
        """
        for d in recent_deliveries
    )
    empty = '<li class="form-help">Aucun envoi récent.</li>'
    return f"""
    <h2 id="deliver" class="section-title reveal accent">
        <span>Envoyer un rapport client</span>
        <small>PDF de remédiation directement sur l'espace client</small>
    </h2>
    <section class="split-grid reveal">
        <form class="panel form-panel" method="post" action="/reports/deliver">
            <h2>Nouvel envoi</h2>
            <label>Client destinataire<select name="client_id" required>{options}</select></label>
            <p class="form-help">Le PDF inclut uniquement les vulnérabilités <strong>ouvertes</strong> ou <strong>en cours</strong> du client sélectionné. Il apparaît instantanément sur son dashboard.</p>
            <button class="primary-button" type="submit"><span>Générer et envoyer</span><span class="button-dot">↗</span></button>
        </form>
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Envois récents</h2><small>{len(recent_deliveries)} dernier{'s' if len(recent_deliveries) > 1 else ''}</small></div>
            <ul class="delivery-list">{rows or empty}</ul>
        </article>
    </section>
    """


def _pending_requests_block(requests) -> str:
    if not requests:
        return ""
    cards = "".join(_request_card_admin(req) for req in requests)
    return f"""
    <h2 id="requests" class="section-title reveal accent">
        <span>Demandes clients en attente</span>
        <small>{len(requests)} à traiter</small>
    </h2>
    <section class="request-grid reveal">{cards}</section>
    """


def _request_card_admin(req) -> str:
    rules = f'<p><strong>Règles :</strong> {e(req.rules)}</p>' if req.rules else ""
    target = f'<small>Date cible : {e(req.target_date)}</small>' if req.target_date else ""
    return f"""
    <article class="request-card status-{e(req.status)}">
        <header>
            <span class="badge badge-{URGENCY_KIND[req.urgency]}">{URGENCY_LABELS[req.urgency]}</span>
            <strong><a href="/clients/{req.client_id}">{e(req.client_name)}</a></strong>
            <small>{e(req.requested_by_name)} · {e(req.created_at)}</small>
        </header>
        <div class="request-body">
            <p class="request-type">{e(AUDIT_TYPE_LABELS.get(req.audit_type, req.audit_type))}</p>
            <p>{e(req.scope)}</p>
            {rules}
            {target}
        </div>
        <form class="request-actions" method="post" action="/audit-requests/{req.id}/respond">
            <input type="text" name="title" placeholder="Titre de l'audit (optionnel)">
            <input type="date" name="starts_at">
            <textarea name="message" rows="2" placeholder="Message au client..."></textarea>
            <div class="request-buttons">
                <button class="inline-button accept" type="submit" name="decision" value="accept">Accepter</button>
                <button class="inline-button reject" type="submit" name="decision" value="reject">Refuser</button>
            </div>
        </form>
    </article>
    """


def audit_requests_page(user: SessionUser, requests) -> bytes:
    pending = [r for r in requests if r.status == "pending"]
    history = [r for r in requests if r.status != "pending"]
    pending_cards = "".join(_request_card_admin(r) for r in pending) or '<p class="form-help">Aucune demande en attente.</p>'
    history_rows = "".join(
        f"""
        <tr>
            <td><a href="/clients/{r.client_id}">{e(r.client_name)}</a></td>
            <td>{e(AUDIT_TYPE_LABELS.get(r.audit_type, r.audit_type))}</td>
            <td><span class="badge badge-{URGENCY_KIND[r.urgency]}">{URGENCY_LABELS[r.urgency]}</span></td>
            <td><span class="badge badge-{REQUEST_STATUS_KIND[r.status]}">{REQUEST_STATUS_LABEL[r.status]}</span></td>
            <td>{e(r.responded_by_name or '-')}</td>
            <td>{e(r.responded_at or '-')}</td>
            <td>{e(r.admin_response or '-')}</td>
        </tr>
        """
        for r in history
    )
    content = page_header(
        "Demandes d'audit",
        f"{len(pending)} en attente - {len(history)} traitées.",
        '<a class="secondary-button" href="/dashboard">Retour dashboard</a>',
    )
    content += f"""
    <h2 class="section-title reveal accent"><span>À traiter</span><small>{len(pending)} demandes</small></h2>
    <section class="request-grid reveal">{pending_cards}</section>
    <h2 class="section-title reveal"><span>Historique</span><small>{len(history)} entrées</small></h2>
    <article class="panel reveal">
        <div class="table-wrap"><table><thead><tr><th>Client</th><th>Type</th><th>Urgence</th><th>Décision</th><th>Par</th><th>Le</th><th>Message</th></tr></thead><tbody>{history_rows or ''}</tbody></table></div>
    </article>
    """
    return layout("Demandes d'audit", user, content, "dashboard")


def _activity_icon(kind: str) -> str:
    return {"vulnerability": "⚠", "note": "✎", "report": "▤"}.get(kind, "•")


def _activity_label(kind: str, detail: str) -> str:
    if kind == "vulnerability":
        labels = {"critical": "Critique", "high": "Haute", "medium": "Moyenne", "low": "Faible"}
        return f"Vulnérabilité {labels.get(detail, detail)}"
    if kind == "note":
        return {"note": "Note", "contact": "Contact", "alert": "Alerte", "meeting": "Réunion"}.get(detail, "Note")
    if kind == "report":
        return "Rapport publié"
    return ""


URGENCY_LABELS = {"low": "Faible", "normal": "Normale", "high": "Haute", "urgent": "Urgente"}
URGENCY_KIND = {"low": "low", "normal": "neutral", "high": "high", "urgent": "critical"}
AUDIT_TYPE_LABELS = {"web": "Web / API", "infra": "Infrastructure", "ad": "Active Directory", "cloud": "Cloud", "code": "Revue de code"}
REQUEST_STATUS_LABEL = {"pending": "En attente", "accepted": "Acceptée", "rejected": "Refusée"}
REQUEST_STATUS_KIND = {"pending": "high", "accepted": "success", "rejected": "critical"}


def _request_card_client(req) -> str:
    response = ""
    if req.admin_response:
        response = f'<p class="request-response"><strong>YOps :</strong> {e(req.admin_response)}</p>'
    return f"""
    <article class="request-card status-{e(req.status)}">
        <header>
            <span class="badge badge-{REQUEST_STATUS_KIND[req.status]}">{REQUEST_STATUS_LABEL[req.status]}</span>
            <span class="badge badge-{URGENCY_KIND[req.urgency]}">{URGENCY_LABELS[req.urgency]}</span>
            <strong>{e(AUDIT_TYPE_LABELS.get(req.audit_type, req.audit_type))}</strong>
            <small>{e(req.created_at)}</small>
        </header>
        <p>{e(req.scope)}</p>
        {f'<p class="form-help"><strong>Règles :</strong> {e(req.rules)}</p>' if req.rules else ''}
        {f'<p class="form-help"><strong>Date cible :</strong> {e(req.target_date)}</p>' if req.target_date else ''}
        {response}
    </article>
    """


def client_dashboard_page(
    user: SessionUser,
    client,
    audits,
    vulnerabilities,
    tickets,
    reports,
    requests=None,
    request_errors: list[str] | None = None,
    request_form: dict[str, str] | None = None,
    deliveries=None,
) -> bytes:
    requests = requests or []
    deliveries = deliveries or []
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
    sorted_vulns = sorted(vulnerabilities, key=lambda v: float(v.cvss_score or 0), reverse=True)
    vuln_rows = "".join(
        f"""
        <tr>
            <td>{e(vuln.title)}<small>{e(vuln.asset)}</small></td>
            <td>{severity_badge(vuln.severity)}</td>
            <td>{cvss_chip(vuln.cvss_score)}</td>
            <td>{status_badge(vuln.status)}</td>
        </tr>
        """
        for vuln in sorted_vulns[:6]
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
        <article class="kpi-card"><span>Audits</span><strong data-count="{len(audits)}">{len(audits)}</strong></article>
        <article class="kpi-card danger"><span>Critiques ouvertes</span><strong data-count="{critical_vulns}">{critical_vulns}</strong></article>
        <article class="kpi-card"><span>Vulnérabilités ouvertes</span><strong data-count="{open_vulns}">{open_vulns}</strong></article>
        <article class="kpi-card"><span>Tickets ouverts</span><strong data-count="{open_tickets}">{open_tickets}</strong></article>
    </section>
    <section class="bento-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Mes audits</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Audit</th><th>Type</th><th>Statut</th><th>Début</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
        </article>
        <article class="panel">
            <div class="panel-head"><h2>Mes tickets</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Faille</th><th>Priorité</th><th>Échéance</th><th>Statut</th></tr></thead><tbody>{ticket_rows}</tbody></table></div>
        </article>
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Vulnérabilités principales</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Criticité</th><th>CVSS</th><th>Statut</th></tr></thead><tbody>{vuln_rows}</tbody></table></div>
        </article>
    </section>
    <section class="report-grid reveal">{report_cards}</section>
    {_client_deliveries_section(deliveries)}
    {_client_request_section(user, client, requests, request_errors, request_form)}
    """
    return layout("Espace client", user, content, "dashboard")


def _client_deliveries_section(deliveries) -> str:
    if not deliveries:
        return ""
    unread = sum(1 for d in deliveries if not d.read_at)
    cards = "".join(
        f"""
        <article class="delivery-card {'is-unread' if not d.read_at else ''}">
            <header>
                <span class="badge badge-{'high' if not d.read_at else 'success'}">{'Nouveau' if not d.read_at else 'Lu'}</span>
                <strong>Rapport de remédiation</strong>
                <small>{d.vuln_count} vulnérabilités · {d.critical_count} critiques</small>
            </header>
            <p class="delivery-meta">Envoyé par {e(d.sent_by_name)} · {e(d.delivered_at)}</p>
            <a class="primary-button" href="/reports/delivered/{d.id}.pdf">
                <span>Télécharger le PDF</span><span class="button-dot">↓</span>
            </a>
        </article>
        """
        for d in deliveries
    )
    return f"""
    <h2 id="deliveries" class="section-title reveal accent">
        <span>Rapports reçus de YOps</span>
        <small>{len(deliveries)} document{'s' if len(deliveries) > 1 else ''} — {unread} non lu{'s' if unread > 1 else ''}</small>
    </h2>
    <section class="delivery-grid reveal">{cards}</section>
    """


def _client_request_section(
    user: SessionUser,
    client,
    requests,
    errors: list[str] | None = None,
    form: dict[str, str] | None = None,
) -> str:
    form = form or {}
    cards = "".join(_request_card_client(r) for r in requests) or '<p class="form-help">Aucune demande pour le moment.</p>'
    selected_type = form.get("audit_type", "")
    selected_urgency = form.get("urgency", "normal")
    audit_type_options = "".join(
        f'<option value="{key}" {"selected" if key == selected_type else ""}>{label}</option>'
        for key, label in AUDIT_TYPE_LABELS.items()
    )
    urgency_options = "".join(
        f'<option value="{key}" {"selected" if key == selected_urgency else ""}>{label}</option>'
        for key, label in URGENCY_LABELS.items()
    )
    error_html = "".join(f'<div class="notice error">{e(err)}</div>' for err in (errors or []))
    return f"""
    <h2 id="requests" class="section-title reveal">Demandes d'audit</h2>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head">
                <h2>Mes demandes ({len(requests)})</h2>
                <small>Suivez l'état de vos demandes envoyées à YOps</small>
            </div>
            <div class="request-list">{cards}</div>
        </article>
        <form class="panel form-panel" method="post" action="/audit-requests">
            <h2>Nouvelle demande</h2>
            {error_html}
            <label>Type d'audit<select name="audit_type" required>{audit_type_options}</select></label>
            <label>Périmètre (scope)<textarea name="scope" rows="4" placeholder="Quels actifs, URLs, applications ?" required>{e(form.get("scope", ""))}</textarea></label>
            <label>Règles d'engagement<textarea name="rules" rows="3" placeholder="Comptes de test, fenêtre de tir, exclusions, contraintes...">{e(form.get("rules", ""))}</textarea></label>
            <label>Urgence<select name="urgency">{urgency_options}</select></label>
            <label>Date souhaitée<input name="target_date" type="date" value="{e(form.get("target_date", ""))}"></label>
            <button class="primary-button" type="submit"><span>Envoyer la demande</span><span class="button-dot">↗</span></button>
            <p class="form-help">Demandeur : {e(user.name)} - {e(client.name)}</p>
        </form>
    </section>
    """


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
            <label>Téléphone<input name="phone" required></label>
            <input type="hidden" name="status" value="active">
            <button class="primary-button" type="submit"><span>Créer</span><span class="button-dot">↗</span></button>
        </form>
    </section>
    """
    return layout("Clients", user, content, "clients")


NOTE_KINDS = {
    "note": ("Note", "neutral"),
    "contact": ("Contact", "low"),
    "alert": ("Alerte", "critical"),
    "meeting": ("Réunion", "medium"),
}


def _note_icon(kind: str) -> str:
    icons = {"note": "✎", "contact": "✆", "alert": "⚠", "meeting": "◷"}
    return icons.get(kind, "✎")


def client_detail_page(user: SessionUser, client, audits, vulnerabilities, risk, notes=None) -> bytes:
    notes = notes or []
    audit_options = "".join(f'<option value="{audit.id}">{e(audit.title)}</option>' for audit in audits)
    create_vulnerability = ""
    if user.role != "client":
        create_vulnerability = f"""
        <form class="panel form-panel" method="post" action="/vulnerabilities?return_to=/clients/{client.id}">
            <h2>Ajouter une vulnérabilité</h2>
            <label>Audit du client<select name="audit_id">{audit_options}</select></label>
            <label>Titre<input name="title" required></label>
            <label>Description<textarea name="description" required></textarea></label>
            <label>Score CVSS (0-10)<input name="cvss_score" type="number" min="0" max="10" step="0.1" value="7.0" required></label>
            <p class="form-help">La criticité est déduite automatiquement du score (CVSS v3).</p>
            <label>Actif<input name="asset" required></label>
            <label>Preuve<textarea name="evidence" required></textarea></label>
            <label>Recommandation<textarea name="recommendation" required></textarea></label>
            <button class="primary-button" type="submit"><span>Ajouter au client</span><span class="button-dot">↗</span></button>
        </form>
        """
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
            <td>{cvss_chip(vuln.cvss_score)}</td>
        </tr>
        """
        for vuln in sorted(vulnerabilities, key=lambda v: float(v.cvss_score or 0), reverse=True)[:8]
    )
    content = page_header(
        client.name,
        f"{client.sector} - contact {client.contact_name} - {client.email}",
        '<a class="secondary-button" href="/clients">Retour clients</a>',
    )
    content += f"""
    <section class="kpi-grid reveal">
        <article class="kpi-card"><span>Score risque</span><strong data-count="{risk.score}">{risk.score}</strong></article>
        <article class="kpi-card danger"><span>Critiques</span><strong data-count="{risk.critical}">{risk.critical}</strong></article>
        <article class="kpi-card"><span>Hautes</span><strong data-count="{risk.high}">{risk.high}</strong></article>
        <article class="kpi-card"><span>Niveau</span><strong>{e(risk.level)}</strong></article>
    </section>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Audits</h2></div>
            <div class="table-wrap"><table><thead><tr><th>Mission</th><th>Type</th><th>Statut</th><th>Début</th><th>Fin</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
        </article>
        <article class="panel">
            <h2>Fiche client</h2>
            <dl class="detail-list">
                <dt>Secteur</dt><dd>{e(client.sector)}</dd>
                <dt>Contact</dt><dd>{e(client.contact_name)}</dd>
                <dt>Email</dt><dd>{e(client.email)}</dd>
                <dt>Téléphone</dt><dd>{e(client.phone)}</dd>
            </dl>
        </article>
    </section>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="panel-head"><h2>Vulnérabilités principales</h2><a href="/vulnerabilities">Registre complet</a></div>
            <div class="table-wrap"><table><thead><tr><th>Titre</th><th>Criticité</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{vulnerability_rows}</tbody></table></div>
        </article>
        {create_vulnerability}
    </section>
    {_notes_section(user, client, notes)}
    """
    return layout(client.name, user, content, "clients")


def _notes_section(user: SessionUser, client, notes) -> str:
    if user.role == "client":
        return ""
    timeline = "".join(
        f"""
        <li class="timeline-item kind-{e(note.kind)}">
            <span class="timeline-marker" aria-hidden="true">{_note_icon(note.kind)}</span>
            <div class="timeline-body">
                <div class="timeline-meta">
                    <span class="badge badge-{NOTE_KINDS.get(note.kind, ('Note','neutral'))[1]}">{NOTE_KINDS.get(note.kind, ('Note','neutral'))[0]}</span>
                    <strong>{e(note.author_name)}</strong>
                    <small>{e(note.created_at)}</small>
                </div>
                <p>{e(note.body)}</p>
            </div>
        </li>
        """
        for note in notes
    )
    empty = '<li class="timeline-empty">Aucune note pour ce client. Ajoutez le premier suivi ci-contre.</li>'
    options = "".join(
        f'<option value="{key}">{label}</option>' for key, (label, _) in NOTE_KINDS.items()
    )
    return f"""
    <section id="notes" class="split-grid reveal notes-grid">
        <article class="panel panel-wide">
            <div class="panel-head">
                <h2>Suivi & notes</h2>
                <small>{len(notes)} entrée{'s' if len(notes) > 1 else ''}</small>
            </div>
            <ol class="timeline">{timeline or empty}</ol>
        </article>
        <form class="panel form-panel" method="post" action="/clients/{client.id}/notes">
            <h2>Ajouter une note</h2>
            <label>Type<select name="kind">{options}</select></label>
            <label>Contenu<textarea name="body" rows="5" placeholder="Échange, alerte, décision, prochaine étape..." required></textarea></label>
            <button class="primary-button" type="submit"><span>Enregistrer</span><span class="button-dot">↗</span></button>
            <p class="form-help">Auteur : {e(user.name)}</p>
        </form>
    </section>
    """


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
            <td>{e(v.title)}</td><td>{severity_badge(v.severity)}</td><td>{e(v.asset)}</td><td>{status_badge(v.status)}</td><td>{cvss_chip(v.cvss_score)}</td>
        </tr>
        """
        for v in sorted(vulnerabilities, key=lambda v: float(v.cvss_score or 0), reverse=True)
    )
    content = page_header(audit.title, f"{audit.client_name} · {audit.audit_type} · responsable {audit.owner_name}")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Vulnérabilité</th><th>Criticité</th><th>Actif</th><th>Statut</th><th>CVSS</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Audit", user, content, "audits")


def vulnerabilities_page(user: SessionUser, vulnerabilities, audits, clients, query: dict, errors: list[str] | None = None) -> bytes:
    selected_client = query.get("client", "").strip().lower()
    search = query.get("q", "").strip().lower()
    filtered = vulnerabilities
    if selected_client:
        filtered = [v for v in filtered if v.client_name.lower() == selected_client]
    if search:
        filtered = [v for v in filtered if search in v.title.lower() or search in v.asset.lower() or search in v.description.lower()]

    return_to = "/vulnerabilities" + (("?" + urlencode({k: v for k, v in query.items() if v})) if any(query.values()) else "")

    rows = "".join(
        f"""
        <tr>
            <td>
                <strong>{e(v.title)}</strong>
                <small>{e(v.asset)} · {e(v.audit_title)}</small>
            </td>
            <td><a href="/clients/{_client_id_by_name(clients, v.client_name)}">{e(v.client_name)}</a></td>
            <td>{severity_badge(v.severity)}</td>
            <td>{status_badge(v.status)}</td>
            <td>{score_edit_form(v.id, v.cvss_score, return_to)}</td>
            <td class="row-actions">{status_action_form(v.id, v.status, return_to)}</td>
        </tr>
        """
        for v in filtered
    )
    if not rows:
        rows = '<tr><td colspan="6" class="empty-row">Aucune vulnérabilité ne correspond à ces filtres.</td></tr>'

    audit_options_by_client: dict[str, str] = {}
    for audit in audits:
        opt = f'<option value="{audit.id}">{e(audit.title)}</option>'
        audit_options_by_client.setdefault(audit.client_name, "")
        audit_options_by_client[audit.client_name] += opt
    audit_optgroups = "".join(
        f'<optgroup label="{e(client_name)}">{opts}</optgroup>'
        for client_name, opts in sorted(audit_options_by_client.items())
    )

    client_chips = "".join(
        f'<a class="chip {"is-active" if c.name.lower() == selected_client else ""}" href="/vulnerabilities?client={e(c.name)}">{e(c.name)}</a>'
        for c in clients
    )

    error_html = "".join(f'<div class="notice error">{e(error)}</div>' for error in (errors or []))
    filters = urlencode({key: value for key, value in query.items() if value})
    content = page_header(
        "Vulnérabilités",
        f"Registre technique · {len(filtered)} sur {len(vulnerabilities)} affichées.",
        '<a class="primary-button pdf-button" href="/reports/vulnerabilities.pdf"><span>Exporter PDF</span><span class="button-dot">↓</span></a>',
    )
    content += f"""
    <section class="filter-bar reveal">
        <a class="chip {'is-active' if not any(query.values()) else ''}" href="/vulnerabilities">Toutes</a>
        <a class="chip {'is-active' if query.get('severity') == 'critical' else ''}" href="/vulnerabilities?severity=critical">Critiques</a>
        <a class="chip {'is-active' if query.get('severity') == 'high' else ''}" href="/vulnerabilities?severity=high">Hautes</a>
        <a class="chip {'is-active' if query.get('status') == 'ouverte' else ''}" href="/vulnerabilities?status=ouverte">Ouvertes</a>
        <span class="filter-divider"></span>
        {client_chips}
    </section>
    <section class="filter-bar reveal">
        <input class="search-input" type="search" placeholder="Rechercher par titre, actif ou description..." value="{e(query.get('q', ''))}" data-search-target="#vuln-table tbody tr">
    </section>
    <section class="split-grid reveal">
        <article class="panel panel-wide">
            <div class="table-wrap"><table id="vuln-table"><thead><tr><th>Titre</th><th>Client</th><th>Criticité</th><th>Statut</th><th>CVSS</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
        </article>
        <form class="panel form-panel" method="post" action="/vulnerabilities?{filters}">
            <h2>Ajouter</h2>
            {error_html}
            <label>Audit (regroupé par client)<select name="audit_id" required>{audit_optgroups}</select></label>
            <label>Titre<input name="title" required></label>
            <label>Description<textarea name="description" required></textarea></label>
            <label>Score CVSS (0-10)<input name="cvss_score" type="number" min="0" max="10" step="0.1" value="7.0" required></label>
            <p class="form-help">La criticité est déduite automatiquement du score (CVSS v3).</p>
            <label>Actif<input name="asset" required></label>
            <label>Preuve<textarea name="evidence" required></textarea></label>
            <label>Recommandation<textarea name="recommendation" required></textarea></label>
            <button class="primary-button" type="submit"><span>Enregistrer</span><span class="button-dot">↗</span></button>
        </form>
    </section>
    """
    return layout("Vulnérabilités", user, content, "vulnerabilities")


def _client_id_by_name(clients, name: str) -> int:
    for c in clients:
        if c.name == name:
            return c.id
    return 0


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
    content = page_header("Tickets", "Suivi opérationnel des corrections.")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Vulnérabilité</th><th>Priorité</th><th>Assigné</th><th>Échéance</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
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
    content = page_header("Rapports", "Synthèses exploitables pour le client et le management.")
    content += f'<section class="report-grid reveal">{cards}</section>'
    return layout("Rapports", user, content, "reports")


def users_page(user: SessionUser, users) -> bytes:
    rows = "".join(
        f"<tr><td>{e(item.name)}</td><td>{e(item.email)}</td><td>{badge(item.role)}</td><td>{e(item.client_id or '-')}</td></tr>"
        for item in users
    )
    content = page_header("Utilisateurs", "Comptes locaux de démonstration et rôles applicatifs.")
    content += f'<article class="panel reveal"><div class="table-wrap"><table><thead><tr><th>Nom</th><th>Email</th><th>Rôle</th><th>Client</th></tr></thead><tbody>{rows}</tbody></table></div></article>'
    return layout("Utilisateurs", user, content, "admin")


def not_found_page(user: SessionUser | None) -> bytes:
    content = page_header("Page introuvable", "La route demandée n'existe pas.")
    return layout("404", user, content)
