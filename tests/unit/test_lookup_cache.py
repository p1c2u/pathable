from typing import Any

from pathable.paths import LookupPath


class CounterDict(dict):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.getitem_counter = 0

    def __getitem__(self, key: Any) -> Any:
        self.getitem_counter += 1
        return super().__getitem__(key)


def test_lookuppath_caches_within_instance() -> None:
    value = {"test3": "test4"}
    resource = CounterDict(test1=1, test2=value)

    p = LookupPath.from_lookup(resource, "test2")

    assert p.read_value() == value
    assert p.read_value() == value
    assert resource.getitem_counter == 1


def test_lookuppath_cache_is_not_shared_between_instances() -> None:
    value = {"test3": "test4"}
    resource = CounterDict(test1=1, test2=value)

    p1 = LookupPath.from_lookup(resource, "test2")
    p2 = LookupPath.from_lookup(resource, "test2")

    assert p1.read_value() == value
    assert p1.read_value() == value
    assert resource.getitem_counter == 1

    assert p2.read_value() == value
    assert p2.read_value() == value
    assert resource.getitem_counter == 2


def test_lookup_accessor_disable_cache_reads_each_time() -> None:
    resource = CounterDict({"a": {"b": "value"}})
    path = LookupPath.from_lookup(resource, "a/b")

    # Disable caching on this accessor instance.
    path.accessor.disable_cache()

    path.read_value()
    path.read_value()

    assert resource.getitem_counter == 2


def test_lookup_accessor_clear_cache_forces_reread() -> None:
    resource = CounterDict({"a": {"b": "value"}})
    path = LookupPath.from_lookup(resource, "a/b")

    path.read_value()
    assert resource.getitem_counter == 1

    path.accessor.clear_cache()
    path.read_value()
    assert resource.getitem_counter == 2


def test_lookup_accessor_lru_eviction_respects_maxsize() -> None:
    resource = CounterDict({"a": {"b": "value"}, "x": {"y": "value"}})
    root = LookupPath.from_lookup(resource)
    a = root / "a" / "b"
    x = root / "x" / "y"

    root.accessor.enable_cache(maxsize=1)

    # Populate cache with a/b
    a.read_value()
    assert resource.getitem_counter == 1

    # Add second key -> should evict first due to maxsize=1
    x.read_value()
    assert resource.getitem_counter == 2

    # a/b should be a cache miss now
    a.read_value()
    assert resource.getitem_counter == 3


def test_lookup_accessor_node_is_immutable() -> None:
    value1 = {"v": 1}
    value2 = {"v": 2}
    resource1 = CounterDict(test2=value1)
    resource2 = CounterDict(test2=value2)

    p = LookupPath.from_lookup(resource1, "test2")

    assert p.read_value() == value1
    assert resource1.getitem_counter == 1
    assert resource2.getitem_counter == 0

    try:
        p.accessor.node = resource2  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("Expected node to be immutable")

    # Still reads from the original node.
    assert p.read_value() == value1
