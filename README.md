# UPA projekt, 1. časť: ukladanie rozsiahlych dát v NoSQL databázach

**Názov tímu:** FIT gigachads 🍆

**Autori**:

- Bc. Ivan Halomi <xhalom00@stud.fit.vutbr.cz>
- Bc. Peter Koprda <xkoprd00@stud.fit.vutbr.cz>
- Bc. Adam Múdry <xmudry01@stud.fit.vutbr.cz>

## Použitie programu:
```
$ python main.py [-h] [-d] [-s] [--dont-save-fixes] [--drop-db] [--from STATION] [--to STATION] [-D DATE] [-T TIME]
```

### Argumenty:
```
-h, --help            ukáže túto pomocnú správu a skonči
-d, --download        stiahne dáta z webstránky
-s, --save            uloží dáta do NoSQL databáze
--dont-save-fixes     neukladaj opravy do databázy
--drop-db             odstráni databázu
--from STATION        východisková stanica
--to STATION          cieľová stanica
-D DATE, --date DATE  ukáž cestovné poriadky pre daný deň
                      DATE musí byť vo formáte YYYY-MM-DD
-T TIME, --time TIME  ukáž cestovné poriadky po tomto čase
                      TIME musí byť vo formáte hh:mm:dd (predvolene: 00:00:00)

```

### Príklady použitia:

<br />

Príkaz
```
$ python main.py --from Fulnek --to "Suchdol nad Odrou" --date 2021-12-21
```
vypíše všetky vlaky, ktoré premávajú 21. decembra 2021 z obce Fulnek do obce Suchdol nad Odrou.

<br />

Príkaz
```
$ python main.py --from "Praha hl. n." --to Praha-Cibulka --date 2022-09-01 --time 20:30:00
```
vypíše všetky vlaky, ktoré premávajú 1. septembra 2022 po 20. hodine a 30. minúte zo stanice Praha hl. n. do stanice Praha-Cibulka.
