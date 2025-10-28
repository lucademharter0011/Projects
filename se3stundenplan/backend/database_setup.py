#!/usr/bin/env python3
"""
Database Setup Script für Stundenplan Backend
Automatisches Setup von MySQL Datenbank mit Beispieldaten
"""

import os
import sys
from datetime import datetime, time, timedelta
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """MySQL Datenbank erstellen falls sie nicht existiert"""
    try:
        print("Erstelle MySQL Datenbank...")
        
        connection = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        db_name = os.environ.get('MYSQL_DB', 'stundenplan_db')
        
        # Datenbank erstellen
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Datenbank '{db_name}' erstellt/überprüft")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Fehler beim Erstellen der Datenbank: {e}")
        print("Stellen Sie sicher, dass MySQL läuft und die Zugangsdaten in .env korrekt sind")
        return False

def init_database():
    """Tabellen erstellen"""
    try:
        print("Erstelle Datenbank-Tabellen...")
        
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            # Alle Tabellen erstellen
            db.create_all()
            print("Tabellen erfolgreich erstellt")
            return True
            
    except Exception as e:
        print(f"Fehler beim Erstellen der Tabellen: {e}")
        return False

def create_sample_data():
    """Beispieldaten für Entwicklung erstellen"""
    try:
        print("Erstelle Beispieldaten...")
        
        from app import create_app, db
        from app.models import User, Timetable, Course, CourseComment, Notification, DegreeProgram
        
        app = create_app()
        with app.app_context():
            # Prüfen ob bereits Daten vorhanden
            if User.query.first():
                print("Datenbank enthält bereits Daten - überspringe Beispieldaten")
                return True
            
            # Demo User erstellen
            print("👤 Erstelle Demo-Benutzer...")
            demo_user = User(
                username="demo_student",
                email="demo@uni.de",
                full_name="Demo Student",
                student_id="12345",
                timezone="Europe/Berlin",
                notification_enabled=True,
                theme_preference="light"
            )
            demo_user.set_password("demo123")
            db.session.add(demo_user)
            db.session.flush()  # Um ID zu erhalten
            
            # Admin User erstellen
            admin_user = User(
                username="admin",
                email="admin@uni.de", 
                full_name="System Administrator",
                student_id="00000",
                timezone="Europe/Berlin",
                notification_enabled=True,
                theme_preference="dark"
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.flush()
            
            # Demo Stundenplan erstellen
            print("Erstelle Demo-Stundenplan...")
            demo_timetable = Timetable(
                user_id=demo_user.id,
                name="Wintersemester 2024/25",
                description="Mein Hauptstundenplan für das WS24/25",
                semester="WS24",
                year=2024,
                color_theme="blue",
                is_active=True
            )
            db.session.add(demo_timetable)
            db.session.flush()
            
            # Backup Stundenplan
            backup_timetable = Timetable(
                user_id=demo_user.id,
                name="Backup Stundenplan",
                description="Alternative Kurswahl",
                semester="WS24",
                year=2024,
                color_theme="green",
                is_active=False
            )
            db.session.add(backup_timetable)
            db.session.flush()
            
            # Demo Kurse erstellen
            print("Erstelle Demo-Kurse...")
            demo_courses = [
                {
                    'name': 'Mathematik I',
                    'code': 'MATH101',
                    'instructor': 'Prof. Dr. Schmidt',
                    'room': 'A1.01',
                    'day_of_week': 0,  # Montag
                    'start_time': time(8, 0),
                    'end_time': time(9, 30),
                    'course_type': 'Vorlesung',
                    'credits': 6,
                    'color': '#e74c3c',
                    'description': 'Grundlagen der Mathematik für Informatiker'
                },
                {
                    'name': 'Programmieren I',
                    'code': 'CS101',
                    'instructor': 'Prof. Dr. Müller',
                    'room': 'B2.05',
                    'day_of_week': 0,  # Montag
                    'start_time': time(10, 0),
                    'end_time': time(11, 30),
                    'course_type': 'Vorlesung',
                    'credits': 8,
                    'color': '#3498db',
                    'description': 'Einführung in die Programmierung mit Python'
                },
                {
                    'name': 'Datenbanken',
                    'code': 'DB101',
                    'instructor': 'Dr. Weber',
                    'room': 'C1.12',
                    'day_of_week': 1,  # Dienstag
                    'start_time': time(14, 0),
                    'end_time': time(15, 30),
                    'course_type': 'Vorlesung',
                    'credits': 5,
                    'color': '#2ecc71',
                    'description': 'Grundlagen relationaler Datenbanksysteme'
                },
                {
                    'name': 'Mathematik Übung',
                    'code': 'MATH101-UE',
                    'instructor': 'M.Sc. Fischer',
                    'room': 'A2.08',
                    'day_of_week': 2,  # Mittwoch
                    'start_time': time(8, 0),
                    'end_time': time(9, 30),
                    'course_type': 'Übung',
                    'credits': 0,
                    'color': '#e67e22',
                    'description': 'Übungen zu Mathematik I'
                },
                {
                    'name': 'Algorithmen und Datenstrukturen',
                    'code': 'ADS101',
                    'instructor': 'Prof. Dr. Klein',
                    'room': 'B1.15',
                    'day_of_week': 3,  # Donnerstag
                    'start_time': time(10, 0),
                    'end_time': time(11, 30),
                    'course_type': 'Vorlesung',
                    'credits': 6,
                    'color': '#9b59b6',
                    'description': 'Grundlegende Algorithmen und Datenstrukturen'
                },
                {
                    'name': 'Programmieren Praktikum',
                    'code': 'CS101-PRAK',
                    'instructor': 'M.Sc. Hoffmann',
                    'room': 'PC-Pool 1',
                    'day_of_week': 4,  # Freitag
                    'start_time': time(14, 0),
                    'end_time': time(17, 0),
                    'course_type': 'Praktikum',
                    'credits': 2,
                    'color': '#1abc9c',
                    'description': 'Praktische Programmierübungen'
                }
            ]
            
            for course_data in demo_courses:
                course = Course(
                    timetable_id=demo_timetable.id,
                    name=course_data['name'],
                    room=course_data['room'],
                    code=course_data['code'],
                    instructor=course_data['instructor'],
                    day_of_week=course_data['day_of_week'],
                    start_time=course_data['start_time'],
                    end_time=course_data['end_time'],
                    course_type=course_data['course_type'],
                    credits=course_data['credits'],
                    color=course_data['color'],
                    description=course_data['description'],
                    horst_url=f"https://horst.hochschule.de/{course_data['code'].lower()}",
                    is_active=True
                )
                db.session.add(course)
            
            db.session.flush()  # Um Course IDs zu erhalten
            
            # Demo Kommentare erstellen
            print("Erstelle Demo-Kommentare...")
            courses = Course.query.filter_by(timetable_id=demo_timetable.id).all()
            
            if courses:
                # Kommentar für Mathematik
                math_course = next((c for c in courses if 'Mathematik I' in c.name), None)
                if math_course:
                    comment1 = CourseComment(
                        course_id=math_course.id,
                        user_id=demo_user.id,
                        comment="Skript auf Seite 45 besonders wichtig für die Klausur!",
                        comment_type="important",
                        is_private=True
                    )
                    db.session.add(comment1)
                
                # Kommentar für Programmieren
                cs_course = next((c for c in courses if 'Programmieren I' in c.name), None)
                if cs_course:
                    comment2 = CourseComment(
                        course_id=cs_course.id,
                        user_id=demo_user.id,
                        comment="Nächste Woche: Abgabe der ersten Programmieraufgabe",
                        comment_type="reminder",
                        is_private=True
                    )
                    db.session.add(comment2)
            
            # Demo Benachrichtigungen erstellen
            print("Erstelle Demo-Benachrichtigungen...")
            
            # Benachrichtigung für morgen
            tomorrow = datetime.now() + timedelta(days=1)
            notification1 = Notification(
                user_id=demo_user.id,
                course_id=courses[0].id if courses else None,
                title="Erinnerung: Mathematik I",
                message="Die Vorlesung 'Mathematik I' beginnt in 15 Minuten in Raum A1.01",
                notification_type="course_start",
                notify_time=tomorrow.replace(hour=7, minute=45, second=0),
                is_sent=False,
                is_read=False
            )
            db.session.add(notification1)
            
            # Info-Benachrichtigung
            notification2 = Notification(
                user_id=demo_user.id,
                title="Willkommen im Stundenplan-System!",
                message="Herzlich willkommen! Sie können hier Ihre Kurse verwalten, Benachrichtigungen einstellen und Stundenpläne importieren/exportieren.",
                notification_type="info",
                notify_time=datetime.now(),
                is_sent=True,
                is_read=False
            )
            db.session.add(notification2)
            
            # Studiengänge erstellen
            print("Erstelle Studiengänge...")
            degree_programs = [
                DegreeProgram(name="Informatik", code="INF", description="Bachelor of Science Informatik"),
                DegreeProgram(name="Wirtschaftsinformatik", code="WIN", description="Bachelor of Science Wirtschaftsinformatik"),
                DegreeProgram(name="Medieninformatik", code="MIN", description="Bachelor of Science Medieninformatik"),
                DegreeProgram(name="Cyber Security", code="CYS", description="Master of Science Cyber Security"),
                DegreeProgram(name="Data Science", code="DAS", description="Master of Science Data Science")
            ]
            
            for degree in degree_programs:
                db.session.add(degree)
            
            # Alle Änderungen speichern
            db.session.commit()
            
            print("Beispieldaten erfolgreich erstellt!")
            print("\n Demo-Zugangsdaten:")
            print("   Benutzer: demo_student")
            print("   Passwort: demo123")
            print("\n   Admin: admin") 
            print("   Passwort: admin123")
            
            return True
            
    except Exception as e:
        print(f"Fehler beim Erstellen der Beispieldaten: {e}")
        return False

def reset_database():
    """Datenbank zurücksetzen (alle Daten löschen)"""
    try:
        print("Setze Datenbank zurück...")
        
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Datenbank erfolgreich zurückgesetzt")
            return True
            
    except Exception as e:
        print(f"Fehler beim Zurücksetzen der Datenbank: {e}")
        return False

def check_database_connection():
    """Datenbankverbindung testen"""
    try:
        print("Teste Datenbankverbindung...")
        
        connection = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'stundenplan_db'),
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        print(f"Verbindung erfolgreich - MySQL Version: {version[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Datenbankverbindung fehlgeschlagen: {e}")
        return False

