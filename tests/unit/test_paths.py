from collections.abc import Hashable
from collections.abc import Mapping
from types import GeneratorType
from typing import Any
from typing import Union

import pytest

from pathable.accessors import NodeAccessor
from pathable.parsers import SEPARATOR
from pathable.paths import AccessorPath
from pathable.paths import BasePath
from pathable.paths import LookupPath


class MockAccessor(
    NodeAccessor[Union[Mapping[Hashable, Any], Any], Hashable, Any]
):
    """Mock accessor."""

    def __init__(
        self, *children_keys: str, content: Any = None, exists: bool = False
    ):
        super().__init__(None)
        self._children_keys = children_keys
        self._content = content
        self._exists = exists

    def keys(self, parts: list[Hashable]) -> Any:
        return self._children_keys

    def len(self, parts: list[Hashable]) -> int:
        return len(self._children_keys)

    def read(
        self, parts: list[Hashable]
    ) -> Union[Mapping[Hashable, Any], Any]:
        return self._content


class MockPart(str):
    """Mock resource for testing purposes."""

    def __init__(self, s: str):
        self.s = s

        self.str_counter = 0

    def __str__(self) -> str:
        self.str_counter += 1
        return self.s


class MockResource(dict):
    """Mock resource for testing purposes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.getitem_counter = 0

    def __getitem__(self, key: Hashable) -> Any:
        self.getitem_counter += 1
        return super().__getitem__(key)


class TestBasePathInit:
    def test_default(self):
        p = BasePath()

        assert p.parts == ()
        assert p.separator == SEPARATOR

    def test_part_text(self):
        part = "part"
        p = BasePath(part)

        assert p.parts == (part,)
        assert p.separator == SEPARATOR

    def test_part_binary(self):
        part = b"part"
        p = BasePath(part)

        assert p.parts == ("part",)
        assert p.separator == SEPARATOR

    def test_part_binary_many(self):
        part1 = b"part1"
        part2 = b"part2"
        p = BasePath(part1, part2)

        assert p.parts == ("part1", "part2")
        assert p.separator == SEPARATOR

    def test_part_text_many(self):
        part1 = "part1"
        part2 = "part2"
        p = BasePath(part1, part2)

        assert p.parts == (part1, part2)
        assert p.separator == SEPARATOR

    def test_part_path(self):
        part = "part"
        p1 = BasePath(part)
        p = BasePath(p1)

        assert p.parts == (part,)
        assert p.separator == SEPARATOR

    def test_part_path_many(self):
        part1 = "part1"
        part2 = "part2"
        p1 = BasePath(part1)
        p2 = BasePath(part2)
        p = BasePath(p1, p2)

        assert p.parts == (part1, part2)
        assert p.separator == SEPARATOR

    def test_separator(self):
        separator = "."
        p = BasePath(separator=separator)

        assert p.parts == ()
        assert p.separator == separator


class TestBasePathStr:
    def test_empty(self):
        p = BasePath()

        assert str(p) == ""

    def test_single(self):
        p = BasePath("part1")

        assert str(p) == "part1"

    def test_double(self):
        args = ["part1", "part2"]
        p = BasePath(*args)

        assert str(p) == SEPARATOR.join(args)

    def test_separator(self):
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)

        assert str(p) == separator.join(args)

    def test_cparts_cached(self):
        part = MockPart("part1")
        args = [
            part,
        ]
        separator = ","
        p = BasePath(*args, separator=separator)

        assert str(p) == separator.join(args)
        assert part.str_counter == 1
        assert str(p) == separator.join(args)
        assert part.str_counter == 1


class TestBasePathRepr:
    def test_empty(self):
        p = BasePath()

        assert repr(p) == "BasePath('')"

    def test_single(self):
        arg = "part1"
        p = BasePath(arg)

        assert repr(p) == f"BasePath('{arg}')"

    def test_double(self):
        args = ["part1", "part2"]
        p = BasePath(*args)

        p_str = SEPARATOR.join(args)
        assert repr(p) == f"BasePath('{p_str}')"

    def test_separator(self):
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)

        p_str = separator.join(args)
        assert repr(p) == f"BasePath('{p_str}')"


class TestBasePathHash:
    def test_empty(self):
        p = BasePath()

        assert hash(p) == hash((p.separator, p.parts))

    def test_single(self):
        p = BasePath("part1")

        assert hash(p) == hash((p.separator, p.parts))

    def test_double(self):
        args = ["part1", "part2"]
        p = BasePath(*args)

        assert hash(p) == hash((p.separator, p.parts))

    def test_separator(self):
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)

        assert hash(p) == hash((p.separator, p.parts))

    def test_cparts_cached(self):
        part = MockPart("part1")
        args = [
            part,
        ]
        separator = ","
        p = BasePath(*args, separator=separator)

        # Hashing does not stringify parts.
        assert part.str_counter == 0
        assert hash(p) == hash((p.separator, p.parts))
        assert part.str_counter == 0
        assert hash(p) == hash((p.separator, p.parts))
        assert part.str_counter == 0

    def test_separator_part_of_hash(self):
        p1 = BasePath("a", separator="/")
        p2 = BasePath("a", separator=".")
        assert p1 != p2
        assert len({p1, p2}) == 2
        assert {p1: 1, p2: 2}[p1] == 1
        assert {p1: 1, p2: 2}[p2] == 2


class TestBasePathMakeChild:
    @pytest.fixture
    def base_path(self):
        return BasePath(separator=SEPARATOR)

    def test_none(self, base_path):
        args = []
        p = base_path._make_child(args)

        assert p.parts == tuple(args)
        assert p.separator == SEPARATOR

    def test_arg(self, base_path):
        args = ["part1"]
        p = base_path._make_child(args)

        assert p.parts == tuple(args)
        assert p.separator == SEPARATOR

    def test_arg_unparsed(self, base_path):
        parts = ["part1", "part2"]
        arg = SEPARATOR.join(parts)
        args = [arg]
        p = base_path._make_child(args)

        assert p.parts == tuple(parts)
        assert p.separator == SEPARATOR

    def test_args_many(self, base_path):
        args = ["part1", "part2"]
        p = base_path._make_child(args)

        assert p.parts == tuple(args)
        assert p.separator == SEPARATOR


class TestBasePathMakeChildRelPath:
    @pytest.fixture
    def base_path(self):
        return BasePath(separator=SEPARATOR)

    def test_part(self, base_path):
        part = "part1"
        p = base_path._make_child_relpath(part)

        assert p.parts == (part,)
        assert p.separator == SEPARATOR


class TestBasePathTruediv:
    def test_default_empty(self):
        p = BasePath() / ""

        assert p.parts == ()
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        "part1,part2,parts,separator",
        (
            [
                "",
                "",
                (),
                SEPARATOR,
            ],
            [
                "",
                "part1",
                ("part1",),
                SEPARATOR,
            ],
            [
                "part1",
                "",
                ("part1",),
                SEPARATOR,
            ],
            [
                "part1",
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                b"",
                "",
                (),
                SEPARATOR,
            ],
            [
                b"",
                "part1",
                ("part1",),
                SEPARATOR,
            ],
            [
                b"part1",
                "",
                ("part1",),
                SEPARATOR,
            ],
            [
                b"part1",
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                "part1",
                BasePath("part2"),
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                BasePath("part2"),
                ("part1", "part2"),
                SEPARATOR,
            ],
        ),
    )
    def test_parts(self, part1, part2, parts, separator):
        p = BasePath(part1) / part2

        assert p.parts == parts
        assert p.separator == separator

    def test_combined(self):
        part11 = "part11"
        part12 = "part12"
        part21 = "part21"
        part22 = "part22"
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p = BasePath(part1) / part2

        assert p.parts == (part11, part12, part21, part22)
        assert p.separator == SEPARATOR

    def test_combined_different_separators(self):
        part11 = "part11"
        part12 = "part12"
        part21 = "part21"
        part22 = "part22"
        separator1 = "."
        part1 = separator1.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p1 = BasePath(part2)
        p = BasePath(part1, separator=separator1) / p1

        assert p.parts == (part11, part12, part21, part22)
        assert p.separator == separator1

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() / []


class TestBasePathRtruediv:
    def test_default_empty(self):
        p = "" / BasePath()

        assert p.parts == ()
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        "part1,part2,parts,separator",
        (
            [
                "",
                "",
                (),
                SEPARATOR,
            ],
            [
                "",
                "part1",
                ("part1",),
                SEPARATOR,
            ],
            [
                "part1",
                "",
                ("part1",),
                SEPARATOR,
            ],
            [
                "part1",
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                b"",
                "",
                (),
                SEPARATOR,
            ],
            [
                b"",
                "part1",
                ("part1",),
                SEPARATOR,
            ],
            [
                b"part1",
                "",
                ("part1",),
                SEPARATOR,
            ],
            [
                b"part1",
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                "part1",
                BasePath("part2"),
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                "part2",
                ("part1", "part2"),
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                BasePath("part2"),
                ("part1", "part2"),
                SEPARATOR,
            ],
        ),
    )
    def test_parts(self, part1, part2, parts, separator):
        p = part1 / BasePath(part2)

        assert p.parts == parts
        assert p.separator == separator

    def test_combined(self):
        part11 = "part11"
        part12 = "part12"
        part21 = "part21"
        part22 = "part22"
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p = part1 / BasePath(part2)

        assert p.parts == (part11, part12, part21, part22)
        assert p.separator == SEPARATOR

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            [] / BasePath()

    def test_preserves_separator(self):
        p = BasePath("b.c", separator=".")

        result = "a" / p

        assert result.parts == ("a", "b", "c")
        assert result.separator == "."


class TestBasePathEq:
    @pytest.mark.parametrize(
        "part1,part2,expected",
        (
            ["", "", True],
            ["", "part", False],
            ["part", "", False],
            ["part", "part", True],
            ["part", BasePath("part"), True],
            [BasePath("part"), "part", True],
            [BasePath("part"), BasePath("part"), True],
        ),
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) == BasePath(part2)

        assert result is expected

    def test_type_not_implemented(self):
        result = BasePath() == []

        assert result is False

    def test_type_sensitive_parts(self):
        assert BasePath(0) != BasePath("0")

    def test_separator_part_of_equality(self):
        assert BasePath("a", separator="/") != BasePath("a", separator=".")


class TestBasePathLt:
    @pytest.mark.parametrize(
        "part1,part2,expected",
        (
            ["", "", False],
            ["", "part", True],
            ["part", "", False],
            ["part", "part", False],
            ["part", "part2", True],
            ["part", BasePath("part"), False],
            ["part", BasePath("part2"), True],
            [BasePath("part"), "part", False],
            [BasePath("part"), BasePath("part"), False],
            [BasePath("part"), BasePath("part2"), True],
        ),
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) < BasePath(part2)

        assert result is expected

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() < []

    def test_mixed_type_ordering_is_deterministic(self):
        # Ordering is based on (separator, type-aware cmp key).
        # This locks in the current rule that `int` parts sort before `str`
        # parts when their string forms are the same.
        assert BasePath(0) < BasePath("0")
        assert not (BasePath("0") < BasePath(0))

    def test_separator_affects_ordering(self):
        # Separator is compared before parts.
        assert BasePath("a", separator=".") < BasePath("a", separator="/")

    def test_type_identifier_includes_module(self):
        # Two distinct types may share the same __qualname__.
        # Ordering must remain deterministic and distinguish them.
        class Same:
            __module__ = "module_a"

            def __str__(self) -> str:
                return "x"

        SameA = Same

        class Same:
            __module__ = "module_b"

            def __str__(self) -> str:
                return "x"

        SameB = Same

        root = AccessorPath(MockAccessor())
        p1 = root._make_child_relpath(SameA())
        p2 = root._make_child_relpath(SameB())

        assert p1 != p2
        assert (p1 < p2) ^ (p2 < p1)


class TestBasePathLe:
    @pytest.mark.parametrize(
        "part1,part2,expected",
        (
            ["", "", True],
            ["", "part", True],
            ["part", "", False],
            ["part", "part", True],
            ["part", "part2", True],
            ["part", BasePath("part"), True],
            ["part", BasePath("part2"), True],
            [BasePath("part"), "part", True],
            [BasePath("part"), BasePath("part"), True],
            [BasePath("part"), BasePath("part2"), True],
        ),
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) <= BasePath(part2)

        assert result is expected

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() <= []


class TestBasePathGt:
    @pytest.mark.parametrize(
        "part1,part2,expected",
        (
            ["", "", False],
            ["", "part", False],
            ["part", "", True],
            ["part", "part", False],
            ["part", "part2", False],
            ["part", BasePath("part"), False],
            ["part", BasePath("part2"), False],
            [BasePath("part"), "part", False],
            [BasePath("part"), BasePath("part"), False],
            [BasePath("part"), BasePath("part2"), False],
        ),
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) > BasePath(part2)

        assert result is expected

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() > []


class TestBasePathGe:
    @pytest.mark.parametrize(
        "part1,part2,expected",
        (
            ["", "", True],
            ["", "part", False],
            ["part", "", True],
            ["part", "part", True],
            ["part", "part2", False],
            ["part", BasePath("part"), True],
            ["part", BasePath("part2"), False],
            [BasePath("part"), "part", True],
            [BasePath("part"), BasePath("part"), True],
            [BasePath("part"), BasePath("part2"), False],
        ),
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) >= BasePath(part2)

        assert result is expected

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() >= []


class TestAccessorPathLen:
    def test_empty(self):
        accessor = MockAccessor()
        p = AccessorPath(accessor)

        result = len(p)

        assert result == 0

    def test_value(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)

        result = len(p)

        assert result == 2


class TestAccessorPathKeys:
    def test_empty(self):
        accessor = MockAccessor()
        p = AccessorPath(accessor)

        result = p.keys()

        assert list(result) == []

    def test_value(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)

        result = p.keys()

        assert list(result) == ["test1", "test2"]


class TestAccessorPathContains:
    def test_valid(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)
        result = "test1" in p
        assert result is True

    def test_invalid(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)
        result = "test3" in p
        assert result is False


class TestAccessorPathItems:
    def test_empty(self):
        accessor = MockAccessor()
        p = AccessorPath(accessor)

        result = p.items()

        assert type(result) is GeneratorType
        assert dict(result) == {}

    def test_keys(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)

        result = p.items()

        assert type(result) is GeneratorType
        assert dict(result) == {
            "test1": p / "test1",
            "test2": p / "test2",
        }


class TestAccessorPathIter:
    def test_empty(self):
        accessor = MockAccessor()
        p = AccessorPath(accessor)

        result = iter(p)

        assert type(result) is GeneratorType
        assert list(result) == []

    def test_value(self):
        accessor = MockAccessor("test1", "test2")
        p = AccessorPath(accessor)

        result = iter(p)

        assert type(result) is GeneratorType
        result_list = list(result)
        assert result_list == [
            p / "test1",
            p / "test2",
        ]


class TestLookupPathIter:
    def test_object(self):
        resource = {"test1": {"test2": {"test3": "test"}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = iter(p)

        assert type(result) == GeneratorType
        result_list = list(result)
        assert result_list == [
            LookupPath._from_lookup(resource, "test1/test2/test3"),
        ]

    def test_list(self):
        resource = {"test1": {"test2": ["test3", "test4"]}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = iter(p)

        assert type(result) == GeneratorType
        result_list = list(result)
        assert result_list == [
            LookupPath._from_lookup(resource, "test1/test2", 0),
            LookupPath._from_lookup(resource, "test1/test2", 1),
        ]


class TestLookupPathGetItem:
    def test_valid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = p["test3"]

        assert result == value

    def test_invalid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        with pytest.raises(KeyError):
            p["test4"]


class TestLookupPathReadValue:
    @pytest.mark.parametrize(
        "resource,args,expected",
        [
            (
                {"test1": {"test2": {"test3": "testvalue"}}},
                ("test1/test2/test3",),
                "testvalue",
            ),
            (
                {"test1": [{}, {"test3": "testvalue"}]},
                ("test1", 1, "test3"),
                "testvalue",
            ),
        ],
    )
    def test_valid(self, resource, args, expected):
        p = LookupPath._from_lookup(resource, *args)

        result = p.read_value()

        assert result == expected

    @pytest.mark.parametrize(
        "resource,args",
        [
            (
                {"test1": {"test2": {"test3": "testvalue"}}},
                ("test1/test2/test4",),
            ),
            ({"test1": [{}, {"test3": "testvalue"}]}, ("test1", 0, "test3")),
        ],
    )
    def test_invalid(self, resource, args):
        p = LookupPath._from_lookup(resource, *args)

        with pytest.raises(KeyError):
            p.read_value()


class TestLookupPathGet:
    def test_non_existing_key_default_none(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = p.get("")

        assert result == None

    def test_non_existing_key_default_defined(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = p.get("", default=value)

        assert result == value

    @pytest.mark.parametrize(
        "resource,key,expected",
        (
            [
                {"test1": "test2"},
                "test1",
                "test2",
            ],
            [
                {"test1": {"test2": "test3"}},
                "test1",
                {"test2": "test3"},
            ],
        ),
    )
    def test_key_exists(self, resource, key, expected):
        p = LookupPath._from_lookup(resource)

        result = p.get(key)

        assert result == expected


class TestLookupPathExists:
    def test_non_existing_key(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2/non_existing_key")

        result = p.exists()

        assert result is False

    @pytest.mark.parametrize(
        "resource,key",
        (
            [
                {"test1": "test2"},
                "test1",
            ],
            [
                {"test1": 123},
                "test1",
            ],
            [
                {"test1": True},
                "test1",
            ],
            [
                {"test1": {"test2": "test3"}},
                "test1",
            ],
        ),
    )
    def test_key_exists(self, resource, key):
        p = LookupPath._from_lookup(resource, key)

        result = p.exists()

        assert result is True


class TestLookupPathFloorDiv:

    def test_non_existing_key(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        with pytest.raises(KeyError):
            p // "non_existing_key"

    @pytest.mark.parametrize(
        "resource,key,expected",
        (
            [
                {"test1": "test2"},
                "test1",
                LookupPath._from_lookup({"test1": "test2"}, "test1"),
            ],
            [
                {"test1": {"test2": "test3"}},
                "test1",
                LookupPath._from_lookup(
                    {"test1": {"test2": "test3"}}, "test1"
                ),
            ],
        ),
    )
    def test_key_exists(self, resource, key, expected):
        p = LookupPath._from_lookup(resource)

        result = p // key

        assert result == expected


class TestLookupPathRfloorDiv:

    def test_non_existing_key(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        with pytest.raises(KeyError):
            "non_existing_key" // p

    @pytest.mark.parametrize(
        "resource,key,expected",
        (
            [
                {"test1": "test2"},
                "test1",
                LookupPath._from_lookup({"test1": "test2"}, "test1"),
            ],
            [
                {"test1": {"test2": "test3"}},
                "test1",
                LookupPath._from_lookup(
                    {"test1": {"test2": "test3"}}, "test1"
                ),
            ],
        ),
    )
    def test_key_exists(self, resource, key, expected):
        p = LookupPath._from_lookup(resource)

        result = key // p

        assert result == expected


class TestLookupPathLen:
    def test_empty(self):
        resource = {}
        p = LookupPath._from_lookup(resource)

        result = len(p)

        assert result == 0

    def test_value(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource, "test1")

        result = len(p)

        assert result == 0

    def test_single(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource)

        result = len(p)

        assert result == 1

    def test_list(self):
        resource = {"test1": [{"test2": "test3"}, {"test4": "test5"}]}
        p = LookupPath._from_lookup(resource, "test1")

        result = len(p)

        assert result == 2

    def test_non_existing(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource, "invalid_key")

        with pytest.raises(KeyError):
            len(p)


class TestLookupPathKeys:
    def test_empty(self):
        resource = {}
        p = LookupPath._from_lookup(resource)

        result = p.keys()

        assert list(result) == []

    def test_value(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource, "test1")

        result = p.keys()

        assert list(result) == []

    def test_string(self):
        resource = "test1"
        p = LookupPath._from_lookup(resource)

        result = p.keys()

        assert list(result) == []

    def test_dict(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource)

        result = p.keys()

        assert list(result) == ["test1"]

    def test_list(self):
        resource = {"test1": [{"test2": "test3"}, {"test4": "test5"}]}
        p = LookupPath._from_lookup(resource, "test1")

        result = p.keys()

        assert list(result) == [0, 1]

    def test_non_existing(self):
        resource = {"test1": "test2"}
        p = LookupPath._from_lookup(resource, "invalid_key")

        with pytest.raises(KeyError):
            p.keys()


class TestLookupPathContains:
    def test_valid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = "test3" in p

        assert result is True

    def test_invalid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath._from_lookup(resource, "test1/test2")

        result = "test4" in p

        assert result is False


class TestLookupPathItems:
    def test_empty(self):
        resource = {}
        p = LookupPath._from_lookup(resource)

        result = p.items()

        assert type(result) is GeneratorType
        assert dict(result) == {}

    def test_keys(self):
        resource = {
            "test1": 1,
            "test2": 2,
        }
        p = LookupPath._from_lookup(resource)

        result = p.items()

        assert type(result) is GeneratorType
        assert dict(result) == {
            "test1": p / "test1",
            "test2": p / "test2",
        }


class TestLookupPathOpen:
    def test_content_cached(self):
        value = {
            "test3": "test4",
        }
        resource = MockResource(
            test1=1,
            test2=value,
        )
        p = LookupPath._from_lookup(resource, "test2")

        result = p.read_value()
        assert resource.getitem_counter == 1
        assert result == p.read_value()
        assert resource.getitem_counter == 1


class TestLookupPathFromLookup:
    def test_from_lookup_matches_private_constructor(self):
        resource = {"test1": {"test2": "test3"}}

        p1 = LookupPath._from_lookup(resource, "test1")
        p2 = LookupPath.from_lookup(resource, "test1")

        assert p1 == p2
        assert p1.read_value() == p2.read_value()


class TestAccessorPathOpenAndStat:
    def test_open_yields_read_value(self):
        resource = {"test1": {"test2": "value"}}
        p = LookupPath.from_lookup(resource, "test1")

        with p.open() as value:
            assert value == {"test2": "value"}

    def test_stat_returns_none_for_missing(self):
        resource = {"test1": {"test2": "value"}}
        p = LookupPath.from_lookup(resource, "test1", "missing")

        assert p.stat() is None


class TestPathlibLikeManipulation:
    def test_name_parent_parents(self):
        p = BasePath("a", "b", "c")

        assert p.name == "c"
        assert str(p.parent) == "a/b"
        assert [str(x) for x in p.parents] == ["a/b", "a", ""]

    def test_joinpath(self):
        p = BasePath("a")
        assert str(p.joinpath("b", "c")) == "a/b/c"

    def test_suffix_stem_suffixes(self):
        p = BasePath("archive.tar.gz")
        assert p.suffix == ".gz"
        assert p.suffixes == [".tar", ".gz"]
        assert p.stem == "archive.tar"

        dotfile = BasePath(".bashrc")
        assert dotfile.suffix == ""
        assert dotfile.suffixes == []
        assert dotfile.stem == ".bashrc"

    def test_with_name_and_with_suffix(self):
        p = BasePath("a", "file.txt")
        assert str(p.with_name("other.md")) == "a/other.md"
        assert str(p.with_suffix(".csv")) == "a/file.csv"

    def test_with_name_respects_separator(self):
        p = BasePath("a", "b", separator=".")

        with pytest.raises(ValueError):
            p.with_name("c.d")

    def test_relative_to_and_is_relative_to(self):
        p = BasePath("a", "b", "c")
        assert p.is_relative_to("a")
        assert p.is_relative_to("a", "b")
        assert not p.is_relative_to("x")
        assert str(p.relative_to("a")) == "b/c"
        assert str(p.relative_to("a", "b")) == "c"

        with pytest.raises(ValueError):
            p.relative_to("x")

    def test_relative_to_and_is_relative_to_custom_separator(self):
        p = BasePath("a.b.c", separator=".")

        assert p.is_relative_to("a")
        assert p.is_relative_to("a.b")
        assert not p.is_relative_to("a/b")

        assert str(p.relative_to("a")) == "b.c"
        assert str(p.relative_to("a.b")) == "c"

        with pytest.raises(ValueError):
            p.relative_to("x")

    def test_as_posix_and_fspath(self):
        p = BasePath("a", "b")
        assert p.as_posix() == "a/b"
        assert p.__fspath__() == "a/b"


class TestAccessorPathPathlibCompat:
    def test_parent_preserves_accessor(self):
        resource = {"a": {"b": {"c": "value"}}}
        p = LookupPath.from_lookup(resource, "a", "b", "c")

        assert p.parent.read_value() == {"c": "value"}

    def test_relative_to_preserves_accessor(self):
        resource = {"a": {"b": {"c": "value"}}}
        p = LookupPath.from_lookup(resource, "a", "b", "c")

        rel = p.relative_to("a")
        assert str(rel) == "b/c"
        # Like pathlib, a relative path is not automatically anchored to the
        # stripped prefix; consumers must re-anchor explicitly if needed.

    def test_with_name_preserves_accessor(self):
        resource = {"a": {"x": "value"}}
        p = LookupPath.from_lookup(resource, "a", "x")

        renamed = p.with_name("x")
        assert renamed.read_value() == "value"
