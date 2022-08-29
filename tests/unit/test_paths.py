from types import GeneratorType

import pytest

from pathable.parsers import SEPARATOR
from pathable.paths import BasePath
from pathable.paths import LookupPath


class TestBasePathInit:
    def test_default(self):
        p = BasePath()

        assert p.parts == []
        assert p.separator == SEPARATOR

    def test_part_text(self):
        part = "part"
        p = BasePath(part)

        assert p.parts == [
            part,
        ]
        assert p.separator == SEPARATOR

    def test_part_binary(self):
        part = b"part"
        p = BasePath(part)

        assert p.parts == [
            "part",
        ]
        assert p.separator == SEPARATOR

    def test_part_binary_many(self):
        part1 = b"part1"
        part2 = b"part2"
        p = BasePath(part1, part2)

        assert p.parts == ["part1", "part2"]
        assert p.separator == SEPARATOR

    def test_part_text_many(self):
        part1 = "part1"
        part2 = "part2"
        p = BasePath(part1, part2)

        assert p.parts == [part1, part2]
        assert p.separator == SEPARATOR

    def test_part_path(self):
        part = "part"
        p1 = BasePath(part)
        p = BasePath(p1)

        assert p.parts == [
            part,
        ]
        assert p.separator == SEPARATOR

    def test_part_path_many(self):
        part1 = "part1"
        part2 = "part2"
        p1 = BasePath(part1)
        p2 = BasePath(part2)
        p = BasePath(p1, p2)

        assert p.parts == [part1, part2]
        assert p.separator == SEPARATOR

    def test_separator(self):
        separator = "."
        p = BasePath(separator=separator)

        assert p.parts == []
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
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)
        p._cparts_cached = p._get_cparts()

        assert str(p) == separator.join(args)


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

        assert hash(p) == hash(tuple(p._cparts))

    def test_single(self):
        p = BasePath("part1")

        assert hash(p) == hash(tuple(p._cparts))

    def test_double(self):
        args = ["part1", "part2"]
        p = BasePath(*args)

        assert hash(p) == hash(tuple(p._cparts))

    def test_separator(self):
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)

        assert hash(p) == hash(tuple(p._cparts))

    def test_cparts_cached(self):
        args = ["part1", "part2"]
        separator = ","
        p = BasePath(*args, separator=separator)
        p._cparts_cached = p._get_cparts()

        assert hash(p) == hash(tuple(p._cparts))


class TestBasePathMakeChild:
    @pytest.fixture
    def base_path(self):
        return BasePath(separator=SEPARATOR)

    def test_none(self, base_path):
        args = []
        p = base_path._make_child(args)

        assert p.parts == args
        assert p.separator == SEPARATOR

    def test_arg(self, base_path):
        args = ["part1"]
        p = base_path._make_child(args)

        assert p.parts == args
        assert p.separator == SEPARATOR

    def test_arg_unparsed(self, base_path):
        parts = ["part1", "part2"]
        arg = SEPARATOR.join(parts)
        args = [arg]
        p = base_path._make_child(args)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_args_many(self, base_path):
        args = ["part1", "part2"]
        p = base_path._make_child(args)

        assert p.parts == args
        assert p.separator == SEPARATOR


class TestBasePathMakeChildRelPath:
    @pytest.fixture
    def base_path(self):
        return BasePath(separator=SEPARATOR)

    def test_part(self, base_path):
        part = "part1"
        p = base_path._make_child_relpath(part)

        assert p.parts == [part]
        assert p.separator == SEPARATOR


