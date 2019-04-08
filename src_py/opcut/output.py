import io

import cairo

from opcut import common


def generate_output(result, output_type, panel_id=None,
                    settings=common.OutputSettings()):
    """Generate output

    Args:
        result (common.Result): result
        output_type (common.OutputType): output type
        panel_id (Optional[str]): panel id (None represents all panels)
        settings (common.OutputSettings): output settings

    Returns:
        bytes

    """
    ret = io.BytesIO()
    surface_cls = {common.OutputType.PDF: cairo.PDFSurface,
                   common.OutputType.SVG: cairo.SVGSurface}[output_type]
    with surface_cls(ret, settings.pagesize[0],
                     settings.pagesize[1]) as surface:
        for panel in result.params.panels:
            if panel_id and panel.id != panel_id:
                continue
            _write_panel(surface, settings, result, panel)
            surface.show_page()
    return ret.getvalue()


def _write_panel(surface, settings, result, panel):
    scale = _calculate_scale(settings, panel)
    width = panel.width * scale
    height = panel.height * scale
    x0 = ((settings.pagesize[0] - width) * settings.margin_left /
          (settings.margin_left + settings.margin_right))
    y0 = ((settings.pagesize[1] - height) * settings.margin_top /
          (settings.margin_top + settings.margin_bottom))

    ctx = cairo.Context(surface)
    ctx.set_line_width(0)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.rectangle(x0, y0, width, height)
    ctx.fill()

    for used in result.used:
        if used.panel != panel:
            continue
        _write_used(surface, scale, x0, y0, used)

    for unused in result.unused:
        if unused.panel != panel:
            continue
        _write_unused(surface, scale, x0, y0, unused)

    _write_centered_text(surface, settings.pagesize[0] / 2,
                         settings.pagesize[1] - settings.margin_bottom / 2,
                         panel.id)


def _write_used(surface, scale, x0, y0, used):
    width = used.item.width * scale
    height = used.item.height * scale
    if used.rotate:
        width, height = height, width
    x = x0 + used.x * scale
    y = y0 + used.y * scale

    ctx = cairo.Context(surface)
    ctx.set_line_width(0)
    ctx.set_source_rgb(0.9, 0.9, 0.9)
    ctx.rectangle(x, y, width, height)
    ctx.fill()

    _write_centered_text(surface, x + width / 2, y + height / 2,
                         used.item.id + (' (r)' if used.rotate else ''))


def _write_unused(surface, scale, x0, y0, unused):
    width = unused.width * scale
    height = unused.height * scale
    x = x0 + unused.x * scale
    y = y0 + unused.y * scale

    ctx = cairo.Context(surface)
    ctx.set_line_width(0)
    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.rectangle(x, y, width, height)
    ctx.fill()


def _write_centered_text(surface, x, y, text):
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0, 0, 0)
    text_ext = ctx.text_extents(text)
    ctx.move_to(x - text_ext.width / 2,
                y + text_ext.height / 2)
    ctx.show_text(text)


def _calculate_scale(settings, panel):
    page_width = (settings.pagesize[0] - settings.margin_left -
                  settings.margin_right)
    page_height = (settings.pagesize[1] - settings.margin_top -
                   settings.margin_bottom)
    page_ratio = page_width / page_height
    panel_ratio = panel.width / panel.height
    return (page_width / panel.width if panel_ratio > page_ratio
            else page_height / panel.height)
