# Handoff: GreenLog — Dashboard logistica su strada

## Overview
Dashboard web per GreenLog (trasporto merci su strada, committente ItalLogistic). Risponde a sette domande di business con grafici interattivi calcolati dalle view `vw_*` del database MySQL:

1. Quali mezzi consumano più del previsto? (`vw_consumo_previsto`)
2. Dove perdiamo efficienza? (`vw_efficienza_flotta`)
3. Su quali mezzi intervenire per primi? (`vw_priorita_interventi`)
4. Quanto possiamo risparmiare? (`vw_risparmio_potenziale` + simulatore)
5. Com'è composta la flotta? (`vw_stato_flotta`)
6. Le consegne arrivano in orario? (`vw_puntualita_consegne`)
7. Quali clienti rendono meno del potenziale? (`vw_redditivita_cliente`)

La tesi editoriale della dashboard — visibile nella home — è che **il risparmio non è nel carburante ma nelle attese ai magazzini e nei mezzi fermi**: la flotta consuma già in modo omogeneo (scostamento massimo ~1%), mentre la puntualità media è bassa e l'attesa media al carico è di decine di minuti.

## About the Design Files
`site/dashboard.html` **è un design di riferimento in HTML**, non codice di produzione da estendere indefinitamente. Funziona: si apre in un browser, carica i JSON e disegna grafici SVG/DOM interattivi senza alcuna dipendenza esterna oltre `support.js` (runtime incluso) e i font Google.

Per il deploy hai quindi **due strade legittime**, descritte in `DEPLOY.md`:

- **A — pubblicare il bundle così com'è.** È un sito statico completo. Zero build, zero framework. Corretto se l'obiettivo è "mettere online la dashboard entro oggi".
- **B — ricostruirla nel codebase target** (React/Next, Vue, quello che userai). Corretto se la dashboard deve diventare un prodotto con autenticazione, più utenti, dati live. In quel caso questo README è la specifica: colori, tipografia, layout e logica di ogni grafico sono documentati sotto, e la logica di calcolo è leggibile nella classe `Component` in fondo a `dashboard.html`.

Non copiare `support.js` in un progetto React: è il runtime del prototipo. In un codebase reale i grafici si rifanno con la libreria già in uso (Recharts, visx, D3, ECharts), replicando i valori qui documentati.

## Fidelity
**High-fidelity.** Colori, tipografia, spaziature, stati hover e copy sono definitivi. I dati sono reali, esportati dal database Aiven il 2026-09-14. Se scegli la strada B, la UI va ricostruita pixel-perfect a partire dai token qui sotto.

## Screens / Views

Quattro schede in una singola pagina, commutate da stato client (`state.tab`), senza routing. Header sticky, barra filtri sotto l'header, footer con conteggi.

### 1. Sintesi (`tab: "sintesi"`)
- **Purpose**: dare al direttore operativo la risposta in dieci secondi e indirizzarlo alla scheda giusta.
- **Layout**: eyebrow mono (periodo + numero mezzi) → `h1` 32px max 26ch → paragrafo di sommario 17px max 70ch → griglia KPI `repeat(auto-fit, minmax(210px, 1fr))` gap 16px → due card affiancate `repeat(auto-fit, minmax(320px, 1fr))` gap 18px → card "Cosa guardare per primo".
- **Componenti**:
  - **4 KPI card**: `#151e24`, bordo `1px solid #223038`, radius 10px, padding 20px. Label 14px `#93a4ad`; valore IBM Plex Mono 30px weight 500 letter-spacing −0.02em, colore semantico (verde risparmio, rosso puntualità, ambra mezzi fermi e clienti); nota 13px `#7f939d`.
  - **Grafico trend consumo**: SVG `viewBox="0 0 1000 210"` `preserveAspectRatio="none"`, altezza fissa 210px. Tre linee griglia `#1d2a31` al 25/50/75%. Area `#4fc98c` opacity 0.1, linea `#4fc98c` 2px con `vector-effect: non-scaling-stroke`. Punti come div assoluti 24×24 (hit area) con pallino 7px che passa a 13px in hover. Tooltip `#0b1114` bordo `#4fc98c` radius 7px, `translate(-50%, -140%)`. Asse Y: min/max in mono 11px agli angoli; asse X: max 8 etichette mese (`gen 24`).
  - **Stato flotta**: barra segmentata 16px radius 8px gap 2px (verde In servizio / ambra In manutenzione / rosso Fermi), poi righe `grid-template-columns: 12px minmax(0,1fr) auto auto` gap 12px con pastiglia colore 10px radius 2px, label 15px, conteggio mono, percentuale mono 13px allineata a destra. Chiude con un commento che monetizza i mezzi fermi.
  - **Cosa guardare per primo**: lista di 4 righe cliccabili, `grid-template-columns: auto minmax(0,1fr) auto`, separate da gap 1px su fondo `#223038` (effetto hairline), riga `#121b21` → hover `#16222a`. Tag mono 12px (CRITICO rosso / ALTO ambra / MEDIO ambra / BASSO verde), testo 15px `#cfdadf`, call to action `#7f939d` con freccia. Il click porta alla scheda relativa.

