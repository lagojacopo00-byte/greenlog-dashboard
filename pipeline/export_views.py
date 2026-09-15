"""
GreenLog — esporta le view KPI in JSON per la dashboard web
===========================================================
Le view sono già nel database (le crea greenlog_kpi.py). Questo script si limita
a leggerle tutte e a scriverle in ./data/*.json, nella forma che la dashboard
HTML carica.

    pip install pymysql
    python export_views.py

Alla prima esecuzione, se non trova un .env, chiede la "Service URI" che Aiven
mostra nella console (mysql://utente:password@host:porta/GreenLog). Per non
reinserirla ogni volta, crea un .env nella stessa cartella:

    DB_HOST=...
    DB_PORT=...
    DB_USER=...
    DB_PASSWORD=...
    DB_NAME=GreenLog
    DB_SSL_CA=ca.pem        # opzionale: il certificato scaricato da Aiven

Scopre le view da solo (tutto ciò che si chiama vw_*), quindi se aggiungi una
view nuova a greenlog_kpi.py non serve toccare questo file: riesegui e c'è.
"""

import json
import os
import ssl
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # il .env è opzionale: senza python-dotenv si usano i prompt

OUT = Path(__file__).parent / "data"
CA = os.getenv("DB_SSL_CA", "ca.pem")


def ask_credentials():
    print("Nessun file .env trovato.")
    print("Incolla la 'Service URI' che trovi nella console Aiven, oppure premi")
    print("Invio per inserire i parametri uno alla volta.\n")
    uri = input("Service URI: ").strip()
    if uri:
        u = urlparse(uri)
        os.environ["DB_HOST"] = u.hostname or ""
        os.environ["DB_PORT"] = str(u.port or 3306)
        os.environ["DB_USER"] = unquote(u.username or "")
        os.environ["DB_PASSWORD"] = unquote(u.password or "")
        os.environ["DB_NAME"] = (u.path or "/").lstrip("/") or "defaultdb"
    else:
        from getpass import getpass

        os.environ["DB_HOST"] = input("Host: ").strip()
        os.environ["DB_PORT"] = input("Porta [3306]: ").strip() or "3306"
        os.environ["DB_USER"] = input("Utente [avnadmin]: ").strip() or "avnadmin"
        os.environ["DB_PASSWORD"] = getpass("Password (non viene mostrata): ")
        os.environ["DB_NAME"] = input("Database [GreenLog]: ").strip() or "GreenLog"
    print(f"\nMi collego a {os.environ['DB_NAME']} su {os.environ['DB_HOST']}…")


def connect():
    if not os.getenv("DB_HOST"):
        ask_credentials()
    kwargs = dict(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
    )
    ca_path = Path(__file__).parent / CA
    if ca_path.exists():
        kwargs["ssl"] = ssl.create_default_context(cafile=str(ca_path))
    else:
        # Aiven richiede TLS: senza CA si cifra comunque, senza verificare il certificato
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl"] = ctx
    return pymysql.connect(**kwargs)


def jsonable(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()[:10]
    if isinstance(v, timedelta):
        return v.total_seconds()
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return v


def fetch(cur, sql):
    cur.execute(sql)
    return [{k: jsonable(v) for k, v in row.items()} for row in cur.fetchall()]


def main():
    OUT.mkdir(exist_ok=True)
    conn = connect()
    written, errors = {}, {}

    with conn.cursor() as cur:
        cur.execute(
            "SELECT TABLE_NAME AS v FROM information_schema.VIEWS "
            "WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME",
            (os.environ["DB_NAME"],),
        )
        views = [r["v"] for r in cur.fetchall()]
        if not views:
            print("Nessuna view trovata: esegui prima greenlog_kpi.py.")
            return
        print(f"View trovate ({len(views)}): {', '.join(views)}\n")

        for v in views:
            name = v[3:] if v.lower().startswith("vw_") else v
            try:
                rows = fetch(cur, f"SELECT * FROM `{v}`")
            except Exception as e:  # una view rotta non deve fermare le altre
                errors[name] = str(e)
                print(f"- {name}: ERRORE ({e})")
                continue
            (OUT / f"{name}.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            written[name] = len(rows)
            cols = ", ".join(rows[0].keys()) if rows else "(vuota)"
            print(f"✓ {name}: {len(rows)} righe — {cols}")

        # Serie mensile per mezzo: il simulatore la usa per il prima/dopo.
        # Non è una view, quindi la leggo dalla tabella sorgente se c'è.
        try:
            rows = fetch(
                cur,
                """
                SELECT truck_id,
                       DATE_FORMAT(month, '%Y-%m-01') AS month,
                       average_l_100km, utilization_rate_pct,
                       downtime_hours, maintenance_cost_eur
                FROM truck_utilization_metrics
                ORDER BY truck_id, month
                """,
            )
            (OUT / "utilizzo_mensile.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            written["utilizzo_mensile"] = len(rows)
            print(f"✓ utilizzo_mensile: {len(rows)} righe")
        except Exception as e:
            errors["utilizzo_mensile"] = str(e)
            print(f"- utilizzo_mensile: SALTATA ({e})")

        # Prezzo medio del gasolio: serve al simulatore per convertire litri in euro
        for sql in (
            "SELECT ROUND(AVG(prezzo_litro_eur),4) AS prezzo_litro_eur FROM fuel_purchases",
            "SELECT ROUND(AVG(price_per_gallon)/3.785411784,4) AS prezzo_litro_eur FROM fuel_purchases",
        ):
            try:
                rows = fetch(cur, sql)
                (OUT / "prezzo_carburante.json").write_text(
                    json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
                )
                written["prezzo_carburante"] = len(rows)
                print(f"✓ prezzo_carburante: {rows[0] if rows else '(vuoto)'}")
                break
            except Exception as e:
                last = str(e)
        else:
            errors["prezzo_carburante"] = last
            print(f"- prezzo_carburante: SALTATA ({last})")

    conn.close()

    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "generato_il": datetime.now().isoformat(timespec="seconds"),
                "database": os.environ["DB_NAME"],
                "file": written,
                "errori": errors,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\nScritti {len(written)} file in {OUT}")
    if errors:
        print("Con problemi:")
        for k, v in errors.items():
            print(f"  - {k}: {v}")
    print("Ora carica la cartella data/ nel progetto della dashboard.")


if __name__ == "__main__":
    main()
