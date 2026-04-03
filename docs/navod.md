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

1. Stiahnite subor **Wander Remote Host-1.0.0-arm64.dmg**
2. Otvorte stiahnuty subor
3. Presunte ikonu **Wander Remote Host** do priecinka **Applications**
4. Otvorte aplikaciu z Applications

### Mac (Intel)

1. Stiahnite subor **Wander Remote Host-1.0.0.dmg**
2. Otvorte stiahnuty subor
3. Presunte ikonu **Wander Remote Host** do priecinka **Applications**
4. Otvorte aplikaciu z Applications

### Windows

1. Stiahnite a spustite subor **Wander Remote Host Setup 1.0.0.exe**
2. Instalator sa spusti automaticky
3. Po instalacii sa aplikacia spusti sama

---

## 2. Povolenia (DOLEZITE!)

Aby aplikacia mohla snimat obrazovku a ovladat mys/klavesnicu, musite jej dat povolenia. **Bez tohto kroku nebude fungovat.**

Pri prvom spusteni vas aplikacia automaticky vyzve na udelenie povoleni.

### Mac — Pristupnost (Accessibility)

Toto povolenie umoznuje ovladanie mysi a klavesnice.

1. Po spusteni sa zobrazi dialog s vyzvou
2. Kliknite **Otvorit nastavenia**
3. V System Settings > Sukromie a bezpecnost > Pristupnost
4. Najdite **Wander Remote Host** a zapnite prepinac
5. Restartujte aplikaciu

### Mac — Nahravanie obrazovky (Screen Recording)

Toto povolenie umoznuje snimanie obrazovky.

1. Po spusteni sa zobrazi dialog s vyzvou
2. Kliknite **Otvorit nastavenia**
3. V System Settings > Sukromie a bezpecnost > Nahravanie obrazovky
4. Kliknite **+** dole a pridajte **Wander Remote Host** z Applications
5. Zapnite prepinac
6. Restartujte aplikaciu

### Windows

Na Windows sa zobrazi vyskakovacie okno s otazkou ci chcete povolit pristup. Kliknite **Ano**.

---

## 3. Pouzivanie Host aplikacie

1. Otvorte **Wander Remote Host**
2. Zobrazi sa okno s vasim **Host ID** (6-miestne cislo) a **Heslom**
3. Tieto udaje su trvale — nemenia sa ani po restarte alebo aktualizacii

Priklad:

```
Host ID: 439554
Heslo:   0ecf30
```

### Beh na pozadi

Aplikacia bezi na pozadi v systemovej liste (tray):

- **Tlacidlo "Skryt do pozadia"** — skryje okno, aplikacia bezi dalej
- **Zatvorenie okna (X)** — tiez len skryje do pozadia
- **Klik na ikonu v tray** — zobrazi/skryje okno
- **Pravy klik na tray** — menu so stavom a moznostou ukoncit
- **"Ukoncit" v tray menu** — naozaj ukonci aplikaciu

### Aktualizacie

Aplikacia automaticky kontroluje dostupnost novych verzii pri kazdom spusteni. Ked je dostupna aktualizacia, zobrazi sa dialog s moznostou stiahnut a nainstalovat.

---

## 4. Pripojenie z Viewera (ovladanie na dialku)

Toto robite na pocitaci alebo telefone, z ktoreho chcete ovladat host.

1. Otvorte prehliadac (Chrome, Safari, Firefox, Edge)
2. Chodte na adresu: **https://remote.wanderhub.tech**
3. Zadajte **Host ID** ktore vidite v Host aplikacii
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
- **Host**: Kliknite **Ukoncit** v tray menu (zatvorenie okna len skryje do pozadia)

---

## Caste otazky

### Nevidim kurzor mysi na remote obrazovke

To je normalne — kurzor sa nezobrazuje v prenose. Na obrazovke je cerveny krizik ktory ukazuje kde sa nachadza vasa mys.

### Mys sa nehybe / klavesnica nefunguje

Skontrolujte ci mate povolenu **Pristupnost** v nastaveniach systemu (pozri krok 2).

### Pripojenie zlyhalo

- Skontrolujte ci je Host aplikacia spustena
- Skontrolujte ci ste zadali spravne Host ID a Heslo
- Skontrolujte ci mate pripojenie na internet

### Obraz je pomaly / trha sa

- Skuste znizit kvalitu v nastaveniach viewera
- Overte ci mate stabilne internetove pripojenie na oboch stránach

### Zmenilo sa mi Host ID alebo Heslo

Host ID a Heslo su trvale — viazu sa na zariadenie. Nemenia sa ani po restarte, aktualizacii alebo reinstalacii. Ak sa predsa zmenili, kontaktujte podporu.

### Mozem pouzit Viewer na telefone?

Ano! Otvorte `https://remote.wanderhub.tech` v prehliadaci na telefone. Mozete ho aj "pridat na plochu" pre rychlejsi pristup (PWA).

---

## Bezpecnost

- Kazde zariadenie ma unikatne Host ID a Heslo ktore sa nemeni
- Po ukonceni Host aplikacie sa session ukoncí a nikto sa nemoze pripojit
- Vsetka komunikacia prebieha cez sifrovane spojenie (WSS/HTTPS)

---

*Powered by Tulave kino*
