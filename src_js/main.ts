import * as u from '@hat-open/util';
import r from '@hat-open/renderer';

import * as common from './common';
import * as vt from './vt/index';


function main() {
    const settings = common.loadSettings();
    const state = u.set('settings', settings, common.defaultState);

    const root = document.body.appendChild(document.createElement('div'));

    r.init(root, state, vt.main);
}


window.addEventListener('load', main);
(window as any).r = r;
(window as any).u = u;
