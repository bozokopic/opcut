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

    a = _lib.opcut_allocator_create(ctypes.pythonapi.PyMem_Malloc,
                                    ctypes.pythonapi.PyMem_Free)
    if a is None:
        raise Exception("allocation error")

    try:
        native_params = _encode_params(params)
        native_used = ctypes.POINTER(_lib.opcut_used_t)()
        native_unused = ctypes.POINTER(_lib.opcut_unused_t)()
        ret = _lib.opcut_calculate(a, native_method,
                                   ctypes.byref(native_params),
                                   ctypes.byref(native_used),
                                   ctypes.byref(native_unused))

        if ret == _lib.OPCUT_UNSOLVABLE:
            raise common.UnresolvableError()

        if ret != _lib.OPCUT_SUCCESS:
            raise Exception("calculation error")

        used = list(_decode_used(params, native_used))
        unused = list(_decode_unused(params, native_unused))
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


def _encode_params(params):
    panels_type = _lib.opcut_panel_t * len(params.panels)
    panels = panels_type(*(_lib.opcut_panel_t(width=panel.width,
                                              height=panel.height,
                                              area=panel.width * panel.height)
                           for panel in params.panels))

    items_type = _lib.opcut_item_t * len(params.items)
    items = items_type(*(_lib.opcut_item_t(width=item.width,
                                           height=item.height,
                                           can_rotate=item.can_rotate,
                                           area=item.width * item.height)
                         for item in params.items))

    return _lib.opcut_params_t(cut_width=params.cut_width,
                               min_initial_usage=params.min_initial_usage,
                               panels=panels,
                               panels_len=len(panels),
                               items=items,
                               items_len=len(items),
                               panels_area=sum(panel.width * panel.height
                                               for panel in params.panels))


def _decode_used(params, used):
    while used:
        yield common.Used(panel=params.panels[used.contents.panel_id],
                          item=params.items[used.contents.item_id],
                          x=used.contents.x,
                          y=used.contents.y,
                          rotate=used.contents.rotate)
        used = used.contents.next


def _decode_unused(params, unused):
    while unused:
        yield common.Unused(panel=params.panels[unused.contents.panel_id],
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
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('area', ctypes.c_double)]

        self.opcut_item_t = type('opcut_item_t', (ctypes.Structure, ), {})
        self.opcut_item_t._fields_ = [
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('can_rotate', ctypes.c_bool),
            ('area', ctypes.c_double)]

        self.opcut_params_t = type('opcut_params_t', (ctypes.Structure, ), {})
        self.opcut_params_t._fields_ = [
            ('cut_width', ctypes.c_double),
            ('min_initial_usage', ctypes.c_bool),
            ('panels', ctypes.POINTER(self.opcut_panel_t)),
            ('panels_len', ctypes.c_size_t),
            ('items', ctypes.POINTER(self.opcut_item_t)),
            ('items_len', ctypes.c_size_t),
            ('panels_area', ctypes.c_double)]

        self.opcut_used_t = type('opcut_used_t', (ctypes.Structure, ), {})
        self.opcut_used_t._fields_ = [
            ('panel_id', ctypes.c_size_t),
            ('item_id', ctypes.c_size_t),
            ('x', ctypes.c_double),
            ('y', ctypes.c_double),
            ('rotate', ctypes.c_bool),
            ('next', ctypes.POINTER(self.opcut_used_t))]

        self.opcut_unused_t = type('opcut_unused_t', (ctypes.Structure, ), {})
        self.opcut_unused_t._fields_ = [
            ('panel_id', ctypes.c_size_t),
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('x', ctypes.c_double),
            ('y', ctypes.c_double),
            ('next', ctypes.POINTER(self.opcut_unused_t)),
            ('area', ctypes.c_double),
            ('initial', ctypes.c_bool)]

        functions = [
            (self.opcut_allocator_t_p,
             'opcut_allocator_create',
             [self.opcut_malloc_t, self.opcut_free_t]),

            (None,
             'opcut_allocator_destroy',
             [self.opcut_allocator_t_p]),

            (ctypes.c_int,
             'opcut_calculate',
             [self.opcut_allocator_t_p, ctypes.c_int,
              ctypes.POINTER(self.opcut_params_t),
              ctypes.POINTER(ctypes.POINTER(self.opcut_used_t)),
              ctypes.POINTER(ctypes.POINTER(self.opcut_unused_t))])
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
