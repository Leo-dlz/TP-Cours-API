import os
import sys
import requests

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
TIMEOUT = 5

def lister_conteneurs(session):
    # TODO : GET {DOCKER}/containers/json avec all=true, timeout=TIMEOUT
    # TODO : renvoyer le JSON
    pass

def main():
    session = requests.Session()
    for c in lister_conteneurs(session):
        # TODO : afficher nom, image, état
        pass

if __name__ == "__main__":
    main()