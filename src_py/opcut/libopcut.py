from pathlib import Path
import ctypes
import sys

from opcut import common


def calculate(method: common.Method,
              params: common.Params
              ) -> common.Result:
    if not _lib:
        raise Exception("native implementation not available")

    native_method = _encode_method(method)

    id_panels = {panel_id: panel
                 for panel_id, panel in enumerate(params.panels)}
    id_items = {item_id: item
                for item_id, item in enumerate(params.items)}

    a = _lib.opcut_allocator_create(ctypes.pythonapi.PyMem_Malloc,
                                    ctypes.pythonapi.PyMem_Free)
    if a is None:
        raise Exception("allocation error")

    try:
        native_panels = _encode_panels(a, id_panels)
        native_items = _encode_items(a, id_items)
        native_params = _encode_params(a, params, native_panels, native_items)

        native_result = ctypes.POINTER(_lib.opcut_result_t)()
        ret = _lib.opcut_calculate(a, native_method, native_params,
                                   ctypes.byref(native_result))

        if ret == _lib.OPCUT_UNSOLVABLE:
            raise common.UnresolvableError()

        if ret != _lib.OPCUT_SUCCESS:
            raise Exception()

        used = list(_decode_used(native_result.contents.used, id_panels,
                                 id_items))
        unused = list(_decode_unused(native_result.contents.unused,
                                     id_panels))
        return common.Result(params=params,
                             used=used,
                             unused=unused)

    finally:
        _lib.opcut_allocator_destroy(a)


def _encode_method(method):
    if method == common.Method.GREEDY_NATIVE:
        return _lib.OPCUT_METHOD_GREEDY

    if method == common.Method.FORWARD_GREEDY_NATIVE:
        return _lib.OPCUT_METHOD_FORWARD_GREEDY

    raise ValueError('unsupported method')


def _encode_panels(a, id_panels):
    panels = None
    for panel_id, panel in id_panels.items():
        panels = _lib.opcut_panel_create(a, panel_id, panel.width,
                                         panel.height, panels)
        if panels is None:
            raise Exception("allocation error")
    return panels


def _encode_items(a, id_items):
    items = None
    for item_id, item in id_items.items():
        items = _lib.opcut_item_create(a, item_id, item.width, item.height,
                                       item.can_rotate, items)
        if items is None:
            raise Exception("allocation error")
    return items


def _encode_params(a, params, panels, items):
    params = _lib.opcut_params_create(a, params.cut_width,
                                      params.min_initial_usage, panels, items)
    if params is None:
        raise Exception("allocation error")
    return params


def _decode_used(used, id_panels, id_items):
    while used:
        yield common.Used(panel=id_panels[used.contents.panel.contents.id],
                          item=id_items[used.contents.item.contents.id],
                          x=used.contents.x,
                          y=used.contents.y,
                          rotate=used.contents.rotate)
        used = used.contents.next


def _decode_unused(unused, id_panels):
    while unused:
        yield common.Unused(panel=id_panels[unused.contents.panel.contents.id],
                            width=unused.contents.width,
                            height=unused.contents.height,
                            x=unused.contents.x,
                            y=unused.contents.y)
        unused = unused.contents.next


