import requests, json, os, time
WATTTIME_USER = os.getenv("WATTTIME_USER", "kjune922")
WATTTIME_PASS = os.getenv("WATTTIME_PASS", "dlrudalswns2!")
TOKEN_CACHE_FILE = "token_cache.json"

def get_token():
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE) as f:
            cache = json.load(f)
            if time.time() - cache.get("timestamp", 0) < 3600:
                return cache["token"]
    r = requests.get("https://api.watttime.org/v2/login", auth=(WATTTIME_USER, WATTTIME_PASS))
    if r.status_code != 200:
        print("[WattTime] 로그인 실패:", r.text)
        return None
    token = r.json().get("token")
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump({"token": token, "timestamp": time.time()}, f)
    return token
