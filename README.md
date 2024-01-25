# PlanerFS 
![pfs_kal_b](https://github.com/fs-plugins/PlanerFS/assets/24637469/3735adc2-d45e-4a5c-8876-0c09f2463198)

für enigma2-Systeme, basierend auf Python 2 und Python 3
**_fast überall hilft die HELP-Taste !_**

## **eigene (und online-) ical - Dateien anzeigen (*.ics, Google-Kalender usw.)**
- iCal-Dateien und PlanerFS_online.txt im Ordner ‚etc/ConfFS‘ und einem einstellbaren Verzeichnis (intern, Mount) möglich
- URL's zu iCal-Dateien (z.B. Google, Cloud's): eintragen in Datei PlanerFS_online.txt (in ‚etc/ConfFS‘ oder einem einstellbaren Verzeichnis)
- externe Dateien nicht editierbar, Termine können aber importiert werden in den internen Kalender
- iCal-Dateien vom PlanerFS können problemlos auch mit anderer iCal-Software verwendet/bearbeitet werden
- deutsche Feiertage in den Online-Kalendern per default (kann entfernt werden)
- Schulferien (Menü -> Einstellungen -> Taste gelb ---> Neustart nach speichern erforderlich)
- Schichten (oder zB Belegung Ferienwohnung) anzeigen
- Meldung am TV unter Verwendung von 'VALARM'+'DISPLAY', bei Katergorie 'timer' keine Anzeige als Termin (zB medi-Timer)
- Sichern/Wiedeherstellen der ical-Dateien und Einstellungen
- Termine eines Kalender können separat angezeigt/bearbeitet werden, z.B. für Dienst- Bereitschaftsplan, Ferien usw. (Wechsel mit Bouquet-Taste)
- bei installiertem mspFS (Schichtplan) werden die Schichten im Kalender angezeigt
- auf Wunsch Anzeige aktuelle Termine bei Reciver-Start und/oder Uhrzeit, Anzeige auf ext. Displays mit LCD4Linux
- bewegliche christl. Feiertage können vom PlanerFS (wahlweise greg. oder jul.) berechnet und angezeigt werden

- Screens komplett skinfähig (Ausnahme: Farben für Ereignisse usw.),
Farben direkt im Programm wählbar, Ereignisse/Kategorien mit unterschiedlichen Farben enthalten: skins für SD, HD, fHD

## **Adressenkarten anzeigen und verwalten**
- Import von vcf-Dateien (sog. Visitenkarten-Daten)
- anlegen/editieren direkt im Plugin möglich
