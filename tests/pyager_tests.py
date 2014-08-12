import collections
import unittest

from ddt import data, ddt, unpack
import mock
from pyager import Pyager

@ddt
class PyagerTest(unittest.TestCase):
    def setUp(self):
        self.pageable = range(1,96)
        self.url = 'foo.com?page=__page__'
        self.pyager = Pyager(self.pageable, self.url)

    def test_init_defaults(self):
        self.assertEqual(self.pageable, self.pyager.pageable)
        self.assertEqual(self.url, self.pyager.url)
        self.assertEqual(1, self.pyager.page)
        self.assertEqual(10, self.pyager.page_size)
        self.assertEqual(3, self.pyager.window)

    def test_init_override_defaults(self):
        page = 5
        page_size = 11
        window = 5
        self.pyager = Pyager(self.pageable, self.url, page=page, page_size=page_size, window=window)

        self.assertEqual(page, self.pyager.page)
        self.assertEqual(page_size, self.pyager.page_size)
        self.assertEqual(window, self.pyager.window)

    def test_window(self):
        self.pyager._do_calc = mock.MagicMock(name='_do_calc')

        # good change
        self.pyager.window = 2
        self.assertEqual(2, self.pyager._window)
        self.assertEqual(2, self.pyager.window)

        self.pyager._do_calc.assert_called_with()

        # called with garbage
        self.pyager.window = 'cheese'

        #values dont' change
        self.assertEqual(2, self.pyager._window)
        self.assertEqual(2, self.pyager.window)

        self.pyager._do_calc.assert_called_with()

    def test_page_size(self):
        self.pyager._do_calc = mock.MagicMock(name='_do_calc')

        # good change
        self.pyager.page_size = 2
        self.assertEqual(2, self.pyager._page_size)
        self.assertEqual(2, self.pyager.page_size)

        self.pyager._do_calc.assert_called_with()

        # called with garbage
        self.pyager.page_size = 'cheese'

        #values dont' change
        self.assertEqual(2, self.pyager._page_size)
        self.assertEqual(2, self.pyager.page_size)

        self.pyager._do_calc.assert_called_with()

    def test_page(self):
        self.pyager._do_calc = mock.MagicMock(name='_do_calc')

        # good change
        self.pyager.page = 2
        self.assertEqual(2, self.pyager._page)
        self.assertEqual(2, self.pyager.page)

        self.pyager._do_calc.assert_called_with()

        # called with garbage
        self.pyager.page = 'cheese'

        #values dont' change
        self.assertEqual(2, self.pyager._page)
        self.assertEqual(2, self.pyager.page)

        self.pyager._do_calc.assert_called_with()

    @data(
        (1, 3, 10, [1, 2, 3]),    # beginning
        (5, 3, 10, [4, 5, 6]),    # middle
        (10, 3, 10, [8, 9, 10]),  # end
        (1, 4, 10, [1, 2, 3, 4]), # larger window
        (5, 4, 10, [3, 4, 5, 6]), # even middle
        (1, 4, 100, [1]),         # less pages than window
    )
    @unpack
    def test_pages(self, page, window, page_size, expected_pages):
        self.pyager.page = page
        self.pyager.window = window
        self.pyager.page_size = page_size

        pages = self.pyager.pages

        self.assertEqual(len(expected_pages), len(pages))

        for p in expected_pages:
            expected = {
                'url': self.url.replace('__page__', str(p)),
                'number': p,
                'current': p == page
            }
            self.assertIn(expected, pages)

    @data(
        (1, None),                      # beginning
        (2, {'url':'foo.com?page=1'}),  # middle
        (10, {'url':'foo.com?page=1'}), # end
    )
    @unpack
    def test_first(self, page, expected):
        self.pyager.page = page
        self.assertEqual(expected, self.pyager.first)

    @data(
        (1, None),                      # beginning
        (2, {'url':'foo.com?page=1'}),  # middle
        (10, {'url':'foo.com?page=9'}), # end
    )
    @unpack
    def test_previous(self, page, expected):
        self.pyager.page = page
        self.assertEqual(expected, self.pyager.previous)

    @data(
        (1, {'url':'foo.com?page=10'}), # beginning
        (2, {'url':'foo.com?page=10'}), # middle
        (10, None),                     # end
    )
    @unpack
    def test_last(self, page, expected):
        self.pyager.page = page
        self.assertEqual(expected, self.pyager.last)

    @data(
        (1, {'url':'foo.com?page=2'}), # beginning
        (2, {'url':'foo.com?page=3'}), # middle
        (10, None),                    # end
    )
    @unpack
    def test_next(self, page, expected):
        self.pyager.page = page
        self.assertEqual(expected, self.pyager.next)

    @data(
        ('foo', 1, 'foo'),
        ('__page__', 1, '1'),
        ('__page__/__page__', 1, '1/1'),
    )
    @unpack
    def test_build_url(self, url, page, expected):
        self.pyager.url = url
        self.assertEqual(expected, self.pyager._build_url(page))

    @data(
        (1, 10, [1,2,3,4,5,6,7,8,9,10], 1, 10, 95),
        (2, 10, [11,12,13,14,15,16,17,18,19,20], 2, 10, 95),
        (10, 10, [91,92,93,94,95], 10, 10, 95),
        (1, 2, [1,2], 1, 48, 95),
        ("not a page number", 2, [1,2], 1, 48, 95),
        (-1, 2, [1,2], 1, 48, 95),
        (100, 2, [95], 48, 48, 95),
    )
    @unpack
    def test_do_calc(self, page, page_size, expected_items, expected_page, expected_total_pages, expected_total_items):
        self.pyager.page_size = page_size
        self.pyager.page = page
        self.assertEqual(expected_total_pages, self.pyager.total_pages)
        self.assertEqual(expected_total_items, self.pyager.total_items)
        self.assertEqual(expected_page, self.pyager.page)
        self.assertEqual(expected_items, self.pyager.items)

    def test_do_calc_error(self):
        not_pageable = 7
        self.pyager.pageable = not_pageable

        self.assertRaises(TypeError, self.pyager._do_calc)

    def test_empty(self):
        class CrankyList(collections.Sequence):
            def __len__(self):
                return 0
            def __getitem__(self, slice):
                if slice.start < 0:
                    raise ValueError('negative initial offset in this slice: '+str(slice))
                return []
        self.pyager.pageable = CrankyList()
        self.pyager._do_calc()

if __name__ == '__main__':
    unittest.main()
