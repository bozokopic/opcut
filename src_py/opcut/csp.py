import enum
import itertools

from opcut import util


State = util.namedtuple(
    '_State',
    ['cut_width', 'float'],
    ['panels', 'List[Panel]'],
    ['items', 'List[Item]'],
    ['used', 'List[Used]'],
    ['unused', 'List[Unused]'])

Panel = util.namedtuple(
    'Panel',
    ['id', 'Any'],
    ['width', 'float'],
    ['height', 'float'])

Item = util.namedtuple(
    'Item',
    ['id', 'Any'],
    ['width', 'float'],
    ['height', 'float'],
    ['rotate', 'bool'])

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

Method = enum.Enum('Method', [
    'GREEDY',
    'FORWARD_GREEDY'])


class UnresolvableError(Exception):
    pass


def calculate(panels, items, cut_width, method):
    """Calculate cutting stock problem

    Args:
        panels (List[Panel]): input panels
        items (List[Item]): input items
        cut_width (float): cut width
        method (Method): calculation method

    Returns:
        State

    """
    state = State(
        cut_width=cut_width,
        panels=panels,
        items=items,
        used=[],
        unused=[Unused(panel=panel,
                       width=panel.width,
                       height=panel.height,
                       x=0,
                       y=0)
                for panel in panels])
    return {
        Method.GREEDY: _calculate_greedy,
        Method.FORWARD_GREEDY: _calculate_forward_greedy
    }[method](state)


_fitness_K = 0.03


def _calculate_greedy(state):
    while not _is_done(state):
        new_state = None
        new_fitness = None
        for next_state in _get_next_states(state):
            next_state_fitness = _fitness(next_state)
            if new_fitness is None or next_state_fitness < new_fitness:
                new_state = next_state
                new_fitness = next_state_fitness
        if not new_state:
            raise UnresolvableError()
        state = new_state
    return state


def _calculate_forward_greedy(state):
    while not _is_done(state):
        new_state = None
        new_fitness = None
        for next_state in _get_next_states(state):
            try:
                next_state_fitness = _fitness(_calculate_greedy(next_state))
            except UnresolvableError:
                continue
            if new_fitness is None or next_state_fitness < new_fitness:
                new_state = next_state
                new_fitness = next_state_fitness
        if not new_state:
            raise UnresolvableError()
        state = new_state
    return state


def _get_next_states(state):
    selected_item = None
    used_items = {used.item for used in state.used}
    for item in state.items:
        if item in used_items:
            continue
        if (not selected_item or
                max(item.width, item.height) >
                max(selected_item.width, selected_item.height)):
            selected_item = item
    if not selected_item:
        raise Exception('state is done')
    return _get_next_states_for_item(state, selected_item)


def _get_next_states_for_item(state, item):
    ret = []
    loop_iter = ((False, i, unused) for i, unused in enumerate(state.unused))
    if item.rotate:
        loop_iter = itertools.chain(
            loop_iter,
            ((True, i, unused) for i, unused in enumerate(state.unused)))
    for rotate, i, unused in loop_iter:
        for vertical in [True, False]:
            new_used, new_unused = _cut_item_from_unused(
                unused, item, rotate, state.cut_width, vertical)
            if not new_used:
                continue
            ret.append(state._replace(
                used=state.used + [new_used],
                unused=state.unused[:i] + new_unused + state.unused[i+1:]))
    return ret


def _cut_item_from_unused(unused, item, rotate, cut_width, vertical):
    item_width = item.width if not rotate else item.height
    item_height = item.height if not rotate else item.width
    if unused.height < item_height or unused.width < item_width:
        return None, []
    used = Used(panel=unused.panel,
                item=item,
                x=unused.x,
                y=unused.y,
                rotate=rotate)
    new_unused = []
    width = unused.width - item_width - cut_width
    height = unused.height if vertical else item.height
    if width > 0:
        new_unused.append(Unused(panel=unused.panel,
                                 width=width,
                                 height=height,
                                 x=unused.x + item_width + cut_width,
                                 y=unused.y))
    width = item_width if vertical else unused.width
    height = unused.height - item_height - cut_width
    if height > 0:
        new_unused.append(Unused(panel=unused.panel,
                                 width=width,
                                 height=height,
                                 x=unused.x,
                                 y=unused.y + item_height + cut_width))
    return used, new_unused


def _is_done(state):
    return len(state.items) == len(state.used)


def _fitness(state):
    total_area = sum(panel.width * panel.height for panel in state.panels)
    result = 0
    for panel in state.panels:
        used_areas = [used.item.width * used.item.height
                      for used in state.used]
        unused_areas = [unused.width * unused.height
                        for unused in state.unused]
        result += (panel.width * panel.height - sum(used_areas)) / total_area
        result -= (_fitness_K *
                   min(used_areas, default=0) * max(unused_areas, default=0) /
                   (total_area * total_area))
    return result
