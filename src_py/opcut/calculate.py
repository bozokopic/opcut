import itertools

from opcut import common
from opcut import libopcut


def calculate(method: common.Method,
              params: common.Params
              ) -> common.Result:
    """Calculate cutting stock problem"""

    if method == common.Method.GREEDY:
        return _calculate_greedy(_create_initial_result(params))

    if method == common.Method.FORWARD_GREEDY:
        return _calculate_forward_greedy(_create_initial_result(params))

    if method in (common.Method.GREEDY_NATIVE,
                  common.Method.FORWARD_GREEDY_NATIVE):
        return libopcut.calculate(method, params)

    raise ValueError('unsupported method')


_fitness_K = 0.03


def _create_initial_result(params):
    return common.Result(params=params,
                         used=[],
                         unused=[common.Unused(panel=panel,
                                               width=panel.width,
                                               height=panel.height,
                                               x=0,
                                               y=0)
                                 for panel in params.panels])


def _calculate_greedy(result):
    while not _is_done(result):
        new_result = None
        new_fitness = None
        for next_result in _get_next_results(result):
            next_result_fitness = _fitness(next_result)
            if new_fitness is None or next_result_fitness < new_fitness:
                new_result = next_result
                new_fitness = next_result_fitness
        if not new_result:
            raise common.UnresolvableError()
        result = new_result
    return result


def _calculate_forward_greedy(result):
    while not _is_done(result):
        new_result = None
        new_fitness = None
        for next_result in _get_next_results(result):
            try:
                next_result_fitness = _fitness(_calculate_greedy(next_result))
            except common.UnresolvableError:
                continue
            if new_fitness is None or next_result_fitness < new_fitness:
                new_result = next_result
                new_fitness = next_result_fitness
        if not new_result:
            raise common.UnresolvableError()
        result = new_result
    return result


def _get_next_results(result):
    selected_item = None
    used_items = {used.item.id for used in result.used}
    for item in result.params.items:
        if item.id in used_items:
            continue
        if (not selected_item or
                max(item.width, item.height) >
                max(selected_item.width, selected_item.height)):
            selected_item = item
    if not selected_item:
        raise Exception('result is done')
    return _get_next_results_for_item(result, selected_item)


def _get_next_results_for_item(result, item):
    ret = []
    loop_iter = ((False, i, unused) for i, unused in enumerate(result.unused))
    if item.can_rotate:
        loop_iter = itertools.chain(
            loop_iter,
            ((True, i, unused) for i, unused in enumerate(result.unused)))
    for rotate, i, unused in loop_iter:
        for vertical in [True, False]:
            new_used, new_unused = _cut_item_from_unused(
                unused, item, rotate, result.params.cut_width, vertical)
            if not new_used:
                continue
            ret.append(result._replace(
                used=result.used + [new_used],
                unused=result.unused[:i] + new_unused + result.unused[i+1:]))
    return ret


def _cut_item_from_unused(unused, item, rotate, cut_width, vertical):
    item_width = item.width if not rotate else item.height
    item_height = item.height if not rotate else item.width
    if unused.height < item_height or unused.width < item_width:
        return None, []
    used = common.Used(panel=unused.panel,
                       item=item,
                       x=unused.x,
                       y=unused.y,
                       rotate=rotate)
    new_unused = []
    width = unused.width - item_width - cut_width
    height = unused.height if vertical else item_height
    if width > 0:
        new_unused.append(common.Unused(panel=unused.panel,
                                        width=width,
                                        height=height,
                                        x=unused.x + item_width + cut_width,
                                        y=unused.y))
    width = item_width if vertical else unused.width
    height = unused.height - item_height - cut_width
    if height > 0:
        new_unused.append(common.Unused(panel=unused.panel,
                                        width=width,
                                        height=height,
                                        x=unused.x,
                                        y=unused.y + item_height + cut_width))
    return used, new_unused


def _is_done(result):
    return len(result.params.items) == len(result.used)


def _fitness(result):
    total_area = sum(panel.width * panel.height
                     for panel in result.params.panels)
    fitness = 0
    for panel in result.params.panels:
        used_areas = [used.item.width * used.item.height
                      for used in result.used
                      if used.panel == panel]
        unused_areas = [unused.width * unused.height
                        for unused in result.unused
                        if unused.panel == panel]
        fitness += (panel.width * panel.height - sum(used_areas)) / total_area
        fitness -= (_fitness_K *
                    min(used_areas, default=0) * max(unused_areas, default=0) /
                    (total_area * total_area))

    if not result.params.min_initial_usage:
        return fitness

    unused_initial_count = sum(1 for unused in result.unused
                               if _is_unused_initial(unused))
    return (-unused_initial_count, fitness)


def _is_unused_initial(unused):
    return (unused.x == 0 and
            unused.y == 0 and
            unused.width == unused.panel.width and
            unused.height == unused.panel.height)
