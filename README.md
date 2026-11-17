# GoByde Tech

GoByde Tech is an independent mobile game and app studio based in Romania.

We create focused digital products with clear ideas, distinctive personalities, and experiences that respect people's time. Our goal is to make games and apps that are easy to understand, enjoyable to use, and worth coming back to.

## What we build

We work on mobile-first products that combine thoughtful design with simple, satisfying interactions.

Our approach is guided by three principles:

- **Start simple.** A good idea should be easy to understand.
- **Make it feel good.** Every interaction, screen, and response should have a purpose.
- **Respect people's time.** Products should fit naturally into everyday life.

## Aura Clicker

Aura Clicker is our first mobile game.

It is a casual incremental experience built around short sessions, clear progression, character customization, collectible pets, upgrades, and offline progress. Players collect Aura, develop their character, unlock new areas, and choose how they want to grow.

Aura Clicker is available on [Google Play](https://play.google.com/store/apps/details?id=com.gobyde.aurafarmer) and the [App Store](https://apps.apple.com/ro/app/aura-clicker/id6819347587?l=ro).

## Looking ahead

Aura Clicker is only the beginning. GoByde Tech is building a foundation for more original mobile games and useful apps, each with its own identity and a clear reason to exist.

We prefer to share real progress instead of making early promises. New projects will be announced when they are ready.

## Contact

For general enquiries, partnerships, or project discussions, contact us at [support@gobyde.com](mailto:support@gobyde.com).

## Company

- **Legal name:** Gobyde Tech SRL
- **Country:** Romania

© 2026 Gobyde Tech SRL. All rights reserved.

## Development notes

The site is static and served by Cloudflare (`wrangler.jsonc`). URLs are extensionless (`/aura-clicker`, not `/aura-clicker.html`).

- **Bilingual pages.** The Romanian pages (`index.html`, `aura-clicker.html`, `turning-tails.html`) are the source of truth. The English versions in `en/` are generated from them with the dictionary in `script.js`. After editing those pages or `translations.en`, run `python3 tools/build_en.py` (needs `python3` and `node`). `python3 tools/build_en.py --check` tells you if `en/` is out of date.
- **Privacy policy pages** are not part of that generator and are translated in the browser by `script.js`.
- `sitemap.xml` lists all public URLs with `hreflang` alternates. Update it when a page is added.
- `_redirects` holds permanent redirects (for example `/aura-farm` to `/aura-clicker`).
