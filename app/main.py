from fastapi import FastAPI

app = FastAPI(title="API d'administration de conteneurs")


@app.get("/health")
def sante():
    return {"status": "ok"}