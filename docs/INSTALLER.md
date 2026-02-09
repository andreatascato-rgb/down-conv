# Installer Windows - Down&Conv

**Decisione:** Inno Setup come unico strumento per l'installer Windows. Nessun NSIS/WiX senza approvazione esplicita.

---

## 1. Perché Inno Setup

- **Standard de facto** per app Windows non-MSIX.
- **Script testabile** (`.iss` in repo), compilabile in CI.
- **Gratuito**, nessuna dipendenza commerciale.
- **Risultato:** wizard italiano, shortcut Start Menu, voce "Disinstalla" in Impostazioni di Windows.

---

## 2. Cosa fa l'installer

- Copia l'exe (build PyInstaller) in `%LocalAppData%\Programs\DownConv\` (o `C:\Program Files\DownConv` se installazione per tutti).
- Crea shortcut nel Menu Start (cartella "DownConv").
- Opzionale: shortcut sul desktop (checkbox in wizard).
- Registra la disinstallazione (Installazione e disinstallazione programmi).
- **Non** tocca FFmpeg: è già dentro l'exe (bundle PyInstaller).

---

## 3. File e convenzioni

| Elemento | Regola |
|----------|--------|
| Script | `installer/DownConv.iss` — un solo script, version da `/DMyAppVersion=...` in CI |
| Output | `DownConv-Setup-{version}.exe` (es. `DownConv-Setup-1.0.0.exe`) |
| Nome app | "DownConv" (no "Down&Conv" in path/registry) |
| Lingua wizard | Italiano come default; file lingua Inno in `installer/Languages` se servono |

- **Non** aggiungere logica custom (driver, servizi, firewall) senza documento di specifica.
- **Non** cambiare tool (es. passare a NSIS) senza aggiornare questa doc e la regola Cursor.

---

## 4. Build in CI

1. PyInstaller produce `dist\DownConv.exe`.
2. Inno Setup (installato via Chocolatey) compila `installer/DownConv.iss` con `/DMyAppVersion=%VERSION%` (dal tag, es. `v1.0.0` → `1.0.0`).
3. Output: `DownConv-Setup-1.0.0.exe`.
4. La release contiene:
   - **Portable:** `DownConv-v1.0.0-win64.exe` (exe nudo per chi non vuole installare).
   - **Installer:** `DownConv-Setup-1.0.0.exe` (consigliato per utenti finali).

---

## 5. Build locale

- Installare [Inno Setup](https://jrsoftware.org/isinfo.php).
- Da repo: `.\scripts\build.ps1` (genera `dist\DownConv.exe`), poi aprire `installer\DownConv.iss` in Inno Setup e Compile, oppure da riga di comando:
  `& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion=0.8.4 installer\DownConv.iss`

---

## 6. Manutenzione

- Aggiornare `.iss` solo per cambi di percorso, nome app, shortcut o requisiti (es. .NET).
- La versione **non** va hardcoded nel `.iss`: sempre passata da CI (o da `/DMyAppVersion` in locale).
