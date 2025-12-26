import json, hashlib, time, os, subprocess, shlex
from multiprocessing import Process, Queue
from typing import Dict, Any

class SandboxRunner:
    def __init__(self, timeout_seconds:int=5, max_result_size:int=10000):
        self.timeout = timeout_seconds
        self.max_result_size = max_result_size
    def _worker(self, evaluator_class, model_path, out_q:Queue):
        try:
            # If evaluator_class is a class, instantiate it
            evaluator = evaluator_class() if isinstance(evaluator_class, type) else evaluator_class
            res = evaluator.evaluate(model_path)
            raw = json.dumps(res, default=str)
            if len(raw) > self.max_result_size:
                out_q.put({'error':'result too large'})
            else:
                out_q.put(res)
        except Exception as e:
            out_q.put({'error':'exception','message':str(e)})
    def run(self, evaluator_class, model_path) -> Dict[str,Any]:
        q = Queue()
        p = Process(target=self._worker, args=(evaluator_class, model_path, q))
        p.start()
        p.join(timeout=self.timeout)
        if p.is_alive():
            p.terminate()
            return {'error':'timeout','message':f'Evaluator exceeded {self.timeout}s'}
        if not q.empty():
            return q.get()
        return {'error':'no_result'}

class DockerRunner:
    """A helper that knows how to run a small evaluation docker image.
    NOTE: This requires Docker to be installed and accessible. For prototypes, you can construct
    and print the docker command and run it manually on a machine with Docker.
    """
    def __init__(self, image_name='ai_eval_runner:latest', workdir='/work'):
        self.image_name = image_name
        self.workdir = workdir
    def build_command(self, model_path, evaluator_module, evaluator_class_name):
        # mount model_path to container and run a simple python invocation
        # The container image should contain python and access to evaluator plugin code.
        cmd = f"docker run --rm -v {os.path.abspath(model_path)}:{self.workdir}/model.json {self.image_name} \"python -c 'from {evaluator_module} import {evaluator_class_name}; print({evaluator_class_name}().evaluate(\"/work/model.json\"))'\""
        return cmd
    def run(self, model_path, evaluator_module, evaluator_class_name):
        cmd = self.build_command(model_path, evaluator_module, evaluator_class_name)
        # In this environment we will NOT execute docker; we return the command string for the user.
        return {'cmd':cmd, 'note':'Run this command on a machine with Docker installed.'}
