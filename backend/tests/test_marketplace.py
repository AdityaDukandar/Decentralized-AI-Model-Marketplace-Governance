from backend.app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)

def test_register_and_evaluate():
    sample = {'predictions':[0,1,1,0],'labels':[0,1,1,0]}
    resp = client.post('/register', json={'model_id':'t_model','owner_id':'t_owner','content':sample,'visibility':'public','price':1.0})
    assert resp.status_code == 200
    j = resp.json()
    assert j.get('registered',{}).get('id') == 't_model'
    # evaluate
    resp2 = client.post('/evaluate', json={'user_id':'t_user','role':'visitor','model_id':'t_model','evaluator':'accuracy'})
    assert resp2.status_code == 200
    out = resp2.json()
    assert 'evaluation' in out
