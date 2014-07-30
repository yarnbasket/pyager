class Pyager(object):
    def __init__(self, pageable, url, page=1, page_size=10, window=3):
        self.pageable = pageable
        self.url = url

        self._window = int(window)
        self._page = int(page)
        self._page_size = int(page_size)
        self._do_calc()

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        try:
            self._window = int(value)
        except (ValueError, TypeError):
            pass # don't change the window if we dont' get a number
        self._do_calc()

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        try:
            self._page_size = int(value)
        except (ValueError, TypeError):
            pass # don't change the page_size if we dont' get a number
        self._do_calc()

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        try:
            self._page = int(value)
        except (ValueError, TypeError):
            pass # don't change the page if we dont' get a number
        self._do_calc()

    @property
    def pages(self):
        pages = []
        low = self._page - (self.window / 2)
        high = self._page + (self.window / 2) + (self.window % 2)

        if low < 1:
            _range = range(1, self.window + 1)
        elif high > self.total_pages:
            _range = range(self.total_pages - self.window + 1, self.total_pages + 1)
        else:
            _range = range(low, high)

        count = 1
        for p in _range:
            pages.append({
                'url': self._build_url(p),
                'number': p,
                'current': p == self._page
            })

            count += 1
            if count > self.total_pages:
                break

        return pages

    @property
    def first(self):
        if self._page == 1:
            return None
        else:
            return {
                'url': self._build_url(1),
            }

    @property
    def previous(self):
        if self._page == 1:
            return None
        else:
            return {
                'url': self._build_url(self._page - 1),
            }

    @property
    def next(self):
        if self._page == self.total_pages:
            return None
        else:
            return {
                'url': self._build_url(self._page + 1),
            }

    @property
    def last(self):
        if self._page == self.total_pages:
            return None
        else:
            return {
                'url': self._build_url(self.total_pages),
            }

    def _build_url(self, page):
        return self.url.replace('__page__', str(page))

    def _do_calc(self):
        try:
            self.total_items = len(self.pageable)
            self.total_pages = ((self.total_items - 1) // self._page_size) + 1
            self._page = max(1, self._page) # handle negative page
            self._page = min(self._page, self.total_pages) # handle page too large
            first = (self._page - 1) * self._page_size + 1
            last = min(first + self._page_size - 1, self.total_items)
            self.items = list(self.pageable[first - 1:last])
        except TypeError:
            raise TypeError("Pagable of type %s must implement __getitem__ and __len__" % type(self.pageable))
