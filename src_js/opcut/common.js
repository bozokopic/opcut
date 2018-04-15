import * as URI from 'uri-js';
import iziToast from 'izitoast';

import r from 'opcut/renderer';
import * as u from 'opcut/util';


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
    
}


function showNotification(message, type) {
    iziToast[type]({message: message});
}
