# api-framework/app/services/inference_service.py

import json
import asyncio
from typing import Dict, Any

from app.services.model_loader import get_model          # ✅ singleton model
from app.utils.image_decode import decode_bgr            # ✅ minimal-copy decode
from app.utils.image_cache import sha256_bytes, build_key
from app.core.redis import r_get, r_set

# ------ Cache / versioning config ------
MODEL_NAME = "overhead-stock-vlm"
MODEL_VERSION = "0.1.0"           # bump when you change model or preprocessing
TTL_SECONDS = 24 * 60 * 60        # 24h cache; tune as needed

# Limit concurrent inferences to protect RAM/VRAM
_INFER_CONCURRENCY = 2             # tune for your machine
_SEM = asyncio.Semaphore(_INFER_CONCURRENCY)


# ------ The heavy bit (now memory-friendly) ------
async def run_model(image_bytes: bytes, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace the stub body with your REAL model call when ready.
    For now, it simulates a heavy compute with asyncio.sleep(2).
    """
    # 1) Reuse the loaded model (singleton)
    model = get_model()

    # 2) Decode with minimal copies
    img = decode_bgr(image_bytes)  # HxWxC (BGR) numpy array

    # 3) Restrict parallelism to avoid memory spikes
    async with _SEM:
        # TODO: call your actual model here using `model` and `img`
        # e.g., outputs = model.predict(img, **params)
        await asyncio.sleep(2)  # simulate heavy forward pass

        result = {
            "banana": 12,
            "broccoli": 4,
            "confidence": 0.91,
            "params": params,
        }

    # Optional if you still see peaks:
    # del img

    return result


# ------ Cache wrapper (unchanged) ------
async def infer_with_cache(image_bytes: bytes, params: Dict[str, Any]) -> Dict[str, Any]:
    img_hash = sha256_bytes(image_bytes)
    key = build_key("inference", img_hash, MODEL_NAME, MODEL_VERSION, params)

    cached = await r_get(key)
    if cached:
        return json.loads(cached)

    result = await run_model(image_bytes, params)
    await r_set(key, json.dumps(result), TTL_SECONDS)
    return result
