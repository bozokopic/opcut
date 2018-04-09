/** @module opcut/renderer2 */

import * as snabbdom from 'snabbdom/es/snabbdom';
import snabbdomAttributes from 'snabbdom/es/modules/attributes';
import snabbdomClass from 'snabbdom/es/modules/class';
import snabbdomProps from 'snabbdom/es/modules/props';
// import snabbdomStyle from 'snabbdom/es/modules/style';
import snabbdomDataset from 'snabbdom/es/modules/dataset';
import snabbdomEvent from 'snabbdom/es/modules/eventlisteners';

import * as u from 'opcut/util';
import * as ev from 'opcut/ev';


const patch = snabbdom.init([
    snabbdomAttributes,
    snabbdomClass,
    snabbdomProps,
    // snabbdomStyle,
    snabbdomDataset,
    snabbdomEvent
]);


function vhFromArray(node) {
    if (!node)
        return [];
    if (u.isString(node))
        return node;
    if (!u.isArray(node))
        throw 'Invalid node structure';
    if (node.length < 1)
        return [];
    if (typeof node[0] != 'string')
        return node.map(vhFromArray);
    const hasData = node.length > 1 && u.isObject(node[1]);
    const children = u.pipe(
        u.map(vhFromArray),
        u.flatten,
        Array.from
    )(node.slice(hasData ? 2 : 1));
    const result = hasData ?
        snabbdom.h(node[0], node[1], children) :
        snabbdom.h(node[0], children);
    return result;
}

/**
 * Virtual DOM renderer
 */
export class Renderer {

    /**
     * Calls `init` method
     * @param {HTMLElement} [el=document.body]
     * @param {Any} [initState=null]
     * @param {Function} [vtCb=null]
     * @param {Number} [maxFps=30]
     */
    constructor(el, initState, vtCb, maxFps) {
        this.init(el, initState, vtCb, maxFps);
    }

    /**
     * Initialize renderer
     * @param {HTMLElement} [el=document.body]
     * @param {Any} [initState=null]
     * @param {Function} [vtCb=null]
     * @param {Number} [maxFps=30]
     * @return {Promise}
     */
    init(el, initState, vtCb, maxFps) {
        this._state = null;
        this._changes = [];
        this._promise = null;
        this._timeout = null;
        this._lastRender = null;
        this._vtCb = vtCb;
        this._maxFps = u.isNumber(maxFps) ? maxFps : 30;
        this._vNode = el || document.querySelector('body');
        if (initState)
            return this.change(_ => initState);
        return new Promise(resolve => { resolve(); });
    }

    /**
     * Get current state value referenced by `paths`
     * @param {...Path} paths
     * @return {Any}
     */
    get(...paths) {
        return u.get(paths, this._state);
    }

    /**
     * Change current state value referenced by `path`
     * @param {Path} path
     * @param {Any} value
     * @return {Promise}
     */
    set(path, value) {
        if (arguments.length < 2) {
            value = path;
            path = [];
        }
        return this.change(path, _ => value);
    }

    /**
     * Change current state value referenced by `path`
     * @param {Path} path
     * @param {Function} cb
     * @return {Promise}
     */
    change(path, cb) {
        if (arguments.length < 2) {
            cb = path;
            path = [];
        }
        this._changes.push([path, cb]);
        if (this._promise)
            return this._promise;
        this._promise = new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    this._change();
                } catch(e) {
                    this._promise = null;
                    reject(e);
                    throw e;
                }
                this._promise = null;
                resolve();
            }, 0);
        });
        return this._promise;
    }

    _change() {
        let change = false;
        while (this._changes.length > 0) {
            const [path, cb] = this._changes.shift();
            const view = u.get(path);
            const oldState = this._state;
            this._state = u.change(path, cb, this._state);
            if (this._state && u.equals(view(oldState),
                                        view(this._state)))
                continue;
            change = true;
            if (!this._vtCb || this._timeout)
                continue;
            const delay = (!this._lastRender || !this._maxFps ?
                0 :
                (1000 / this._maxFps) -
                (performance.now() - this._lastRender));
            this._timeout = setTimeout(() => {
                this._timeout = null;
                this._lastRender = performance.now();
                const vNode = vhFromArray(this._vtCb(this));
                patch(this._vNode, vNode);
                this._vNode = vNode;
                ev.fire(this, 'render', [this._state]);
            }, (delay > 0 ? delay : 0));
        }
        if (change)
            ev.fire(this, 'change', [this._state]);
    }

}
// Renderer.prototype.set = u.curry(Renderer.prototype.set);
// Renderer.prototype.change = u.curry(Renderer.prototype.change);


/**
 * Default renderer
 * @static
 * @type {Renderer}
 */
const defaultRenderer = new Renderer();
export default defaultRenderer;
