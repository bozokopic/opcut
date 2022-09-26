import enum
import importlib.resources
import typing

from hat import json


mm: float = 72 / 25.4

with importlib.resources.path(__package__, 'json_schema_repo.json') as _path:
    json_schema_repo: json.SchemaRepository = json.SchemaRepository(
        json.json_schema_repo,
        json.SchemaRepository.from_json(_path))


class Panel(typing.NamedTuple):
    id: str
    width: float
    height: float


class Item(typing.NamedTuple):
    id: str
    width: float
    height: float
    can_rotate: bool


class Params(typing.NamedTuple):
    cut_width: float
    min_initial_usage: bool
    panels: typing.List[Panel]
    items: typing.List[Item]


class Used(typing.NamedTuple):
    panel: Panel
    item: Item
    x: float
    y: float
    rotate: bool


class Unused(typing.NamedTuple):
    panel: Panel
    width: float
    height: float
    x: float
    y: float


class Result(typing.NamedTuple):
    params: Params
    used: typing.List[Used]
    unused: typing.List[Unused]


class OutputSettings(typing.NamedTuple):
    pagesize: typing.Tuple[float, float] = (210 * mm, 297 * mm)
    margin_top: float = 10 * mm
    margin_bottom: float = 20 * mm
    margin_left: float = 10 * mm
    margin_right: float = 10 * mm


class Method(enum.Enum):
    GREEDY = 'greedy'
    FORWARD_GREEDY = 'forward_greedy'
    GREEDY_NATIVE = 'greedy_native'
    FORWARD_GREEDY_NATIVE = 'forward_greedy_native'


class OutputFormat(enum.Enum):
    PDF = 'pdf'
    SVG = 'svg'


class UnresolvableError(Exception):
    """Exception raised when Result is not solvable"""


def params_to_json(params: Params) -> json.Data:
    """Convert params to json serializable data specified by
    ``opcut://opcut.yaml#/definitions/params``"""
    return {'cut_width': params.cut_width,
            'min_initial_usage': params.min_initial_usage,
            'panels': {panel.id: {'width': panel.width,
                                  'height': panel.height}
                       for panel in params.panels},
            'items': {item.id: {'width': item.width,
                                'height': item.height,
                                'can_rotate': item.can_rotate}
                      for item in params.items}}


def params_from_json(data: json.Data) -> Params:
    """Convert json serializable data specified by
    ``opcut://opcut.yaml#/definitions/params`` to params"""
    return Params(cut_width=data['cut_width'],
                  min_initial_usage=data.get('min_initial_usage', False),
                  panels=[Panel(id=k,
                                width=v['width'],
                                height=v['height'])
                          for k, v in data['panels'].items()],
                  items=[Item(id=k,
                              width=v['width'],
                              height=v['height'],
                              can_rotate=v['can_rotate'])
                         for k, v in data['items'].items()])


def result_to_json(result: Result) -> json.Data:
    """Convert result to json serializable data specified by
    ``opcut://opcut.yaml#/definitions/result``"""
    return {'params': params_to_json(result.params),
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


def result_from_json(data: json.Data) -> Result:
    """Convert json serializable data specified by
    ``opcut://opcut.yaml#/definitions/result`` to result"""
    params = params_from_json(data['params'])
    panels = {panel.id: panel for panel in params.panels}
    items = {item.id: item for item in params.items}
    return Result(params=params,
                  used=[Used(panel=panels[used['panel']],
                             item=items[used['item']],
                             x=used['x'],
                             y=used['y'],
                             rotate=used['rotate'])
                        for used in data['used']],
                  unused=[Unused(panel=panels[unused['panel']],
                                 width=unused['width'],
                                 height=unused['height'],
                                 x=unused['x'],
                                 y=unused['y'])
                          for unused in data['unused']])
