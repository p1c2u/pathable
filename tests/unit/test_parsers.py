import pytest
from six import u

from dictpath.paths import BasePath
from dictpath.parsers import parse_parts, parse_args


class TestParseParts(object):

    separator = '/'

    def test_empty(self):
        parts = []

        result = parse_parts(parts, self.separator)

        assert result == []

    def test_one(self):
        parts = ['test']

        result = parse_parts(parts, self.separator)

        assert result == ['test']

    def test_simple(self):
        parts = ['test', 'test1', 'test2']

        result = parse_parts(parts, self.separator)

        assert result == ['test', 'test1', 'test2']

    def test_none(self):
        parts = ['test', None, 'test1', None, 'test2']

        result = parse_parts(parts, self.separator)

        assert result == ['test', 'test1', 'test2']

    def test_relative(self):
        parts = ['test', '.', 'test1', '.', 'test2']

        result = parse_parts(parts, self.separator)

        assert result == ['test', 'test1', 'test2']

    def test_separator(self):
        sep_part = 'test1{sep}test2{sep}test3'.format(
            sep=self.separator)
        parts = ['test', sep_part]

        result = parse_parts(parts, self.separator)

        assert result == ['test', 'test1', 'test2', 'test3']

    def test_separator_with_relative(self):
        sep_part = 'test1{sep}.{sep}test2{sep}.{sep}test3'.format(
            sep=self.separator)
        parts = ['test', sep_part]

        result = parse_parts(parts, self.separator)

        assert result == ['test', 'test1', 'test2', 'test3']


class TestParseArgs(object):

    separator = '/'

    def test_empty(self):
        args = []

        result = parse_args(args, self.separator)

        assert result == []

    def test_string(self):
        args = [u('test')]

        result = parse_args(args, self.separator)

        assert result == ['test']

    def test_string_many(self):
        args = [u('test'), u('test2')]

        result = parse_args(args, self.separator)

        assert result == ['test', 'test2']

    def test_path(self):
        args = [BasePath(u('test'))]

        result = parse_args(args, self.separator)

        assert result == ['test']

    def test_invalid_part(self):
        args = [2, 3]

        with pytest.raises(TypeError):
            parse_args(args, self.separator)