### 2. Flotta (`tab: "flotta"`)
- **Purpose**: capire quali mezzi si discostano dalla media della loro marca e quali stanno fermi.
- **Componenti**:
  - **Domanda 01 — scostamento consumo**: classifica di N righe (prop `topN`, default 12). Riga `grid-template-columns: minmax(0,1fr) 78px`. Barra 9px radius 5px su fondo `#0d1317`, ancorata a sinistra per scostamenti positivi e a destra per negativi (`justify-content`), larghezza proporzionale al massimo assoluto. Colore: rosso oltre il 60% del massimo, ambra positivo, verde negativo. Click = filtro mezzo globale; le righe non selezionate scendono a opacity 0.32.
  - **Domanda 02 — scatter efficienza**: 340px di altezza, assi disegnati con `border-left`/`border-bottom` `#2a3b44`, margine sinistro 46px per le etichette Y. X = utilizzo medio %, Y = ore di fermo, diametro = costo di manutenzione (8→24px). Verde translucido sopra l'82% di utilizzo, rosso translucido sotto. Hover = tooltip a 4 righe; click = filtro mezzo.
  - **Dettaglio mezzo** (solo con un mezzo selezionato): card con bordo verde `#4fc98c`, 5 KPI mini e istogramma mensile del consumo (barre `flex: 1 1 0` gap 2px, altezza 18–100% normalizzata, ambra sopra la media del mezzo, verde sotto, hover verde pieno + tooltip).

### 3. Costi & Risparmi (`tab: "costi"`)
- **Domanda 03 — costo per km**: barre 100% impilate carburante (`#4fc98c`) / manutenzione (`#e0a458`), altezza 20px radius 3px; riga `grid-template-columns: 118px minmax(0,1fr) 92px`. Ordinate dal costo/km più alto. L'hover non usa un tooltip flottante ma **una riga di dettaglio in fondo alla card** (id, marca, km, euro carburante, euro manutenzione) — scelta deliberata: con 12 barre sottili un tooltip copre le vicine.
- **Domanda 04 — simulatore**: due slider nativi (`accent-color: #4fc98c`).
  - *Mezzi portati alla media*: 0–100 step 5, default 100.
  - *Prezzo gasolio*: 0,60–2,20 €/L step 0,05, default = prezzo medio reale dai dati.
  - Output: risparmio annuo, litri non bruciati, CO₂ evitata (2,68 kg/L). **I valori delle view coprono tutto l'archivio** (36 mesi, gen 2022 - dic 2024): la dashboard divide per `anni = mesiArchivio / 12` per esporre cifre annue e cita il totale di periodo nella nota. Replicare questa annualizzazione, altrimenti i numeri risultano gonfiati.
  - Bottone "RIPRISTINA DATI REALI" riporta gli slider ai valori del database (`state.simCop = null`, `state.simPrezzo = null`).

### 4. Clienti & Consegne (`tab: "clienti"`)
- **Domanda 06 — puntualità**: 3 KPI mini + istogramma di 50 magazzini ordinati dal peggiore al migliore, barre `flex: 1 1 0` gap 3px altezza 170px (25–100% normalizzata), rosso sotto la media ponderata, verde sopra. Tooltip con id magazzino, % puntualità, minuti di attesa medi. Le medie sono **ponderate sul numero di eventi**, non medie di percentuali.
- **Domanda 07 — redditività clienti**: scatter 360px, assi in euro, **diagonale tratteggiata `#38505c` come parità potenziale/effettivo** (SVG `viewBox="0 0 100 100"` non-scaling). Punti 9px: rossi sotto il 100% del potenziale, verdi sopra. Sotto, due liste da 10: "Sotto potenziale" (divario in euro, rosso) e "Oltre potenziale" (% del potenziale, verde), ciascuna con nome cliente e `customer_id` in mono 11px.

