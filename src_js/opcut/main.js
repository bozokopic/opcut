import * as u from '@hat-core/util';
import r from '@hat-core/renderer';

import * as states from 'opcut/states';
import * as vt from 'opcut/vt';

import 'main.scss';


function main() {
    const root = document.body.appendChild(document.createElement('div'));
    r.init(root, states.main, vt.main);
}


window.addEventListener('load', main);
window.r = r;
window.u = u;
