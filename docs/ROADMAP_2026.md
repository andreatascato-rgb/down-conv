# Down&Conv - Roadmap qualità desktop 2026

**Obiettivo:** App desktop “perfetta” 2026 (esclusa firma codice a pagamento).  
**Procedura:** un punto alla volta, poi verifica e merge.

---

## 1. Dipendenze pinnate ✅

**Problema:** `requirements.txt` con `>=` → build non riproducibili.  
**Soluzione 2026:** Versioni esatte (pinned) in `requirements.txt` per CI e release.

- `requirements.txt`: `PySide6==X.Y.Z`, `platformdirs==X.Y.Z`, `yt-dlp[default]==...`
- Aggiornamento: quando si aggiorna, cambiare le versioni esplicitamente e testare.
- `pyproject.toml`: si mantiene `>=` per sviluppo locale; `requirements.txt` è la fonte per build produzione.

---

## 2. Single instance ✅ (fatto)

**Problema:** Doppio clic apre due finestre.  
**Soluzione 2026:** Una sola istanza; seconda istanza porta in primo piano la finestra esistente e termina.

- **Meccanismo:** `QLocalServer` + `QLocalSocket` (Qt, cross‑platform).
- Primo avvio: crea server con nome univoco (es. `DownConv-{user}` o `DownConv-{pid}`). Secondo avvio: tenta connessione come client; se ok → invia messaggio "show", primo alza finestra, secondo esce con codice 0.
- Nome server: da `platformdirs.user_data_dir` o app name per evitare conflitti tra utenti.
- Edge case: primo crash senza chiusura server → il server muore con il processo; prossimo avvio ricrea. Nessun lock file da pulire.

**File:** nuovo modulo `utils/single_instance.py` + hook in `main.py` prima di `QApplication`.

---

## 3. Auto-update (Controlla aggiornamenti) ✅ (fatto)

**Problema:** Utente non sa se c’è una nuova versione.  
**Soluzione 2026:** Voce di menu “Controlla aggiornamenti” che confronta con GitHub Releases (no download automatico in-app).

- **Flusso:** Menu (es. Help / ?) → “Controlla aggiornamenti” → richiesta in thread/secondary process a `https://api.github.com/repos/OWNER/REPO/releases/latest` → confronto `tag_name` (es. `v1.0.1`) con `downconv.__version__` (es. `1.0.0`) → se maggiore: dialog “Disponibile la versione X. Scarica da [link]”; altrimenti “Sei aggiornato”.
- **Dettagli:** Non bloccare UI (QThread o equivalente). Gestire assenza rete, rate limit, timeout. Repository da costante o `pyproject.toml` (non hardcode sensibili).
- **Dove:** Menu nella `MainWindow` (es. “Aiuto” con “Controlla aggiornamenti” e “Segnala un bug”).

---

## 4. Crash reporting (feedback utente) ✅ (fatto)

**Problema:** In caso di crash l’utente non sa come inviare informazioni.  
**Soluzione 2026:** Nessun servizio a pagamento; massima utilità con link e log locali.

- **Dialog eccezione (già presente):** Aggiungere pulsante **“Apri cartella log”** che apre `user_log_dir()` (dove sta `downconv.log`). L’utente può allegare il file a una issue.
- **Menu Aiuto:** Voce **“Segnala un bug”** → apre in browser la pagina GitHub Issues (o template da CONTRIBUTING). Opzionale: precompilare titolo con versione e OS (es. `[1.0.0] Windows 10`).
- Nessun upload automatico di stack trace; tutto sotto controllo utente.

---

## Ordine di implementazione (tutti completati)

1. ✅ **Dipendenze pinnate**  
2. ✅ **Single instance** — `utils/single_instance.py`, hook in `main.py`  
3. ✅ **Aggiornamenti** — check avvio, tab Aiuto evidenziata, Aggiorna + Riprova in tab  
4. ✅ **Crash reporting** — `utils/report_bug.py`, dialog crash con Apri log + Segnala errore, tab Aiuto Segnala bug

Dopo ogni punto: `.\scripts\check.ps1`, CHANGELOG/STATUS aggiornati. **Stato:** pronto per commit, push e release.
