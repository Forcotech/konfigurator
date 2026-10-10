#!/usr/bin/env python3
"""Ergänzt die sechs Seiten um Inhalte, die Suchmaschinen und KI-Systeme ohne JavaScript lesen können.

- Titel, Meta-Beschreibung, Canonical, hreflang, Open Graph
- strukturierte Daten (JSON-LD): Organisation, Katalog als Produktliste
- statischer Text in den data-t-Elementen (wird beim Laden vom Skript identisch überschrieben)
- Katalog-Übersicht (Tabellen) als normales HTML am Seitenende
- Datenschutz-Link mit echter Adresse statt "#"

Der geschützte Rechen-Code bleibt unverändert. Das Skript ist wiederholbar: alle Ergänzungen
stehen zwischen <!-- seo:… --> Markierungen und werden bei jedem Lauf ersetzt.

Aufruf (aus dem Repository-Wurzelverzeichnis):
  node tools/extract_catalog.mjs /tmp/catalog-data.json
  python3 tools/seo_build.py /tmp/catalog-data.json
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://forcotech.github.io/konfigurator/"
PRIVACY = "https://silent-mode.com/datenschutz"
STAND = {"de": "Stand: Oktober 2026", "en": "As of October 2026"}

PAGES = {
    "index.html": dict(lang="de", path="", alt="en/", kind="cfg",
        title="Schallhauben-Konfigurator für Wärmepumpen, Kälteanlagen und PV-Wechselrichter | ForCoTech",
        desc="Schallhaube online auslegen: Abmessungen, Kältemittel (R290), Luftvolumenstrom, TA-Lärm-Akustik und Windzone eingeben – Außenmaße, Pegelminderung und Richtpreis sofort. ForCoTech, Engineered with Absora Technology."),
    "en/index.html": dict(lang="en", path="en/", alt="", kind="cfg",
        title="Acoustic Enclosure Configurator for Heat Pumps, Chillers and PV Inverters | ForCoTech",
        desc="Design an acoustic enclosure online: enter dimensions, refrigerant (R290), air flow, noise requirements and wind zone – get outer dimensions, noise reduction and a budget price instantly. ForCoTech, engineered with Absora Technology."),
    "vrf/index.html": dict(lang="de", path="vrf/", alt="en/vrf/", kind="vrf",
        title="Schallhauben für VRF/VRV-Außengeräte – Daikin, Mitsubishi Electric, Panasonic, LG, Samsung, Toshiba, Haier | ForCoTech",
        desc="Standard-Schallhauben passend zu VRF/VRV-Außengeräten von Daikin, Mitsubishi Electric, Panasonic, LG, Samsung, Toshiba und Haier – ca. −15 bzw. −20 dB(A), mit Haubenmaßen und Richtpreisen."),
    "en/vrf/index.html": dict(lang="en", path="en/vrf/", alt="vrf/", kind="vrf",
        title="Acoustic Enclosures for VRF/VRV Outdoor Units – Daikin, Mitsubishi Electric, Panasonic, LG, Samsung, Toshiba, Haier | ForCoTech",
        desc="Standard acoustic enclosures for VRF/VRV outdoor units from Daikin, Mitsubishi Electric, Panasonic, LG, Samsung, Toshiba and Haier – approx. −15 or −20 dB(A), with enclosure dimensions and budget prices."),
    "pv/index.html": dict(lang="de", path="pv/", alt="en/pv/", kind="pv",
        title="Schallhauben für PV-Wechselrichter – Huawei, SMA, Fronius, Sungrow, SolarEdge u. a. | ForCoTech",
        desc="Schallschutzhauben für PV-Wechselrichter: Vorbau-Hauben für Wandmontage und freistehende Gehäuse mit Montage-Shelter, für 1 bis 5 Geräte, ca. −15 bzw. −20 dB(A), mit Richtpreisen."),
    "en/pv/index.html": dict(lang="en", path="en/pv/", alt="pv/", kind="pv",
        title="Acoustic Enclosures for PV Inverters – Huawei, SMA, Fronius, Sungrow, SolarEdge and more | ForCoTech",
        desc="Acoustic enclosures for PV inverters: wall-mounted front enclosures and free-standing housings with mounting shelter, for 1 to 5 units, approx. −15 or −20 dB(A), with budget prices."),
}

ORG = {
    "@type": "Organization",
    "@id": BASE + "#org",
    "name": "Silent Engineering di Romolo Vicari",
    "alternateName": ["ForCoTech", "Silent-Mode", "Silent Engineering"],
    "brand": [{"@type": "Brand", "name": "ForCoTech"}, {"@type": "Brand", "name": "Silent-Mode"}],
    "url": "https://www.silent-mode.com",
    "email": "info@forcotech.com",
    "vatID": "IT03833150133",
    "founder": {"@type": "Person", "name": "Romolo Vicari"},
    "address": {"@type": "PostalAddress", "streetAddress": "Via Trento 22", "postalCode": "23875",
                "addressLocality": "Osnago", "addressRegion": "LC", "addressCountry": "IT"},
    "sameAs": ["https://forcotech.github.io/", "https://www.forcotech.com", "https://github.com/Forcotech"],
    "knowsAbout": ["Schallhauben", "Schallschutzhauben für Wärmepumpen", "Schalleinhausung Kälteanlagen",
                   "VRF/VRV-Außengeräte", "PV-Wechselrichter", "R290", "TA Lärm", "HSA3",
                   "acoustic enclosures", "noise control for heat pumps and chillers"],
}

T = {
    "de": dict(
        ov="Katalog-Übersicht als Tabelle", ovNote="Alle Richtpreise netto, ohne Montage, zzgl. MwSt. und Fracht. Verbindliches Angebot nach Prüfung.",
        mf="Hersteller", series="Baureihe", models="Passende Modelle", dev="Gerät (B × T × H)", inv="Wechselrichter (B × H × T)",
        hood="Haube (L × B × H)", hoodpv="Haube 1 Gerät (L × T × H)", code="Artikel-Nr.", std="Standard ca. −15 dB(A)",
        pro="Premium ca. −20 dB(A)", stdn="Standard für 1 / 2 / 3 / 4 / 5 Geräte", wall="Wandmontage (Vorbau-Haube)",
        free="Freistehend mit Montage-Shelter",
        vrfH="Standardhauben für VRF/VRV-Außengeräte – alle Modelle",
        vrfL="Jede Standardhaube passt zu den genannten Außengeräten. Haubenmaße für die Ausführung ohne Untergestell; Modulkombinationen mehrerer Geräte unter einer Haube sind möglich.",
        pvH="Schallhauben für PV-Wechselrichter – alle Modelle",
        pvL="Für jede Wechselrichter-Baureihe gibt es eine Vorbau-Haube für Wandmontage und ein freistehendes Gehäuse mit Montage-Shelter, jeweils für 1 bis 5 Wechselrichter.",
        prodVrf="ForCoTech Schallhaube {c} für {mf} {s}", prodPv="ForCoTech Schallhaube {c} für {mf} {s}",
        prodDesc="Passend für {m}.", catName="Standardhauben VRF/VRV", catNamePv="Schallhauben PV-Wechselrichter",
        about="Über ForCoTech",
        aboutT="ForCoTech ist die Schallhauben-Marke von Silent Engineering di Romolo Vicari (Osnago, Italien), gefertigt mit Absora-Technologie. Die Hauben werden projektbezogen ausgelegt – Akustik, Druckverlust und Statik, u. a. mittels CFD-Simulation – und sind für Wärmepumpen, Kaltwassersätze, Rückkühler, VRF/VRV-Außengeräte und PV-Wechselrichter erhältlich. Mehr über uns: <a href=\"https://forcotech.github.io/\">forcotech.github.io</a> · Kontakt: <a href=\"mailto:info@forcotech.com\">info@forcotech.com</a> · <a href=\"https://www.silent-mode.com\">silent-mode.com</a>",
    ),
    "en": dict(
        ov="Catalogue overview as a table", ovNote="All budget prices net, excl. installation, VAT and freight. Binding quotation after review.",
        mf="Manufacturer", series="Series", models="Matching models", dev="Unit (W × D × H)", inv="Inverter (W × H × D)",
        hood="Enclosure (L × W × H)", hoodpv="Enclosure for 1 unit (L × D × H)", code="Item no.", std="Standard approx. −15 dB(A)",
        pro="Premium approx. −20 dB(A)", stdn="Standard for 1 / 2 / 3 / 4 / 5 units", wall="Wall mounting (front enclosure)",
        free="Free-standing with mounting shelter",
        vrfH="Standard enclosures for VRF/VRV outdoor units – all models",
        vrfL="Each standard enclosure fits the outdoor units listed. Enclosure dimensions are for the version without base frame; combinations of several modules under one enclosure are available.",
        pvH="Acoustic enclosures for PV inverters – all models",
        pvL="For each inverter series there is a front enclosure for wall mounting and a free-standing housing with mounting shelter, each for 1 to 5 inverters.",
        prodVrf="ForCoTech acoustic enclosure {c} for {mf} {s}", prodPv="ForCoTech acoustic enclosure {c} for {mf} {s}",
        prodDesc="Fits {m}.", catName="Standard enclosures VRF/VRV", catNamePv="Acoustic enclosures PV inverters",
        about="About ForCoTech",
        aboutT="ForCoTech is the acoustic enclosure brand of Silent Engineering di Romolo Vicari (Osnago, Italy), built with Absora technology. Enclosures are engineered per project – acoustics, pressure drop and structural design, including CFD simulation – for heat pumps, chillers, dry coolers, VRF/VRV outdoor units and PV inverters. More about us: <a href=\"https://forcotech.github.io/en/\">forcotech.github.io</a> · Contact: <a href=\"mailto:info@forcotech.com\">info@forcotech.com</a> · <a href=\"https://www.silent-mode.com\">silent-mode.com</a>",
    ),
}

CSS = """<style id="seo-css">
.seo-ov{margin-top:24px;background:var(--card,#fff);border:1px solid var(--line,#e6e1e1);border-radius:var(--r,10px);padding:4px 16px}
.seo-ov>summary{cursor:pointer;padding:10px 0;font-weight:700;color:var(--accent,#c8202f)}
.seo-ov h2{font-size:17px;margin:6px 0 4px}.seo-ov h3{font-size:15px;margin:16px 0 6px}
.seo-ov p{font-size:13px;color:var(--muted,#5c5c5c);margin:0 0 8px;max-width:80ch}
.seo-tw{overflow-x:auto;margin:0 0 12px}
.seo-ov table{border-collapse:collapse;font-size:12.5px;width:100%;min-width:760px}
.seo-ov th,.seo-ov td{border-bottom:1px solid var(--line,#e6e1e1);padding:6px 8px;text-align:left;vertical-align:top}
.seo-ov th{background:var(--accent-l,#fdecee);font-weight:700}
.seo-ov td.n{white-space:nowrap;font-variant-numeric:tabular-nums}
.seo-about{font-size:12.5px;color:var(--muted,#5c5c5c);margin:16px 0 0;max-width:90ch}
.seo-about a{color:var(--accent,#c8202f)}
</style>"""

esc = html.escape


def num(price):
    """'15.500 €' / '€15,500' -> 15500"""
    return int(re.sub(r"[^0-9]", "", price))


def spec(card, *keys):
    for k in keys:
        if k in card["spec"]:
            return card["spec"][k]
    return ""


def head_block(f, cfg):
    url = BASE + cfg["path"]
    de_url = BASE + (cfg["path"] if cfg["lang"] == "de" else cfg["alt"])
    en_url = BASE + (cfg["path"] if cfg["lang"] == "en" else cfg["alt"])
    loc = "de_DE" if cfg["lang"] == "de" else "en_GB"
    return "\n".join([
        "<!-- seo:head -->",
        f'<meta name="description" content="{esc(cfg["desc"])}">',
        '<meta name="robots" content="index,follow,max-snippet:-1">',
        f'<link rel="canonical" href="{url}">',
        f'<link rel="alternate" hreflang="de" href="{de_url}">',
        f'<link rel="alternate" hreflang="en" href="{en_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{de_url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="ForCoTech">',
        f'<meta property="og:title" content="{esc(cfg["title"])}">',
        f'<meta property="og:description" content="{esc(cfg["desc"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:locale" content="{loc}">',
        CSS,
        "<!-- /seo:head -->",
    ])


def jsonld(cfg, products=None, cat_name=None):
    page = {"@type": "WebPage", "@id": BASE + cfg["path"] + "#page", "url": BASE + cfg["path"],
            "name": cfg["title"], "description": cfg["desc"], "inLanguage": cfg["lang"],
            "publisher": {"@id": BASE + "#org"}}
    graph = [ORG, page]
    if cfg["kind"] == "cfg":
        graph.append({"@type": "WebApplication", "name": cfg["title"].split(" | ")[0],
                      "url": BASE + cfg["path"], "applicationCategory": "BusinessApplication",
                      "operatingSystem": "Web", "inLanguage": cfg["lang"],
                      "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
                      "provider": {"@id": BASE + "#org"}})
    if products:
        page["mainEntity"] = {"@type": "ItemList", "name": cat_name, "numberOfItems": len(products),
                              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": p}
                                                  for i, p in enumerate(products)]}
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return '<!-- seo:jsonld -->\n<script type="application/ld+json">' + data.replace("</", "<\\/") + "</script>\n<!-- /seo:jsonld -->"


def product(t, name_tpl, card, low, high, sku):
    return {"@type": "Product", "name": name_tpl.format(c=sku, mf=card["mf"], s=card["series"]),
            "sku": sku, "brand": {"@type": "Brand", "name": "ForCoTech"},
            "manufacturer": {"@id": BASE + "#org"}, "category": "Schallhaube / acoustic enclosure",
            "description": t["prodDesc"].format(m=", ".join(card["models"])),
            "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": low, "highPrice": high,
                       "availability": "https://schema.org/InStock",
                       "priceSpecification": {"@type": "PriceSpecification", "priceCurrency": "EUR",
                                              "valueAddedTaxIncluded": False}}}


def base_code(code):
    return re.sub(r"-[A-Z]{1,2}$", "", code)


def vrf_section(d, cfg, t):
    std, pro = d["std"], d["pro"]
    rows, prods = [], []
    for a, b in zip(std, pro):
        rows.append("<tr>" + "".join([
            f"<td>{esc(a['mf'])}</td>", f"<td>{esc(a['series'])}</td>", f"<td>{esc(', '.join(a['models']))}</td>",
            f"<td class=n>{esc(spec(a, 'Gerät (B × T × H)', 'Unit (W × D × H)'))}</td>",
            f"<td class=n>{esc(spec(a, 'Haube (L × B × H)', 'Enclosure (L × W × H)'))}</td>",
            f"<td class=n>{esc(a['price'])}</td>", f"<td class=n>{esc(b['price'])}</td>",
            f"<td class=n>{esc(a['code'])} / {esc(b['code'])}</td>"]) + "</tr>")
        prods.append(product(t, t["prodVrf"], a, num(a["price"]), num(b["price"]), base_code(a["code"])))
    head = "".join(f"<th>{esc(h)}</th>" for h in [t["mf"], t["series"], t["models"], t["dev"], t["hood"], t["std"], t["pro"], t["code"]])
    body = (f"<h2>{esc(t['vrfH'])}</h2><p>{esc(t['vrfL'])} {esc(t['ovNote'])} {STAND[cfg['lang']]}.</p>"
            f"<div class=seo-tw><table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")
    return body, prods


def pv_section(d, cfg, t):
    body = [f"<h2>{esc(t['pvH'])}</h2><p>{esc(t['pvL'])} {esc(t['ovNote'])} {STAND[cfg['lang']]}.</p>"]
    prods = {}
    for mode, label in (("wall", t["wall"]), ("free", t["free"])):
        rows = []
        for a, b in zip(d[mode + "_plus"], d[mode + "_pro"]):
            if not a.get("price"):  # z. B. Mikrowechselrichter: keine Haube nötig
                rows.append(f"<tr><td>{esc(a['mf'])}</td><td>{esc(a['series'])}</td>"
                            f"<td>{esc(', '.join(a['models']))}</td><td colspan=5>{esc(a.get('note', ''))}</td></tr>")
                continue
            steps = " / ".join(r[2] for r in a["rows"])
            rows.append("<tr>" + "".join([
                f"<td>{esc(a['mf'])}</td>", f"<td>{esc(a['series'])}</td>", f"<td>{esc(', '.join(a['models']))}</td>",
                f"<td class=n>{esc(spec(a, 'Wechselrichter (B × H × T)', 'Inverter (W × H × D)'))}</td>",
                f"<td class=n>{esc(a['rows'][0][1] if a['rows'] else '')}</td>",
                f"<td class=n>{esc(steps)}</td>", f"<td class=n>{esc(b['price'])}</td>",
                f"<td class=n>{esc(a['code'])}</td>"]) + "</tr>")
            key = base_code(a["code"])
            lo, hi = num(a["price"]), num(b["price"])
            if key in prods:
                o = prods[key]["offers"]
                o["lowPrice"], o["highPrice"] = min(o["lowPrice"], lo), max(o["highPrice"], hi)
            else:
                prods[key] = product(t, t["prodPv"], a, lo, hi, key)
        head = "".join(f"<th>{esc(h)}</th>" for h in [t["mf"], t["series"], t["models"], t["inv"], t["hoodpv"], t["stdn"], t["pro"] + " (1)", t["code"]])
        body.append(f"<h3>{esc(label)}</h3><div class=seo-tw><table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")
    return "".join(body), list(prods.values())


def replace_block(src, name, block, anchor_re, before=True):
    """Ersetzt einen bestehenden <!-- seo:name --> Block oder fügt ihn am Anker ein."""
    pat = re.compile(rf"<!-- seo:{name} -->.*?<!-- /seo:{name} -->\n?", re.S)
    if pat.search(src):
        return pat.sub(lambda m: block + "\n", src, count=1)
    m = re.search(anchor_re, src)
    if not m:
        raise SystemExit(f"Anker für {name} nicht gefunden: {anchor_re}")
    i = m.start() if before else m.end()
    return src[:i] + block + "\n" + src[i:]


def prefill(src, texts):
    """Füllt leere data-t-Elemente mit dem Text, den das Skript sonst erst beim Laden einsetzt."""
    def fill(m):
        tag, attrs, key = m.group(1), m.group(2), m.group(3)
        if key not in texts or not texts[key].strip():
            return m.group(0)
        return f"<{tag}{attrs}>{texts[key]}</{tag}>"
    # nur Elemente, die im Quelltext leer sind oder schon einmal reinen Text erhalten haben
    return re.sub(r'<(\w+)(\s[^>]*?\bdata-t="([^"]+)"[^>]*)>[^<]*</\1>', fill, src)


def build(data):
    for f, cfg in PAGES.items():
        p = ROOT / f
        src = p.read_text(encoding="utf-8")
        d = data.get(f, {})
        t = T[cfg["lang"]]
        src = re.sub(r"<title>.*?</title>", "<title>" + esc(cfg["title"]) + "</title>", src, count=1, flags=re.S)
        src = replace_block(src, "head", head_block(f, cfg), r"</head>")
        prods, section = None, ""
        if cfg["kind"] == "vrf":
            section, prods = vrf_section(d, cfg, t)
        elif cfg["kind"] == "pv":
            section, prods = pv_section(d, cfg, t)
        cat = t["catName"] if cfg["kind"] == "vrf" else t["catNamePv"]
        src = replace_block(src, "jsonld", jsonld(cfg, prods, cat), r"</head>")
        about = f'<p class="seo-about"><b>{esc(t["about"])}:</b> {t["aboutT"]}</p>'
        if section:
            body = f'<details class="seo-ov" id="uebersicht"><summary>{esc(t["ov"])}</summary>{section}</details>{about}'
        else:
            body = about
        src = replace_block(src, "body", "<!-- seo:body -->\n" + body + "\n<!-- /seo:body -->", r"\s*<footer class=\"copy\">")
        if d.get("dataT"):
            src = prefill(src, d["dataT"])
        src = src.replace('id="privacyLink" href="#"', f'id="privacyLink" href="{PRIVACY}"')
        src = src.replace('id="privacyLink2" href="#"', f'id="privacyLink2" href="{PRIVACY}"')
        p.write_text(src, encoding="utf-8")
        print(f"{f}: ok ({len(prods or [])} Produkte)")

    urls = []
    for f, cfg in PAGES.items():
        other = BASE + cfg["alt"]
        urls.append(f"  <url><loc>{BASE + cfg['path']}</loc><lastmod>2026-10-10</lastmod>"
                    f'<xhtml:link rel="alternate" hreflang="{"en" if cfg["lang"] == "de" else "de"}" href="{other}"/></url>')
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print("sitemap.xml: ok")


if __name__ == "__main__":
    build(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
