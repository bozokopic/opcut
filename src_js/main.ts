import * as u from '@hat-open/util';
import r from '@hat-open/renderer';

import * as common from './common';
import * as vt from './vt/index';

import '../src_scss/main.scss';


function main() {
    const root = document.body.appendChild(document.createElement('div'));
    r.init(root, common.defaultState, vt.main);
}


window.addEventListener('load', main);
(window as any).r = r;
(window as any).u = u;
