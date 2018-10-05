import re


def _regex_match(testing, expected):
    assert bool(re.match(expected, testing))

def recursive_regex_test(testing, expected, _assert=_regex_match):
    if isinstance(expected, str):
        return _assert(testing, expected)
    if hasattr(expected, 'items') and callable(expected.items):
        for key, value in expected.items():
            recursive_regex_test(testing.get(key, ''), value, _assert)
