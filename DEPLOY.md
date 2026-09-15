# Deploy — GreenLog Dashboard

Due strade. Scegli in base a quanto deve vivere il sito.

---

## Strada A — pubblicare il bundle così com'è

`site/` è già un sito statico completo e funzionante. Nessuna build, nessuna dipendenza npm.

Online su GitHub Pages: https://lagojacopo00-byte.github.io/greenlog-dashboard/
- `/` presentazione del progetto
- `/dashboard.html` la dashboard (`#sintesi`, `#flotta`, `#costi`, `#clienti` aprono la scheda)
- `/brand.html` identità visiva

Lo screenshot in `site/assets/dashboard-sintesi.jpg` non si aggiorna con i dati: se la dashboard cambia aspetto, rigeneralo.

**Vincolo unico:** va servito via HTTP, non aperto con doppio clic. Con `file://` i `fetch` dei JSON vengono bloccati dal browser e vedi la card d'errore rossa.

### Provalo in locale
```bash
cd site
python -m http.server 8000
# apri http://localhost:8000
```

### Pubblicalo

**Netlify / Cloudflare Pages / Vercel** — trascina la cartella `site/` nella dashboard del servizio, oppure:
```bash
npx netlify-cli deploy --dir=site --prod
```
Nessun comando di build, publish directory `site`.

**GitHub Pages**
```bash
git switch -c gh-pages
cp -r site/* .
git add . && git commit -m "Dashboard GreenLog"
git push -u origin gh-pages
```
Poi *Settings → Pages → Branch: gh-pages*.

### Prima di pubblicare, decidi sulla riservatezza
I JSON in `site/data/` contengono **nomi clienti, ricavi e potenziale annuo**. Pubblicati su un URL statico sono leggibili da chiunque conosca l'indirizzo. Opzioni, in ordine di solidità:

1. Netlify/Cloudflare Access con password o SSO sul sito intero (la via rapida).
2. Anonimizzare `customer_name` nell'export (`SELECT CONCAT('Cliente ', customer_id)`).
3. Strada B con autenticazione vera.

---

## Strada B — ricostruirla in un codebase

Ha senso se servono login, più clienti, dati live o integrazione con altri sistemi. Il `README.md` è la specifica completa: token, layout di ogni grafico, logica di calcolo, trappole sui dati.

Stack che consiglierei, ma decidi tu: **Next.js + Recharts o visx**, con le query SQL delle view spostate in API route e i JSON sostituiti da chiamate al DB. La classe `Component` in fondo a `site/dashboard.html` è la fonte da cui leggere la logica: ogni aggregato è lì, in JavaScript leggibile.

Prompt di partenza per Claude Code, da dare nella cartella scompattata:

> Leggi README.md e site/dashboard.html. Ricostruisci questa dashboard come app Next.js con App Router e TypeScript. Grafici con Recharts. I dati arrivano da MySQL tramite API route che eseguono le stesse view `vw_*`, non da JSON statici. Rispetta esattamente i design token e i testi generati dai dati documentati nel README. Mantieni il cross-filter marca/mezzo, il simulatore e l'annualizzazione descritta.

---

## Aggiornare i dati

I JSON sono una fotografia del 14/09/2026. Per rinfrescarli:
```bash
cd pipeline
pip install pymysql python-dotenv
python export_views.py          # chiede la Service URI se non trova .env
cp -r data/* ../site/data/
```

### In automatico su GitHub Actions
`.github/workflows/refresh-data.yml` rigenera i JSON ogni notte, li committa e richiama `deploy-pages.yml` per ripubblicare (i push fatti con `GITHUB_TOKEN` non avviano da soli altri workflow). Senza secret il job si salta con un avviso. Crea i secret del repo:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `DB_CA_PEM` — contenuto del `ca.pem` scaricato da Aiven

Con Netlify o Vercel collegati al repo, il commit dei JSON fa da trigger al redeploy: la dashboard si aggiorna da sola e l'header mostra la nuova data.

---

## Checklist

- [ ] Password Aiven cambiata (era stata esposta in chat)
- [ ] `.env` e `ca.pem` in `.gitignore`, mai committati
- [ ] Deciso cosa fare dei nomi cliente nei JSON pubblici
- [ ] Sito protetto da password, se i dati restano reali
- [ ] Verificato che l'header mostri la data attesa (`manifest.generato_il`)
- [ ] Provata la pagina a ~360px di larghezza, se qualcuno la aprirà da telefono
