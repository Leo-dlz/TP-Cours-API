import os
import sys
import requests

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
TIMEOUT = 5

def lister_conteneurs(session):
    reponse = session.get(
        f"{DOCKER}/containers/json",
        params={"all": "true"},
        timeout=TIMEOUT,
    )
    reponse.raise_for_status()
    return reponse.json()

def main():
    session = requests.Session()
    for c in lister_conteneurs(session):
        nom = c["Names"][0].lstrip("/")
        print(f"{nom:30} {c['Image']:30} {c['State']}")

if __name__ == "__main__":
    main()