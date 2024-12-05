import json
from typing import Any
from dataclasses import fields
import base64
import pickle
from pyxel_ui.models import tasks


class TaskJsonifier:
    def __init__(self):
        self._task_registry = {
            name: getattr(tasks, name)
            for name in dir(tasks)
            if isinstance(getattr(tasks, name), type)
        }

    def convert_task_to_json(self, task: Any) -> str:
        """
        Converts a Task instance to a JSON string.
        Uses highest pickle protocol for better performance.
        """
        class_name = task.__class__.__name__
        task_data = {field.name: getattr(task, field.name) for field in fields(task)}

        # Use highest protocol for better performance
        pickled_data = pickle.dumps(task_data, protocol=pickle.HIGHEST_PROTOCOL)
        encoded_data = base64.b64encode(pickled_data).decode("utf-8")

        task_dict = {"class_name": class_name, "data": encoded_data}
        # Use compact JSON encoding
        return json.dumps(task_dict, ensure_ascii=False, separators=(",", ":"))

    def make_task_from_json(self, json_str: str) -> Any:
        """
        Creates a Task instance from a JSON string.
        """
        if not json_str:
            return None

        task_dict = json.loads(json_str)

        # Use registry lookup for better performance
        task_class = self._task_registry.get(task_dict["class_name"])
        if task_class is None:
            raise ValueError(f"Unknown task class: {task_dict['class_name']}")

        decoded_data = base64.b64decode(task_dict["data"])
        instance_data = pickle.loads(decoded_data)

        return task_class(**instance_data)
