# api-framework/app/services/model_loader.py
from functools import lru_cache
# import your real model libs here (torch, onnxruntime, etc.)

@lru_cache()
def get_model():
    """
    Load your model once per process and reuse it for all requests.
    Replace the placeholder with your real load logic later.
    """
    # Example when you wire it up:
    # import torch
    # model = MyModel.load_from_path("path/to/weights.pt")
    # model.to("cuda" if torch.cuda.is_available() else "cpu")
    model = object()  # placeholder so everything runs now
    return model