def print_usage():
    """Hilfe anzeigen"""
    print("\nStundenplan Database Setup")
    print("=" * 40)
    print("Verwendung: python database_setup.py [BEFEHL]")
    print("\nBefehle:")
    print("  create    - Nur Datenbank erstellen")
    print("  init      - Nur Tabellen erstellen")
    print("  sample    - Nur Beispieldaten hinzufügen")
    print("  full      - Vollständiges Setup (empfohlen)")
    print("  reset     - Datenbank zurücksetzen")
    print("  check     - Datenbankverbindung testen")
    print("  help      - Diese Hilfe anzeigen")
    print("\nBeispiel:")
    print("  python database_setup.py full")
    print("\nStellen Sie sicher, dass MySQL läuft und .env konfiguriert ist!")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    print("\n🎓 Stundenplan Database Setup")
    print("=" * 40)
    
    if command == "help":
        print_usage()
    
    elif command == "check":
        if check_database_connection():
            print("Datenbankverbindung funktioniert!")
        else:
            print("Bitte überprüfen Sie Ihre MySQL-Konfiguration")
    
    elif command == "create":
        if create_database():
            print("Datenbank erstellt!")
        else:
            print("Datenbank-Erstellung fehlgeschlagen")
    
    elif command == "init":
        if init_database():
            print("Tabellen erstellt!")
        else:
            print("Tabellen-Erstellung fehlgeschlagen")
    
    elif command == "sample":
        if create_sample_data():
            print("Beispieldaten hinzugefügt!")
        else:
            print("Beispieldaten-Erstellung fehlgeschlagen")
    
    elif command == "reset":
        confirm = input("Möchten Sie wirklich ALLE Daten löschen? (yes/no): ")
        if confirm.lower() == 'yes':
            if reset_database():
                print("Datenbank zurückgesetzt!")
        else:
            print("Vorgang abgebrochen")
    
    elif command == "full":
        print("Starte vollständiges Setup...")
        success = True
        
        if not create_database():
            success = False
        if success and not init_database():
            success = False
        if success and not create_sample_data():
            success = False
        
        if success:
            print("\nVollständiges Setup erfolgreich abgeschlossen!")
            print("\nSie können jetzt das Backend starten:")
            print("   python run.py")
        else:
            print("\nSetup fehlgeschlagen - bitte Fehler überprüfen")
    
    else:
        print(f"Unbekanntes Kommando: {command}")
        print_usage()

if __name__ == "__main__":
    main()