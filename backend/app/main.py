from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.interfaces import EvaluationStrategy, GovernancePolicy, PricingStrategy, StorageService
from core.implementations import AccuracyEvaluator, RobustnessEvaluator, LatencyEvaluator, FairnessEvaluator, RuleBasedPolicy, FixedPricing, LocalStorage, PluginLoader
from services.registry import ModelRegistry
from services.marketplace import Marketplace
from services.sandbox import SandboxRunner, DockerRunner
from reputation import ReputationService
import os, json

app = FastAPI(title="AI Model Marketplace (MVP)")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Initialize components (in-memory/simple)
storage = LocalStorage(base_dir=os.path.join(os.getcwd(),'storage'))
registry = ModelRegistry(storage)
governance = RuleBasedPolicy()
pricing = FixedPricing(amount=9.99)
sandbox = SandboxRunner(timeout_seconds=5)
docker_runner = DockerRunner()  # optional; requires Docker available
reputation = ReputationService()

# Plugin loader will register evaluator classes dynamically
plugin_loader = PluginLoader(plugins_dir=os.path.join(os.getcwd(),'plugins'))
plugin_loader.load_plugins()
# built-in evaluators are available directly

marketplace = Marketplace(registry, governance, pricing, sandbox, reputation)

@app.post('/register')
def register_model(payload: dict):
    model_id = payload.get('model_id')
    owner_id = payload.get('owner_id')
    content = payload.get('content')
    if not (model_id and owner_id and content):
        raise HTTPException(status_code=400, detail='missing fields')
    # Accept dict or JSON string content
    if isinstance(content, dict):
        content_bytes = json.dumps(content).encode('utf-8')
    else:
        content_bytes = str(content).encode('utf-8')
    meta = registry.register(model_id, owner_id, content_bytes, {"visibility": payload.get('visibility','public'), "price": payload.get('price',9.99)})
    return {"registered": meta}

@app.post('/evaluate')
def evaluate_model(payload: dict):
    user = {"id": payload.get('user_id'), "role": payload.get('role','visitor')}
    model_id = payload.get('model_id')
    evaluator_key = payload.get('evaluator','accuracy')
    # map keys to either built-ins or plugin classes
    eval_map = {
        'accuracy': AccuracyEvaluator,
        'robustness': RobustnessEvaluator,
        'latency': LatencyEvaluator,
        'fairness': FairnessEvaluator
    }
    evaluator_cls = eval_map.get(evaluator_key) or plugin_loader.get_evaluator(evaluator_key)
    if evaluator_cls is None:
        raise HTTPException(status_code=400, detail='unknown evaluator')
    out = marketplace.evaluate_model(user, model_id, evaluator_cls)
    if out.get('error'):
        raise HTTPException(status_code=403, detail=out)
    return out

@app.post('/purchase')
def purchase_model(payload: dict):
    user = {"id": payload.get('user_id'), "role": payload.get('role','visitor')}
    model_id = payload.get('model_id')
    out = marketplace.purchase_model(user, model_id)
    if out.get('error'):
        raise HTTPException(status_code=403, detail=out)
    return out

@app.get('/health')
def health():
    return {'status':'ok'}
