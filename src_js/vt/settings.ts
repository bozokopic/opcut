import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import version from '../version';
import * as common from '../common';
import * as i18n from '../i18n';

import * as input from './input';


export function main(): u.VNode {
    const state = common.getState();
    const dict = common.getDict();

    return ['div.settings', {
        on: {
            click: (evt: MouseEvent) => evt.stopPropagation()
        }},
        ['div.header',
            ['div.title', dict.settings],
            ['button', {
                on: {
                    click: () => r.set('showSettings', false)
                }},
                icon('window-close')
            ]
        ],
        ['div.form',
            ['label.label', dict.version],
            ['span', version],
            ['label.label', dict.language],
            input.select(
                state.settings.lang,
                Object.entries(i18n.langs),
                setSettings('lang')
            ),
            ['div.title', dict.result_colors],
            ['label.label', dict.cut],
            input.color(
                state.settings.colors.cut,
                setSettings(['colors', 'cut'])
            ),
            ['label.label', dict.item],
            input.color(
                state.settings.colors.item,
                setSettings(['colors', 'item'])
            ),
            ['label.label', dict.selected],
            input.color(
                state.settings.colors.selected,
                setSettings(['colors', 'selected'])
            ),
            ['label.label', dict.unused],
            input.color(
                state.settings.colors.unused,
                setSettings(['colors', 'unused'])
            ),
            ['div.title', dict.default_panel_values],
            ['label.label', dict.height],
            input.number(
                state.settings.panel.height,
                u.isNumber,
                setSettings(['panel', 'height'])
            ),
            ['label.label', dict.width],
            input.number(
                state.settings.panel.width,
                u.isNumber,
                setSettings(['panel', 'width'])
            ),
            ['label.label', dict.name],
            input.text(
                state.settings.panel.name,
                Boolean,
                setSettings(['panel', 'name'])
            ),
            ['div.title', dict.default_item_values],
            ['label.label', dict.height],
            input.number(
                state.settings.item.height,
                u.isNumber,
                setSettings(['item', 'height'])
            ),
            ['label.label', dict.width],
            input.number(
                state.settings.item.width,
                u.isNumber,
                setSettings(['item', 'width'])
            ),
            ['label.label', dict.name],
            input.text(
                state.settings.item.name,
                Boolean,
                setSettings(['item', 'name'])
            ),
            ['label.label'],
            input.checkbox(
                dict.rotate,
                state.settings.item.canRotate,
                setSettings(['item', 'canRotate'])
            )
        ]
    ];
}


const setSettings = u.curry((path: u.JPath, val: u.JData) =>
    r.change([], ((state: common.State) => {
        state = u.set(['settings', path], val, state) as common.State;
        common.saveSettings(state.settings);
        return state;
    }) as any)
);


function icon(name: string): u.VNode {
    return ['img.icon', {
        props: {
            src: `icons/${name}.svg`
        }
    }];
}
