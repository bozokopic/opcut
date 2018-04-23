import enum

from opcut import util


mm = 72 / 25.4

Params = util.namedtuple(
    'Params',
    ['cut_width', 'float'],
    ['panels', 'List[Panel]'],
    ['items', 'List[Item]'])

Result = util.namedtuple(
    'Result',
    ['params', 'Params'],
    ['used', 'List[Used]'],
    ['unused', 'List[Unused]'])

Panel = util.namedtuple(
    'Panel',
    ['id', 'str'],
    ['width', 'float'],
    ['height', 'float'])

Item = util.namedtuple(
    'Item',
    ['id', 'str'],
    ['width', 'float'],
    ['height', 'float'],
    ['can_rotate', 'bool'])

Used = util.namedtuple(
    'Used',
    ['panel', 'Panel'],
    ['item', 'Item'],
    ['x', 'float'],
    ['y', 'float'],
    ['rotate', 'bool'])

Unused = util.namedtuple(
    'Unused',
    ['panel', 'Panel'],
    ['width', 'float'],
    ['height', 'float'],
    ['x', 'float'],
    ['y', 'float'])

OutputSettings = util.namedtuple(
    'OutputSettings',
    ['pagesize', 'Tuple[float,float]', (210 * mm, 297 * mm)],
    ['margin_top', 'float', 10 * mm],
    ['margin_bottom', 'float', 20 * mm],
    ['margin_left', 'float', 10 * mm],
    ['margin_right', 'float', 10 * mm])

Method = enum.Enum('Method', [
    'GREEDY',
    'FORWARD_GREEDY'])

OutputType = enum.Enum('OutputType', [
    'PDF',
    'SVG'])


class UnresolvableError(Exception):
    """Exception raised when Result is not solvable"""


def params_to_json_data(params):
    """Convert params to json serializable data specified by
    ``opcut://params.yaml#``

    Args:
        params (Params): params

    Returns:
        Any: json serializble data

    """
    return {'cut_width': params.cut_width,
            'panels': {panel.id: {'width': panel.width,
                                  'height': panel.height}
                       for panel in params.panels},
            'items': {item.id: {'width': item.width,
                                'height': item.height,
                                'can_rotate': item.can_rotate}
                      for item in params.items}}


def json_data_to_params(json_data):
    """Convert json serializable data specified by ``opcut://params.yaml#``
    to params

    Args:
        json_data (Any): json serializable data

    Returns:
        Params

    """
    return Params(cut_width=json_data['cut_width'],
                  panels=[Panel(id=k,
                                width=v['width'],
                                height=v['height'])
                          for k, v in json_data['panels'].items()],
                  items=[Item(id=k,
                              width=v['width'],
                              height=v['height'],
                              can_rotate=v['can_rotate'])
                         for k, v in json_data['items'].items()])


def result_to_json_data(result):
    """Convert result to json serializable data specified by
    ``opcut://result.yaml#``

    Args:
        result (Result): result

    Returns:
        Any: json serializble data

    """
    return {'params': params_to_json_data(result.params),
            'used': [{'panel': used.panel.id,
                      'item': used.item.id,
                      'x': used.x,
                      'y': used.y,
                      'rotate': used.rotate}
                     for used in result.used],
            'unused': [{'panel': unused.panel.id,
                        'width': unused.width,
                        'height': unused.height,
                        'x': unused.x,
                        'y': unused.y}
                       for unused in result.unused]}


def json_data_to_result(json_data):
    """Convert json serializable data specified by ``opcut://result.yaml#``
    to result

    Args:
        json_data (Any): json serializable data

    Returns:
        Result

    """
    params = json_data_to_params(json_data['params'])
    panels = {panel.id: panel for panel in params.panels}
    items = {item.id: item for item in params.items}
    return Result(params=params,
                  used=[Used(panel=panels[used['panel']],
                             item=items[used['item']],
                             x=used['x'],
                             y=used['y'],
                             rotate=used['rotate'])
                        for used in json_data['used']],
                  unused=[Unused(panel=panels[unused['panel']],
                                 width=unused['width'],
                                 height=unused['height'],
                                 x=unused['x'],
                                 y=unused['y'])
                          for unused in json_data['unused']])
