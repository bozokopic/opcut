import r from 'opcut/renderer';
import * as u from 'opcut/util';
import * as grid from 'opcut/grid';
import * as common from 'opcut/common';
import * as states from 'opcut/states';
import * as validators from 'opcut/validators';


export function main() {
    return ['div.window',
        leftPanel(),
        ['div.center-panel'],
        ['div.right-panel']
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
    const widthValidator = validators.dimensionValidator;
    const heightValidator = validators.dimensionValidator;
    const csvColumns = grid.createStringCsvColumns('name', 'width', 'height');
    return ['div',
        ['table.grid',
            ['thead',
                ['tr',
                    ['th', 'Panel name'],
                    ['th.fixed', 'Width'],
                    ['th.fixed', 'Height'],
                    ['th.fixed']
                ]
            ],
            grid.tbody(panelsPath,
                       ['name', 'width', 'height', deleteColumn],
                       [nameValidator, widthValidator, heightValidator]),
            grid.tfoot(panelsPath, 4, states.panelsItem, csvColumns)
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
    const widthValidator = validators.dimensionValidator;
    const heightValidator = validators.dimensionValidator;
    const csvColumns =  u.merge(
        grid.createStringCsvColumns('name', 'width', 'height'),
        grid.createBooleanCsvColumns('can_rotate'));
    return ['div',
        ['table.grid',
            ['thead',
                ['tr',
                    ['th', 'Item name'],
                    ['th.fixed', 'Width'],
                    ['th.fixed', 'Height'],
                    ['th.fixed', 'Rotate'],
                    ['th.fixed']
                ]
            ],
            grid.tbody(itemsPath,
                       ['name', 'width', 'height', rotateColumn, deleteColumn],
                       [nameValidator, widthValidator, heightValidator]),
            grid.tfoot(itemsPath, 5, states.itemsItem, csvColumns)
        ]
    ];
}
