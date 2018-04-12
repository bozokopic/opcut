import io

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from opcut import util


def generate_pdf(result, pagesize_mm=(210, 297),
                 margin_top_mm=10, margin_bottom_mm=20,
                 margin_left_mm=10, margin_right_mm=10):
    """Generate PDF output

    Args:
        result (opcut.common.Result): result
        pagesize (Tuple[float,float]): page size as (with, height) in mm
        margin_top_mm (float): margin top in mm
        margin_bottom_mm (float): margin bottom in mm
        margin_left_mm (float): margin left in mm
        margin_right_mm (float): margin right in mm

    Returns:
        bytes

    """
    pagesize = tuple(map(lambda x: x * mm, pagesize_mm))
    margin = _Margin(top=margin_top_mm * mm,
                     right=margin_right_mm * mm,
                     bottom=margin_bottom_mm * mm,
                     left=margin_left_mm * mm)
    ret = io.BytesIO()
    c = canvas.Canvas(ret, pagesize=pagesize)
    c.setFillColorRGB(0.9, 0.9, 0.9)
    for panel in result.params.panels:
        _pdf_write_panel(c, pagesize, margin, result, panel)
    c.save()
    return ret.getvalue()


def generate_csv(result):
    """Generate CSV output

    Args:
        result (opcut.common.Result): result

    Returns:
        bytes

    """
    return b''


_Margin = util.namedtuple('_Margin', 'top', 'right', 'bottom', 'left')


def _pdf_write_panel(c, pagesize, margin, result, panel):
    if (panel.width / panel.height >
            (pagesize[0] - margin.left - margin.right) /
            (pagesize[1] - margin.top - margin.bottom)):
        scale = (
            (pagesize[0] - (margin.left + margin.right) * mm) /
            panel.width)
    else:
        scale = (
            (pagesize[1] - (margin.top + margin.bottom) * mm) /
            panel.height)
    width = panel.width * scale
    height = panel.height * scale
    x0 = ((pagesize[0] - width) * margin.left /
          (margin.left + margin.right))
    y0 = ((pagesize[1] - height) * margin.bottom /
          (margin.top + margin.bottom))
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.rect(x0, y0, width, height, stroke=1, fill=1)
    for used in result.used:
        if used.panel != panel:
            continue
        _pdf_write_used(c, x0, y0, scale, result, used)
    for unused in result.unused:
        if unused.panel != panel:
            continue
        _pdf_write_unused(c, x0, y0, scale, result, unused)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(pagesize[0] / 2,  margin.bottom / 2,
                        panel.id)
    c.showPage()


def _pdf_write_used(c, x0, y0, scale, result, used):
    width = used.item.width * scale
    height = used.item.height * scale
    if used.rotate:
        width, height = height, width
    x = used.x * scale + x0
    y = (used.panel.height - used.y) * scale + y0 - height
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, width, height, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(x + width / 2,  y + height / 2 - 6, used.item.id)


def _pdf_write_unused(c, x0, y0, scale, result, unused):
    width = unused.width * scale
    height = unused.height * scale
    x = unused.x * scale + x0
    y = (unused.panel.height - unused.y) * scale + y0 - height
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(x, y, width, height, stroke=0, fill=1)
