# Kestrel returns-risk service
Needs Python 3.10+. No API key, no internet at run time.
```
pip install -r requirements.txt
uvicorn app:app --port 8000
```
Open http://localhost:8000 (screen). API: `POST /predict` (JSON order, see screen for fields), `GET /health`.
Bad input returns HTTP 422 with a message. `predictions.csv` is the test-set submission. `python train.py` retrains (needs the client CSVs in ./data, not included).
Note: `last_service_event_type` and `pickup_scheduled_at` are accepted but ignored (they are not known at dispatch).
