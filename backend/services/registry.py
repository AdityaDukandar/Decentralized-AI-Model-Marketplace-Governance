import os, json
from datetime import datetime

class ModelRegistry:
    def __init__(self, storage):
        self.storage = storage
        self._meta = {}
    def register(self, model_id: str, owner_id: str, content_bytes: bytes, metadata: dict):
        path = self.storage.save(model_id, content_bytes)
        meta = {'id':model_id,'owner_id':owner_id,'path':path,'created_at':datetime.utcnow().isoformat(), **metadata}
        self._meta[model_id]=meta
        return meta
    def get(self, model_id: str):
        return self._meta.get(model_id)
