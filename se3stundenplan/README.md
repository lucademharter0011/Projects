# SE3Stundenplan

[![pipeline status](https://gitlab.mi.hdm-stuttgart.de/ls282/se3stundenplan/badges/main/pipeline.svg)](https://gitlab.mi.hdm-stuttgart.de/ls282/se3stundenplan/-/commits/main)

## Kurzbeschreibung

Dies ist eine vollständige Webanwendung zur Verwaltung von Stundenplänen. Das Projekt besteht aus einem **Backend-API-Service**, der mit Python (Flask) und einer MySQL-Datenbank erstellt wurde, und einem interaktiven **Frontend**, das auf Next.js (React) und TypeScript basiert.

Benutzer können sich registrieren, anmelden, ihr Profil verwalten und ihre Kurse in einer übersichtlichen Kalenderansicht einsehen.

## Installation und Start

Um das Projekt lokal auszuführen, können sowohl das Backend als auch das Frontend separat eingerichtet und gestartet werden. Alternative kann man mit
`make install` alle Dependencies installieren. Das Datenbank Setup muss man selber ausführen.

### **Voraussetzungen**

- Node.js und npm (oder ein anderer Paketmanager)
- Python 3.x und pip
- Ein laufender MySQL-Server

### Start im Schnelldurchgang

```shell
make install

cd backend

# .env für MySQL konfigurieren

.venv/bin/python database_setup.py full

cd ..

npm run dev

# localhost:3000/ aufrufen
```

### **1. Backend (API-Server)**

1.  **Navigiere ins Backend-Verzeichnis**:

    ```shell
    cd backend
    ```

2.  **Richte eine virtuelle Umgebung ein und installiere die Python-Abhängigkeiten**:

    ```shell
    # Virtuelle Umgebung erstellen
    python -m venv venv

    # Aktivieren (macOS/Linux)
    source venv/bin/activate
    # Aktivieren (Windows)
    # venv\Scripts\activate

    # Abhängigkeiten installieren
    pip install -r requirements.txt
    ```

3.  **Konfiguriere die Datenbank**:

    - Erstelle eine Datei namens `.env` im `backend`-Verzeichnis.
    - Füge die Zugangsdaten zur MySQL-Datenbank hinzu. Das Skript `database_setup.py` wird diese Variablen verwenden.

    ```env
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_USER=dein_mysql_benutzer
    MYSQL_PASSWORD=dein_passwort
    MYSQL_DB=stundenplan_db
    JWT_SECRET_KEY=ein_sehr_geheimer_schluessel
    ```

    Führe diesen Befehl aus, um die Datenbank mit Tabellen und Testdaten zu befüllen.

    ```shell
    python database_setup.py full
    ```

    Für eine Übersicht an verfügbaren Commands:

    ```shell
    python database_setup.py
    ```

4.  **Starte das Backend**:

    ```bash
    python run.py
    ```

    Die API ist jetzt unter `http://127.0.0.1:5000` erreichbar.

### **2. Frontend (Next.js-Anwendung)**

1.  **Navigiere in einem neuen Terminal ins Frontend-Verzeichnis**:

    ```bash
    cd frontend
    ```

2.  **Installiere die Node.js-Abhängigkeiten**:

    ```bash
    npm install
    ```

3.  **Konfiguriere die Umgebungsvariablen**:

    - Füge die URL der Backend-API und ein Secret + URL für NextAuth

      ```env
      NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api
      NEXTAUTH_URL=http://localhost:3000
      NEXTAUTH_SECRET=ein_anderer_sehr_geheimer_schluessel
      ```

4.  **Starte das Frontend**:

    ```bash
    npm run dev
    ```

    Die Webanwendung ist jetzt unter `http://localhost:3000` verfügbar.

## Nutzung mit Testdaten

1.  Öffne `http://localhost:3000` in deinem Browser.
2.  Du wirst zur **Login-Seite** weitergeleitet.
3.  Logge dich mit dem Benutzernamen `demo_student` und dem Passwort `demo123` ein.
4.  Nach der Anmeldung siehst du die Hauptansicht mit dem Kalender. Wähle den Stundenplan `Wintersemester 2024/25`.
5.  Dein Profil kannst du über das Benutzermenü oben rechts aufrufen.

## Nutzung

1.  Öffne `http://localhost:3000` in deinem Browser.
2.  Du wirst zur **Login-Seite** weitergeleitet.
3.  Erstelle ein neues Konto über den **Registrierungslink**.
4.  Nach der Anmeldung siehst du die Hauptansicht mit dem Kalender. Hier kannst du deine Stundenpläne verwalten und Kurse einsehen.
5.  Dein Profil kannst du über das Benutzermenü oben rechts aufrufen.

## Bekannte Bugs und Fehler

- **SQLAlchemy error während dem Starten des backends**
  -> manueller SQLAlchemy & Flask uninstall und manueller install mit den richtigen Versionsnummern

  ```bash
  pip uninstall SQLAlchemy Flask-SQLAlchemy -y
  pip install SQLAlchemy==1.4.53
  pip install Flask-SQLAlchemy==3.0.5
  ```
