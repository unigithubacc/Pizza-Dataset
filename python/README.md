zeigt aktuelles Verzeichnis:
pwd 

Zu python Verzeichnis bzw. Ordner wechseln mit:
cd Python

Virtuale Umgebung nur einmalig (im python) ordner erzeugen:
python -m venv env

zeigt aktuelles Verzeichnis:
pwd 

Zu env Verzeichnis wechseln mit:
cd Pizza-Dataset
cd Python

env Verzeichnis aktivieren mit:
.\env\Scripts\activate

requirements installieren:
pip install -r requirements.txt

Programmausführung
1. backend starten:
(man muss im \Pizza-Dataset Ordner sein)
uvicorn python.main:app --reload

2. frontend starten:
(man muss im \Pizza-Dataset\Python Ordner sein)
streamlit run app.py

