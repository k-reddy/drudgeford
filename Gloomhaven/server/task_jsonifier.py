import json
from typing import Any
from dataclasses import fields
from pyxel_ui.models import tasks


class TaskJsonifier:
    @staticmethod
    def convert_task_to_json(task: Any) -> str:
        """
        Converts a Task instance to a JSON string.
        Saves the class name and instance attributes.

        Args:
            task: Any Task instance

        Returns:
            str: JSON string representation of the task
        """
        class_name = task.__class__.__name__

        # only get the actual data fields
        task_data = {field.name: getattr(task, field.name) for field in fields(task)}
        task_dict = {"class_name": class_name, "data": task_data}
        return json.dumps(task_dict, ensure_ascii=False)

    @staticmethod
    def make_task_from_json(json_str: str) -> Any:
        """
        Creates a Task instance from a JSON string.

        Args:
            json_str: JSON string created by convert_task_to_json

        Returns:
            Any: Reconstructed Task instance

        Raises:
            AttributeError: If the task class doesn't exist in tasks module
            json.JSONDecodeError: If the JSON string is invalid
        """
        if not json_str:
            return None
        # Parse the JSON
        task_dict = json.loads(json_str)

        # Get the class from tasks module
        task_class = getattr(tasks, task_dict["class_name"])
        task_instance = task_class(**task_dict["data"])

        return task_instance
