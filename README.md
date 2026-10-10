# ForCoTech Schallhauben-Konfigurator

Live (Deutsch): https://forcotech.github.io/konfigurator/
Live (English): https://forcotech.github.io/konfigurator/en/
Standardprodukte VRF: https://forcotech.github.io/konfigurator/vrf/ · https://forcotech.github.io/konfigurator/en/vrf/
Standardprodukte PV-Wechselrichter: https://forcotech.github.io/konfigurator/pv/ · https://forcotech.github.io/konfigurator/en/pv/

© Silent-Engineering di Romolo Vicari · Via Trento 22 · 23875 Osnago (LC) · Italien.
Alle Rechte vorbehalten. Konfigurator, Berechnungsverfahren und Gestaltung sind urheberrechtlich geschützt.
Jede Vervielfältigung, Bearbeitung, Weitergabe oder Nutzung des Codes – ganz oder in Teilen – ist ohne
schriftliche Genehmigung untersagt.

## Suchmaschinen / KI-Lesbarkeit

Titel, Meta-Beschreibungen, strukturierte Daten (JSON-LD), die Katalog-Übersicht als Tabelle und
`sitemap.xml` werden aus den gerenderten Seiten erzeugt. Nach jeder Änderung an Katalog oder Texten neu erzeugen:

    node tools/extract_catalog.mjs /tmp/catalog-data.json
    python3 tools/seo_build.py /tmp/catalog-data.json

Der geschützte Rechen-Code wird dabei nicht verändert.
