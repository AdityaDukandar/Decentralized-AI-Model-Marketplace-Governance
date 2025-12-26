import os, json, time, random
from typing import Dict, Any
from .interfaces import EvaluationStrategy, GovernancePolicy, PricingStrategy, StorageService

class LocalStorage(StorageService):
    def __init__(self, base_dir='models_storage'):
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
    def save(self, model_id: str, content: bytes) -> str:
        path = os.path.join(self.base_dir, f"{model_id}.json")
        with open(path, 'wb') as f:
            f.write(content)
        return path

class AccuracyEvaluator(EvaluationStrategy):
    def evaluate(self, model_path: str) -> Dict[str, Any]:
        with open(model_path, 'r') as f:
            data = json.load(f)
        preds = data.get('predictions', [])
        labels = data.get('labels', [])
        if not preds or not labels or len(preds) != len(labels):
            return {'error':'invalid model data'}
        correct = sum(1 for p,l in zip(preds,labels) if p==l)
        accuracy = correct / len(preds)
        return {'metric':'accuracy','value':accuracy,'n':len(preds)}

class RobustnessEvaluator(EvaluationStrategy):
    def evaluate(self, model_path: str) -> Dict[str, Any]:
        with open(model_path, 'r') as f:
            data = json.load(f)
        preds = data.get('predictions', [])
        if not preds:
            return {'error':'invalid model data'}
        n=len(preds)
        flips = max(1,n//10)
        unchanged = 0
        for i in range(n):
            if random.randrange(n) < flips:
                continue
            unchanged += 1
        robustness = unchanged / n
        return {'metric':'robustness','value':robustness,'n':n,'sim_flips':flips}

class LatencyEvaluator(EvaluationStrategy):
    def __init__(self, repeats:int=200):
        self.repeats = repeats
    def evaluate(self, model_path:str)->Dict[str,Any]:
        with open(model_path,'r') as f:
            data = json.load(f)
        preds = data.get('predictions', [])
        if not preds:
            return {'error':'invalid model data'}
        start=time.time()
        s=0
        for _ in range(self.repeats):
            for p in preds:
                s += (p * 31) % 7
        end=time.time()
        avg_ms = (end-start)*1000/self.repeats
        return {'metric':'latency_ms_per_inference','value_ms':avg_ms,'repeats':self.repeats}

class FairnessEvaluator(EvaluationStrategy):
    def evaluate(self, model_path:str)->Dict[str,Any]:
        with open(model_path,'r') as f:
            data = json.load(f)
        preds = data.get('predictions', [])
        labels = data.get('labels', [])
        groups = data.get('groups', None)
        if not preds or not labels or len(preds)!=len(labels):
            return {'error':'invalid model data'}
        if groups and len(groups)==len(preds):
            from collections import defaultdict
            accs = defaultdict(lambda:[0,0])
            for p,l,g in zip(preds,labels,groups):
                accs[g][1]+=1
                if p==l:
                    accs[g][0]+=1
            group_acc = {g:c/t for g,(c,t) in accs.items()}
            max_acc=max(group_acc.values()); min_acc=min(group_acc.values())
            disparity = max_acc-min_acc
            return {'metric':'group_accuracy_disparity','value':disparity,'group_acc':group_acc}
        return {'metric':'fairness_synthetic','value':0.05}

class RuleBasedPolicy(GovernancePolicy):
    def can_access(self, user: Dict[str,Any], model_meta: Dict[str,Any]) -> bool:
        vis = model_meta.get('visibility','public')
        if vis=='public': return True
        if user.get('id')==model_meta.get('owner_id'): return True
        return user.get('role')=='buyer'

class FixedPricing(PricingStrategy):
    def __init__(self, amount:float=9.99):
        self.amount = amount
    def price(self, model_meta:Dict[str,Any])->float:
        return float(model_meta.get('price', self.amount))

# Simple plugin loader (loads evaluator classes from plugins directory)
import importlib.util, inspect
class PluginLoader:
    def __init__(self, plugins_dir='plugins'):
        self.plugins_dir = plugins_dir
        self._evaluators = {}
    def load_plugins(self):
        if not os.path.isdir(self.plugins_dir):
            return
        for fname in os.listdir(self.plugins_dir):
            if not fname.endswith('.py'): continue
            path = os.path.join(self.plugins_dir, fname)
            name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)  # type: ignore
            except Exception as e:
                print(f"Failed to load plugin {fname}: {e}")
                continue
            # register any classes inheriting EvaluationStrategy
            for obj_name, obj in inspect.getmembers(mod, inspect.isclass):
                try:
                    if issubclass(obj, EvaluationStrategy) and obj is not EvaluationStrategy:
                        key = getattr(obj, 'KEY', obj_name.lower())
                        self._evaluators[key] = obj
                except Exception:
                    pass
    def get_evaluator(self, key:str):
        return self._evaluators.get(key)
    def list_evaluators(self):
        return list(self._evaluators.keys())
