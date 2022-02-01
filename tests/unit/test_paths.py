from types import GeneratorType

import pytest

from pathable.paths import SEPARATOR
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


class TestBasePathFromParts:
    def test_default(self):
        parts = []
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts(self):
        parts = ["part1"]
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_unparsed(self):
        parts = ["part1", "part2"]
        part = SEPARATOR.join(parts)
        p = BasePath._from_parts([part])

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_many(self):
        parts = ["part1", "part2"]
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_separator(self):
        parts = []
        separator = "."
        p = BasePath._from_parts(parts, separator=separator)

        assert p.parts == parts
        assert p.separator == separator


class TestBasePathFromParsedParts:
    def test_default(self):
        parts = []
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts(self):
        parts = ["part1"]
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_unparsed(self):
        part = SEPARATOR.join(["part1", "part2"])
        parts = [part]
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_many(self):
        parts = ["part1", "part2"]
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_separator(self):
        parts = []
        separator = "."
        p = BasePath._from_parsed_parts(parts, separator=separator)

        assert p.parts == parts
        assert p.separator == separator


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


class TestLookupPathPathGetItem:
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


class TestLookupPathPathContains:
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


class TestLookupPathPathItems:
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
