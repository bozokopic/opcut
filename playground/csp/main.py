import sys
sys.path += ['../../src_py']

from opcut import csp


def main():
    panels = [
        csp.Panel(id='p1', width=100, height=100)
    ]
    items = [
        csp.Item(id='i1', width=10, height=10, rotate=True),
        csp.Item(id='i2', width=10, height=9, rotate=True),
        csp.Item(id='i3', width=20, height=8, rotate=True),
        csp.Item(id='i4', width=10, height=20, rotate=True),
        csp.Item(id='i5', width=30, height=19, rotate=True),
        csp.Item(id='i6', width=10, height=18, rotate=True),
        csp.Item(id='i7', width=10, height=17, rotate=True),
        csp.Item(id='i8', width=20, height=16, rotate=True),
        csp.Item(id='i9', width=10, height=15, rotate=True),
        csp.Item(id='i10', width=30, height=14, rotate=True),
        csp.Item(id='i11', width=10, height=20, rotate=True),
        csp.Item(id='i12', width=30, height=19, rotate=True),
        csp.Item(id='i13', width=10, height=18, rotate=True),
        csp.Item(id='i14', width=10, height=17, rotate=True),
        csp.Item(id='i15', width=20, height=16, rotate=True),
        csp.Item(id='i16', width=10, height=15, rotate=True),
        csp.Item(id='i17', width=30, height=14, rotate=True),
        csp.Item(id='i18', width=10, height=20, rotate=True),
        csp.Item(id='i19', width=30, height=19, rotate=True),
    ]
    cut_width = 1
    method = csp.Method.FORWARD_GREEDY
    result = csp.calculate(panels, items, cut_width, method)
    print(result)


if __name__ == '__main__':
    sys.exit(main())
