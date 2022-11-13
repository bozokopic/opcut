import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from '../common';

import * as input from './input';


export function main(): u.VNodeChild[] {
    return [
        ['div.header',
            ['span.title', 'OPCUT'],
            ['a.github', {
                props: {
                    title: 'GitHub',
                    href: 'https://github.com/bozokopic/opcut'
                }},
                ['span.fa.fa-github']
            ]
        ],
        ['div.form',
            ['label', 'Method'],
            input.select(
                r.get('form', 'method') as string,
                [['forward_greedy', 'Forward greedy'],
                 ['greedy', 'Greedy'],
                 ['forward_greedy_native', 'Forward greedy (native)'],
                 ['greedy_native', 'Greedy (native)']],
                val => r.set(['form', 'method'], val)
            ),
            ['label', 'Cut width'],
            input.number(
                r.get('form', 'cut_width') as number,
                u.isNumber,
                val => r.set(['form', 'cut_width'], val)
            ),
            ['label'],
            input.checkbox(
                'Minimize initial panel usage',
                r.get('form', 'min_initial_usage') as boolean,
                val => r.set(['form', 'min_initial_usage'], val)
            )
        ],
        ['div.content',
            panels(),
            items()
        ],
        ['button.calculate', {
            props: {
                disabled: r.get('calculating')
            },
            on: {
                click: common.calculate
            }},
            'Calculate'
        ]
    ];
}


function panels(): u.VNode {
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
                    ['th.col-name', 'Panel name'],
                    ['th.col-quantity', 'Quantity'],
                    ['th.col-height', 'Height'],
                    ['th.col-width', 'Width'],
                    ['th.col-delete']
                ]
            ],
            ['tbody',
                (r.get(panelsPath) as common.FormPanel[]).map((panel, index) => ['tr',
                    ['td.col-name',
                        ['div',
                            input.text(
                                panel.name,
                                nameValidator,
                                val => r.set([panelsPath, index, 'name'], val)
                            )
                        ]
                    ],
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
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: () => r.change(panelsPath, u.omit(index))
                            }},
                            ['span.fa.fa-minus']
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
                                ['span.fa.fa-plus'],
                                ' Add'
                            ],
                            ['span.spacer'],
                            ['button', {
                                on: {
                                    click: common.csvImportPanels
                                }},
                                ['span.fa.fa-download'],
                                ' CSV Import'
                            ],
                            ['button', {
                                on: {
                                    click: common.csvExportPanels
                                }},
                                ['span.fa.fa-upload'],
                                ' CSV Export'
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
}


function items(): u.VNode {
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
                    ['th.col-name', 'Item name'],
                    ['th.col-quantity', 'Quantity'],
                    ['th.col-height', 'Height'],
                    ['th.col-width', 'Width'],
                    ['th.col-rotate', 'Rotate'],
                    ['th.col-delete']
                ]
            ],
            ['tbody',
                (r.get(itemsPath) as common.FormItem[]).map((item, index) => ['tr',
                    ['td.col-name',
                        ['div',
                            input.text(
                                item.name,
                                nameValidator,
                                val => r.set([itemsPath, index, 'name'], val)
                            )
                        ]
                    ],
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
                    ['td.col-rotate',
                        ['div',
                            input.checkbox(
                                null,
                                item.can_rotate,
                                val => r.set([itemsPath, index, 'can_rotate'], val)
                            )
                        ]
                    ],
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: () => r.change(itemsPath, u.omit(index))
                            }},
                            ['span.fa.fa-minus']
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
                                ['span.fa.fa-plus'],
                                ' Add'
                            ],
                            ['span.spacer'],
                            ['button', {
                                on: {
                                    click: common.csvImportItems
                                }},
                                ['span.fa.fa-download'],
                                ' CSV Import'
                            ],
                            ['button', {
                                on: {
                                    click: common.csvExportItems
                                }},
                                ['span.fa.fa-upload'],
                                ' CSV Export'
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
}
