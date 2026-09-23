# dt-orders-api (shared sample application)

A deliberately small Flask + SQLite service used by the labs. This folder holds the **secure baseline**.
Labs that need an insecure variant ship it in their own `starter/` folder and label the weakness clearly.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python app.py   # http://127.0.0.1:8080/health
```

All data is synthetic. Do not deploy this service outside a disposable lab environment.
