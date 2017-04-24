import bean from 'bean';
import R from 'ramda';

import r from 'opcut/renderer';
import * as l from 'opcut/lenses';
import * as common from 'opcut/common';
import * as vt from 'opcut/vt';

import 'static!static/index.html';
import 'style/main.scss';


function main() {
    let root = document.body.appendChild(document.createElement('div'));
    r.init(root, common.defaultState, vt.main);
}


bean.on(window, 'load', main);