## Interactions & Behavior
- **Filtro marca**: chip nella barra filtri, mutuamente esclusivi, con conteggio mezzi. Selezionare una marca azzera il filtro mezzo.
- **Filtro mezzo**: si attiva cliccando una barra della Domanda 01, un punto dello scatter o una barra della Domanda 03; è **cross-filter globale** — modifica il trend della Sintesi, entrambi i grafici Flotta e apre la card di dettaglio. Chip di rimozione `TRK00042 ✕`; bottone `AZZERA` se c'è almeno un filtro.
- **Hover**: ogni serie ha il suo stato hover in `state` (`hTrend`, `hScatter`, `hQ3`, `hBar`, `hFac`, `hCust`) — niente hover condiviso, così due grafici non si spengono a vicenda.
- **Cambio scheda**: azzera tutti gli stati di hover, conserva i filtri.
- **Loading**: testo mono centrato "Carico le view dal database…" mentre i dieci fetch sono in volo; la barra filtri e il footer compaiono solo a dati pronti.
- **Errore**: card rossa `#1d1214` bordo `#6b3a3a` con il nome del file mancante e il promemoria che `data/` deve stare accanto al file HTML. È lo stato che vedi se apri l'HTML con `file://` invece che da un server.
- **Responsive**: tutte le griglie sono `auto-fit`/`minmax`, il contenuto è `max-width: 1280px` centrato con padding 24px. I grafici sono a larghezza fluida e altezza fissa. Testato fino a ~360px di larghezza.
- Nessuna animazione oltre le transizioni implicite di hover: scelta deliberata per un cruscotto operativo.

## State Management
```js
{
  d: null,              // tutti i JSON caricati, chiave = nome file
  err: null,            // messaggio di errore fetch
  tab: "sintesi",       // sintesi | flotta | costi | clienti
  make: null,           // filtro marca
  truck: null,          // filtro mezzo (TRK00001…)
  hTrend, hScatter, hQ3, hBar, hFac, hCust,   // hover per serie
  simCop: null,         // % copertura simulatore (null = 100, dato reale)
  simPrezzo: null       // €/L simulatore (null = prezzo medio reale)
}
```
Data fetching: dieci `fetch("./data/<nome>.json")` in `Promise.all` al mount, nessun refetch successivo. Tutti gli aggregati sono ricalcolati in render a partire dai filtri — i dataset sono piccoli (≤100 mezzi, ~2.200 righe mensili), quindi non serve memoizzazione.

## Design Tokens

**Colori**
| Ruolo | Hex |
| --- | --- |
| Fondo pagina | `#0d1317` |
| Fondo card | `#151e24` |
| Fondo barra filtri / footer / card interne | `#111a1f` |
| Fondo riga lista | `#121b21` (hover `#16222a`) |
| Fondo tooltip | `#0b1114` |
| Bordo standard | `#223038` |
| Bordo controlli | `#2a3b44` |
| Bordo bottone secondario | `#38505c` |
| Griglia grafici | `#1d2a31` |
| Testo primario | `#e8eef0` |
| Testo secondario | `#cfdadf` / `#b6c4ca` |
| Testo tenue | `#93a4ad` |
| Testo mono / etichette | `#7f939d` |
| Accento verde (positivo, brand) | `#4fc98c` (hover link `#7edcae`) |
| Ambra (attenzione, manutenzione) | `#e0a458` |
| Rosso (criticità) | `#e07a7a` |
| Fondo / bordo errore | `#1d1214` / `#6b3a3a` |

Riempimenti translucidi negli scatter: `rgba(79,201,140,0.4)` e `rgba(224,122,122,0.55)`; istogrammi `rgba(224,164,88,0.75)` e `rgba(79,201,140,0.5)`.

**Tipografia** — IBM Plex Sans 400/500/600/700 per il testo, IBM Plex Mono 400/500 per **tutti i numeri, gli id e le etichette d'asse** (regola forte: nessuna cifra in font proporzionale). Scala: h1 32px/1.15 −0.02em 700 · h1 di sezione 29px · h2 19–20px 600 · h3 17px 600 · corpo 15–17px/1.5 · secondario 13–14px · mono etichette 11–12px letter-spacing 0.04–0.08em uppercase · valore KPI mono 30px · valore KPI mini mono 21–27px.

**Spaziature** — 2 · 4 · 6 · 8 · 10 · 12 · 14 · 16 · 18 · 20 · 22 · 24 · 26 · 34 px. Padding card 20–24px, gap griglie 14–18px, padding main `32px 24px 90px`.

**Radius** — 10px card · 8px card interne e bottoni tab · 7px bottoni e tooltip · 5px barre sottili · 3px barre impilate · 2px pastiglie colore e cime barre · 20px chip · 50% punti scatter.

