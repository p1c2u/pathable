from collections.abc import Hashable
from typing import Protocol
from typing import runtime_checkable
from typing import TypeVar

K = TypeVar('K', bound=Hashable, contravariant=True)
V = TypeVar('V', covariant=True)

@runtime_checkable
class Subscriptable(Protocol[K, V]):
    def __contains__(self, key: K) -> bool: ...
    def __getitem__(self, key: K) -> V: ...
    def __len__(self) -> int: ...
