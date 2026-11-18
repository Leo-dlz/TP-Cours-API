import json
import os
import sys
from datetime import datetime, timezone

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

def stats_conteneur(session, conteneur_id):
    reponse = session.get(
        f"{DOCKER}/containers/{conteneur_id}/stats",
        params={"stream": "false"},
        timeout=TIMEOUT + 5,
    )
    reponse.raise_for_status()
    stats = reponse.json()

    cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
    delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
    delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
    pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0

    memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
    return round(pourcent, 2), round(memoire_mo, 1)

def releve_docker(session):
    resultat = []
    for c in lister_conteneurs(session):
        entree = {
            "id": c["Id"],
            "nom": c["Names"][0].lstrip("/"),
            "image": c["Image"],
            "etat": c["State"],
            "cpu_pourcent": None,
            "memoire_mo": None,
        }
        if c["State"] == "running":
            entree["cpu_pourcent"], entree["memoire_mo"] = stats_conteneur(session, c["Id"])
        resultat.append(entree)
    return resultat

def afficher_resume(inventaire):
    conteneurs = inventaire["conteneurs"]
    demarres = [c for c in conteneurs if c["etat"] == "running"]
    print(f"Relevé du {inventaire['date']}")
    print(f"{len(conteneurs)} conteneurs, dont {len(demarres)} démarrés\n")
    for c in conteneurs:
        ligne = f"{c['nom']:30} {c['image']:30} {c['etat']:10}"
        if c["cpu_pourcent"] is not None:
            ligne += f" CPU {c['cpu_pourcent']:6.2f} %  RAM {c['memoire_mo']:7.1f} Mo"
        print(ligne)

def main():
    session = requests.Session()
    inventaire = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "conteneurs": releve_docker(session),
    }
    with open("inventaire.json", "w", encoding="utf-8") as f:
        json.dump(inventaire, f, indent=2, ensure_ascii=False)
    afficher_resume(inventaire)

if __name__ == "__main__":
    main()