# Wander Remote — Navod na pouzitie

## Co to je?

Wander Remote ti umozni ovladat pocitac na dialku z hocijakeho prehliadaca. Vidis jeho obrazovku a mozes ovladat mys aj klavesnicu — akoby si sedel priamo za nim.

Sklada sa z dvoch casti:

- **Host** — program ktory nainstalujete na pocitac, ktory chcete ovladat
- **Viewer** — webova stranka, z ktorej budete ovladat host pocitac

---

## 1. Instalacia Host aplikacie

Host aplikaciu nainstalujete na pocitac, ktory chcete ovladat na dialku.

### Mac (Apple Silicon — M1/M2/M3/M4)

1. Otvorte subor **Wander Remote Host-1.0.0-arm64.dmg**
2. Presunte ikonu **Wander Remote Host** do priecinka **Applications**
3. Otvorte aplikaciu z Applications
4. Ak sa zobrazi hlaska "aplikaciu nie je mozne otvorit" — kliknite pravym tlacidlom na ikonu → **Otvorit** → **Otvorit**

### Mac (Intel)

1. Otvorte subor **Wander Remote Host-1.0.0.dmg**
2. Presunte ikonu **Wander Remote Host** do priecinka **Applications**
3. Otvorte aplikaciu z Applications
4. Ak sa zobrazi hlaska "aplikaciu nie je mozne otvorit" — kliknite pravym tlacidlom na ikonu → **Otvorit** → **Otvorit**

### Windows

1. Spustite subor **Wander Remote Host Setup 1.0.0.exe**
2. Instalator sa spusti automaticky
3. Po instalacii sa aplikacia spusti sama

---

## 2. Povolenie pristupnosti (DOLEZITE!)

Aby aplikacia mohla ovladat mys a klavesnicu, musite jej dat povolenie v nastaveniach systemu. **Bez tohto kroku nebude fungovat ovladanie.**

### Mac

1. Otvorte **Nastavenia systemu** (System Settings)
2. Chodte do **Sukromie a bezpecnost** (Privacy & Security)
3. Kliknite na **Pristupnost** (Accessibility)
4. Kliknite na zamok vlavo dole a zadajte heslo
5. Kliknite **+** a pridajte aplikaciu **Wander Remote Host**
6. Uistite sa ze je zaskrtnuta (zapnuta)

Ak pouzivate Terminal na spustenie, pridajte aj **Terminal** do zoznamu.

### Windows

Na Windows sa zobrazi vyskakovacie okno s otazkou ci chcete povolit pristup. Kliknite **Ano**.

---

## 3. Spustenie Host aplikacie

1. Otvorte **Wander Remote Host**
2. Pocajte kym sa zobrazi **Session ID** (6-miestne cislo) a **Heslo**
3. Tieto udaje budete potrebovat na pripojenie z viewera

Priklad:

```
Session ID: 439554
Heslo:      0ecf30
```

Aplikaciu nechajte otvorenu — kym bezi, pocitac je dostupny na dialku.

---

## 4. Pripojenie z Viewera (ovladanie na dialku)

Toto robite na pocitaci alebo telefone, z ktoreho chcete ovladat host.

1. Otvorte prehliadac (Chrome, Safari, Firefox, Edge)
2. Chodte na adresu: **https://remote.wanderhub.tech**
3. Zadajte **Session ID** ktore vidite v Host aplikacii
4. Zadajte **Heslo** ktore vidite v Host aplikacii
5. Kliknite **Pripojit sa**

Po pripojeni uvidite obrazovku host pocitaca. Teraz mozete:

- **Pohybovat mysou** — pohybujte mysou po obrazovke
- **Klikat** — kliknutie sa prenese na host pocitac
- **Pisat na klavesnici** — stlacenia klavesov sa prenesú na host
- **Scrollovat** — kolieskom mysi

---

## 5. Odpojenie

- **Viewer**: Kliknite tlacidlo **Odpojit** v hornom paneli alebo zavrite prehliadac
- **Host**: Zavrite okno aplikacie Wander Remote Host

---

## Caste otazky

### Nevidim kurzor mysi na remote obrazovke

To je normalne — kurzor sa nezobrazuje v prenose. Na obrazovke je cerveny krizik ktory ukazuje kde sa nachadza vasa mys.

### Mys sa nehybe / klavesnica nefunguje

Skontrolujte ci mate povolenu **Pristupnost** v nastaveniach systemu (pozri krok 2).

### Pripojenie zlyhalo

- Skontrolujte ci je Host aplikacia spustena
- Skontrolujte ci ste zadali spravne Session ID a Heslo
- Skontrolujte ci mate pripojenie na internet

### Obraz je pomaly / trha sa

- Skuste znizit kvalitu v nastaveniach viewera
- Overte ci mate stabilne internetove pripojenie na oboch stránach

### Mozem pouzit Viewer na telefone?

Ano! Otvorte `https://remote.wanderhub.tech` v prehliadaci na telefone. Mozete ho aj "pridat na plochu" pre rychlejsi pristup (PWA).

---

## Bezpecnost

- Kazda session ma unikatne Session ID a Heslo
- Po zatvoreni Host aplikacie sa session ukoncí
- Vsetka komunikacia prebieha cez sifrovane spojenie (WSS/HTTPS)

---

*Powered by Tulave kino*
