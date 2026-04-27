#!/usr/bin/env python3
"""
Modelo 30 — Gestão de Fornecedores Não Residentes
Base de dados para preenchimento da declaração Modelo 30 (AT Portugal)
"""

import sqlite3
import json
import csv
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "modelo30.db")

TIPOS_RENDIMENTO = {
    "A": "Rendimentos de capitais (dividendos, juros)",
    "B": "Rendimentos prediais",
    "C": "Rendimentos empresariais e profissionais / Serviços",
    "D": "Royalties / Licenças de software",
    "E": "Mais-valias",
    "F": "Pensões",
    "G": "Outros rendimentos",
    "H": "Rendimentos do trabalho dependente",
}

PAISES = {
    "AT": "Áustria",       "BE": "Bélgica",       "BG": "Bulgária",
    "CY": "Chipre",        "CZ": "República Checa","DE": "Alemanha",
    "DK": "Dinamarca",     "EE": "Estónia",        "ES": "Espanha",
    "FI": "Finlândia",     "FR": "França",         "GR": "Grécia",
    "HR": "Croácia",       "HU": "Hungria",        "IE": "Irlanda",
    "IT": "Itália",        "LT": "Lituânia",       "LU": "Luxemburgo",
    "LV": "Letónia",       "MT": "Malta",          "NL": "Países Baixos",
    "PL": "Polónia",       "RO": "Roménia",        "SE": "Suécia",
    "SI": "Eslovénia",     "SK": "Eslováquia",     "GB": "Reino Unido",
    "US": "Estados Unidos","CA": "Canadá",         "AU": "Austrália",
    "CH": "Suíça",         "NO": "Noruega",        "JP": "Japão",
    "CN": "China",         "BR": "Brasil",         "IN": "Índia",
    "SG": "Singapura",     "AE": "Emirados Árabes","MX": "México",
    "ZA": "África do Sul", "IL": "Israel",         "KR": "Coreia do Sul",
    "NZ": "Nova Zelândia", "AR": "Argentina",      "CL": "Chile",
    "CO": "Colômbia",      "MU": "Maurícias",      "HK": "Hong Kong",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nome_comercial TEXT,
            nif_pt TEXT,
            nif_pais TEXT,
            pais_codigo TEXT NOT NULL,
            tipo_rendimento TEXT NOT NULL DEFAULT 'C',
            taxa_cdt REAL DEFAULT 0.0,
            taxa_domestica REAL DEFAULT 25.0,
            percentagem_participacao REAL DEFAULT 0.0,
            categoria TEXT,
            notas TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT (datetime('now')),
            atualizado_em TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor_id INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            valor_bruto REAL NOT NULL,
            taxa_aplicada REAL NOT NULL,
            retencao REAL NOT NULL,
            regime TEXT DEFAULT 'CDT',
            notas TEXT,
            criado_em TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        );

        CREATE INDEX IF NOT EXISTS idx_forn_nome ON fornecedores(nome);
        CREATE INDEX IF NOT EXISTS idx_forn_pais ON fornecedores(pais_codigo);
        CREATE INDEX IF NOT EXISTS idx_pag_forn ON pagamentos(fornecedor_id);
    """)
    conn.commit()
    conn.close()


def seed_fornecedores():
    """Popula com 200 fornecedores não residentes mais comuns em Portugal."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM fornecedores").fetchone()[0]
    if count > 0:
        conn.close()
        return

    fornecedores = [
        # ── PUBLICIDADE & MARKETING ──────────────────────────────────────────
        ("Google Ireland Limited",           "Google Ads / Workspace",  None, "IE6388047V",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Meta Platforms Ireland Limited",   "Facebook / Instagram Ads",None, "IE9692928F",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("LinkedIn Ireland Unlimited Company","LinkedIn Ads / Recruiter",None, "IE6336960T",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Twitter International Company",    "X / Twitter Ads",         None, "IE9803175Q",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("TikTok Technology Limited",        "TikTok Ads",              None, "IE3480548BH", "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Pinterest Europe Limited",         "Pinterest Ads",           None, "IE9832928O",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Snap Group Limited",               "Snapchat Ads",            None, "IE9740782G",  "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Criteo SA",                        "Criteo",                  None, "FR44443577rad","FR","C", 0.0, 25.0, 0.0, "Publicidade Digital"),
        ("Outbrain Ireland Limited",         "Outbrain",                None, None,           "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Taboola Europe Limited",           "Taboola",                 None, None,           "IE", "C", 0.0, 0.0,  0.0, "Publicidade Digital"),
        ("Trade Desk Europe Limited",        "The Trade Desk",          None, None,           "GB", "C", 0.0, 25.0, 0.0, "Publicidade Digital"),
        ("AppLovin Corporation",             "AppLovin",                None, None,           "US", "C", 0.0, 25.0, 0.0, "Publicidade Digital"),
        ("Unity Technologies",              "Unity Ads",               None, None,           "US", "C", 0.0, 25.0, 0.0, "Publicidade Digital"),
        ("Awin AG",                          "Awin Afiliados",          None, None,           "DE", "C", 0.0, 25.0, 0.0, "Publicidade Digital"),
        ("CJ Affiliate by Conversant",      "Commission Junction",     None, None,           "US", "C", 0.0, 25.0, 0.0, "Publicidade Digital"),

        # ── CLOUD & INFRAESTRUTURA ────────────────────────────────────────────
        ("Amazon Web Services EMEA SARL",    "AWS",                     None, "LU24560133",   "LU", "C", 0.0, 0.0,  0.0, "Cloud"),
        ("Microsoft Ireland Operations Ltd","Azure / M365",            None, "IE8256796U",   "IE", "D", 0.0, 0.0,  0.0, "Cloud"),
        ("Google Cloud EMEA Limited",        "Google Cloud",            None, "IE6388047V",   "IE", "C", 0.0, 0.0,  0.0, "Cloud"),
        ("OVH SAS",                          "OVH Cloud",               None, "FR22424761480","FR", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("DigitalOcean LLC",                 "DigitalOcean",            None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Hetzner Online GmbH",              "Hetzner",                 None, "DE812871812",  "DE", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Cloudflare Inc",                   "Cloudflare",              None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Fastly Inc",                       "Fastly CDN",              None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Akamai Technologies Ltd",          "Akamai CDN",              None, "IE9728919J",   "IE", "C", 0.0, 0.0,  0.0, "Cloud"),
        ("Rackspace International GmbH",     "Rackspace",               None, None,           "DE", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("IBM Cloud",                        "IBM Cloud",               None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Oracle Corporation Ireland Ltd",   "Oracle Cloud",            None, "IE6556167Q",   "IE", "C", 0.0, 0.0,  0.0, "Cloud"),
        ("Vultr Holdings LLC",               "Vultr",                   None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Linode LLC (Akamai)",              "Linode",                  None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Vercel Inc",                       "Vercel",                  None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),
        ("Netlify Inc",                      "Netlify",                 None, None,           "US", "C", 0.0, 25.0, 0.0, "Cloud"),

        # ── SOFTWARE & SAAS ───────────────────────────────────────────────────
        ("Salesforce.com EMEA Limited",      "Salesforce CRM",          None, "IE9795582K",   "IE", "D", 0.0, 0.0,  0.0, "SaaS CRM"),
        ("HubSpot Ireland Limited",          "HubSpot",                 None, "IE9849258T",   "IE", "D", 0.0, 0.0,  0.0, "SaaS CRM"),
        ("Zendesk International Ltd",        "Zendesk",                 None, "IE9782684F",   "IE", "D", 0.0, 0.0,  0.0, "SaaS CRM"),
        ("Intercom R&D Unlimited Company",   "Intercom",                None, "IE9517876T",   "IE", "D", 0.0, 0.0,  0.0, "SaaS CRM"),
        ("Pipedrive OÜ",                     "Pipedrive",               None, None,           "EE", "D", 0.0, 25.0, 0.0, "SaaS CRM"),
        ("Zoom Video Communications Inc",    "Zoom",                    None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Comunicação"),
        ("Slack Technologies LLC",           "Slack",                   None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Comunicação"),
        ("Atlassian Network Services Inc",   "Jira / Confluence",       None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Gestão Projeto"),
        ("Asana Inc",                        "Asana",                   None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Gestão Projeto"),
        ("Monday.com Ltd",                   "Monday.com",              None, None,           "IL", "D", 0.0, 25.0, 0.0, "SaaS Gestão Projeto"),
        ("Notion Labs Inc",                  "Notion",                  None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Gestão Projeto"),
        ("Trello (Atlassian)",               "Trello",                  None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Gestão Projeto"),
        ("Adobe Systems Software Ireland Ltd","Adobe Creative Cloud",   None, "IE4116560EH",  "IE", "D", 0.0, 0.0,  0.0, "SaaS Design"),
        ("Figma Inc",                        "Figma",                   None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Design"),
        ("Canva Pty Ltd",                    "Canva",                   None, None,           "AU", "D", 0.0, 25.0, 0.0, "SaaS Design"),
        ("Sketch BV",                        "Sketch",                  None, None,           "NL", "D", 0.0, 25.0, 0.0, "SaaS Design"),
        ("InVision App Inc",                 "InVision",                None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Design"),
        ("Miro (RealtimeBoard Inc)",         "Miro",                    None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Colaboração"),
        ("Loom Inc",                         "Loom",                    None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Colaboração"),
        ("Dropbox International Unlimited Co","Dropbox",                None, "IE9749486E",   "IE", "D", 0.0, 0.0,  0.0, "SaaS Armazenamento"),
        ("Box Inc",                          "Box",                     None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Armazenamento"),
        ("DocuSign Inc",                     "DocuSign",                None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Documentos"),
        ("Adobe Sign",                       "Adobe Sign (eSign)",      None, "IE4116560EH",  "IE", "D", 0.0, 0.0,  0.0, "SaaS Documentos"),
        ("HelloSign Inc (Dropbox)",          "HelloSign",               None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Documentos"),
        ("PandaDoc Inc",                     "PandaDoc",                None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Documentos"),
        ("Typeform SL",                      "Typeform",                None, None,           "ES", "D", 0.0, 25.0, 0.0, "SaaS Formulários"),
        ("SurveyMonkey Europe UC",           "SurveyMonkey",            None, "IE9812226M",   "IE", "D", 0.0, 0.0,  0.0, "SaaS Formulários"),
        ("Twilio Ireland Limited",           "Twilio SMS/Voice",        None, "IE3369296UH",  "IE", "C", 0.0, 0.0,  0.0, "SaaS Comunicação"),
        ("SendGrid (Twilio)",                "SendGrid Email",          None, None,           "US", "C", 0.0, 25.0, 0.0, "SaaS Email"),
        ("Mailchimp (Intuit)",               "Mailchimp",               None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Email Marketing"),
        ("Mailgun Technologies Inc",         "Mailgun",                 None, None,           "US", "C", 0.0, 25.0, 0.0, "SaaS Email"),
        ("ActiveCampaign LLC",               "ActiveCampaign",          None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Email Marketing"),
        ("Brevo (Sendinblue)",               "Brevo",                   None, None,           "FR", "D", 0.0, 25.0, 0.0, "SaaS Email Marketing"),
        ("Klaviyo Inc",                      "Klaviyo",                 None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Email Marketing"),
        ("Shopify International Limited",    "Shopify",                 None, "IE3347808LH",  "IE", "D", 0.0, 0.0,  0.0, "SaaS E-commerce"),
        ("WooCommerce (Automattic)",         "WooCommerce",             None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS E-commerce"),
        ("BigCommerce Pty Ltd",              "BigCommerce",             None, None,           "AU", "D", 0.0, 25.0, 0.0, "SaaS E-commerce"),
        ("PrestaShop SA",                    "PrestaShop",              None, None,           "FR", "D", 0.0, 25.0, 0.0, "SaaS E-commerce"),
        ("Hotjar Limited",                   "Hotjar Analytics",        None, "MT2562645",    "MT", "D", 0.0, 25.0, 0.0, "SaaS Analytics"),
        ("Mixpanel Inc",                     "Mixpanel",                None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Analytics"),
        ("Amplitude Inc",                    "Amplitude",               None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Analytics"),
        ("Segment.io Inc (Twilio)",          "Segment",                 None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Analytics"),
        ("Datadog Inc",                      "Datadog",                 None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Monitoring"),
        ("New Relic Inc",                    "New Relic",               None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Monitoring"),
        ("Sentry IO Inc",                    "Sentry",                  None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Monitoring"),
        ("PagerDuty Inc",                    "PagerDuty",               None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Monitoring"),
        ("GitHub Inc (Microsoft)",           "GitHub",                  None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),
        ("GitLab Inc",                       "GitLab",                  None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),
        ("CircleCI LLC",                     "CircleCI",                None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),
        ("Postman Inc",                      "Postman",                 None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),
        ("JetBrains s.r.o.",                 "JetBrains IDEs",          None, None,           "CZ", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),
        ("Netlify Inc",                      "Netlify Forms/Functions", None, None,           "US", "D", 0.0, 25.0, 0.0, "SaaS Desenvolvimento"),

        # ── PAGAMENTOS & FINTECH ──────────────────────────────────────────────
        ("Stripe Payments Europe Ltd",       "Stripe",                  None, "IE3206488LH",  "IE", "C", 0.0, 0.0,  0.0, "Pagamentos"),
        ("PayPal (Europe) SARL et Cie SCA",  "PayPal",                  None, "LU22046007",   "LU", "C", 0.0, 0.0,  0.0, "Pagamentos"),
        ("Adyen NV",                         "Adyen",                   None, "NL849699515B01","NL","C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Mollie BV",                        "Mollie",                  None, "NL818848558B01","NL","C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Square Ireland Limited",           "Square / Block",          None, "IE9940741G",   "IE", "C", 0.0, 0.0,  0.0, "Pagamentos"),
        ("GoCardless Ltd",                   "GoCardless",              None, "GB07495895",    "GB", "C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Wise Payments Limited",            "Wise (Transferwise)",     None, "GB7081744",     "GB", "C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Revolut Ltd",                      "Revolut Business",        None, "GB791762755",   "GB", "C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Sumup Payments Limited",           "SumUp",                   None, "IE9820906T",    "IE", "C", 0.0, 0.0,  0.0, "Pagamentos"),
        ("Chargebee Inc",                    "Chargebee",               None, None,            "US", "C", 0.0, 25.0, 0.0, "Pagamentos"),
        ("Paddle.com Market Ltd",            "Paddle",                  None, "GB154218234",   "GB", "C", 0.0, 25.0, 0.0, "Pagamentos"),

        # ── INTELIGÊNCIA ARTIFICIAL ───────────────────────────────────────────
        ("Anthropic PBC",                    "Claude AI",               None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("OpenAI Ireland Ltd",               "OpenAI / ChatGPT",        None, "IE3656082TH",   "IE", "D", 0.0, 0.0,  0.0, "IA"),
        ("OpenAI LLC",                       "OpenAI API",              None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("Mistral AI SAS",                   "Mistral AI",              None, None,            "FR", "D", 0.0, 25.0, 0.0, "IA"),
        ("Cohere Inc",                       "Cohere",                  None, None,            "CA", "D", 0.0, 25.0, 0.0, "IA"),
        ("Scale AI Inc",                     "Scale AI",                None, None,            "US", "C", 0.0, 25.0, 0.0, "IA"),
        ("Jasper AI",                        "Jasper",                  None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("Copy.ai Inc",                      "Copy.ai",                 None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("ElevenLabs Inc",                   "ElevenLabs",              None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("Midjourney Inc",                   "Midjourney",              None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("Runway ML Inc",                    "Runway AI",               None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),
        ("Stability AI Ltd",                 "Stable Diffusion",        None, "GB13652753",    "GB", "D", 0.0, 25.0, 0.0, "IA"),
        ("Perplexity AI Inc",                "Perplexity",              None, None,            "US", "D", 0.0, 25.0, 0.0, "IA"),

        # ── SEGURANÇA & COMPLIANCE ────────────────────────────────────────────
        ("Crowdstrike Holdings Inc",         "CrowdStrike Falcon",      None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("SentinelOne Inc",                  "SentinelOne",             None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Palo Alto Networks Inc",           "Palo Alto / Cortex",      None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Tenable Inc",                      "Tenable / Nessus",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Qualys Inc",                       "Qualys",                  None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Rapid7 Inc",                       "Rapid7 InsightVM",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("KnowBe4 Inc",                      "KnowBe4 Awareness",       None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Proofpoint Inc",                   "Proofpoint Email",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Vanta Inc",                        "Vanta Compliance",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Compliance"),
        ("Drata Inc",                        "Drata",                   None, None,            "US", "D", 0.0, 25.0, 0.0, "Compliance"),
        ("OneTrust LLC",                     "OneTrust Privacy",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Compliance"),
        ("Varonis Systems Inc",              "Varonis",                 None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("1Password Ltd",                    "1Password",               None, "IE3728285BH",   "IE", "D", 0.0, 0.0,  0.0, "Cibersegurança"),
        ("Bitwarden Inc",                    "Bitwarden",               None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("NordVPN (NordVPN s.a.)",           "NordVPN",                 None, "LT100011962114","LT", "D", 0.0, 25.0, 0.0, "Cibersegurança"),
        ("Cloudflare Inc",                   "Cloudflare Zero Trust",   None, None,            "US", "D", 0.0, 25.0, 0.0, "Cibersegurança"),

        # ── ERP / CONTABILIDADE / RH ──────────────────────────────────────────
        ("SAP SE",                           "SAP ERP",                 None, "DE114103470",   "DE", "D", 0.0, 25.0, 0.0, "ERP"),
        ("Oracle Corporation Ireland Ltd",   "Oracle ERP",              None, "IE6556167Q",    "IE", "D", 0.0, 0.0,  0.0, "ERP"),
        ("Sage Group PLC",                   "Sage",                    None, "GB733849219",   "GB", "D", 0.0, 25.0, 0.0, "ERP"),
        ("Xero Limited",                     "Xero",                    None, None,            "NZ", "D", 0.0, 25.0, 0.0, "Contabilidade"),
        ("QuickBooks (Intuit)",              "QuickBooks",              None, None,            "US", "D", 0.0, 25.0, 0.0, "Contabilidade"),
        ("Workday Inc",                      "Workday HCM",             None, None,            "US", "D", 0.0, 25.0, 0.0, "RH"),
        ("BambooHR LLC",                     "BambooHR",                None, None,            "US", "D", 0.0, 25.0, 0.0, "RH"),
        ("Personio SE & Co KG",              "Personio HR",             None, None,            "DE", "D", 0.0, 25.0, 0.0, "RH"),
        ("Factorial HR SL",                  "Factorial",               None, None,            "ES", "D", 0.0, 25.0, 0.0, "RH"),
        ("Hibob Ltd",                        "HiBob",                   None, None,            "IL", "D", 0.0, 25.0, 0.0, "RH"),
        ("Deel Inc",                         "Deel Payroll",            None, None,            "US", "C", 0.0, 25.0, 0.0, "RH / Payroll"),
        ("Remote Technology Inc",            "Remote.com",              None, None,            "US", "C", 0.0, 25.0, 0.0, "RH / Payroll"),
        ("Rippling Inc",                     "Rippling",                None, None,            "US", "D", 0.0, 25.0, 0.0, "RH"),

        # ── MARKETPLACE & PLATAFORMAS ─────────────────────────────────────────
        ("Amazon Services Europe SARL",      "Amazon Marketplace",      None, "LU20260743",    "LU", "C", 0.0, 0.0,  0.0, "Marketplace"),
        ("eBay Europe SARL",                 "eBay",                    None, "LU21416127",    "LU", "C", 0.0, 0.0,  0.0, "Marketplace"),
        ("Etsy Ireland UC",                  "Etsy",                    None, "IE3346135OG",   "IE", "C", 0.0, 0.0,  0.0, "Marketplace"),
        ("Booking.com BV",                   "Booking.com",             None, "NL805734958B01","NL", "C", 0.0, 25.0, 0.0, "Marketplace"),
        ("Airbnb Ireland UC",                "Airbnb",                  None, "IE9807855G",    "IE", "C", 0.0, 0.0,  0.0, "Marketplace"),
        ("Upwork Global Inc",                "Upwork",                  None, None,            "US", "C", 0.0, 25.0, 0.0, "Marketplace Freelance"),
        ("Fiverr International Ltd",         "Fiverr",                  None, None,            "IL", "C", 0.0, 25.0, 0.0, "Marketplace Freelance"),
        ("Toptal LLC",                       "Toptal",                  None, None,            "US", "C", 0.0, 25.0, 0.0, "Marketplace Freelance"),

        # ── DOMÍNIOS, HOSTING & SSL ───────────────────────────────────────────
        ("GoDaddy.com LLC",                  "GoDaddy",                 None, None,            "US", "C", 0.0, 25.0, 0.0, "Domínios"),
        ("Namecheap Inc",                    "Namecheap",               None, None,            "US", "C", 0.0, 25.0, 0.0, "Domínios"),
        ("Gandi SAS",                        "Gandi",                   None, None,            "FR", "C", 0.0, 25.0, 0.0, "Domínios"),
        ("Registrar.eu (Eurid)",             "Registrar.eu",            None, None,            "BE", "C", 0.0, 25.0, 0.0, "Domínios"),
        ("WPEngine Inc",                     "WP Engine Hosting",       None, None,            "US", "C", 0.0, 25.0, 0.0, "Hosting"),
        ("Kinsta Inc",                       "Kinsta",                  None, None,            "US", "C", 0.0, 25.0, 0.0, "Hosting"),
        ("SiteGround Ltd",                   "SiteGround",              None, "BG131457471",   "BG", "C", 0.0, 25.0, 0.0, "Hosting"),
        ("Sectigo Limited",                  "Sectigo SSL",             None, "GB6690527",     "GB", "C", 0.0, 25.0, 0.0, "SSL"),
        ("DigiCert Inc",                     "DigiCert SSL",            None, None,            "US", "C", 0.0, 25.0, 0.0, "SSL"),

        # ── CONTEÚDO, MEDIA & STOCK ───────────────────────────────────────────
        ("Getty Images Inc",                 "Getty Images",            None, None,            "US", "D", 0.0, 25.0, 0.0, "Stock Media"),
        ("Shutterstock Inc",                 "Shutterstock",            None, None,            "US", "D", 0.0, 25.0, 0.0, "Stock Media"),
        ("Adobe Stock (Adobe)",              "Adobe Stock",             None, "IE4116560EH",   "IE", "D", 0.0, 0.0,  0.0, "Stock Media"),
        ("iStockphoto LP",                   "iStock",                  None, None,            "US", "D", 0.0, 25.0, 0.0, "Stock Media"),
        ("Envato Pty Ltd",                   "Envato Elements",         None, None,            "AU", "D", 0.0, 25.0, 0.0, "Stock Media"),
        ("Freepik Company SL",               "Freepik",                 None, None,            "ES", "D", 0.0, 25.0, 0.0, "Stock Media"),
        ("Spotify AB",                       "Spotify for Podcasters",  None, "SE556703748501","SE", "D", 0.0, 25.0, 0.0, "Audio"),
        ("SoundCloud Limited",               "SoundCloud",              None, "IE9696793K",    "IE", "D", 0.0, 0.0,  0.0, "Audio"),
        ("Vimeo Inc",                        "Vimeo",                   None, None,            "US", "D", 0.0, 25.0, 0.0, "Vídeo"),
        ("Wistia Inc",                       "Wistia",                  None, None,            "US", "D", 0.0, 25.0, 0.0, "Vídeo"),

        # ── FORMAÇÃO & E-LEARNING ─────────────────────────────────────────────
        ("Udemy Inc",                        "Udemy",                   None, None,            "US", "D", 0.0, 25.0, 0.0, "E-Learning"),
        ("Coursera Inc",                     "Coursera",                None, None,            "US", "D", 0.0, 25.0, 0.0, "E-Learning"),
        ("LinkedIn Learning (Microsoft)",    "LinkedIn Learning",       None, "IE8256796U",    "IE", "D", 0.0, 0.0,  0.0, "E-Learning"),
        ("Pluralsight LLC",                  "Pluralsight",             None, None,            "US", "D", 0.0, 25.0, 0.0, "E-Learning"),
        ("Skillshare Inc",                   "Skillshare",              None, None,            "US", "D", 0.0, 25.0, 0.0, "E-Learning"),
        ("Teachable Inc",                    "Teachable",               None, None,            "US", "D", 0.0, 25.0, 0.0, "E-Learning"),
        ("Thinkific Labs Inc",               "Thinkific",               None, None,            "CA", "D", 0.0, 25.0, 0.0, "E-Learning"),

        # ── LOGÍSTICA & TRANSPORTE ────────────────────────────────────────────
        ("FedEx Express (FedEx Corp)",       "FedEx",                   None, None,            "US", "C", 0.0, 25.0, 0.0, "Logística"),
        ("United Parcel Service Inc",        "UPS",                     None, None,            "US", "C", 0.0, 25.0, 0.0, "Logística"),
        ("DHL International GmbH",           "DHL Express",             None, "DE811267577",   "DE", "C", 0.0, 25.0, 0.0, "Logística"),
        ("Maersk A/S",                       "Maersk Shipping",         None, "DK22756214",    "DK", "C", 0.0, 25.0, 0.0, "Logística"),
        ("Uber Technologies Inc",            "Uber Eats / Business",    None, None,            "US", "C", 0.0, 25.0, 0.0, "Transporte"),

        # ── CONSULTORIA & SERVIÇOS PROFISSIONAIS ─────────────────────────────
        ("Accenture Holdings PLC",           "Accenture",               None, "IE317425",      "IE", "C", 0.0, 0.0,  0.0, "Consultoria"),
        ("McKinsey & Company Inc",           "McKinsey",                None, None,            "US", "C", 0.0, 25.0, 0.0, "Consultoria"),
        ("Deloitte Touche Tohmatsu Ltd",     "Deloitte",                None, "GB195560",      "GB", "C", 0.0, 25.0, 0.0, "Auditoria"),
        ("PricewaterhouseCoopers Intl Ltd",  "PwC",                     None, "GB676278",      "GB", "C", 0.0, 25.0, 0.0, "Auditoria"),
        ("Ernst & Young Global Limited",     "EY",                      None, "GB660047",      "GB", "C", 0.0, 25.0, 0.0, "Auditoria"),
        ("KPMG International Ltd",           "KPMG",                    None, "CH660-0165955-0","CH","C", 0.0, 25.0, 0.0, "Auditoria"),
        ("Gartner Inc",                      "Gartner Research",        None, None,            "US", "D", 0.0, 25.0, 0.0, "Consultoria"),
        ("IDC Europe",                       "IDC Research",            None, None,            "GB", "D", 0.0, 25.0, 0.0, "Consultoria"),

        # ── TELECOMUNICAÇÕES ──────────────────────────────────────────────────
        ("Twilio Ireland Limited",           "Twilio WhatsApp API",     None, "IE3369296UH",   "IE", "C", 0.0, 0.0,  0.0, "Telecomunicações"),
        ("MessageBird BV",                   "MessageBird / Bird",      None, "NL857286986B01","NL", "C", 0.0, 25.0, 0.0, "Telecomunicações"),
        ("Vonage Holdings Corp",             "Vonage",                  None, None,            "US", "C", 0.0, 25.0, 0.0, "Telecomunicações"),
        ("Bandwidth Inc",                    "Bandwidth",               None, None,            "US", "C", 0.0, 25.0, 0.0, "Telecomunicações"),
        ("Plivo Inc",                        "Plivo SMS",               None, None,            "US", "C", 0.0, 25.0, 0.0, "Telecomunicações"),

        # ── IMOBILIÁRIO & GESTÃO ──────────────────────────────────────────────
        ("CBRE Group Inc",                   "CBRE",                    None, None,            "US", "C", 0.0, 25.0, 0.0, "Imobiliário"),
        ("JLL (Jones Lang LaSalle Inc)",     "JLL",                     None, None,            "US", "C", 0.0, 25.0, 0.0, "Imobiliário"),
        ("WeWork Companies LLC",             "WeWork Coworking",        None, None,            "US", "C", 0.0, 25.0, 0.0, "Coworking"),
        ("Regus (IWG PLC)",                  "Regus Coworking",         None, "CH550.1.051.110-4","CH","C", 0.0, 25.0, 0.0, "Coworking"),

        # ── LEGAL & PROPRIEDADE INTELECTUAL ──────────────────────────────────
        ("Legalzoom.com Inc",                "LegalZoom",               None, None,            "US", "C", 0.0, 25.0, 0.0, "Legal"),
        ("Ironclad Inc",                     "Ironclad Contracts",      None, None,            "US", "D", 0.0, 25.0, 0.0, "Legal"),
        ("ContractPodAi Ltd",                "ContractPodAi",           None, "GB203987640",   "GB", "D", 0.0, 25.0, 0.0, "Legal"),

        # ── RESEARCH & DADOS ──────────────────────────────────────────────────
        ("Semrush Inc",                      "SEMrush",                 None, None,            "US", "D", 0.0, 25.0, 0.0, "SEO / Dados"),
        ("Ahrefs Pte Ltd",                   "Ahrefs",                  None, None,            "SG", "D", 0.0, 25.0, 0.0, "SEO / Dados"),
        ("Moz Inc",                          "Moz SEO",                 None, None,            "US", "D", 0.0, 25.0, 0.0, "SEO / Dados"),
        ("SimilarWeb Ltd",                   "SimilarWeb",              None, None,            "IL", "D", 0.0, 25.0, 0.0, "SEO / Dados"),
        ("Statista GmbH",                    "Statista",                None, "DE813755624",   "DE", "D", 0.0, 25.0, 0.0, "Dados / Research"),
        ("Nielsen Holdings PLC",             "Nielsen",                 None, "GB625734",      "GB", "D", 0.0, 25.0, 0.0, "Dados / Research"),
        ("Dun & Bradstreet Corp",            "D&B",                     None, None,            "US", "D", 0.0, 25.0, 0.0, "Dados / Research"),
        ("Bombora Inc",                      "Bombora Intent Data",     None, None,            "US", "D", 0.0, 25.0, 0.0, "Dados / Research"),

        # ── SUPPLY CHAIN & PROCUREMENT ────────────────────────────────────────
        ("SAP Ariba (SAP SE)",               "SAP Ariba",               None, "DE114103470",   "DE", "D", 0.0, 25.0, 0.0, "Procurement"),
        ("Coupa Software Inc",               "Coupa",                   None, None,            "US", "D", 0.0, 25.0, 0.0, "Procurement"),
        ("Ivalua Inc",                       "Ivalua",                  None, None,            "US", "D", 0.0, 25.0, 0.0, "Procurement"),

        # ── TRAVEL & EXPENSES ─────────────────────────────────────────────────
        ("TravelPerk Technologies SL",       "TravelPerk",              None, None,            "ES", "C", 0.0, 25.0, 0.0, "Viagens"),
        ("Expensify Inc",                    "Expensify",               None, None,            "US", "D", 0.0, 25.0, 0.0, "Despesas"),
        ("SAP Concur (SAP SE)",              "SAP Concur Travel",       None, "DE114103470",   "DE", "D", 0.0, 25.0, 0.0, "Viagens"),
        ("Booking Holdings Inc",             "Booking Holdings",        None, None,            "US", "C", 0.0, 25.0, 0.0, "Viagens"),
        ("Navan (TripActions Inc)",          "Navan",                   None, None,            "US", "D", 0.0, 25.0, 0.0, "Viagens"),

        # ── SUPORTE & ATENDIMENTO ─────────────────────────────────────────────
        ("Freshworks Inc",                   "Freshdesk",               None, None,            "US", "D", 0.0, 25.0, 0.0, "Suporte"),
        ("Help Scout PBC",                   "Help Scout",              None, None,            "US", "D", 0.0, 25.0, 0.0, "Suporte"),
        ("Drift Inc (Salesloft)",             "Drift Chat",              None, None,            "US", "D", 0.0, 25.0, 0.0, "Suporte"),
        ("Tidio Ltd",                        "Tidio",                   None, None,            "PL", "D", 0.0, 25.0, 0.0, "Suporte"),
        ("LiveChat Inc",                     "LiveChat",                None, None,            "PL", "D", 0.0, 25.0, 0.0, "Suporte"),
        ("Crisp IM SARL",                    "Crisp Chat",              None, None,            "FR", "D", 0.0, 25.0, 0.0, "Suporte"),

        # ── OUTROS ───────────────────────────────────────────────────────────
        ("Apple Distribution International","Apple App Store",          None, "IE9700053D",    "IE", "C", 0.0, 0.0,  0.0, "App Store"),
        ("Google Payment Ireland Ltd",       "Google Play Store",       None, "IE6388047V",    "IE", "C", 0.0, 0.0,  0.0, "App Store"),
        ("Spotify AB",                       "Spotify Podcast Ads",     None, "SE556703748501","SE", "C", 0.0, 25.0, 0.0, "Publicidade Audio"),
        ("Wix.com Ltd",                      "Wix",                     None, None,            "IL", "D", 0.0, 25.0, 0.0, "Website Builder"),
        ("Squarespace Inc",                  "Squarespace",             None, None,            "US", "D", 0.0, 25.0, 0.0, "Website Builder"),
        ("Webflow Inc",                      "Webflow",                 None, None,            "US", "D", 0.0, 25.0, 0.0, "Website Builder"),
        ("Tawk.to Ltd",                      "Tawk.to",                 None, "IE3369278OH",   "IE", "D", 0.0, 0.0,  0.0, "Live Chat"),
        ("Stripe Inc (Stripe Atlas)",        "Stripe Atlas",            None, None,            "US", "C", 0.0, 25.0, 0.0, "Serviços Empresa"),
        ("Wise Business",                    "Wise Business",           None, "GB791762755",   "GB", "C", 0.0, 25.0, 0.0, "Fintech"),
        ("Xolo OÜ",                          "Xolo (Estonia)",          None, None,            "EE", "C", 0.0, 25.0, 0.0, "Serviços Empresa"),
        ("Mercury Technologies Inc",         "Mercury Bank",            None, None,            "US", "C", 0.0, 25.0, 0.0, "Fintech"),
        ("Brex Inc",                         "Brex",                    None, None,            "US", "C", 0.0, 25.0, 0.0, "Fintech"),
        ("Ramp Business Corp",               "Ramp",                    None, None,            "US", "C", 0.0, 25.0, 0.0, "Fintech"),
        ("Pleo Technologies A/S",            "Pleo",                    None, "DK37862097",    "DK", "C", 0.0, 25.0, 0.0, "Fintech"),
        ("Spendesk SAS",                     "Spendesk",                None, None,            "FR", "C", 0.0, 25.0, 0.0, "Fintech"),
    ]

    conn.executemany("""
        INSERT INTO fornecedores
          (nome, nome_comercial, nif_pt, nif_pais, pais_codigo, tipo_rendimento,
           taxa_cdt, taxa_domestica, percentagem_participacao, categoria)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fornecedores)
    conn.commit()
    conn.close()
    print(f"✓ {len(fornecedores)} fornecedores carregados.")


# ─────────────────────────────────────────────────────────────────────────────
# OPERAÇÕES CRUD
# ─────────────────────────────────────────────────────────────────────────────

def listar_fornecedores(filtro: str = "", pais: str = "", categoria: str = ""):
    conn = get_db()
    query = "SELECT * FROM fornecedores WHERE ativo=1"
    params = []
    if filtro:
        query += " AND (nome LIKE ? OR nome_comercial LIKE ?)"
        params += [f"%{filtro}%", f"%{filtro}%"]
    if pais:
        query += " AND pais_codigo = ?"
        params.append(pais.upper())
    if categoria:
        query += " AND categoria LIKE ?"
        params.append(f"%{categoria}%")
    query += " ORDER BY nome"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def buscar_fornecedor(id_ou_nome: str):
    conn = get_db()
    try:
        fid = int(id_ou_nome)
        row = conn.execute("SELECT * FROM fornecedores WHERE id=?", (fid,)).fetchone()
    except ValueError:
        row = conn.execute(
            "SELECT * FROM fornecedores WHERE nome LIKE ? OR nome_comercial LIKE ? LIMIT 1",
            (f"%{id_ou_nome}%", f"%{id_ou_nome}%")
        ).fetchone()
    conn.close()
    return row


def adicionar_fornecedor(dados: dict) -> int:
    conn = get_db()
    c = conn.execute("""
        INSERT INTO fornecedores
          (nome, nome_comercial, nif_pt, nif_pais, pais_codigo, tipo_rendimento,
           taxa_cdt, taxa_domestica, percentagem_participacao, categoria, notas)
        VALUES (:nome, :nome_comercial, :nif_pt, :nif_pais, :pais_codigo,
                :tipo_rendimento, :taxa_cdt, :taxa_domestica,
                :percentagem_participacao, :categoria, :notas)
    """, dados)
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def atualizar_fornecedor(fid: int, dados: dict):
    dados["id"] = fid
    dados["agora"] = datetime.now().isoformat()
    conn = get_db()
    conn.execute("""
        UPDATE fornecedores SET
          nome=:nome, nome_comercial=:nome_comercial, nif_pt=:nif_pt,
          nif_pais=:nif_pais, pais_codigo=:pais_codigo,
          tipo_rendimento=:tipo_rendimento, taxa_cdt=:taxa_cdt,
          taxa_domestica=:taxa_domestica,
          percentagem_participacao=:percentagem_participacao,
          categoria=:categoria, notas=:notas, atualizado_em=:agora
        WHERE id=:id
    """, dados)
    conn.commit()
    conn.close()


def desativar_fornecedor(fid: int):
    conn = get_db()
    conn.execute("UPDATE fornecedores SET ativo=0 WHERE id=?", (fid,))
    conn.commit()
    conn.close()


def registar_pagamento(dados: dict) -> int:
    retencao = round(dados["valor_bruto"] * dados["taxa_aplicada"] / 100, 2)
    dados["retencao"] = retencao
    conn = get_db()
    c = conn.execute("""
        INSERT INTO pagamentos
          (fornecedor_id, ano, mes, valor_bruto, taxa_aplicada, retencao, regime, notas)
        VALUES (:fornecedor_id, :ano, :mes, :valor_bruto, :taxa_aplicada,
                :retencao, :regime, :notas)
    """, dados)
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def listar_pagamentos(ano: int = None, mes: int = None, fornecedor_id: int = None):
    conn = get_db()
    query = """
        SELECT p.*, f.nome, f.nome_comercial, f.pais_codigo, f.tipo_rendimento
        FROM pagamentos p
        JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE 1=1
    """
    params = []
    if ano:
        query += " AND p.ano=?"; params.append(ano)
    if mes:
        query += " AND p.mes=?"; params.append(mes)
    if fornecedor_id:
        query += " AND p.fornecedor_id=?"; params.append(fornecedor_id)
    query += " ORDER BY p.ano DESC, p.mes DESC, f.nome"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def exportar_modelo30(ano: int, mes: int, ficheiro: str = None):
    """Exporta CSV para preenchimento do Modelo 30."""
    pagamentos = listar_pagamentos(ano=ano, mes=mes)
    if ficheiro is None:
        ficheiro = f"modelo30_{ano}_{mes:02d}.csv"
    with open(ficheiro, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([
            "ID", "NIF_Beneficiario_PT", "NIF_Pais_Residencia",
            "Pais_Codigo", "Tipo_Rendimento", "Valor_Bruto_EUR",
            "Taxa_Retencao_%", "Valor_Retencao_EUR", "Regime",
            "Participacao_%", "Nome_Fornecedor", "Notas"
        ])
        for p in pagamentos:
            conn = get_db()
            forn = conn.execute("SELECT * FROM fornecedores WHERE id=?",
                                (p["fornecedor_id"],)).fetchone()
            conn.close()
            w.writerow([
                p["id"],
                forn["nif_pt"] or "",
                forn["nif_pais"] or "",
                forn["pais_codigo"],
                forn["tipo_rendimento"],
                f"{p['valor_bruto']:.2f}".replace(".", ","),
                f"{p['taxa_aplicada']:.2f}".replace(".", ","),
                f"{p['retencao']:.2f}".replace(".", ","),
                p["regime"],
                f"{forn['percentagem_participacao']:.2f}".replace(".", ","),
                forn["nome"],
                p["notas"] or "",
            ])
    return ficheiro, len(pagamentos)


def exportar_fornecedores_json(ficheiro: str = "fornecedores_export.json"):
    conn = get_db()
    rows = conn.execute("SELECT * FROM fornecedores WHERE ativo=1 ORDER BY nome").fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    with open(ficheiro, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return ficheiro, len(data)


# ─────────────────────────────────────────────────────────────────────────────
# CLI INTERACTIVO
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_row(f) -> str:
    pais_nome = PAISES.get(f["pais_codigo"], f["pais_codigo"])
    nif = f["nif_pais"] or "—"
    cat = f["categoria"] or "—"
    return (f"  [{f['id']:>4}] {f['nome'][:45]:<46} | {f['pais_codigo']} {pais_nome[:14]:<15}"
            f"| NIF: {nif[:20]:<21}| Tipo:{f['tipo_rendimento']} | {cat}")


def menu_listar():
    print("\n── LISTAR FORNECEDORES ──")
    filtro = input("Filtro de nome (Enter para todos): ").strip()
    pais   = input("Código país ISO (ex: IE, US – Enter para todos): ").strip()
    cat    = input("Categoria (ex: Cloud, IA – Enter para todos): ").strip()
    rows   = listar_fornecedores(filtro, pais, cat)
    if not rows:
        print("Sem resultados."); return
    print(f"\n{'ID':>6}  {'Nome':45} {'País':18} {'NIF País':21} Tipo  Categoria")
    print("─" * 120)
    for r in rows:
        print(_fmt_row(r))
    print(f"\nTotal: {len(rows)} fornecedores")


def menu_detalhe():
    print("\n── DETALHE FORNECEDOR ──")
    termo = input("ID ou nome: ").strip()
    f = buscar_fornecedor(termo)
    if not f:
        print("Não encontrado."); return
    pais_nome = PAISES.get(f["pais_codigo"], f["pais_codigo"])
    print(f"""
  ID               : {f['id']}
  Nome fiscal      : {f['nome']}
  Nome comercial   : {f['nome_comercial'] or '—'}
  NIF PT           : {f['nif_pt'] or '—'}
  NIF país res.    : {f['nif_pais'] or '—'}
  País residência  : {f['pais_codigo']} — {pais_nome}
  Tipo rendimento  : {f['tipo_rendimento']} — {TIPOS_RENDIMENTO.get(f['tipo_rendimento'], '?')}
  Taxa CDT         : {f['taxa_cdt']}%
  Taxa doméstica   : {f['taxa_domestica']}%
  % Participação   : {f['percentagem_participacao']}%
  Categoria        : {f['categoria'] or '—'}
  Notas            : {f['notas'] or '—'}
  Criado em        : {f['criado_em']}
""")


def _pedir_dados_fornecedor(defaults: dict = None) -> dict:
    d = defaults or {}
    def ask(label, key, default=""):
        val = input(f"  {label} [{d.get(key, default)}]: ").strip()
        return val if val else d.get(key, default)

    print("  Tipos rendimento: " + " | ".join(f"{k}={v[:30]}" for k, v in TIPOS_RENDIMENTO.items()))
    dados = {
        "nome":                    ask("Nome fiscal completo", "nome"),
        "nome_comercial":          ask("Nome comercial / produto", "nome_comercial"),
        "nif_pt":                  ask("NIF PT (se tiver)", "nif_pt"),
        "nif_pais":                ask("NIF no país de residência", "nif_pais"),
        "pais_codigo":             ask("Código país (IE, US, DE…)", "pais_codigo", "IE").upper(),
        "tipo_rendimento":         ask("Tipo rendimento (A-H)", "tipo_rendimento", "C").upper(),
        "taxa_cdt":                float(ask("Taxa CDT %", "taxa_cdt", "0.0") or 0),
        "taxa_domestica":          float(ask("Taxa doméstica %", "taxa_domestica", "25.0") or 25.0),
        "percentagem_participacao":float(ask("% Participação", "percentagem_participacao", "0.0") or 0),
        "categoria":               ask("Categoria", "categoria"),
        "notas":                   ask("Notas", "notas"),
    }
    return dados


def menu_adicionar():
    print("\n── ADICIONAR FORNECEDOR ──")
    dados = _pedir_dados_fornecedor()
    if not dados["nome"]:
        print("Nome obrigatório."); return
    fid = adicionar_fornecedor(dados)
    print(f"✓ Fornecedor adicionado com ID {fid}.")


def menu_editar():
    print("\n── EDITAR FORNECEDOR ──")
    termo = input("ID ou nome a editar: ").strip()
    f = buscar_fornecedor(termo)
    if not f:
        print("Não encontrado."); return
    print(f"  A editar: {f['nome']} (ID {f['id']})")
    dados = _pedir_dados_fornecedor(dict(f))
    atualizar_fornecedor(f["id"], dados)
    print("✓ Fornecedor atualizado.")


def menu_pagamento():
    print("\n── REGISTAR PAGAMENTO ──")
    termo = input("ID ou nome do fornecedor: ").strip()
    f = buscar_fornecedor(termo)
    if not f:
        print("Não encontrado."); return
    print(f"  Fornecedor: {f['nome']} | Taxa CDT: {f['taxa_cdt']}% | Taxa dom.: {f['taxa_domestica']}%")
    agora = datetime.now()
    ano  = int(input(f"  Ano [{agora.year}]: ").strip() or agora.year)
    mes  = int(input(f"  Mês [{agora.month}]: ").strip() or agora.month)
    vb   = float(input("  Valor bruto (EUR): ").strip())
    regime = input("  Regime (CDT/DOM) [CDT]: ").strip().upper() or "CDT"
    taxa = f["taxa_cdt"] if regime == "CDT" else f["taxa_domestica"]
    taxa_inp = input(f"  Taxa a aplicar % [{taxa}]: ").strip()
    taxa = float(taxa_inp) if taxa_inp else taxa
    notas = input("  Notas: ").strip()

    retencao = round(vb * taxa / 100, 2)
    print(f"  Retenção calculada: {retencao:.2f} EUR ({taxa}% de {vb:.2f})")
    if input("  Confirmar? (s/N): ").strip().lower() != "s":
        print("Cancelado."); return

    pid = registar_pagamento({
        "fornecedor_id": f["id"], "ano": ano, "mes": mes,
        "valor_bruto": vb, "taxa_aplicada": taxa,
        "retencao": retencao, "regime": regime, "notas": notas
    })
    print(f"✓ Pagamento registado (ID {pid}).")


def menu_exportar():
    print("\n── EXPORTAR MODELO 30 ──")
    agora = datetime.now()
    ano = int(input(f"  Ano [{agora.year}]: ").strip() or agora.year)
    mes = int(input(f"  Mês [{agora.month}]: ").strip() or agora.month)
    ficheiro = input(f"  Ficheiro [modelo30_{ano}_{mes:02d}.csv]: ").strip() or None
    f, n = exportar_modelo30(ano, mes, ficheiro)
    print(f"✓ Exportados {n} registos para: {f}")


def menu_exportar_json():
    print("\n── EXPORTAR FORNECEDORES JSON ──")
    f, n = exportar_fornecedores_json()
    print(f"✓ {n} fornecedores exportados para: {f}")


def menu_categorias():
    conn = get_db()
    rows = conn.execute(
        "SELECT categoria, COUNT(*) as n FROM fornecedores WHERE ativo=1 "
        "GROUP BY categoria ORDER BY n DESC"
    ).fetchall()
    conn.close()
    print("\n── CATEGORIAS ──")
    for r in rows:
        print(f"  {r['categoria'] or '(sem categoria)':30} {r['n']:>4} fornecedores")


def main():
    init_db()
    seed_fornecedores()

    MENU = {
        "1": ("Listar fornecedores",     menu_listar),
        "2": ("Detalhe de fornecedor",   menu_detalhe),
        "3": ("Adicionar fornecedor",    menu_adicionar),
        "4": ("Editar fornecedor",       menu_editar),
        "5": ("Registar pagamento",      menu_pagamento),
        "6": ("Exportar CSV Modelo 30",  menu_exportar),
        "7": ("Exportar JSON completo",  menu_exportar_json),
        "8": ("Resumo por categorias",   menu_categorias),
        "0": ("Sair", None),
    }

    print("\n╔══════════════════════════════════════╗")
    print("║   MODELO 30 — Gestão Fornecedores   ║")
    print("╚══════════════════════════════════════╝")

    while True:
        print("\n" + "─" * 40)
        for k, (label, _) in MENU.items():
            print(f"  {k}. {label}")
        op = input("\nOpção: ").strip()
        if op == "0":
            print("Saindo."); break
        if op in MENU:
            _, fn = MENU[op]
            try:
                fn()
            except KeyboardInterrupt:
                print("\nInterrompido.")
            except Exception as e:
                print(f"Erro: {e}")
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
