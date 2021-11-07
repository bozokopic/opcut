import * as u from '@hat-open/util';
import r from '@hat-open/renderer';

import * as states from './states';
import * as vt from './vt';

import '../src_scss/main.scss';


function main() {
    const root = document.body.appendChild(document.createElement('div'));
    r.init(root, states.main, vt.main);
}


window.addEventListener('load', main);
window.r = r;
window.u = u;
