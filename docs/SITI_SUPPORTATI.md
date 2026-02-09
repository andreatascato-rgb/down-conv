# Siti supportati dal downloader (sicuri)

**Riferimento:** Down&Conv v1.0.0 | yt-dlp stable ≥2024.1.0

---

## Cosa fa (e non fa) l’app

- **Singolo URL:** da un link si scarica **un solo** video/audio (se l’URL è una playlist, viene usato solo il primo elemento).
- **Nessun login:** solo contenuti **pubblici**; niente account, cookie o autenticazione.
- **Formati:** video (Ottimale / 1080p / 720p / 4K) e audio (Ottimale / FLAC / WAV / M4A / MP3 / Nativo).
- **Ottimale:** l’app sceglie il formato migliore in base alla sorgente (YouTube, Bandcamp, SoundCloud, Vimeo hanno mapping dedicati).

I siti sotto sono considerati **sicuri** per questa versione e per queste funzionalità: pubblico, nessun login, uso tipico a singolo video/audio.

---

## Siti sicuri (testati e compatibili con le feature)

Siti per cui il comportamento è allineato a quanto l’app può fare (URL singolo, pubblico, formati supportati).

### Video (pubblici, senza login)

| Sito | Note |
|------|------|
| **YouTube** | youtube.com, youtu.be — supporto completo, formato ottimale dedicato. |
| **Vimeo** | vimeo.com — video pubblici; formato ottimale dedicato. |
| **Dailymotion** | dailymotion.com — video pubblici. |
| **BitChute** | bitchute.com — video pubblici. |
| **Odysee** | odysee.com (LBRY) — video pubblici. |
| **Internet Archive** | archive.org — video e audio pubblici. |
| **Coub** | coub.com — clip pubbliche. |
| **9GAG** | 9gag.com — video da post pubblici. |

### Audio (pubblici, senza login)

| Sito | Note |
|------|------|
| **SoundCloud** | soundcloud.com — tracce pubbliche; formato ottimale dedicato. |
| **Bandcamp** | bandcamp.com — tracce/album pubblici; preferenza FLAC dove disponibile. |
| **Audius** | audius.co — tracce pubbliche. |
| **Audiomack** | audiomack.com — tracce pubbliche. |
| **Mixcloud** | mixcloud.com — mix/set pubblici. |
| **Jamendo** | jamendo.com — musica libera. |

### Social / embed (pubblici)

| Sito | Note |
|------|------|
| **Instagram** | Post/reel pubblici (nessun login in app). |
| **TikTok** | Video pubblici. |
| **Facebook** | Video e reel pubblici (embed/URL diretti). |
| **Flickr** | flickr.com — video pubblici. |
| **Imgur** | imgur.com — video/gallery pubbliche. |

---

## Limitazioni importanti

1. **Playlist:** con un URL di playlist viene elaborato **solo il primo elemento**; non è supportato lo scaricamento dell’intera playlist.
2. **Contenuti privati/protetti:** non sono supportati (niente login, niente cookie).
3. **Geo-restrizioni:** se il sito blocca per area geografica, l’app mostrerà un messaggio di errore (es. “Video non disponibile nella tua area geografica”).
4. **Siti non in lista:** yt-dlp supporta molti altri siti; se un sito non è in questa lista, può comunque funzionare (embed/generic), ma non è garantito né testato in questa versione.

---

## Lista completa yt-dlp

L’elenco ufficiale di tutti gli extractor (anche non “sicuri” o attualmente broken) è qui:

- [supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

Alcuni siti in quella lista sono marcati come **Currently broken**; non sono inclusi nella tabella “Siti sicuri” sopra.

---

## Versione e aggiornamenti

- **App:** 1.0.0  
- **yt-dlp:** `yt-dlp[default]>=2024.1.0` (requirements.txt)

Se un sito smette di funzionare (es. cambio API), aggiornare yt-dlp; in casi estremi usare la build nightly come da [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md).
