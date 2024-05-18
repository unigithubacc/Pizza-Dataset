import psycopg2

try:
    # Erstellen einer Verbindung zur Datenbank
    conn = psycopg2.connect(database="pizza_data", user="postgres", password="ProLab895+", host="localhost", port="5432")
    print("Datenbankverbindung erfolgreich hergestellt.")
    
    # Erstellen eines Cursor-Objekts, um SQL-Befehle auszuführen
    cur = conn.cursor()
    
    # Ausführung einer SQL-Abfrage, um alle Zeilen aus der Tabelle 'stores' abzurufen
    cur.execute("SELECT * FROM stores;")
    print("SQL-Abfrage ausgeführt.")
    
    # Abrufen aller Ergebnisse
    rows = cur.fetchall()
    
    # Durchlaufen aller Zeilen und Ausgabe der Daten
    for row in rows:
        print(row)
    
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
finally:
    # Schließen der Verbindung zur Datenbank
    if conn:
        conn.close()
        print("Verbindung zur Datenbank erfolgreich geschlossen.")