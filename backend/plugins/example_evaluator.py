# Example plugin evaluator
from core.interfaces import EvaluationStrategy
import json
class ExamplePluginEvaluator(EvaluationStrategy):
    KEY = 'example_plugin'
    def evaluate(self, model_path: str):
        with open(model_path,'r') as f:
            data = json.load(f)
        # simplistic: return number of predictions
        preds = data.get('predictions',[])
        return {'metric':'count_predictions','value':len(preds)}
