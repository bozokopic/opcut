import * as URI from 'uri-js';
import iziToast from 'izitoast';

import r from '@hat-core/renderer';
import * as u from '@hat-core/util';

import * as states from 'opcut/states';
import * as fs from 'opcut/fs';


const calculateUrl = URI.resolve(window.location.href, './calculate');
const generateOutputUrl = URI.resolve(window.location.href, './generate_output');


export function calculate() {
    try {
        let msg = createValidateRequest();
        send(calculateUrl, msg).then(parseCalculateResponse);
    } catch (e) {
        showNotification(e, 'error');
    }
}


export function generateOutput(output_type, panel) {
    const msg = {
        output_type: output_type,
        result: r.get('result'),
        panel: panel
    };
    send(generateOutputUrl, msg).then(msg => parseGenerateOutputResponse(msg, output_type));
}


function send(url, msg) {
    return new Promise(resolve => {
        const req = new XMLHttpRequest();
        req.onload = () => { resolve(JSON.parse(req.responseText)); };
        req.open('POST', url);
        req.setRequestHeader('Content-Type', 'application/json');
        req.send(JSON.stringify(msg));
    });
}


function createValidateRequest() {
    const cutWidth = u.strictParseFloat(r.get('form', 'cut_width'));
    if (!Number.isFinite(cutWidth) || cutWidth < 0)
        throw 'Invalid cut width';

    const panels = {};
    for (let panel of r.get('form', 'panels', 'items')) {
        const quantity = u.strictParseInt(panel.quantity);
        const width = u.strictParseFloat(panel.width);
        const height = u.strictParseFloat(panel.height);
        if (!panel.name)
            throw 'Invalid panel name';
        if (!Number.isFinite(quantity) || quantity < 1)
            throw 'Invalid quantity for panel ' + panel.name;
        if (!Number.isFinite(width) || width <= 0)
            throw 'Invalid width for panel ' + panel.name;
        if (!Number.isFinite(height) || height <= 0)
            throw 'Invalid height for panel ' + panel.name;
        for (let i = 1; i <= quantity; ++i) {
            const name = panel.name + ' ' + String(i);
            if (name in panels) {
                throw 'Duplicate panel name ' + name;
            }
            panels[name] = {width: width, height: height};
        }
    }
    if (u.equals(panels, {}))
        throw 'No panels defined';

    const items = {};
    for (let item of r.get('form', 'items', 'items')) {
        const quantity = u.strictParseInt(item.quantity);
        const width = u.strictParseFloat(item.width);
        const height = u.strictParseFloat(item.height);
        if (!item.name)
            throw 'Invalid item name';
        if (!Number.isFinite(quantity) || quantity < 1)
            throw 'Invalid quantity for item ' + item.name;
        if (!Number.isFinite(width) || width <= 0)
            throw 'Invalid width for item ' + item.name;
        if (!Number.isFinite(height) || height <= 0)
            throw 'Invalid height for item ' + item.name;
        for (let i = 1; i <= quantity; ++i) {
            const name = item.name + ' ' + String(i);
            if (name in items) {
                throw 'Duplicate item name ' + name;
            }
            items[name] = {
                width: width,
                height: height,
                can_rotate: item.can_rotate
            };
        }
    }
    if (u.equals(items, {}))
        throw 'No items defined';

    return {
        method: r.get('form', 'method'),
        params: {
            cut_width: cutWidth,
            panels: panels,
            items: items
        }
    };
}


function parseCalculateResponse(msg) {
    r.change(u.pipe(
        u.set('result', msg.result),
        u.set('selected', states.main.selected)
    ));
    if (msg.result) {
        showNotification('New calculation available', 'success');
    } else {
        showNotification('Could not resolve calculation', 'error');
    }
}


function parseGenerateOutputResponse(msg, output_type) {
    if (output_type == 'PDF' && msg.data) {
        const fileName = 'output.pdf';
        fs.saveB64Data(msg.data, fileName);
    } else {
        showNotification('Error generating output', 'error');
    }
}


function showNotification(message, type) {
    iziToast[type]({message: message});
}
