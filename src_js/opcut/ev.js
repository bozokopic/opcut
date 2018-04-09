/** @module opcut/ev */

import bean from 'bean';

import * as u from 'opcut/util';


export function on(element, eventType, selector, handler, args) {
    bean.on(element, eventType, selector, handler, args);
}

export function one(element, eventType, selector, handler, args) {
    bean.one(element, eventType, selector, handler, args);
}

export function off(element, eventType, handler) {
    bean.off(element, eventType, handler);
}

export function fire(element, eventType, args) {
    u.delay(bean.fire, 0, element, eventType, args);
}