class TestBasePathTruediv:
    def test_default_empty(self):
        p = BasePath() / ""

        assert p.parts == []
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        "part1,part2,parts,separator",
        (
            [
                "",
                "",
                [],
                SEPARATOR,
            ],
            [
                "",
                "part1",
                ["part1"],
                SEPARATOR,
            ],
            [
                "part1",
                "",
                ["part1"],
                SEPARATOR,
            ],
            [
                "part1",
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                b"",
                "",
                [],
                SEPARATOR,
            ],
            [
                b"",
                "part1",
                ["part1"],
                SEPARATOR,
            ],
            [
                b"part1",
                "",
                ["part1"],
                SEPARATOR,
            ],
            [
                b"part1",
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                "part1",
                BasePath("part2"),
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                BasePath("part2"),
                ["part1", "part2"],
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

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == SEPARATOR

    def test_combined_different_separators(self):
        part11 = "part11"
        part12 = "part12"
        part21 = "part21"
        part22 = "part22"
        separator1 = "."
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p1 = BasePath(part2)
        p = BasePath(part1, separator=separator1) / p1

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == separator1

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            BasePath() / []


class TestBasePathRtruediv:
    def test_default_empty(self):
        p = "" / BasePath()

        assert p.parts == []
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        "part1,part2,parts,separator",
        (
            [
                "",
                "",
                [],
                SEPARATOR,
            ],
            [
                "",
                "part1",
                ["part1"],
                SEPARATOR,
            ],
            [
                "part1",
                "",
                ["part1"],
                SEPARATOR,
            ],
            [
                "part1",
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                b"",
                "",
                [],
                SEPARATOR,
            ],
            [
                b"",
                "part1",
                ["part1"],
                SEPARATOR,
            ],
            [
                b"part1",
                "",
                ["part1"],
                SEPARATOR,
            ],
            [
                b"part1",
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                "part1",
                BasePath("part2"),
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                "part2",
                ["part1", "part2"],
                SEPARATOR,
            ],
            [
                BasePath("part1"),
                BasePath("part2"),
                ["part1", "part2"],
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

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == SEPARATOR

    def test_type_not_implemented(self):
        with pytest.raises(TypeError):
            [] / BasePath()


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


class TestLookupPathIter:
    def test_object(self):
        resource = {"test1": {"test2": {"test3": "test"}}}
        p = LookupPath(resource, "test1/test2")

        result = iter(p)

        assert type(result) == GeneratorType
        result_list = list(result)
        assert result_list == [
            LookupPath(resource, "test1/test2/0"),
        ]

    def test_list(self):
        resource = {"test1": {"test2": ["test3", "test4"]}}
        p = LookupPath(resource, "test1/test2")

        result = iter(p)

        assert type(result) == GeneratorType
        result_list = list(result)
        assert result_list == [
            LookupPath(resource, "test1/test2/0"),
            LookupPath(resource, "test1/test2/1"),
        ]


class TestLookupPathGetItem:
    def test_valid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = p["test3"]

        assert result == value

    def test_invalid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        with pytest.raises(KeyError):
            p["test4"]


class TestLookupPathGetkey:
    def test_valid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = p.getkey("test3")

        assert result == value

    def test_invalid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = p.getkey("test4")

        assert result is None


class TestLookupPathGet:
    def test_non_existing_key_default_none(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = p.get("")

        assert result == None

    def test_non_existing_key_default_defined(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = p.get("", default=value)

        assert result == value

    @pytest.mark.parametrize(
        "resource,key,expected",
        (
            [
                {"test1": "test2"},
                "test1",
                LookupPath({"test1": "test2"}, "test1"),
            ],
            [
                {"test1": {"test2": "test3"}},
                "test1",
                LookupPath({"test1": {"test2": "test3"}}, "test1"),
            ],
        ),
    )
    def test_key_exists(self, resource, key, expected):
        p = LookupPath(resource)

        result = p.get(key)

        assert result == expected


class TestLookupPathLen:
    def test_empty(self):
        resource = {}
        p = LookupPath(resource)

        result = len(p)

        assert result == 0

    def test_value(self):
        resource = {"test1": "test2"}
        p = LookupPath(resource, "test1")

        result = len(p)

        assert result == 5

    def test_single(self):
        resource = {"test1": "test2"}
        p = LookupPath(resource)

        result = len(p)

        assert result == 1

    def test_list(self):
        resource = {"test1": [{"test2": "test3"}, {"test4": "test5"}]}
        p = LookupPath(resource, "test1")

        result = len(p)

        assert result == 2


class TestLookupPathKeys:
    def test_empty(self):
        resource = {}
        p = LookupPath(resource)

        result = p.keys()

        assert list(result) == []

    def test_value(self):
        resource = {"test1": "test2"}
        p = LookupPath(resource, "test1")

        with pytest.raises(AttributeError):
            p.keys()

    def test_single(self):
        resource = {"test1": "test2"}
        p = LookupPath(resource)

        result = p.keys()

        assert list(result) == ["test1"]

    def test_list(self):
        resource = {"test1": [{"test2": "test3"}, {"test4": "test5"}]}
        p = LookupPath(resource, "test1")

        with pytest.raises(AttributeError):
            p.keys()


class TestLookupPathContains:
    def test_valid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = "test3" in p

        assert result is True

    def test_invalid(self):
        value = "testvalue"
        resource = {"test1": {"test2": {"test3": value}}}
        p = LookupPath(resource, "test1/test2")

        result = "test4" in p

        assert result is False


class TestLookupPathItems:
    def test_empty(self):
        resource = {}
        p = LookupPath(resource)

        result = p.items()

        assert type(result) is GeneratorType
        assert dict(result) == {}

    def test_keys(self):
        resource = {
            "test1": 1,
            "test2": 2,
        }
        p = LookupPath(resource)

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
        resource = {
            "test1": 1,
            "test2": value,
        }
        p = LookupPath(resource, "test2")

        result = p.getkey("test3")
        assert result == p.getkey("test3")

        assert p._content_cached == value
