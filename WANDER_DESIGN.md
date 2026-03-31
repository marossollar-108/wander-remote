# Design System — Túlavé kino / Wandering Cinema

Zdroj: Dizajn manuál Túlavé kino (2020, Fiolab)

## Farby

Tri základné brandové farby: červená, čierna a biela.

### Brandové farby (z dizajn manuálu)

| Názov | HEX | RGB | Pantone | CMYK |
|---|---|---|---|---|
| **Červená** | `#EB002F` | 235, 0, 47 | 185C | C1 M100 Y88 K0 |
| **Čierna** | `#1A1A1A` | 26, 26, 26 | 419C | C73 M67 Y65 K78 |
| **Biela** | `#FFFFFF` | 255, 255, 255 | — | — |

### Odtiene červenej (z dizajn manuálu)

| Odtieň | HEX | Použitie |
|---|---|---|
| 100% | `#EB002F` | Tlačidlá, linky, aktívne stavy, CTA |
| 80% | `#EF3359` | Hover alternatíva na svetlom pozadí |
| 60% | `#F36683` | Aktívne/selected stavy, subtle accenty |
| 40% | `#F799AD` | Focus ring, light border accenty |
| 20% | `#FBCCD6` | Pozadia badges, notifikácie, subtle bg |

### Odtiene čiernej (z dizajn manuálu)

| Odtieň | HEX | Použitie |
|---|---|---|
| 100% | `#1A1A1A` | Hlavný text, nadpisy |
| 80% | `#484848` | Sekundárne tlačidlá, ikony |
| 60% | `#777777` | Sekundárny text, popisky |
| 40% | `#A5A5A5` | Muted text, placeholdery, disabled |
| 20% | `#D2D2D2` | Bordery, oddeľovače |

### Mapovanie na UI prvky

#### Primárne
- **Primary**: `#EB002F` — hlavné tlačidlá, aktívne stavy, linky, CTA
- **Primary hover**: `#C50028` — hover stav tlačidiel (tmavší)
- **Primary light**: `#FBCCD6` — pozadia badges, subtle highlights (červená 20%)
- **Primary ring**: `#F799AD` — focus ring na inputoch (červená 40%)

#### Sekundárne
- **Secondary**: `#484848` — sekundárne tlačidlá, menej dôležité akcie (čierna 80%)
- **Secondary hover**: `#1A1A1A` — hover sekundárnych tlačidiel (čierna 100%)

#### Systémové
- **Success**: `#10B981` — úspešné akcie, potvrdenia
- **Warning**: `#F59E0B` — upozornenia
- **Error**: `#EB002F` — chyby, validácia, mazanie (= primary červená)
- **Info**: `#3B82F6` — informačné hlášky

#### Neutrálne
- **Background**: `#FFFFFF` — hlavné pozadie stránky
- **Surface**: `#F5F5F5` — karty, panely, sidebary, tabuľka header
- **Border**: `#D2D2D2` — rámčeky, oddeľovače (čierna 20%)
- **Text primary**: `#1A1A1A` — hlavný text, nadpisy (čierna 100%)
- **Text secondary**: `#777777` — popisky, meta info (čierna 60%)
- **Text muted**: `#A5A5A5` — placeholdery, disabled stavy (čierna 40%)

### CSS Custom Properties (odporúčaný zápis)

```css
:root {
  /* Brand */
  --color-red: #EB002F;
  --color-red-80: #EF3359;
  --color-red-60: #F36683;
  --color-red-40: #F799AD;
  --color-red-20: #FBCCD6;
  --color-black: #1A1A1A;
  --color-black-80: #484848;
  --color-black-60: #777777;
  --color-black-40: #A5A5A5;
  --color-black-20: #D2D2D2;
  --color-white: #FFFFFF;

  /* UI mapovanie */
  --primary: var(--color-red);
  --primary-hover: #C50028;
  --primary-light: var(--color-red-20);
  --primary-ring: var(--color-red-40);
  --secondary: var(--color-black-80);
  --secondary-hover: var(--color-black);
  --success: #10B981;
  --warning: #F59E0B;
  --error: var(--color-red);
  --info: #3B82F6;
  --bg: var(--color-white);
  --surface: #F5F5F5;
  --border: var(--color-black-20);
  --text-primary: var(--color-black);
  --text-secondary: var(--color-black-60);
  --text-muted: var(--color-black-40);
}
```

## Typografia

### Font Family

Logotyp používa **Merengue Script** (komerčný font) — v UI sa nepoužíva, logo sa vkladá vždy ako SVG/PNG obrázok.

Pre UI sa používa **Montserrat** (sekundárne písmo z dizajn manuálu) — dostupný na Google Fonts.

- **Headings**: `Montserrat, system-ui, sans-serif`
- **Body**: `Montserrat, system-ui, sans-serif`
- **Monospace**: `JetBrains Mono, monospace` — kód, technické údaje

### Google Fonts import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

CSS import alternatíva:
```css
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
```

### Hierarchia písma (prepočítaná na web)

