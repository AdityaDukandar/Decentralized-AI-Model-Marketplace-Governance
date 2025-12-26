class ReputationService:
    def __init__(self):
        self._scores = {}  # user_id -> score
    def get(self, user_id):
        return self._scores.get(user_id, 0.0)
    def increment(self, user_id, delta:float):
        if user_id is None: return
        self._scores[user_id] = self.get(user_id) + float(delta)
