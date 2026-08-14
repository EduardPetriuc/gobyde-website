# GoByde website

Website static de prezentare pentru studioul GoByde și jocurile sale. Pagina principală funcționează ca hub, iar fiecare joc publicat are propria pagină de prezentare.

## Rulare locală

Nu există dependențe sau pas de build. Deschide `index.html` direct sau pornește un server local:

```bash
python3 -m http.server 8080
```

Apoi vizitează `http://localhost:8080`.

## Publicare

Conținutul repository-ului poate fi publicat direct pe GitHub Pages, Netlify, Vercel sau Cloudflare Pages. Directorul de publicare este rădăcina proiectului, fără comandă de build.

## Înainte de lansare

- Înlocuiește `hello@gobyde.com` dacă adresa oficială este diferită.
- Adaugă linkurile reale Google Play și App Store după publicarea jocului.
- Adaugă domeniul final în metadatele Open Graph dacă site-ul primește un domeniu propriu.

## Structură

- `index.html` — conținut, SEO și structură semantică
- `aura-farm.html` — pagina dedicată jocului Aura Farm
- `styles.css` — design responsive și animații
- `script.js` — traduceri RO/EN, meniu mobil și reveal animations
- `assets/` — imagini optimizate din Aura Farm
