from __future__ import division
from types import GeneratorType

import pytest
from six import u, b, iteritems

from dictpath.paths import SEPARATOR, BasePath, DictOrListPath


class TestBasePathInit(object):

    def test_default(self):
        p = BasePath()

        assert p.parts == []
        assert p.separator == SEPARATOR

    def test_part_text(self):
        part = u('part')
        p = BasePath(part)

        assert p.parts == [part, ]
        assert p.separator == SEPARATOR

    def test_part_binary(self):
        part = b('part')
        p = BasePath(part)

        assert p.parts == [u('part'), ]
        assert p.separator == SEPARATOR

    def test_part_binary_many(self):
        part1 = b('part1')
        part2 = b('part2')
        p = BasePath(part1, part2)

        assert p.parts == [u('part1'), u('part2')]
        assert p.separator == SEPARATOR

    def test_part_text_many(self):
        part1 = u('part1')
        part2 = u('part2')
        p = BasePath(part1, part2)

        assert p.parts == [part1, part2]
        assert p.separator == SEPARATOR

    def test_part_path(self):
        part = u('part')
        p1 = BasePath(part)
        p = BasePath(p1)

        assert p.parts == [part, ]
        assert p.separator == SEPARATOR

    def test_part_path_many(self):
        part1 = u('part1')
        part2 = u('part2')
        p1 = BasePath(part1)
        p2 = BasePath(part2)
        p = BasePath(p1, p2)

        assert p.parts == [part1, part2]
        assert p.separator == SEPARATOR

    def test_separator(self):
        separator = '.'
        p = BasePath(separator=separator)

        assert p.parts == []
        assert p.separator == separator


class TestBasePathFromParts(object):

    def test_default(self):
        parts = []
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts(self):
        parts = [u('part1')]
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_unparsed(self):
        parts = [u('part1'), u('part2')]
        part = SEPARATOR.join(parts)
        p = BasePath._from_parts([part])

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_many(self):
        parts = [u('part1'), u('part2')]
        p = BasePath._from_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_separator(self):
        parts = []
        separator = '.'
        p = BasePath._from_parts(
            parts, separator=separator)

        assert p.parts == parts
        assert p.separator == separator


class TestBasePathFromParsedParts(object):

    def test_default(self):
        parts = []
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts(self):
        parts = ['part1']
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_unparsed(self):
        part = SEPARATOR.join(['part1', 'part2'])
        parts = [part]
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_parts_many(self):
        parts = ['part1', 'part2']
        p = BasePath._from_parsed_parts(parts)

        assert p.parts == parts
        assert p.separator == SEPARATOR

    def test_separator(self):
        parts = []
        separator = '.'
        p = BasePath._from_parsed_parts(
            parts, separator=separator)

        assert p.parts == parts
        assert p.separator == separator


class TestBasePathTruediv(object):

    def test_default_empty(self):
        p = BasePath() / u('')

        assert p.parts == []
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        'part1,part2,parts,separator',
        (
            [
                u(''), u(''),
                [], SEPARATOR,
            ],
            [
                u(''), u('part1'),
                ['part1'], SEPARATOR,
            ],
            [
                u('part1'), u(''),
                ['part1'], SEPARATOR,
            ],
            [
                u('part1'), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                b(''), u(''),
                [], SEPARATOR,
            ],
            [
                b(''), u('part1'),
                ['part1'], SEPARATOR,
            ],
            [
                b('part1'), u(''),
                ['part1'], SEPARATOR,
            ],
            [
                b('part1'), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                u('part1'), BasePath(u('part2')),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                BasePath(u('part1')), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                BasePath(u('part1')), BasePath(u('part2')),
                ['part1', 'part2'], SEPARATOR,
            ],
        )
    )
    def test_parts(self, part1, part2, parts, separator):
        p = BasePath(part1) / part2

        assert p.parts == parts
        assert p.separator == separator

    def test_combined(self):
        part11 = u('part11')
        part12 = u('part12')
        part21 = u('part21')
        part22 = u('part22')
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p = BasePath(part1) / part2

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == SEPARATOR

    def test_combined_different_separators(self):
        part11 = u('part11')
        part12 = u('part12')
        part21 = u('part21')
        part22 = u('part22')
        separator1 = '.'
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p1 = BasePath(part2)
        p = BasePath(part1, separator=separator1) / p1

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == separator1


