import unittest
from ..pyxel_main import (
    ActionTask,
    Direction,
    PyxelTaskQueue,
)

# python3 -m unittest discover -s tests


class TestPyxelTaskQueue(unittest.TestCase):
    def setUp(self):
        self.queue = PyxelTaskQueue()

    def test_enqueue_action(self):
        action = ActionTask(
            "knight",
            "walk",
            Direction.EAST,
            (0, 0),
            (0, 1),
        )
        self.queue.enqueue(action)
        self.assertFalse(
            self.queue.is_empty(),
            "Queue should not be empty after enqueue",
        )

    def test_dequeue_action(self):
        action = ActionTask(
            "knight",
            "walk",
            Direction.EAST,
            (0, 0),
            (0, 1),
        )
        self.queue.enqueue(action)
        dequeued_action = self.queue.dequeue()
        self.assertEqual(
            action,
            dequeued_action,
            "Dequeued action should match enqueued action.",
        )

    def test_dequeue_index_error(self):
        with self.assertRaises(IndexError):
            self.queue.dequeue()

    def test_peek(self):
        self.assertIsNone(self.queue.peek(), "Empty queue should return None")
        action = ActionTask(
            "knight",
            "walk",
            Direction.EAST,
            (0, 0),
            (0, 1),
        )
        self.queue.enqueue(action)
        next_action = self.queue.peek()
        self.assertEqual(
            action,
            next_action,
            "Next action in queue with one action does not match.",
        )
        action2 = ActionTask(
            "knight2",
            "walk",
            Direction.EAST,
            (0, 0),
            (0, 1),
        )
        self.queue.enqueue(action2)
        self.assertEqual(
            action,
            next_action,
            "Next action in multi-action queue does not match.",
        )

    def test_clear(self):
        action = ActionTask(
            "knight",
            "walk",
            Direction.EAST,
            (0, 0),
            (0, 1),
        )
        self.queue.enqueue(action)
        self.queue.clear()
        self.assertTrue(
            self.queue.is_empty(),
            "Queue clear has failed",
        )


if __name__ == "__main__":
    print("hello")
    unittest.main()
