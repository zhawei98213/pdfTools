from pdftools.core import parse_page_ranges


def test_parse_page_ranges_merges_adjacent_segments():
    assert parse_page_ranges("1-3,4,7-8", 10) == [(1, 4), (7, 8)]


def test_parse_page_ranges_all_default():
    assert parse_page_ranges("all", 5) == [(1, 5)]
