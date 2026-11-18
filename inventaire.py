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

def main():
    session = requests.Session()
    for c in lister_conteneurs(session):
        nom = c["Names"][0].lstrip("/")
        ligne = f"{nom:30} {c['Image']:30} {c['State']:10}"
        if c["State"] == "running":
            cpu, memoire = stats_conteneur(session, c["Id"])
            ligne += f" CPU {cpu:6.2f} %  RAM {memoire:7.1f} Mo"
        print(ligne)

if __name__ == "__main__":
    main()