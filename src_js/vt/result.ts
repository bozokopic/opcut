import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common.js';

import * as input from './input.js';


export function main(): u.VNodeChild {
    const state = common.getState();
    const dict = common.getDict();

    if (state.result == null)
        return [];

    const fontSizes = u.map(
        i => [i, dict[i]] as [common.FontSize, string],
        Object.keys(common.fontSizes) as common.FontSize[]
    );

    return [
        ['div.form',
            ['label.label', dict.export],
            ['div',
                ['button', {
                    on: {
                        click: common.generate
                    }},
                    icon('application-pdf'),
                    ' PDF'
                ]
            ],
            ['label.label', dict.font_size],
            input.select(
                state.svg.fontSize,
                fontSizes,
                val => r.set(['svg', 'fontSize'], val)
            ),
            ['label.label'],
            input.checkbox(
                dict.show_names,
                state.svg.showNames,
                val => r.set(['svg', 'showNames'], val)
            ),
            ['label.label'],
            input.checkbox(
                dict.show_dimensions,
                state.svg.showDimensions,
                val => r.set(['svg', 'showDimensions'], val)
            ),

            ['label.label', dict.cut_area],
            ['span', String(Math.round(calculateCutArea(state.result) * 100) / 100)]
        ],
        Object.keys(state.result.params.panels).map(panelResult)
    ];
}


function panelResult(panel: string): u.VNodeChild {
    const state = common.getState();

    if (state.result == null)
        return [];

    const select = (item: string | null) => r.set('selected', {panel, item});
    const isSelected = (item: string | null) =>
        state.selected.panel == panel && state.selected.item == item;

    return ['div.panel',
        ['div.panel-name', {
            class: {
                selected: isSelected(null)
            },
            on: {
                click: () => select(null)
            }},
            panel
        ],
        u.filter(used => used.panel == panel, state.result.used).map(used =>
            ['div.item', {
                class: {
                    selected: isSelected(used.item)
                },
                on: {
                    click: () => select(used.item)
                }},
                ['div.item-name', used.item],
                (used.rotate ? icon('object-rotate-right') : []),
                ['div.item-x',
                    'X:',
                    String(Math.round(used.x * 100) / 100)
                ],
                ['div.item-y',
                    'Y:',
                    String(Math.round(used.y * 100) / 100)
                ]
            ]
        )
    ];
}



function icon(name: string): u.VNode {
    return ['img.icon', {
        props: {
            src: `icons/${name}.svg`
        }
    }];
}


function calculateCutArea(result: common.Result): number {
    type T = {width: number, height: number};

    const area = ({width, height}: T) => width * height;
    const sum = u.reduce((acc, i: number) => acc + i, 0);
    const sumAreas = (x: T[]) => sum(u.map(area, x));

    const panels = Object.values(result.params.panels);
    const used = u.map(
        i => result.params.items[i.item],
        Object.values(result.used)
    );
    const unused = Object.values(result.unused);

    return sumAreas(panels) - sumAreas(used) - sumAreas(unused);
}