class _Lib:

    def __init__(self, path: Path):
        lib = ctypes.cdll.LoadLibrary(str(path))

        self.OPCUT_SUCCESS = 0
        self.OPCUT_ERROR = 1
        self.OPCUT_UNSOLVABLE = 42

        self.OPCUT_METHOD_GREEDY = 0
        self.OPCUT_METHOD_FORWARD_GREEDY = 1

        self.opcut_malloc_t = ctypes.c_void_p
        self.opcut_free_t = ctypes.c_void_p
        self.opcut_allocator_t_p = ctypes.c_void_p

        self.opcut_panel_t = type('opcut_panel_t', (ctypes.Structure, ), {})
        self.opcut_panel_t._fields_ = [
            ('id', ctypes.c_int),
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('next', ctypes.POINTER(self.opcut_panel_t)),
            ('area', ctypes.c_double)]

        self.opcut_item_t = type('opcut_item_t', (ctypes.Structure, ), {})
        self.opcut_item_t._fields_ = [
            ('id', ctypes.c_int),
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('can_rotate', ctypes.c_bool),
            ('next', ctypes.POINTER(self.opcut_item_t)),
            ('area', ctypes.c_double)]

        self.opcut_params_t = type('opcut_params_t', (ctypes.Structure, ), {})
        self.opcut_params_t._fields_ = [
            ('cut_width', ctypes.c_double),
            ('min_initial_usage', ctypes.c_bool),
            ('panels', ctypes.POINTER(self.opcut_panel_t)),
            ('items', ctypes.POINTER(self.opcut_item_t)),
            ('panels_area', ctypes.c_double)]

        self.opcut_used_t = type('opcut_used_t', (ctypes.Structure, ), {})
        self.opcut_used_t._fields_ = [
            ('panel', ctypes.POINTER(self.opcut_panel_t)),
            ('item', ctypes.POINTER(self.opcut_item_t)),
            ('x', ctypes.c_double),
            ('y', ctypes.c_double),
            ('rotate', ctypes.c_bool),
            ('next', ctypes.POINTER(self.opcut_used_t))]

        self.opcut_unused_t = type('opcut_unused_t', (ctypes.Structure, ), {})
        self.opcut_unused_t._fields_ = [
            ('panel', ctypes.POINTER(self.opcut_panel_t)),
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('x', ctypes.c_double),
            ('y', ctypes.c_double),
            ('next', ctypes.POINTER(self.opcut_unused_t)),
            ('area', ctypes.c_double),
            ('initial', ctypes.c_bool)]

        self.opcut_result_t = type('opcut_result_t', (ctypes.Structure, ), {})
        self.opcut_result_t._fields_ = [
            ('params', ctypes.POINTER(self.opcut_params_t)),
            ('used', ctypes.POINTER(self.opcut_used_t)),
            ('unused', ctypes.POINTER(self.opcut_unused_t))]

        functions = [
            (self.opcut_allocator_t_p,
             'opcut_allocator_create',
             [self.opcut_malloc_t, self.opcut_free_t]),

            (None,
             'opcut_allocator_destroy',
             [self.opcut_allocator_t_p]),

            (ctypes.POINTER(self.opcut_panel_t),
             'opcut_panel_create',
             [self.opcut_allocator_t_p, ctypes.c_int, ctypes.c_double,
              ctypes.c_double, ctypes.POINTER(self.opcut_panel_t)]),

            (ctypes.POINTER(self.opcut_item_t),
             'opcut_item_create',
             [self.opcut_allocator_t_p, ctypes.c_int, ctypes.c_double,
              ctypes.c_double, ctypes.c_bool,
              ctypes.POINTER(self.opcut_item_t)]),

            (ctypes.POINTER(self.opcut_params_t),
             'opcut_params_create',
             [self.opcut_allocator_t_p, ctypes.c_double, ctypes.c_bool,
              ctypes.POINTER(self.opcut_panel_t),
              ctypes.POINTER(self.opcut_item_t)]),

            (ctypes.c_int,
             'opcut_calculate',
             [self.opcut_allocator_t_p, ctypes.c_int,
              ctypes.POINTER(self.opcut_params_t),
              ctypes.POINTER(ctypes.POINTER(self.opcut_result_t))])
        ]

        for restype, name, argtypes in functions:
            function = getattr(lib, name)
            function.argtypes = argtypes
            function.restype = restype
            setattr(self, name, function)


if sys.platform == 'win32':
    _lib_suffix = '.dll'
elif sys.platform == 'darwin':
    _lib_suffix = '.dylib'
else:
    _lib_suffix = '.so'

try:
    _lib = _Lib(Path(__file__).parent / f'_libopcut{_lib_suffix}')
except Exception:
    _lib = None