| Úroveň | Font | Veľkosť | Váha | Riadkovanie | Použitie |
|---|---|---|---|---|---|
| **h1** | Montserrat | 2rem (32px) | 700 (Bold) | 1.2 | Názov stránky |
| **h2** | Montserrat | 1.5rem (24px) | 700 (Bold) | 1.2 | Sekcie |
| **h3** | Montserrat | 1.25rem (20px) | 500 (Medium) | 1.2 | Podsekcie |
| **body** | Montserrat | 1rem (16px) | 400 (Regular) | 1.5 | Bežný text |
| **small** | Montserrat | 0.875rem (14px) | 400 (Regular) | 1.5 | Popisky, meta info |
| **caption** | Montserrat | 0.75rem (12px) | 300 (Light) | 1.5 | Drobné poznámky |

### CSS Custom Properties (fonty)

```css
:root {
  --font-heading: 'Montserrat', system-ui, sans-serif;
  --font-body: 'Montserrat', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

## Spacing a Layout

### Spacing škála (rem)
- `xs`: 0.25rem (4px)
- `sm`: 0.5rem (8px)
- `md`: 1rem (16px)
- `lg`: 1.5rem (24px)
- `xl`: 2rem (32px)
- `2xl`: 3rem (48px)

### Layout
- **Max šírka obsahu**: 1200px
- **Sidebar šírka**: 260px (ak existuje)
- **Padding stránky**: 1.5rem (desktop), 1rem (mobile)
- **Gap medzi kartami**: 1rem
- **Breakpointy**: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)

## Border Radius
- **Buttons**: 0.5rem (8px)
- **Cards**: 0.75rem (12px)
- **Inputs**: 0.375rem (6px)
- **Badges / chips**: 9999px (full rounded)
- **Modal**: 1rem (16px)

## Shadows
- **sm**: `0 1px 2px rgba(0,0,0,0.05)` — inputy, malé elementy
- **md**: `0 4px 6px rgba(0,0,0,0.07)` — karty, dropdowny
- **lg**: `0 10px 15px rgba(0,0,0,0.1)` — modály, floating panely

## Komponenty

### Tlačidlá
- **Primárne**: bg `#EB002F`, text `#FFFFFF`, hover bg `#C50028`
- **Sekundárne**: bg transparent, border `#1A1A1A`, text `#1A1A1A`, hover bg `#1A1A1A` + text `#FFFFFF`
- **Danger**: bg `#EB002F`, text `#FFFFFF` — len pre mazanie (rovnaké ako primary, s ikonou koša)
- **Disabled**: opacity 0.5, cursor not-allowed
- Padding: 0.5rem 1rem (default), 0.375rem 0.75rem (small)
- Font: Montserrat 500 (Medium)
- Border-radius: 0.5rem (8px)

### Inputy
- Border: 1px solid `#D2D2D2`
- Focus: border `#EB002F`, ring 2px `#F799AD`
- Placeholder: `#A5A5A5`
- Padding: 0.5rem 0.75rem
- Font: Montserrat 400
- Error stav: border `#EB002F`, chybová hláška pod inputom v `#EB002F`

### Karty
- Bg: `#FFFFFF`
- Border: 1px solid `#D2D2D2`
- Shadow: sm
- Padding: 1.5rem
- Hover (ak klikateľné): shadow md

### Tabuľky
- Header: bg `#F5F5F5`, font Montserrat 600, text `#777777`
- Riadky: border-bottom 1px `#D2D2D2`
- Hover riadku: bg `#F5F5F5`
- Padding bunky: 0.75rem 1rem

### Linky
- Farba: `#EB002F`
- Hover: underline
- Visited: `#C50028`

### Navbar / Header
- Svetlá verzia: bg `#FFFFFF`, border-bottom `#D2D2D2`, logo COLOR
- Tmavá verzia: bg `#1A1A1A`, text `#FFFFFF`, logo COLOR INVERSE alebo WHITE

### Notifikácie / Flash správy
- Plný riadok hore alebo toast v pravom hornom rohu
- Farba podľa typu: success `#10B981`, warning `#F59E0B`, error `#EB002F`, info `#3B82F6`
- Pozadie: príslušná farba pri 10% opacity
- Automaticky zmizne po 5s

## Ikonky
- Knižnica: Lucide Icons (odporúčaná) alebo Heroicons
- Veľkosť: 1.25rem (20px) default
- Farba: currentColor (dedí od textu)

## Stav: Loading, Empty, Error
- **Loading**: spinner vo farbe `#EB002F` alebo skeleton v `#F5F5F5`
- **Empty state**: ikonka + text "Žiadne záznamy" v `#777777` + CTA tlačidlo (primary)
- **Error state**: text v `#EB002F` + "Skúsiť znova" tlačidlo

## Dark Mode
- Nie (zatiaľ nie je potrebný)

## Brand Assets

Base URL: `https://www.tulavekino.sk/wp-content/uploads/2026/02/`

Preferuj SVG formát. PNG používaj len ako fallback alebo kde SVG nie je podporované.

