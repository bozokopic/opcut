import r from 'opcut/renderer';
import * as u from 'opcut/util';
import * as ev from 'opcut/ev';
import * as states from 'opcut/states';
import * as vt from 'opcut/vt';

import 'style/main.scss';


function main() {
    let root = document.body.appendChild(document.createElement('div'));
    r.init(root, states.main, vt.main);
}


ev.on(window, 'load', main);
window.r = r;
window.u = u;
