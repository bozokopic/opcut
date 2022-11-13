import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common';

import * as input from './input';


export function main(): u.VNodeChild[] {
    const result = r.get('result') as common.Result | null;
    if (result == null)
        return [];
    return [
        ['div.form',
            ['label', 'Export'],
            ['div',
                ['button', {
                    on: {
                        click: common.generate
                    }},
                    ['span.fa.fa-file-pdf-o'],
                    ' PDF'
                ]
            ],
            ['label', 'Font size'],
            input.select(
                r.get('svg', 'font_size') as string,
                [['0.5', 'Small'],
                 ['1', 'Medium'],
                 ['1.5', 'Large']],
                val => r.set(['svg', 'font_size'], val)
            ),
            ['label'],
            input.checkbox(
                'Show names',
                r.get('svg', 'show_names') as boolean,
                val => r.set(['svg', 'show_names'], val)
            ),
            ['label'],
            input.checkbox(
                'Show dimensions',
                r.get('svg', 'show_dimensions') as boolean,
                val => r.set(['svg', 'show_dimensions'], val)
            ),
            ['label', 'Cut color'],
            input.color(
                r.get('svg', 'cut_color') as string,
                val => r.set(['svg', 'cut_color'], val)
            ),
            ['label', 'Item color'],
            input.color(
                r.get('svg', 'item_color') as string,
                val => r.set(['svg', 'item_color'], val)
            ),
            ['label', 'Selected color'],
            input.color(
                r.get('svg', 'selected_color') as string,
                val => r.set(['svg', 'selected_color'], val)
            ),
            ['label', 'Unused color'],
            input.color(
                r.get('svg', 'unused_color') as string,
                val => r.set(['svg', 'unused_color'], val)
            )
        ],
        Object.keys(result.params.panels).map(panelResult)
    ];
}


function panelResult(panel: string): u.VNode {
    const isSelected = (item: string | null) => u.equals(r.get('selected'), {panel: panel, item: item});

    return ['div.panel',
        ['div.panel-name', {
            class: {
                selected: isSelected(null)
            },
            on: {
                click: () => r.set('selected', {panel: panel, item: null})
            }},
            panel
        ],
        u.filter(used => used.panel == panel, r.get('result', 'used') as common.Used[]).map(used =>
            ['div.item', {
                class: {
                    selected: isSelected(used.item)
                },
                on: {
                    click: () => r.set('selected', {panel: panel, item: used.item})
                }},
                ['div.item-name', used.item],
                (used.rotate ? ['span.item-rotate.fa.fa-refresh'] : []),
                ['div.item-x',
                    'X:',
                    String(Math.round(used.x * 100) / 100)
                ],
                ['div.item-y',
                    'Y:',
                    String(Math.round(used.y * 100) / 100)
                ]
            ])
    ];
}
