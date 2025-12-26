import hashlib, json
from datetime import datetime

class ProofOfEvaluation:
    @staticmethod
    def create(model_id:str, evaluator_name:str, result:dict):
        artifact = {'model_id':model_id,'evaluator':evaluator_name,'result':result,'timestamp':datetime.utcnow().isoformat()}
        raw = json.dumps(artifact, sort_keys=True).encode('utf-8')
        artifact['sha256'] = hashlib.sha256(raw).hexdigest()
        return artifact

class Marketplace:
    def __init__(self, registry, governance, pricing, sandbox_runner, reputation_service):
        self.registry = registry
        self.governance = governance
        self.pricing = pricing
        self.sandbox = sandbox_runner
        self.reputation = reputation_service
    def evaluate_model(self, user, model_id, evaluator_class):
        meta = self.registry.get(model_id)
        if not meta: return {'error':'model not found'}
        if not self.governance.can_access(user, meta): return {'error':'access denied'}
        res = self.sandbox.run(evaluator_class, meta['path'])
        poe = ProofOfEvaluation.create(model_id, getattr(evaluator_class,'__name__',str(evaluator_class)), res)
        # update reputation (simple): increase uploader rep on successful eval
        if not res.get('error'):
            self.reputation.increment(meta.get('owner_id'), 1)
        return {'evaluation':res,'proof':poe}
    def purchase_model(self, user, model_id):
        meta = self.registry.get(model_id)
        if not meta: return {'error':'model not found'}
        if not self.governance.can_access(user, meta): return {'error':'access denied'}
        amount = self.pricing.price(meta)
        receipt = {'buyer':user.get('id'),'model_id':model_id,'amount':amount,'timestamp':datetime.utcnow().isoformat()}
        raw = json.dumps(receipt, sort_keys=True).encode('utf-8')
        receipt['receipt_sha256'] = hashlib.sha256(raw).hexdigest()
        # update reputation for buyer (simple)
        self.reputation.increment(user.get('id'), 0.5)
        return {'receipt':receipt}
