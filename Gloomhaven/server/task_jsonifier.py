import json
import pickle
import base64
from typing import Any
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
        pickled_data = pickle.dumps(task.__dict__)
        encoded_data = base64.b64encode(pickled_data).decode("utf-8")

        task_dict = {"class_name": class_name, "data": encoded_data}

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

        # Decode and unpickle the instance data
        decoded_data = base64.b64decode(task_dict["data"])
        instance_data = pickle.loads(decoded_data)

        # Create a new instance with the unpickled data
        task_instance = task_class(**instance_data)

        return task_instance
