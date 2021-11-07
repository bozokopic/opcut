import * as URI from 'uri-js';
import FileSaver from 'file-saver';
import iziToast from 'izitoast';
import Papa from 'papaparse';

import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as states from './states';


const calculateUrl = URI.resolve(window.location.href, './calculate');
const generateOutputUrl = URI.resolve(window.location.href, './generate_output');

let panelCounter = 0;
let itemCounter = 0;


export async function calculate() {
    try {
        const method = r.get('form', 'method');
        const params = createCalculateParams();
        const res = await fetch(`${calculateUrl}?method=${method}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });
        const result = await res.json();
        r.change(u.pipe(
            u.set('result', result),
            u.set('selected', states.main.selected)
        ));
        if (!result)
            throw 'Could not resolve calculation';
        showNotification('success', 'New calculation available');
    } catch (e) {
        showNotification('error', e);
    }
}


export async function generateOutput() {
    try {
        const result = r.get('result');
        const res = await fetch(`${generateOutputUrl}?output_type=pdf`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(result)
        });
        const blob = await res.blob();
        FileSaver.saveAs(blob, 'output.pdf');
    } catch (e) {
        showNotification('error', e);
    }
}


export async function csvImportPanels() {
    const panels = await csvImport({
        name: String,
        quantity: u.strictParseInt,
        width: u.strictParseFloat,
        height: u.strictParseFloat
    });
    r.change(['form', 'panels'], x => x.concat(panels));
}


export function csvExportPanels() {
    const panels = r.get('form', 'panels');
    const csvData = Papa.unparse(panels);
    const blob = new Blob([csvData], {type: 'text/csv'});
    FileSaver.saveAs(blob, 'panels.csv');
}


export async function csvImportItems() {
    const items = await csvImport({
        name: String,
        quantity: u.strictParseInt,
        width: u.strictParseFloat,
        height: u.strictParseFloat,
        can_rotate: u.equals('true')
    });
    r.change(['form', 'items'], x => x.concat(items));
}


export function csvExportItems() {
    const items = r.get('form', 'items');
    const csvData = Papa.unparse(items);
    const blob = new Blob([csvData], {type: 'text/csv'});
    FileSaver.saveAs(blob, 'items.csv');
}


export function addPanel() {
    panelCounter += 1;
    const panel = u.set('name', `Panel${panelCounter}`, states.panel);
    r.change(['form', 'panels'], u.append(panel));
}


export function addItem() {
    itemCounter += 1;
    const item = u.set('name', `Item${itemCounter}`, states.item);
    r.change(['form', 'items'], u.append(item));
}


function createCalculateParams() {
    const cutWidth = u.strictParseFloat(r.get('form', 'cut_width'));
    if (cutWidth < 0)
        throw 'Invalid cut width';

    const panels = {};
    for (const panel of r.get('form', 'panels')) {
        if (!panel.name)
            throw 'Invalid panel name';
        if (panel.quantity < 1)
            throw 'Invalid quantity for panel ' + panel.name;
        if (panel.width <= 0)
            throw 'Invalid width for panel ' + panel.name;
        if (panel.height <= 0)
            throw 'Invalid height for panel ' + panel.name;
        for (let i = 1; i <= panel.quantity; ++i) {
            const name = panel.name + ' ' + String(i);
            if (name in panels)
                throw 'Duplicate panel name ' + name;
            panels[name] = {width: panel.width, height: panel.height};
        }
    }
    if (u.equals(panels, {}))
        throw 'No panels defined';

    const items = {};
    for (const item of r.get('form', 'items')) {
        if (!item.name)
            throw 'Invalid item name';
        if (item.quantity < 1)
            throw 'Invalid quantity for item ' + item.name;
        if (item.width <= 0)
            throw 'Invalid width for item ' + item.name;
        if (item.height <= 0)
            throw 'Invalid height for item ' + item.name;
        for (let i = 1; i <= item.quantity; ++i) {
            const name = item.name + ' ' + String(i);
            if (name in items) {
                throw 'Duplicate item name ' + name;
            }
            items[name] = {
                width: item.width,
                height: item.width,
                can_rotate: item.can_rotate
            };
        }
    }
    if (u.equals(items, {}))
        throw 'No items defined';

    return {
        cut_width: cutWidth,
        panels: panels,
        items: items
    };
}


function showNotification(type, message) {
    iziToast[type]({message: message});
}


async function csvImport(header) {
    const file = await loadFile('.csv');
    if (!file)
        return [];

    const data = await new Promise(resolve => {
        Papa.parse(file, {
            header: true,
            complete: result => resolve(result.data)
        });
    });

    const result = [];
    for (const i of data) {
        let element = {};
        for (const [k, v] of Object.entries(header)) {
            if (!(k in i)) {
                element = null;
                break;
            }
            element[k] = v(i[k]);
        }
        if (element)
            result.push(element);
    }
    return result;
}


async function loadFile(ext) {
    const el = document.createElement('input');
    el.style = 'display: none';
    el.type = 'file';
    el.accept = ext;
    document.body.appendChild(el);

    const promise = new Promise(resolve => {
        const listener = evt => {
            resolve(u.get(['files', 0], evt.target));
        };
        el.addEventListener('change', listener);

        // TODO blur not fired on close???
        el.addEventListener('blur', listener);

        el.click();
    });

    try {
        return await promise;
    } finally {
        document.body.removeChild(el);
    }
}
