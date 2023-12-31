import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common';


export function main(): u.VNodeChild {
    const state = common.getState();

    if (!state.result || !state.selected.panel)
        return [];

    const result = state.result;
    const selectedPanel = state.selected.panel;
    const selectedItem = state.selected.item;

    const panel = result.params.panels[selectedPanel];
    const used = u.filter(i => i.panel == selectedPanel, state.result.used);
    const unused = u.filter(i => i.panel == selectedPanel, state.result.unused);

    const fontSize = Math.max(panel.height, panel.width) * 0.02 *
        common.fontSizes[state.svg.fontSize];
    const nameFontSize = String(fontSize);
    const dimensionFontSize = String(fontSize * 0.8);

    return ['svg', {
        attrs: {
            width: '100%',
            height: '100%',
            viewBox: [0, 0, panel.width, panel.height].join(' '),
            preserveAspectRatio: 'xMidYMid'
        }},
        ['rect', {
            attrs: {
                x: '0',
                y: '0',
                width: String(panel.width),
                height: String(panel.height),
                'stroke-width': '0',
                fill: state.settings.colors.cut
            }}
        ],
        used.map(used => {
            const item = result.params.items[used.item];
            const width = (used.rotate ? item.height : item.width);
            const height = (used.rotate ? item.width : item.height);

            return ['rect', {
                props: {
                    style: 'cursor: pointer'
                },
                attrs: {
                    x: String(used.x),
                    y: String(used.y),
                    width: String(width),
                    height: String(height),
                    'stroke-width': '0',
                    fill: (used.item == selectedItem ?
                        state.settings.colors.selected :
                        state.settings.colors.item
                    )
                },
                on: {
                    click: () => r.set(['selected', 'item'], used.item)
                }}
            ];
        }),
        unused.map(unused => ['rect', {
            attrs: {
                x: String(unused.x),
                y: String(unused.y),
                width: String(unused.width),
                height: String(unused.height),
                'stroke-width': '0',
                fill: state.settings.colors.unused
            }}
        ]),
        used.map(used => {
            const item = result.params.items[used.item];
            const width = (used.rotate ? item.height : item.width);
            const height = (used.rotate ? item.width : item.height);
            const click = () => r.set(['selected', 'item'], used.item);

            return [
                (!state.svg.showNames ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width / 2),
                        y: String(used.y + height / 2),
                        'dominant-baseline': 'middle',
                        'text-anchor': 'middle',
                        'font-size': nameFontSize
                    },
                    on: {
                        click: click
                    }},
                    used.item + (used.rotate ? ' \u21BB' : '')
                ]),
                (!state.svg.showDimensions ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width / 2),
                        y: String(used.y + height),
                        'dominant-baseline': 'baseline',
                        'text-anchor': 'middle',
                        'font-size': dimensionFontSize
                    },
                    on: {
                        click: click
                    }},
                    String(width)
                ]),
                (!state.svg.showDimensions ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width),
                        y: String(used.y + height / 2),
                        'transform': `rotate(-90, ${used.x + width}, ${used.y + height / 2})`,
                        'dominant-baseline': 'baseline',
                        'text-anchor': 'middle',
                        'font-size': dimensionFontSize
                    },
                    on: {
                        click: click
                    }},
                    String(height)
                ])
            ];
        })
    ];
}
