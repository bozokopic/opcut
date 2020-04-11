import r from '@hat-core/renderer';
import * as u from '@hat-core/util';

import * as grid from 'opcut/grid';
import * as common from 'opcut/common';
import * as states from 'opcut/states';
import * as validators from 'opcut/validators';


export function main() {
    return ['div.window',
        leftPanel(),
        centerPanel(),
        rightPanel()
    ];
}


function leftPanel() {
    const methodPath = ['form', 'method'];
    const cutWidthPath = ['form', 'cut_width'];
    const cutWidthTitle = (cutWidth =>
        (Number.isFinite(cutWidth) && cutWidth >= 0) ? '' : 'not valid cut width'
    )(u.strictParseFloat(r.get(cutWidthPath)));
    return ['div.left-panel',
        ['div.header',
            ['div.title', 'OPCUT'],
            ['a', {
                props: {
                    title: 'GitHub',
                    href: 'https://github.com/bozokopic/opcut'
                }},
                ['span.fa.fa-github']
            ]
        ],
        ['div.group',
            ['label', 'Method'],
            ['select',
                ['FORWARD_GREEDY', 'GREEDY'].map(method =>
                    ['option', {
                        props: {
                            value: method,
                            selected: r.get(methodPath) == method
                        },
                        on: {
                            change: evt => r.set(methodPath, evt.target.value)
                        }},
                        method
                    ])
            ]
        ],
        ['div.group',
            ['label', 'Cut width'],
            ['input', {
                class: {
                    invalid: cutWidthTitle
                },
                props: {
                    value: r.get(cutWidthPath),
                    title: cutWidthTitle
                },
                on: {
                    change: evt => r.set(cutWidthPath, evt.target.value)
                }}
            ]
        ],
        ['div.content',
            leftPanelPanels(),
            leftPanelItems()
        ],
        ['button.calculate', {
            on: {
                click: common.calculate
            }},
            'Calculate'
        ]
    ];
}


function leftPanelPanels() {
    const panelsPath = ['form', 'panels'];
    const deleteColumn = grid.deleteColumn(panelsPath);
    const nameValidator = validators.createChainValidator(
        validators.notEmptyValidator,
        validators.createUniqueValidator());
    const quantityValidator = validators.quantityValidator;
    const widthValidator = validators.dimensionValidator;
    const heightValidator = validators.dimensionValidator;
    const csvColumns = grid.createStringCsvColumns('name', 'quantity', 'width', 'height');
    return ['div',
        ['table.grid',
            ['thead',
                ['tr',
                    ['th', 'Panel name'],
                    ['th.fixed', 'Quantity'],
                    ['th.fixed', 'Height'],
                    ['th.fixed', 'Width'],
                    ['th.fixed']
                ]
            ],
            grid.tbody(panelsPath,
                       ['name', 'quantity', 'height', 'width', deleteColumn],
                       [nameValidator, quantityValidator, heightValidator, widthValidator]),
            grid.tfoot(panelsPath, 5, states.panelsItem, csvColumns)
        ]
    ];
}


function leftPanelItems() {
    const itemsPath = ['form', 'items'];
    const rotateColumn = grid.checkboxColumn(itemsPath, 'can_rotate');
    const deleteColumn = grid.deleteColumn(itemsPath);
    const nameValidator = validators.createChainValidator(
        validators.notEmptyValidator,
        validators.createUniqueValidator());
    const quantityValidator = validators.quantityValidator;
    const widthValidator = validators.dimensionValidator;
    const heightValidator = validators.dimensionValidator;
    const csvColumns =  u.merge(
        grid.createStringCsvColumns('name', 'quantity', 'width', 'height'),
        grid.createBooleanCsvColumns('can_rotate'));
    return ['div',
        ['table.grid',
            ['thead',
                ['tr',
                    ['th', 'Item name'],
                    ['th.fixed', 'Quantity'],
                    ['th.fixed', 'Height'],
                    ['th.fixed', 'Width'],
                    ['th.fixed', 'Rotate'],
                    ['th.fixed']
                ]
            ],
            grid.tbody(itemsPath,
                       ['name', 'quantity', 'height', 'width', rotateColumn, deleteColumn],
                       [nameValidator, quantityValidator, heightValidator, widthValidator]),
            grid.tfoot(itemsPath, 6, states.itemsItem, csvColumns)
        ]
    ];
}


function rightPanel() {
    const result = r.get('result');
    return ['div.right-panel', (!result ?
        [] :
        [
            ['div.toolbar',
                ['button', {
                    on: {
                        click: () => common.generateOutput('PDF', null)
                    }},
                    ['span.fa.fa-file-pdf-o'],
                    ' PDF'
                ]
            ],
            Object.keys(result.params.panels).map(rightPanelPanel)
        ])
    ];
}


function rightPanelPanel(panel) {
    const isSelected = item => u.equals(r.get('selected'), {panel: panel, item: item});
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
        u.filter(used => used.panel == panel)(r.get('result', 'used')).map(used =>
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


function centerPanel() {
    const result = r.get('result');
    const selected = r.get('selected');
    if (!result || !selected.panel)
        return ['div.center-panel'];
    const panel = result.params.panels[selected.panel];
    const used = u.filter(i => i.panel == selected.panel, result.used);
    const unused = u.filter(i => i.panel == selected.panel, result.unused);
    const panelColor = 'rgb(100,100,100)';
    const itemColor = 'rgb(250,250,250)';
    const selectedItemColor = 'rgb(200,140,140)';
    const unusedColor = 'rgb(238,238,238)';
    const fontSize = String(Math.max(panel.height, panel.width) * 0.02);
    return ['div.center-panel',
        ['svg', {
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
                return ['text', {
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
                        click: () => r.set(['selected', 'item'], used.item)
                    }},
                    used.item + (used.rotate ? ' \u293E' : '')
                ];
            })
        ]
    ];
}