### Wandering Point (ikona / značka)

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Wandering-POINT-COLOR.svg](https://kompas.tulavekino.sk/storage/4734/Wandering-POINT-COLOR.svg) | [Wandering-POINT-COLOR.png](https://kompas.tulavekino.sk/storage/4739/Wandering-POINT-COLOR.png) |
| **COLOR INVERSE** | [Wandering-POINT-COLOR-INVERSE.svg](https://kompas.tulavekino.sk/storage/4735/Wandering-POINT-COLOR-INVERSE.svg) | [Wandering-POINT-COLOR-INVERSE.png](https://kompas.tulavekino.sk/storage/4740/Wandering-POINT-COLOR-INVERSE.png) |
| **BLACK** | [Wandering-POINT-BLACK.svg](https://kompas.tulavekino.sk/storage/4733/Wandering-POINT-BLACK.svg) | [Wandering-POINT-BLACK.png](https://kompas.tulavekino.sk/storage/4738/Wandering-POINT-BLACK.png) |
| **RED** | [Wandering-POINT-RED.svg](https://kompas.tulavekino.sk/storage/4732/Wandering-POINT-RED.svg) | [Wandering-POINT-RED.png](https://kompas.tulavekino.sk/storage/4737/Wandering-POINT-RED.png) |
| **WHITE** | [Wandering-POINT-WHITE.svg](https://kompas.tulavekino.sk/storage/4731/Wandering-POINT-WHITE.svg) | [Wandering-POINT-WHITE.png](https://kompas.tulavekino.sk/storage/4736/Wandering-POINT-WHITE.png) |

### Logo EN — Horizontal

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.svg) | [Logo-EN-Cinema-Wandering-COLOR.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.svg) | [Logo-EN-Cinema-Wandering-BLACK.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-1.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.svg) | [Logo-EN-Cinema-Wandering-RED-1.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.svg) | [Logo-EN-Cinema-Wandering-WHITE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.png) |

### Logo EN — Vertical

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.svg) | [Logo-EN-Cinema-Wandering-BLACK-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.svg) | [Logo-EN-Cinema-Wandering-RED-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.svg) | [Logo-EN-Cinema-Wandering-WHITE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.png) |

### Logo SK — Horizontal

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.svg) | [Logo-EN-Cinema-Wandering-COLOR.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.svg) | [Logo-EN-Cinema-Wandering-BLACK.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-1.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.svg) | [Logo-EN-Cinema-Wandering-RED-1.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.svg) | [Logo-EN-Cinema-Wandering-WHITE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.png) |

### Logo SK — Vertical

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.svg) | [Logo-EN-Cinema-Wandering-BLACK-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.svg) | [Logo-EN-Cinema-Wandering-RED-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.svg) | [Logo-EN-Cinema-Wandering-WHITE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.png) |

### Logo HU — Horizontal

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.svg) | [Logo-EN-Cinema-Wandering-COLOR.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.svg) | [Logo-EN-Cinema-Wandering-BLACK.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-1.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.svg) | [Logo-EN-Cinema-Wandering-RED-1.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-1.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.svg) | [Logo-EN-Cinema-Wandering-WHITE.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE.png) |

### Logo HU — Vertical

| Varianta | SVG | PNG |
|---|---|---|
| **COLOR** | [Logo-EN-Cinema-Wandering-COLOR-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-vertical.png) |
| **COLOR INVERSE** | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.svg) | [Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR-INVERSE-vertical.png) |
| **BLACK** | [Logo-EN-Cinema-Wandering-BLACK-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.svg) | [Logo-EN-Cinema-Wandering-BLACK-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-BLACK-vertical.png) |
| **RED** | [Logo-EN-Cinema-Wandering-RED-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.svg) | [Logo-EN-Cinema-Wandering-RED-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-RED-vertical.png) |
| **WHITE** | [Logo-EN-Cinema-Wandering-WHITE-vertical.svg](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.svg) | [Logo-EN-Cinema-Wandering-WHITE-vertical.png](https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-WHITE-vertical.png) |

### Pravidlá použitia log
- **Svetlé pozadie**: používaj COLOR, BLACK alebo RED variantu
- **Tmavé pozadie**: používaj COLOR INVERSE alebo WHITE variantu
- **Favicon / malé rozmery**: používaj Wandering Point (ikona)
- **Header / navigácia**: používaj Logo Horizontal
- **Hero sekcie / splash**: používaj Logo Vertical
- **Minimálna veľkosť loga**: 120px šírka (horizontal), 80px šírka (vertical)
- **Ochranná zóna**: 0.5× výška logo symbolu na každú stranu — žiadne iné grafické prvky v tejto zóne
- **Zakázané**: nerozdeľovať logo na 2 riadky, neinvertovať, nemeniť písmo, nemeniť proporcie, nemeniť rozmer medzi symbolom a typom

## Poznámky
- Logotyp (text "Túlavé kino") používa font **Merengue Script** — komerčný font od Alejandra Paula. V UI sa nepoužíva, logo vždy ako obrázok.
- Dizajn manuál: Fiolab, 2020
- Sociálne siete: FB @tulavekino, IG tulave_kino
- Web: www.tulavekino.sk
