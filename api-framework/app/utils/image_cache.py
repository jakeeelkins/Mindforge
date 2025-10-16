import hashlib, json
from typing import Dict, Any
from app.core.redis import r_get, r_set

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def build_key(kind: str, image_hash: str, model: str, model_version: str, params: Dict[str, Any]) -> str:
    payload = {"k": kind, "img": image_hash, "m": model, "v": model_version, "p": params}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "img:cache:" + hashlib.sha256(raw.encode()).hexdigest()
