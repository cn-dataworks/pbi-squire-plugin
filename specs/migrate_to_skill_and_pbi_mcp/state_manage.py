import json
import os
import time
from datetime import datetime

class PBIStateManager:
    def __init__(self, root_dir):
        self.root = root_dir
        self.state_path = os.path.join(root_dir, ".claude", "state.json")
        self._ensure_dir()
        self.state = self._load()

    def _ensure_dir(self):
        os.makedirs(os.path.join(self.root, ".claude", "tasks"), exist_ok=True)

    def _load(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                return json.load(f)
        return {"global_metadata": {}, "active_tasks": {}, "resource_locks": {}}

    def save(self):
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def create_task(self, name):
        task_id = f"{name.replace(' ', '-')}-{int(time.time())}"
        task_path = os.path.join(".claude", "tasks", task_id)
        os.makedirs(os.path.join(self.root, task_path), exist_ok=True)
        
        self.state["active_tasks"][task_id] = {
            "path": task_path,
            "status": "in_progress",
            "created": str(datetime.now())
        }
        self.save()
        return task_id, task_path

    def acquire_lock(self, resource, task_id):
        current_lock = self.state["resource_locks"].get(resource)
        if current_lock and current_lock != task_id:
            return False
        self.state["resource_locks"][resource] = task_id
        self.save()
        return True

    def release_lock(self, resource, task_id):
        if self.state["resource_locks"].get(resource) == task_id:
            del self.state["resource_locks"][resource]
            self.save()

# CLI logic for Claude to call
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--create_task", type=str)
    # ... additional arguments for locks ...
    args = parser.parse_args()
    # Implementation of CLI triggers...