**Ombre** — nessuna. La gerarchia è affidata ai fondi e ai bordi hairline, non alle elevazioni.

**Numeri** — formattazione `it-IT`: separatore migliaia punto, decimali virgola. Euro abbreviato: `€1,23 M` sopra il milione, `€45k` sopra i 10.000, `€1.234` sotto; segno meno tipografico `−` per i valori negativi. Consumi in L/100 km con 2 decimali, percentuali 1 decimale, costo/km 3 decimali.

## Assets
Nessuna immagine, nessuna icona, nessun SVG decorativo. I soli asset esterni sono i font IBM Plex Sans e IBM Plex Mono da Google Fonts (`<link>` con `preconnect`). Il marchio è reso da un punto verde 11px accanto al wordmark testuale. Se pubblichi in ambienti senza rete verso Google, self-hostare i font (`@font-face` woff2) e togliere il `<link>`.

## Data Pipeline
Le view fanno tutto il calcolo lato database; la dashboard non ricalcola KPI, li aggrega solo per i filtri.

- `pipeline/export_views.py` si collega al MySQL Aiven, scopre tutte le view `vw_*` via `information_schema`, le esporta in `data/<nome>.json` (prefisso `vw_` rimosso) e scrive `data/manifest.json` con timestamp, database, righe per file ed eventuali errori. Aggiunge due dataset non-view: `utilizzo_mensile` (serie mensile per mezzo, dalla tabella `truck_utilization_metrics`) e `prezzo_carburante` (prezzo medio al litro).
- L'header della dashboard mostra `AGGIORNATO gg/mm/aaaa` leggendo `manifest.generato_il`: è la prova visibile della freschezza del dato.
- Credenziali: `.env` (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_SSL_CA`) oppure prompt interattivo con la Service URI di Aiven. **Mai committare `.env` né `ca.pem`.**
- Aggiungere una view a `greenlog_kpi.py` non richiede modifiche allo script: la scopre da sola. Richiede però di leggerla nella dashboard (array `FILES` e `renderVals`).

## Files
| File | Cosa contiene |
| --- | --- |
| `site/index.html` | Pagina di presentazione del progetto (fondo chiaro, identità in `DESIGN.md`). Legge alcuni JSON per mostrare i numeri aggiornati |
| `site/brand.html` | Linee guida pubbliche: logo, colori, tipografia, componenti, tono di voce |
| `site/dashboard.html` | La dashboard completa: markup, stili inline, classe `Component` con tutta la logica di calcolo e disegno. `dashboard.html#costi` apre direttamente una scheda |
| `site/assets/` | Logo, favicon, screenshot della dashboard, `brand.css` (token condivisi) e `site.js` (entrate allo scroll) |
| `DESIGN.md` | Il sistema visivo delle pagine di presentazione |
| `site/support.js` | Runtime del prototipo (template + rendering). Solo per la strada A |
| `site/data/*.json` | Le dieci esportazioni delle view + `manifest.json` |
| `pipeline/export_views.py` | Esportatore DB → JSON |
| `.github/workflows/refresh-data.yml` | GitHub Action notturna: rigenera i JSON e ripubblica |
| `.github/workflows/deploy-pages.yml` | Pubblica `site/` su GitHub Pages a ogni push su `site/**` |
| `DEPLOY.md` | Le due strade di deploy, passo per passo |

## Note per chi ricostruisce (strada B)
- **Il testo è parte del design.** Sommario, note sotto ogni domanda e righe "Cosa guardare per primo" sono generati dai dati (`this.n(...)`, `this.eur(...)`) e contengono la lettura dei numeri, non decorazione. Sono la ragione per cui la dashboard dice qualcosa invece di mostrare grafici. Portarli nel nuovo codebase con la stessa interpolazione.
- **Le medie ponderate.** Puntualità e attesa sono medie pesate sugli eventi per magazzino; rifarle come media aritmetica delle percentuali dà un numero diverso e sbagliato.
- **L'annualizzazione** del simulatore e delle KPI di risparmio (divisione per `anni`) va replicata.
- **`vw_risparmio_potenziale` restituisce una sola riga aggregata**, non una riga per mezzo: il simulatore scala quella riga, non somma per mezzo.
- **`vw_efficienza_flotta` non ha la colonna `make`**: la marca si ricava per join con `vw_priorita_interventi` (in prototipo, la mappa `makeOf()`).
- `truck_id` è testuale nel formato `TRK00001`, non intero — c'è una divergenza aperta con `creazione_db.py`, annotata in `github.md`.