class TestBasePathRtruediv(object):

    def test_default_empty(self):
        p = u('') / BasePath()

        assert p.parts == []
        assert p.separator == SEPARATOR

    @pytest.mark.parametrize(
        'part1,part2,parts,separator',
        (
            [
                u(''), u(''),
                [], SEPARATOR,
            ],
            [
                u(''), u('part1'),
                ['part1'], SEPARATOR,
            ],
            [
                u('part1'), u(''),
                ['part1'], SEPARATOR,
            ],
            [
                u('part1'), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                b(''), u(''),
                [], SEPARATOR,
            ],
            [
                b(''), u('part1'),
                ['part1'], SEPARATOR,
            ],
            [
                b('part1'), u(''),
                ['part1'], SEPARATOR,
            ],
            [
                b('part1'), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                u('part1'), BasePath(u('part2')),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                BasePath(u('part1')), u('part2'),
                ['part1', 'part2'], SEPARATOR,
            ],
            [
                BasePath(u('part1')), BasePath(u('part2')),
                ['part1', 'part2'], SEPARATOR,
            ],
        )
    )
    def test_parts(self, part1, part2, parts, separator):
        p = part1 / BasePath(part2)

        assert p.parts == parts
        assert p.separator == separator

    def test_combined(self):
        part11 = u('part11')
        part12 = u('part12')
        part21 = u('part21')
        part22 = u('part22')
        part1 = SEPARATOR.join([part11, part12])
        part2 = SEPARATOR.join([part21, part22])
        p = part1 / BasePath(part2)

        assert p.parts == [part11, part12, part21, part22]
        assert p.separator == SEPARATOR


class TestBasePathEq(object):

    @pytest.mark.parametrize(
        'part1,part2,expected',
        (
            [
                u(''), u(''), True
            ],
            [
                u(''), u('part'), False
            ],
            [
                u('part'), u(''), False
            ],
            [
                u('part'), u('part'), True
            ],
            [
                u('part'), BasePath(u('part')), True
            ],
            [
                BasePath(u('part')), u('part'), True
            ],
            [
                BasePath(u('part')), BasePath(u('part')), True
            ],
        )
    )
    def test_parts(self, part1, part2, expected):
        result = BasePath(part1) == BasePath(part2)

        assert result is expected


class TestDictOrListPathPathGetItem(object):

    def test_valid(self):
        value = 'testvalue'
        resource = {
            'test1': {
                'test2': {
                    'test3': value
                }
            }
        }
        p = DictOrListPath(resource, u('test1/test2'))

        result = p['test3']

        assert result == value

    def test_invalid(self):
        value = 'testvalue'
        resource = {
            'test1': {
                'test2': {
                    'test3': value
                }
            }
        }
        p = DictOrListPath(resource, u('test1/test2'))

        with pytest.raises(KeyError):
            p['test4']


class TestDictOrListPathPathContains(object):

    def test_valid(self):
        value = 'testvalue'
        resource = {
            'test1': {
                'test2': {
                    'test3': value
                }
            }
        }
        p = DictOrListPath(resource, u('test1/test2'))

        result = 'test3' in p

        assert result is True

    def test_invalid(self):
        value = 'testvalue'
        resource = {
            'test1': {
                'test2': {
                    'test3': value
                }
            }
        }
        p = DictOrListPath(resource, u('test1/test2'))

        result = 'test4' in p

        assert result is False


class TestDictOrListPathPathIteritems(object):

    def test_empty(self):
        resource = {}
        p = DictOrListPath(resource)

        result = iteritems(p)

        assert type(result) is GeneratorType
        assert dict(result) == {}

    def test_keys(self):
        resource = {
            'test1': 1,
            'test2': 2,
        }
        p = DictOrListPath(resource)

        result = iteritems(p)

        assert type(result) is GeneratorType
        assert dict(result) == {
            'test1': p / 'test1',
            'test2': p / 'test2',
        }
