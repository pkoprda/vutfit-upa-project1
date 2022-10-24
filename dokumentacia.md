# Ukladanie rozsiahlych dát v~NoSQL databázach

Autori:

- Ivan Halomi (xhalom00)
- Peter Koprda (xkoprd00)
- Adam Múdry (xmudry01)

## Analýza zdrojových dát a návrh ich uloženia v~NoSQL databázi

### Analýza zdrojových dát

Cestovné poriadky verejnej dopravy je možné získať zo~stránok Ministerstva dopravy Českej republiky~\footnotetext{\url{https://portal.cisjr.cz/pub/draha/celostatni/szdc/}}. Na týchto stránkach sa dá nájsť aj~popis týchto dát, ktoré hovoria o tom, aký formát dát používajú jednotlivé súbory. Súbory sú rozdelené do~hlavných zložiek, kde jedna zložka obsahuje dáta pre obdobie od 1.~decembra predchádzajúceho roka do~30.~novembra aktuálneho roka. Hlavný súbor v~tejto zložke obsahuje najdôležitejšie dáta na spracovanie a~je komprimovaný pomocou Zip. Nachádzajú sa v~ňom súbory vo~formáte \texttt{*.xml}, kde každý súbor obsahuje jednu správu \texttt{CZPTTCISMessage}. Detailný popis štruktúry XML dokumentov je popísaný v~PDF dokumente dostupnom na~webe dopravcu~\footnotetext{\url{https://portal.cisjr.cz/pub/draha/celostatni/szdc/Popis%20DJ%C5%98_CIS_v1_09.pdf}}.

Jednotlivé správy \texttt{CZPTTCISMessage} obsahujú dátové informácie o~cestovných poriadkoch vlaku osobnej dopravy. Je rozdelená na päť častí:
\begin{enumerate}
  \item \texttt{Identifiers} - pole identifikátorov, ktoré obsahuje
  \begin{itemize}
    \item 0 až N elementov \texttt{PlannedTransportIdentifiers}
    \item 0 až N elementov \texttt{RelatedPlannedTransportIdentifiers}
  \end{itemize}
  Identifikátory uvedené v~obidvoch elementoch majú zhodnú štruktúru
  \item \texttt{CZPTTCreation}
  \item \texttt{CZPTTHeader}
  \item \texttt{CZPTTInformation}
  \item \texttt{NetworkSpecificParameter}
\end{enumerate}


### Návrh spôsobu uloženia

...

### Zvolená NoSQL databáza

Zvolili sme NoSQL databázu MongoDB, ktorá dáta ukladá ako~štruktúrované dokumenty vo~formáte BSON, čo je binárna reprezentácia formátu JSON.
Dáta sú zlúčené do~kolekcii, ktoré sú ekvivalent tabuľky systému riadenia báze dát (SRBD) relačnej databázy.
Pôvodné dáta sú vo~formáte XML, ktorý je taktiež štruktúrovaný a~prevediteľný na formát JSON alebo typ premennej "slovník" (asociatívne pole) v~Pythone s~ktorými vieme jednoducho pracovať.
MongoDB ponúka rôznu funkcionalitu, ako napríklad vytváranie indexov na zrýchlenie vyhľadávania určitých dát, špecifikovanie pravdiel jazyka pri porovnávaní reťazcov pri vyhľadávaní v~dátach, . 

## Návrh, implementácia a použitie aplikácie

### Návrh aplikácie
\paragraph{Získavanie dát:}
Aplikácia by pri prvom spustení mala stiahnuť všetky dáta a~vložiť ich do~databázy. Tieto dáta sú voľne dostupné na stránke\footnotemark. Dáta sa na stranke nachádzajú v~dvoch formách. Prvou, tou podstatnejšou, je súbor GVD2022 vo~formáte .zip, ktorý obsahuje všetky naplánované spoje na celý rok. Ďalej sa tam nachádzajú úpravy, zmeny a~náhrady spojov počas roka. Tieto súbory sú rozdelené do~adresárov podľa mesiacov a~sú na stránku nahrávané počas roka. Súbory sú vo~formáte .xml.zip, avšak v~skutočnosti ide o formát .xml.gzip. Od aplikácie sa očakáva, že stiahne všetky tieto dáta, spracuje ich do~vhodného formátu, nahrá spoje do~databázy a~následne aplikuje na ne získané úpravy a~náhrady spojov.
\footnotetext{\url{https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/}}


\paragraph{Vyhľadávanie spojov:}
Aplikácia by mala byť schopná vyhľadať vlakové spojenie pomocou zadaných informácií. Tieto informácie sú: počiatočná stanica, cieľová stanica, dátum a~čas. Zobrazené by mali byť spoje, ktoré idú vo~zvolený dátum z~počiatočnej stanice po zvolenom čase a~zastavujú v~cieľovej stanici. Zobrazujeme názov stanice a~čas odchodu vlaku, z~počiatočnej stanice, cieľovej stanice a~takisto všetkých staníc, v~ktorých vlak zastavuje medzi nimi. 
Potrebné informácie, ktoré potrebujeme získať z~databázy:
\textbf{názov stanice, čas odchodu zo~stanice, akciu vlaku v~danej stanici, bitmapu s~dňami kedy vlak jazdí, platnosť tejto bitmapy}

Zvolená MongoDB umožňuje vytvárať query pomocou agregačných pipelines, tie slúžia na spracovanie veľkého množstva \uv{dokumentov} v~kolekcii pomocou postupného filtrovania a~posúvania ich do~ďalšej fázy. Agregačná pipeline pre najrýchlejšie vyhľadanie bude fungovať nasledovne:
\begin{enumerate}
    \item Odfiltrovanie neplatných dát v~daný dátum
    \item Odfiltrovanie ciest, ktoré neobsahujú počiatočnú a~cieľovú stanicu
    \item Odfiltrovanie ciest, ktoré sú v~počiatočnej stanici neskôr ako v~zvolený čas
\end{enumerate}
Tento výsledok obsahu je všetky spoje, ktoré sú platné v~daný dátum a~prechádzajú(nie nutne stoja) hľadanými stanicami v~oboch smeroch. Preto je ešte potrebné skontrolovať či vlak stojí v~hľadaných staniciach. a~taktiež pomocou bitmapy či vlak skutočne v~daný deň danú trasu ide. Tieto informácie však nie je vhodné kontrolovať v~agregačnej pipeline z~dôvodu zložitosti. Preto sa o to bude starať aplikácia. Ako prvé skontrolujeme či spoj v~daný spoj premáva. Teda v~bitmape je na \textbf{n-tom} mieste nastavený znak \uv{1}. Číslo \textbf{n} získame ako rozdiel v~dňoch medzi začiatkom platnosti a~hľadaným dátumom. Ak spoj nepremáva, ďalej nepokračujeme a~ideme na ďalší vrátený spoj. Následovne budeme hľadať počiatočnú a~cieľovú stanicu. v~úvahu budeme brať len stanice, ktoré obsahujú slovník \uv{TranActivity}( môže priamo obsahovať slovník s~kľúčom \uv{TrainActivityType} alebo pole slovníkov obsahujúcich \uv{TrainActivityType} v~prípade viacerých akcií v~jednej stanici. Pomocou neho zistíme, či vlak v~stanici stojí pre nástup a~výstup cestujúcich. Ak je stanica počiatočná, vlak v~nej stojí a~zároveň ešte nebola nájdená cieľová stanica, teda ideme dobrým smerom, začneme konkatenovať do~výsledného textu nasledovné informácie: názov stanice, čas odchodu vlaku z~danej stanice až pokým nenájdeme cieľovú stanicu. Ak v~cieľovej stanici taktiež existuje akcia na nástup a~výstup cestujúcich, výsledný text zobrazíme na výstup. v~opačnom prípade pokračujeme v~kontrole ďalšieho spoja, ak nejaký ešte je.

### Implementacia 
\chapter{Implementácia}
\paragraph{Získanie dát}Všetko potrebné k stiahnutiu dát sa nachádza v~súbore \textbf{download\_data.py}. Ide o fuknciu \textit{download\_page()}, ktorá získa obsah stránky pomocou \textit{requestu} z~knižnice \textbf{urllib}. Obsah stránky sa následne spracuje pomocou knižnice \textbf{BeautifulSoup}. Získajú sa všetky odkazy, ktoré sa buď stiahnu alebo ak ide o odkaz na podstránku, pre jednotlivé mesiace, pošlú sa do~funkcie \textit{get\_subpages(link, month)}. Tu je postup takmer identický, s~tým rozdielom, že už sa jedná len o súbory, ktoré jednoducho stiahneme.

\paragraph{Vyhľadávanie spojov}
Na vyhľadávanie spojov slúži funkcia \textit{find\_road(departure: str, target: str, start\_datetime: str)} v~\textbf{find\_data.py}. Funkcia príjma ako parametre názov stanice, v~ktorej má spoj začať, resp. má cez ňu prechádzať a~povolovať nástup a~výstup pasažierov, cieľovú stanicu v~ktorej vlak taktiež musí zastaviť. Dátum a~čas, po ktorom daný spoj vyráža zo~začiatočnej stanice. Uvažujeme, že zobrazujeme všetky spoje premávajúce v~daný dátum po danej hodine.

Na samotné vyhľadávanie využívame nasledujúcu agregačnú pipeline:
\lstset{language=Python}
\scriptsize{
\begin{lstlisting}
res = coll.aggregate(
[{
    '$match': {
        'CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.StartDateTime': {
            '$lte': start_datetime
        }
    }
}, {
    '$match': {
        'CZPTTCISMessage.CZPTTInformation.PlannedCalendar.ValidityPeriod.EndDateTime': {
            '$gte': start_datetime
        }
    }
}, {
    '$match': {
      'CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName': departure
    }
}, {
    '$match': {
      'CZPTTCISMessage.CZPTTInformation.CZPTTLocation.Location.PrimaryLocationName': target
    }
}, {
    '$match': {
        'CZPTTCISMessage.CZPTTInformation.CZPTTLocation.TimingAtLocation.Timing.Time': {
            '$gte': start_time
        }
    }
}])
\end{lstlisting}
}
\normalsize
Výsledky vrátené databázou, musíme ešte prefiltrovať aby sme odstránili spoje, ktoré nestoja v~daných staniciach alebo v~daný dátum nepremávajú. Takisto treba odstrániť spoje opačným smerom(cieľová stanica skôr ako počiatočná). Na toto filtrovanie využívame len jednoduché prechádzanie slovníkov a~pár podmienok. Pre zistenie či daný vlak v~daný dátum ide musíme získať \textbf{n-tý} symbol v~\uv{BitmapDays} a~porovnať či sa rovná \textit{'1'}. Kde číslo \textbf{n} je rozdielom dátumov. Keďže však dátumy uchovávame ako \textit{string}, je potrebné ho previesť na typ \textit{date}. Na tento prevod využívame funkciu \textit{strptime} z~knižnice \textbf{datetime}. Následne je možné dátumy od seba jednoducho odčítať, keďže vďaka pipeline vieme, že dátum je väčší ako začiatok platnosti dát a~menší ako koniec platnosti, a~výsledkom je \textbf{n}. Potom kontrolujeme stanice na trase, ak v~stanici nie je žiadna \uv{TrainActivity}, pokračujeme ďaľšou stanicou, keďže aj keby bola daná stanica hľadaná, tak tam vlak nezastavuje a~tým pádom nás nezaujíma. Ak \uv{TrainActivity} existuje tak porovnávame názov stanice s~počiatočnou alebo cieľovou. Ak nájdeme cieľovú stanicu, a~zároveň počiatočná ešte nebola nájdená, ide o spoj opačným smerom a~i pokračujeme na ďalší spoj. Ak nájdeme počiatočnú stanicu, začíname si ukladať názvy staníc a~odchod vlaku z~nich do~\textit{result\_text}. Ak nájdeme cieľovú stanicu a~je v~nej definovaná \uv{TrainActivity} \textit{result\_text} vypíšeme. Ak v~cieľovej stanici nie je definovaná \uv{TrainActivity} text nikdy nevypíšeme. Štruktúra vrátená \textit{coll.aggregate()} so zobrazením využívaných dát:
\footnotesize
\lstset{
    string=[s]{"}{"},
    stringstyle=\color{blue},
    comment=[l]{:},
    commentstyle=\color{black},
}
\begin{lstlisting}
"CZPTTCISMessage": {
    "CZPTTInformation": {
          "CZPTTLocation": [{
              "Location": {
                "PrimaryLocationName": Nazov stanice,
                },
                "TimingAtLocation": {
                    "Timing": [{
                      "Time": Cas odjazdu vlaku,
                    }]
                  },
                "TrainActivity": [{
                    "TrainActivityType:" Kod nastupu ludi- "0001"
                    }]
            }],
            "PlannedCalendar": {
                "BitmapDays": "1111100...111",
                "ValidityPeriod": {
                  "StartDateTime": "2021-12-13T00:00:00",
                  "EndDateTime": "2022-12-09T00:00:00"
                }
            }
        }
    }
\end{lstlisting}
\normalsize
### Spôsob používania 

Program je napísaný v jazyku Python a potrebné knižnice vypísané sú v súbore requirements.txt.
Nainštalovať je ich možné prostredníctvom programu pip:

\begin{lstlisting}
python -m pip install -r requirements.txt 
\end{lstlisting}

Príkaz python main.py -h zobrazí pomocnú správu s popisom argumentov programu.

Pred prvým spustením je potrebné spustiť MongoDB databázu a definovať jej prihlasovacie údaje v súbore process_data.py.
Následne môžme stiahnuť dáta:
\begin{lstlisting}
python main.py -d
\end{lstlisting}

A nahrať ich do databázy: 
\begin{lstlisting}
python main.py -s
\end{lstlisting}

Teraz program umožnuje prehľadávať databázu spojov. Napríklad:

\begin{lstlisting}
python main.py --from STANICA --to STANICA --date DATUM --time CAS
\end{lstlisting}

### Experimenty
