import * as URI from 'uri-js';
import iziToast from 'izitoast';

import r from 'opcut/renderer';
import * as u from 'opcut/util';
import * as states from 'opcut/states';
import * as fs from 'opcut/fs';


const calculateUrl = URI.resolve(window.location.href, './calculate');
const generateOutputUrl = URI.resolve(window.location.href, './generate_output');


export function calculate() {
    const msg = {
        method: r.get('form', 'method'),
        params: {
            cut_width: u.strictParseFloat(r.get('form', 'cut_width')),
            panels: u.pipe(
                u.map(panel => [panel.name, {width: u.strictParseFloat(panel.width),
                                             height: u.strictParseFloat(panel.height)}]),
                u.fromPairs
            )(r.get('form', 'panels', 'items')),
            items: u.pipe(
                u.map(item => [item.name, {width: u.strictParseFloat(item.width),
                                           height: u.strictParseFloat(item.height),
                                           can_rotate: item.can_rotate}]),
                u.fromPairs
            )(r.get('form', 'items', 'items')),
        }
    };
    try {
        validateCalculateRequest(msg);
    } catch (e) {
        showNotification(e, 'error');
        return;
    }
    const req = new XMLHttpRequest();
    req.onload = () => parseCalculateResponse(JSON.parse(req.responseText));
    req.open('POST', calculateUrl);
    req.setRequestHeader('Content-Type', 'application/json');
    req.send(JSON.stringify(msg));
}


export function generateOutput(output_type) {
    const msg = {
        output_type: output_type,
        result: r.get('result')
    };
    const req = new XMLHttpRequest();
    req.onload = () => parseGenerateOutputResponse(JSON.parse(req.responseText), output_type);
    req.open('POST', generateOutputUrl);
    req.setRequestHeader('Content-Type', 'application/json');
    req.send(JSON.stringify(msg));
}


function validateCalculateRequest(msg) {
    if (!Number.isFinite(msg.params.cut_width) || msg.params.cut_width < 0)
        throw 'Invalid cut width';
    if (u.equals(msg.params.panels, {}))
        throw 'No panels defined';
    for (let [name, panel] of u.toPairs(msg.params.panels)) {
        if (!name)
            throw 'Invalid panel name';
        if (!Number.isFinite(panel.width) || panel.width <= 0)
            throw 'Invalid width for panel ' + name;
        if (!Number.isFinite(panel.height) || panel.height <= 0)
            throw 'Invalid height for panel ' + name;
    }
    if (u.equals(msg.params.items, {}))
        throw 'No items defined';
    for (let [name, item] of u.toPairs(msg.params.items)) {
        if (!name)
            throw 'Invalid item name';
        if (!Number.isFinite(item.width) || item.width <= 0)
            throw 'Invalid width for item ' + name;
        if (!Number.isFinite(item.height) || item.height <= 0)
            throw 'Invalid height for item ' + name;
    }
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
    if (msg.data) {
        const fileName = 'output.pdf';
        fs.saveB64Data(msg.data, fileName);
    } else {
        showNotification('Error generating output', 'error');
    };
}


function showNotification(message, type) {
    iziToast[type]({message: message});
}
