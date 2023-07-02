class Queue:
    """Class that represents actions that are queued for a number of following frames."""

    def __init__(self):
        # maps number of queued frames to a dict mapping objects to actions to be executed on that object:
        self.queue = {}

    def add(self, no_frames: int, obj_actions: list[tuple[object, str]]) -> None:
        """Queue actions to be executed after the given number of frames on given objects.
         Actions are string statements that will be executed."""
        if self.queue.get(no_frames) is None:
            self.queue[no_frames] = obj_actions
        self.queue[no_frames] += obj_actions

    def handle(self) -> None:
        """Handles the queue."""
        if (obj_actions := self.queue.get(0)) is None:
            return
        for obj, action in obj_actions:
            exec(f"obj.{action}")
        del self.queue[0]

    def update(self):
        """Updates the queue by decreasing the number of frames for each action."""
        if not self.queue:  # empty queue
            return
        new_queue = {}
        for key, val in self.queue.items():
            new_queue[key - 1] = val
        self.queue = new_queue
