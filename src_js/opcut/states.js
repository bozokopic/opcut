import * as grid from 'opcut/grid';


export const main = {
    form: {
        method: 'FORWARD_GREEDY',
        cut_width: '1',
        panels: grid.state,
        items: grid.state
    },
    result: null,
    selected: {
        panel: null,
        item: null
    },
};


export const panelsItem = {
    name: 'Panel',
    width: '100',
    height: '100'
};


export const itemsItem = {
    name: 'Item',
    width: '10',
    height: '10',
    can_rotate: true
};
