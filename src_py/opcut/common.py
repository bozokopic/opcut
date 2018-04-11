import enum

from opcut import util


State = util.namedtuple(
    'State',
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

Method = enum.Enum('Method', [
    'GREEDY',
    'FORWARD_GREEDY'])


class UnresolvableError(Exception):
    """Exception raised when State is not solvable"""
