import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common.js';

import * as input from './input.js';


export function main(): u.VNodeChild {
    const state = common.getState();
    const dict = common.getDict();

    return [
        ['div.header',
            ['span.title', 'OPCUT'],
            ['button', {
                on: {
                    click: () => r.set('showSettings', true)
                }},
                icon('applications-other'),
                ` ${dict.settings}`
            ],
            ['button', {
                on: {
                    click: () => window.open(
                        'https://github.com/bozokopic/opcut',
                        '_blank'
                    )
                }},
                icon('emblem-git-new'),
                ` ${dict.source_code}`
            ]
        ],
        ['div.form',
            ['label.label', dict.method],
            input.select(
                state.form.method,
                Object.entries(common.methods),
                val => r.set(['form', 'method'], val)
            ),
            ['label.label', dict.cut_width],
            input.number(
                state.form.cutWidth,
                u.isNumber,
                val => r.set(['form', 'cutWidth'], val)
            ),
            ['label.label'],
            input.checkbox(
                dict.minimize_initial_panel_usage,
                state.form.minInitialUsage,
                val => r.set(['form', 'minInitialUsage'], val)
            )
        ],
        ['div.content',
            panels(),
            items()
        ],
        ['button.calculate', {
            props: {
                disabled: state.calculating
            },
            on: {
                click: common.calculate
            }},
            icon('system-run'),
            ` ${dict.calculate}`
        ]
    ];
}


function panels(): u.VNode {
    const state = common.getState();
    const dict = common.getDict();

    const panelsPath = ['form', 'panels'];

    const panelNames = new Set<string>();
    const nameValidator = (name: string) => {
        const valid = !panelNames.has(name);
        panelNames.add(name);
        return valid;
    };

    return ['div',
        ['table',
            ['thead',
                ['tr',
                    ['th.col-quantity', dict.quantity],
                    ['th.col-height', dict.height],
                    ['th.col-width', dict.width],
                    ['th.col-name', dict.panel_name],
                    ['th.col-delete']
                ]
            ],
            ['tbody',
                state.form.panels.map((panel, index) => ['tr',
                    ['td.col-quantity',
                        ['div',
                            input.number(
                                panel.quantity,
                                u.isInteger,
                                val => r.set([panelsPath, index, 'quantity'], val)
                            )
                        ]
                    ],
                    ['td.col-height',
                        ['div',
                            input.number(
                                panel.height,
                                u.isNumber,
                                val => r.set([panelsPath, index, 'height'], val)
                            )
                        ]
                    ],
                    ['td.col-width',
                        ['div',
                            input.number(
                                panel.width,
                                u.isNumber,
                                val => r.set([panelsPath, index, 'width'], val)
                            )
                        ]
                    ],
                    ['td.col-name',
                        ['div',
                            input.text(
                                panel.name,
                                nameValidator,
                                val => r.set([panelsPath, index, 'name'], val)
                            )
                        ]
                    ],
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: () => r.change(panelsPath, u.omit(index))
                            }},
                            icon('list-remove')
                        ]
                    ]
                ])
            ],
            ['tfoot',
                ['tr',
                    ['td', {
                        props: {
                            colSpan: 5
                        }},
                        ['div',
                            ['button', {
                                on: {
                                    click: common.addPanel
                                }},
                                icon('list-add'),
                                ` ${dict.add_panel}`
                            ],
                            ['span.spacer'],
                            ['button', {
                                on: {
                                    click: common.csvImportPanels
                                }},
                                icon('document-import'),
                                ` ${dict.csv_import}`
                            ],
                            ['button', {
                                on: {
                                    click: common.csvExportPanels
                                }},
                                icon('document-export'),
                                ` ${dict.csv_export}`
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
}


function items(): u.VNode {
    const state = common.getState();
    const dict = common.getDict();

    const itemsPath = ['form', 'items'];

    const itemNames = new Set<string>();
    const nameValidator = (name: string) => {
        const valid = !itemNames.has(name);
        itemNames.add(name);
        return valid;
    };

    return ['div',
        ['table',
            ['thead',
                ['tr',
                    ['th.col-quantity', dict.quantity],
                    ['th.col-height', dict.height],
                    ['th.col-width', dict.width],
                    ['th.col-name', dict.item_name],
                    ['th.col-rotate', dict.rotate],
                    ['th.col-delete']
                ]
            ],
            ['tbody',
                state.form.items.map((item, index) => ['tr',
                    ['td.col-quantity',
                        ['div',
                            input.number(
                                item.quantity,
                                u.isInteger,
                                val => r.set([itemsPath, index, 'quantity'], val)
                            )
                        ]
                    ],
                    ['td.col-height',
                        ['div',
                            input.number(
                                item.height,
                                u.isNumber,
                                val => r.set([itemsPath, index, 'height'], val)
                            )
                        ]
                    ],
                    ['td.col-width',
                        ['div',
                            input.number(
                                item.width,
                                u.isNumber,
                                val => r.set([itemsPath, index, 'width'], val)
                            )
                        ]
                    ],
                    ['td.col-name',
                        ['div',
                            input.text(
                                item.name,
                                nameValidator,
                                val => r.set([itemsPath, index, 'name'], val)
                            )
                        ]
                    ],
                    ['td.col-rotate',
                        ['div',
                            input.checkbox(
                                null,
                                item.canRotate,
                                val => r.set([itemsPath, index, 'canRotate'], val)
                            )
                        ]
                    ],
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: () => r.change(itemsPath, u.omit(index))
                            }},
                            icon('list-remove')
                        ]
                    ]
                ])
            ],
            ['tfoot',
                ['tr',
                    ['td', {
                        props: {
                            colSpan: 6
                        }},
                        ['div',
                            ['button', {
                                on: {
                                    click: common.addItem
                                }},
                                icon('list-add'),
                                ` ${dict.add_item}`
                            ],
                            ['span.spacer'],
                            ['button', {
                                on: {
                                    click: common.csvImportItems
                                }},
                                icon('document-import'),
                                ` ${dict.csv_import}`
                            ],
                            ['button', {
                                on: {
                                    click: common.csvExportItems
                                }},
                                icon('document-export'),
                                ` ${dict.csv_export}`
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
}


function icon(name: string): u.VNode {
    return ['img.icon', {
        props: {
            src: `icons/${name}.svg`
        }
    }];
}
