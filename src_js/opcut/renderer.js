import Delegator from 'dom-delegator';
import R from 'ramda';
import bean from 'bean';
import vh from 'virtual-dom/h';
import diff from 'virtual-dom/diff';
import patch from 'virtual-dom/patch';
import createElement from 'virtual-dom/create-element';

import * as l from 'opcut/lenses';


const delegator = Delegator();
const vhTypes = ['VirtualNode', 'Widget'];


function vhFromArray(node) {
    if (!node)
        return [];
    if (typeof node == 'string' || vhTypes.includes(node.type))
        return node;
    if (!Array.isArray(node))
        throw 'Invalid node structure';
    if (node.length < 1)
        return [];
    if (typeof node[0] != 'string')
        return node.map(vhFromArray);
    let hasProps = (node.length > 1 &&
                    typeof node[1] == 'object' &&
                    !Array.isArray(node[1]) &&
                    !vhTypes.includes(node[1].type));
    let children = R.flatten(node.slice(hasProps ? 2 : 1).map(vhFromArray));
    let result = hasProps ? vh(node[0], node[1], children) :
                            vh(node[0], children);

    // disable SoftSetHook for input
    if (result.tagName == 'INPUT' &&
        result.properties &&
        result.properties.value &&
        typeof(result.properties.value) === 'object') {
        result.properties.value = result.properties.value.value;
    }

    return result;
}


class VTreeRenderer {

    constructor(el) {
        this._el = el;
        this._vtree = null;
    }

    render(vtree) {
        let vt = vhFromArray(vtree);
        if (vt.type == 'VirtualNode') {
            if (this._vtree) {
                let d = diff(this._vtree, vt);
                patch(this._el.firstChild, d);
            } else {
                while (this._el.firstChild)
                    this._el.removeChild(this._el.firstChild);
                this._el.appendChild(createElement(vt));
            }
            this._vtree = vt;
        } else {
            this._vtree = null;
            while (this._el.firstChild)
                this._el.removeChild(this._el.firstChild);
        }
    }

}


export class Renderer {

    constructor(el, initState, vtCb) {
        this.init(el, initState, vtCb);
    }

    init(el, initState, vtCb) {
        this._state = null;
        this._changeCbs = [];
        this._vtCb = vtCb;
        this._r = new VTreeRenderer(el || document.querySelector('body'));
        if (initState)
            this.change(R.identity, _ => initState);
    }

    view(...lenses) {
        return R.view(R.apply(l.path, lenses), this._state);
    }

    set(lens, value) {
        if (arguments.length < 2) {
            value = lens;
            lens = R.identity;
        }
        this.change(lens, _ => value);
    }

    change(lens, cb) {
        if (arguments.length < 2) {
            cb = lens;
            lens = R.identity;
        }
        if (this._changeCbs.push(cb) > 1)
            return;
        let startingSubState = this.view(lens);
        while (this._changeCbs.length > 0) {
            this._state = R.over(l.path(lens), this._changeCbs[0], this._state);
            this._changeCbs.shift();
        }
        if (!this._vtCb ||
            (this._state && R.equals(startingSubState, this.view(lens))))
            return;
        this._r.render(this._vtCb(this._state));
        bean.fire(this, 'render', this._state);
    }

}


const defaultRenderer = new Renderer();
export default defaultRenderer;
