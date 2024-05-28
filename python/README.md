Virtuales Environment nur einmalig erzeugen:
python -m venv env

zeigt aktuelles Verzeichnis:
pwd 

Zu env Verzeichnis wechseln mit:
cd Pizza-Dataset
cd Python
.\env\Scripts\activate

requirements installieren:
pip install -r requirements.txt


Programmausführung
1. backend starten:
uvicorn main:app --reload

2. frontend starten:
streamlit run app.py

