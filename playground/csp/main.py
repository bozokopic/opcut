import sys
sys.path += ['../../src_py']

from opcut import common
from opcut import csp
from opcut import output


def main():
    panels = [
        common.Panel(id='p1', width=100, height=65)
    ]
    items = [
        common.Item(id='i1', width=10, height=10, can_rotate=True),
        common.Item(id='i2', width=10, height=9, can_rotate=True),
        common.Item(id='i3', width=20, height=8, can_rotate=True),
        common.Item(id='i4', width=10, height=20, can_rotate=True),
        common.Item(id='i5', width=30, height=19, can_rotate=True),
        common.Item(id='i6', width=10, height=18, can_rotate=False),
        common.Item(id='i7', width=10, height=17, can_rotate=True),
        common.Item(id='i8', width=20, height=16, can_rotate=True),
        common.Item(id='i9', width=10, height=15, can_rotate=True),
        common.Item(id='i10', width=30, height=14, can_rotate=True),
        common.Item(id='i11', width=10, height=20, can_rotate=True),
        common.Item(id='i12', width=19, height=30, can_rotate=False),
        common.Item(id='i13', width=10, height=18, can_rotate=True),
        common.Item(id='i14', width=10, height=17, can_rotate=True),
        common.Item(id='i15', width=20, height=16, can_rotate=True),
        common.Item(id='i16', width=10, height=15, can_rotate=True),
        common.Item(id='i17', width=30, height=14, can_rotate=True),
        common.Item(id='i18', width=10, height=20, can_rotate=True),
        common.Item(id='i19', width=30, height=19, can_rotate=True),
    ]
    cut_width = 0.4
    method = common.Method.FORWARD_GREEDY
    result = csp.calculate(panels, items, cut_width, method)
    pdf_bytes = output.generate_pdf(result)
    with open('output.pdf', 'wb') as f:
        f.write(pdf_bytes)


if __name__ == '__main__':
    sys.exit(main())
