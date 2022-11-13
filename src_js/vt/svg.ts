import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common';


export function main(): u.VNode | null {
    const result = r.get('result') as common.Result | null;
    const selected = r.get('selected') as {
        panel: string | null,
        item: string | null
    };
    if (!result || !selected.panel)
        return null;

    const panel = result.params.panels[selected.panel];
    const used = u.filter(i => i.panel == selected.panel, result.used);
    const unused = u.filter(i => i.panel == selected.panel, result.unused);
    const panelColor = 'rgb(100,100,100)';
    const itemColor = 'rgb(250,250,250)';
    const selectedItemColor = 'rgb(200,140,140)';
    const unusedColor = 'rgb(238,238,238)';
    const fontSize = String(
        Math.max(panel.height, panel.width) * 0.02 *
        u.strictParseFloat(r.get('svg', 'font_size') as string)
    );
    const showNames = r.get('svg', 'show_names');
    const showDimensions = r.get('svg', 'show_dimensions');

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
                fill: panelColor
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
                    fill: (used.item == selected.item ? selectedItemColor : itemColor)
                },
                on: {
                    click: () => r.set(['selected', 'item'], used.item)
                }}
            ];
        }),
        unused.map(unused => {
            return ['rect', {
                attrs: {
                    x: String(unused.x),
                    y: String(unused.y),
                    width: String(unused.width),
                    height: String(unused.height),
                    'stroke-width': '0',
                    fill: unusedColor
                }}
            ];
        }),
        used.map(used => {
            const item = result.params.items[used.item];
            const width = (used.rotate ? item.height : item.width);
            const height = (used.rotate ? item.width : item.height);
            const click = () => r.set(['selected', 'item'], used.item);
            return [
                (!showNames ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width / 2),
                        y: String(used.y + height / 2),
                        'alignment-baseline': 'middle',
                        'text-anchor': 'middle',
                        'font-size': fontSize
                    },
                    on: {
                        click: click
                    }},
                    used.item + (used.rotate ? ' \u293E' : '')
                ]),
                (!showDimensions ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width / 2),
                        y: String(used.y + height),
                        'alignment-baseline': 'baseline',
                        'text-anchor': 'middle',
                        'font-size': fontSize
                    },
                    on: {
                        click: click
                    }},
                    String(width)
                ]),
                (!showDimensions ? [] : ['text', {
                    props: {
                        style: 'cursor: pointer'
                    },
                    attrs: {
                        x: String(used.x + width),
                        y: String(used.y + height / 2),
                        'transform': `rotate(-90, ${used.x + width}, ${used.y + height / 2})`,
                        'alignment-baseline': 'baseline',
                        'text-anchor': 'middle',
                        'font-size': fontSize
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
