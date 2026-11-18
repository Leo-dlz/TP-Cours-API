import json
import os

import requests
from fastapi import FastAPI

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
TIMEOUT = 5
LABEL = "adminapi.managed=true"

app = FastAPI(title="API d'administration de conteneurs")


def formater(c):
    """Met un conteneur Docker au format du contrat."""
    return {
        "id": c["Id"],
        "name": c["Names"][0].lstrip("/"),
        "image": c["Image"],
        "state": c["State"],
    }


@app.get("/health")
def sante():
    return {"status": "ok"}


@app.get("/containers")
def lister_containers():
    reponse = requests.get(
        f"{DOCKER}/containers/json",
        params={"all": "true", "filters": json.dumps({"label": [LABEL]})},
        timeout=TIMEOUT,
    )
    reponse.raise_for_status()
    return [formater(c) for c in reponse.json()]