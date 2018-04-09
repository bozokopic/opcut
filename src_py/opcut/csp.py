import collections
import enum


InputPanel = collections.namedtuple('InputPanel', ['width', 'height', 'label'])
InputItem = collections.namedtuple('InputItem', ['width', 'height', 'label',
                                                 'rotate'])
OutputPanel = collections.namedtuple('OutputPanel', ['width', 'height',
                                                     'label', 'items'])
OutputItem = collections.namedtuple('OutputItem', ['width', 'height', 'label',
                                                   'x', 'y'])

Method = enum.Enum('Method', ['FORWARD_GREEDY'])


def calculate(panels, items, cut_width, method):
    """Calculate cutting stock problem

    Args:
        panels (List[InputPanel]): input panels
        items (List[InputItem]): input items
        cut_width (float): cut width
        method (Method): calculation method

    Returns:
        List[OutputPanel]

    """
    return {
        Method.FORWARD_GREEDY: _calculate_forward_greedy
    }[method](panels, items)


def _calculate_forward_greedy(panels, items):
    pass


_Part = collections.namedtuple('_Part', ['panel', 'width', 'height', 'x', 'y'])
_State = collections.namedtuple('_State', ['inputs', 'outputs'])
_fitness_K = 0.03


def _fitness(state):
    panel_states = {}
    for i in state.inputs:
        if i.panel not in panel_states:
            panel_states[i.panel] = _State([i], [])
        else:
            panel_states[i.panel].inputs.append(i)
    for i in state.outputs:
        if i.panel not in panel_states:
            panel_states[i.panel] = _State([], [i])
        else:
            panel_states[i.panel].outputs.append(i)

    total_area = sum(i.width * i.height for i in panel_states.keys())
    result = 0
    for panel, panel_state in panel_states.items():
        result += (panel.width * panel.height -
                   sum(i.width * i.height
                       for i in panel_state.outputs)) / total_area
        result -= (_fitness_K *
                   min((i.width * i.height for i in panel_state.outputs),
                       default=0) *
                   max((i.width * i.height for i in panel_state.inputs),
                       default=0)) / (total_area * total_area)
    return result
