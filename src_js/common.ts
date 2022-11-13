import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as csv from './csv';
import * as file from './file';
import * as notification from './notification';


export type FormPanel = {
    name: string,
    quantity: number,
    width: number,
    height: number
};

export type FormItem = {
    name: string,
    quantity: number,
    width: number,
    height: number
    can_rotate: boolean
};

export type Params = {
    cut_width: number,
    min_initial_usage: boolean,
    panels: Record<string, {
        width: number,
        height: number
    }>,
    items: Record<string, {
        width: number,
        height: number
        can_rotate: boolean
    }>
};

export type Used = {
    panel: string,
    item: string,
    x: number,
    y: number,
    rotate: boolean
};

export type Unused = {
    panel: string,
    width: number,
    height: number,
    x: number,
    y: number
};

export type Result = {
    params: Params,
    used: Used[],
    unused: Unused[]
};


const calculateUrl = String(new URL('./calculate', window.location.href));
const generateUrl = String(new URL('./generate', window.location.href));

let panelCounter = 0;
let itemCounter = 0;


export const defaultState = {
    form: {
        method: 'forward_greedy_native',
        cut_width: 0.3,
        min_initial_usage: true,
        panels: [],
        items: []
    },
    result: null,
    selected: {
        panel: null,
        item: null
    },
    svg: {
        font_size: '1',
        show_names: true,
        show_dimensions: false
    },
    calculating: false
};


const defaultFormPanel: FormPanel = {
    name: 'Panel',
    quantity: 1,
    width: 100,
    height: 100
};


const defaultFormItem: FormItem = {
    name: 'Item',
    quantity: 1,
    width: 10,
    height: 10,
    can_rotate: true
};


export async function calculate() {
    r.set('calculating', true);
    try {
        const method = r.get('form', 'method');
        const params = createCalculateParams();
        const res = await fetch(`${calculateUrl}?method=${method}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });
        if (!res.ok)
            throw await res.text();
        const result = await res.json();
        const selected = {
            panel: Object.keys(result.params.panels)[0],
            item: null
        };
        r.change(u.pipe(
            u.set('result', result),
            u.set('selected', selected)
        ));
        if (!result)
            throw 'Could not resolve calculation';
        notification.show('success', 'New calculation available');
    } catch (e) {
        notification.show('error', String(e));
    } finally {
        r.set('calculating', false);
    }
}


export async function generate() {
    try {
        const result = r.get('result');
        const res = await fetch(`${generateUrl}?output_format=pdf`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(result)
        });
        if (!res.ok)
            throw await res.text();
        const blob = await res.blob();
        const f = new File([blob], 'output.pdf');
        file.save(f);
    } catch (e) {
        notification.show('error', String(e));
    }
}


export async function csvImportPanels() {
    const f = await file.load('.csv');
    if (f == null)
        return;
    const panels = await csv.decode(f, {
        name: String,
        quantity: u.strictParseInt,
        width: u.strictParseFloat,
        height: u.strictParseFloat
    }) as FormPanel[];
    r.change(['form', 'panels'], x => (x as FormPanel[]).concat(panels));
}


export function csvExportPanels() {
    const panels = r.get('form', 'panels') as FormPanel[];
    const blob = csv.encode(panels);
    const f = new File([blob], 'panels.csv');
    file.save(f);
}


export async function csvImportItems() {
    const f = await file.load('.csv');
    if (f == null)
        return;
    const items = await csv.decode(f, {
        name: String,
        quantity: u.strictParseInt,
        width: u.strictParseFloat,
        height: u.strictParseFloat,
        can_rotate: u.equals('true')
    }) as FormItem[];
    r.change(['form', 'items'], x => (x as FormItem[]).concat(items));
}


export function csvExportItems() {
    const items = r.get('form', 'items') as FormItem[];
    const blob = csv.encode(items);
    const f = new File([blob], 'items.csv');
    file.save(f);
}


export function addPanel() {
    panelCounter += 1;
    const panel = u.set('name', `Panel${panelCounter}`, defaultFormPanel);
    r.change(['form', 'panels'], u.append(panel) as any);
}


export function addItem() {
    itemCounter += 1;
    const item = u.set('name', `Item${itemCounter}`, defaultFormItem);
    r.change(['form', 'items'], u.append(item) as any);
}


function createCalculateParams() {
    const cutWidth = r.get('form', 'cut_width') as number;
    if (cutWidth < 0)
        throw 'Invalid cut width';

    const minInitialUsage = r.get('form', 'min_initial_usage');

    const panels: Record<string, {
        width: number,
        height: number
    }> = {};
    for (const panel of (r.get('form', 'panels') as FormPanel[])) {
        if (!panel.name)
            throw 'Invalid panel name';
        if (panel.quantity < 1)
            throw 'Invalid quantity for panel ' + panel.name;
        if (panel.width <= 0)
            throw 'Invalid width for panel ' + panel.name;
        if (panel.height <= 0)
            throw 'Invalid height for panel ' + panel.name;
        for (let i = 1; i <= panel.quantity; ++i) {
            const name = panel.quantity > 1 ? `${panel.name} ${i}` : panel.name;
            if (name in panels)
                throw 'Duplicate panel name ' + name;
            panels[name] = {width: panel.width, height: panel.height};
        }
    }
    if (u.equals(panels, {}))
        throw 'No panels defined';

    const items: Record<string, {
        width: number,
        height: number,
        can_rotate: boolean
    }> = {};
    for (const item of (r.get('form', 'items') as FormItem[])) {
        if (!item.name)
            throw 'Invalid item name';
        if (item.quantity < 1)
            throw 'Invalid quantity for item ' + item.name;
        if (item.width <= 0)
            throw 'Invalid width for item ' + item.name;
        if (item.height <= 0)
            throw 'Invalid height for item ' + item.name;
        for (let i = 1; i <= item.quantity; ++i) {
            const name = item.quantity > 1 ? `${item.name} ${i}` : item.name;
            if (name in items) {
                throw 'Duplicate item name ' + name;
            }
            items[name] = {
                width: item.width,
                height: item.height,
                can_rotate: item.can_rotate
            };
        }
    }
    if (u.equals(items, {}))
        throw 'No items defined';

    return {
        cut_width: cutWidth,
        min_initial_usage: minInitialUsage,
        panels: panels,
        items: items
    };
}
