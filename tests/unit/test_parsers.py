from uuid import uuid4

import pytest

from pathable.parsers import parse_parts


class TestParseParts:

    separator = "/"

    def test_empty(self):
        parts = []

        result = parse_parts(parts, self.separator)

        assert result == []

    def test_one(self):
        parts = ["test"]

        result = parse_parts(parts, self.separator)

        assert result == [
            "test",
        ]

    def test_simple(self):
        parts = ["test", "test1", "test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test1", "test2"]

    def test_none(self):
        parts = ["test", None, "test1", None, "test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test1", "test2"]

    def test_relative(self):
        parts = ["test", ".", "test1", ".", "test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test1", "test2"]

    def test_separator(self):
        sep_part = "test1{sep}test2{sep}test3".format(sep=self.separator)
        parts = ["test", sep_part]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test1", "test2", "test3"]

    def test_separator_with_relative(self):
        sep_part = "test1{sep}.{sep}test2{sep}.{sep}test3".format(
            sep=self.separator
        )
        parts = ["test", sep_part]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test1", "test2", "test3"]

    def test_int(self):
        parts = ["test", 1, "test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", 1, "test2"]

    def test_hashable_passthrough(self):
        token = uuid4()
        parts = ["test", token, "test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", token, "test2"]

    def test_bytes(self):
        parts = [b"test", b"test2"]

        result = parse_parts(parts, self.separator)

        assert result == ["test", "test2"]

    def test_invalid_part_message(self):
        parts = [[]]

        with pytest.raises(
            TypeError,
            match=r"part must be Hashable or None; got <class 'list'>",
        ):
            parse_parts(parts, self.separator)
