from typing import Optional
import time
import json
from alice_battleship.skill import redis_client
from .request import Request


class Redis:
    def __init__(self, req: Request):
        self._base = f"alice:{req.application_id}"
        self._session = f"{self._base}:{req.session_id}"

    @property
    def name(self) -> Optional[str]:
        name = redis_client.get(f"{self._base}")
        if name is not None:
            return name.decode("utf-8")

    @name.setter
    def name(self, name: str):
        redis_client.set(f"{self._base}", name)

    @property
    def ai(self) -> Optional[list[list[int]]]:
        field = redis_client.get(f"{self._session}:ai")
        if field is not None:
            return json.loads(field.decode("utf-8"))

    @ai.setter
    def ai(self, field: list[list[int]]):
        redis_client.set(f"{self._session}:ai", json.dumps(field))
        self.update()

    @property
    def human(self) -> Optional[list[list[int]]]:
        field = redis_client.get(f"{self._session}:human")
        if field is not None:
            return json.loads(field.decode("utf-8"))

    @human.setter
    def human(self, field: list[list[int]]):
        redis_client.set(f"{self._session}:human", json.dumps(field))
        self.update()

    @property
    def state(self) -> Optional[int]:
        state = redis_client.get(f"{self._session}:state")
        if state is not None:
            return int(state)

    @state.setter
    def state(self, state: int):
        redis_client.set(f"{self._session}:state", state)
        self.update()

    @property
    def coords(self) -> Optional[str]:
        coords = redis_client.get(f"{self._session}:coords")
        if coords is not None:
            return coords.decode("utf-8")

    @coords.setter
    def coords(self, coords: str):
        redis_client.set(f"{self._session}:coords", coords)

    @coords.deleter
    def coords(self):
        redis_client.delete(f"{self._session}:coords")

    def update(self):
        # last change time
        redis_client.set(f"{self._session}:update", int(time.time() * 1000))
