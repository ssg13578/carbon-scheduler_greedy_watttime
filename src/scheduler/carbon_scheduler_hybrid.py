import requests
from src.db import SessionLocal, ClusterStatus, CarbonHistory
from src.scheduler.wattime_auth import get_token

NODE_REGION_MAP = {"node1": "CISO", "node2": "PJM", "node3": "NYISO"}

def _fetch_carbon(ba, token):
    r = requests.get(
        "https://api.watttime.org/v2/data",
        headers={"Authorization": f"Bearer {token}"},
        params={"ba": ba},
        timeout=10
    )
    if r.status_code != 200:
        return None
    return r.json().get("marginal_carbon", None)

def run_hybrid_scheduler():
    db = SessionLocal()
    clusters = db.query(ClusterStatus).all()
    if not clusters:
        db.close()
        return {"error": "no clusters"}

    token = get_token()
    for c in clusters:
        ba = NODE_REGION_MAP.get(c.cluster_name)
        if not ba:
            continue
        carbon = _fetch_carbon(ba, token)
        if carbon is not None:
            c.carbon_emission = carbon
    db.commit()

    weights = {"cpu": 0.3, "memory": 0.2, "carbon": 0.5}
    scores = {}
    for c in clusters:
        score = weights["cpu"] * c.cpu_usage + weights["memory"] * c.memory_usage + weights["carbon"] * c.carbon_emission
        scores[c.cluster_name] = (score, c)

    cpu_base = min(clusters, key=lambda x: x.cpu_usage)
    C_baseline = cpu_base.carbon_emission

    best_name = min(scores, key=lambda k: scores[k][0])
    best_cluster = scores[best_name][1]
    C_selected = best_cluster.carbon_emission

    reduction = ((C_baseline - C_selected) / C_baseline) * 100 if C_baseline and C_baseline > 0 else 0.0

    record = CarbonHistory(
        cluster_name=best_cluster.cluster_name,
        baseline_carbon=C_baseline,
        scheduler_carbon=C_selected,
        reduction_rate=reduction
    )
    db.add(record)
    db.commit()
    db.close()

    return {
        "best_cluster": best_cluster.cluster_name,
        "baseline_carbon": C_baseline,
        "scheduler_carbon": C_selected,
        "reduction_rate": reduction
    }
