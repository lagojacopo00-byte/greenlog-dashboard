# DESIGN.md — Identità GreenLog

Fonte unica delle decisioni visive per `site/index.html` (presentazione) e `site/brand.html` (linee guida pubbliche). I valori vivono in `site/assets/brand.css`: se cambi un token, cambialo lì e aggiorna questa pagina.

La dashboard (`site/dashboard.html`) **non segue ancora questo sistema**: usa il tema scuro originale del design handoff (`README.md`, sezione Design Tokens). Allinearla al fondo chiaro è una decisione aperta.

## Principi

1. **Fondo chiaro, sempre.** Scelta del committente. Nessuna sezione a tema scuro nelle pagine di presentazione; l'unico elemento scuro è lo screenshot della dashboard, trattato come immagine.
2. **Un solo colore di marca.** Il verde del logo. Tutto il resto è neutro. Il colore segnala azioni e risultati.
3. **I numeri vengono dai dati.** Ogni cifra mostrata nella home è calcolata dagli stessi JSON della dashboard; nell'HTML c'è il valore del 14/09/2026 come riserva se il fetch fallisce.
4. **Onestà sul perimetro.** Progetto didattico, dati simulati, limiti dei KPI: si dichiarano in pagina, non in nota a margine.

## Logo

- File: `site/assets/greenlog-logo.png` (351×216, trasparente), ritagliato senza modifiche da `Image20260914174435.png`.
- Si usa così com'è, solo su fondo chiaro. Vietato deformarlo, ricolorarlo, metterlo su fondi scuri o sopra immagini.
- Area di rispetto: l'altezza della scritta GREENLOG su ogni lato.
- Larghezza minima 160px: sotto il payoff non si legge. Per favicon e icone solo il camion (`favicon-64.png`, `apple-touch-icon.png`).

## Colore

| Token | Valore | Uso | Contrasto |
| --- | --- | --- | --- |
| `--brand` | `#238A51` | Verde misurato sul logo. Superfici, icone, nodi della pipeline | 4,35:1 su bianco: **non per testo piccolo** |
| `--brand-ink` | `#1A6B3F` | Bottone primario, link, cifre in evidenza | 6,52:1 su bianco |
| `--brand-ink-hover` | `#145633` | Hover di bottoni e link | 8,72:1 |
| `--brand-tint` | `#EEF5F0` | Fondo del riquadro in evidenza, tag "Pronto" | |
| `--ink` | `#17201B` | Titoli e testo | 16,68:1 |
| `--ink-2` | `#454E49` | Paragrafi, didascalie | 8,61:1 |
| `--muted` | `#69716C` | Etichette, note | 4,85:1 su canvas, 4,54:1 su tint |
| `--canvas` | `#FBFBFA` | Fondo pagina | |
| `--surface` | `#FFFFFF` | Riquadri, cornici | |
| `--band` | `#F3F5F2` | Fasce di sezione (pipeline, team) | |
| `--line` / `--line-strong` | `#E4E7E3` / `#C9CFCA` | Filetti 1px | |
| `--amber-bg` / `--amber-ink` | `#FBF1DA` / `#8A5A00` | Solo tag "In sviluppo" | 5,28:1 |

Vietati nell'interfaccia: rossi, blu, viola, gradienti decorativi. Il rosso `#9F2F2D` compare solo nei "No" della pagina linee guida.

## Tipografia

- **IBM Plex Sans** 400/500/600: titoli, testo, bottoni, cifre grandi (`.display-num`, cifre tabellari, tracking −0,035em).
- **IBM Plex Mono** 400/500: etichette, id (`TRK00042`), nomi di tabelle e tecnologie. Mai per paragrafi né per cifre sopra i ~20px: in corpo grande la virgola monospazio apre un buco.
- Stessa famiglia della dashboard, per continuità.

| Ruolo | Dimensione | Peso / tracking |
| --- | --- | --- |
| Titolo hero | `clamp(2.4rem, 4.4vw, 3.75rem)`, interlinea 1,04 | 600, −0,03em |
| Titolo sezione | `clamp(1.8rem, 3vw, 2.4rem)` | 600, −0,02em |
| Titolo riquadro | `clamp(1.15rem, 1.6vw, 1.35rem)` | 600 |
| Testo | 17px, interlinea 1,6 | 400 |
| Didascalia | 15px | 400 |
| Etichetta | mono 12,5px maiuscolo, +0,06em | 400 |

Numeri sempre in formato `it-IT`: `170.820`, `55,7%`, `€27k`. Nessun trattino lungo nel testo visibile.

## Forma

- Raggi: 6px bottoni, 10px riquadri e cornici, pillola solo per i tag.
- Nessuna ombra. I livelli si separano con fondi e filetti.
- Contenuto massimo 1200px, margini laterali `clamp(20px, 4vw, 40px)`.

## Componenti

- **Bottone primario** `.btn-primary`: fondo `--brand-ink`, testo bianco, altezza 48px (40px la variante `.btn-sm` in header). Una sola etichetta per intento: "Apri la dashboard".
- **Bottone secondario** `.btn-secondary`: fondo bianco, filetto `--line-strong`.
- **Tag** `.tag-green` / `.tag-amber`: solo per stati reali di lavorazione.
- **Cornice screenshot** `.frame`: filetto 1px, barra con tre pallini e nome file in mono. Nella hero esce dal bordo destro della finestra sopra i 960px.
- **Riquadro domanda** `.tile`: link intero verso `dashboard.html#<scheda>`, domanda in h3, risposta come cifra + didascalia.

## Movimento

- Entrata allo scroll (`.reveal`): opacità + `translateY(12px)`, 480ms, `cubic-bezier(0.23, 1, 0.32, 1)`, una volta sola, sfasamento 40–60ms nelle griglie.
- La hero **non** si anima: è la prima cosa che si legge.
- Con `prefers-reduced-motion: reduce` resta solo la dissolvenza.
- Pressione: `scale(0.97)` sui bottoni, `scale(0.99)` sui riquadri. Freccia che scorre di 3px in hover, solo con puntatore fine.

## Accessibilità

- Link "Vai al contenuto" per la tastiera, `:focus-visible` con contorno verde 2px.
- Aree tattili ≥ 40px per i link di navigazione e footer.
- Verificato a 390px senza scroll orizzontale; la tabella della scala tipografica scorre dentro il proprio contenitore.
