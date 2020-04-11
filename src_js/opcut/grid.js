import Papa from 'papaparse';

import r from '@hat-core/renderer';
import * as u from '@hat-core/util';

import * as fs from 'opcut/fs';


export const state = {
    items: [],
    selectedItem: null
};


export function clearState(state) {
    return u.set('selectedItem', null, state);
}


export function tbody(gridPath, columns, validators) {
    const gridState = r.get(gridPath);
    return ['tbody', gridState.items.map((row, rowIndex) =>
        ['tr', u.zip(columns || [], validators || []).map(([column, validator]) => {
            let content = '';
            if (typeof column == 'function') {
                content = column(row, rowIndex);
            } else {
                const selected = u.equals(gridState.selectedItem, [rowIndex, column]);
                content = u.get(column, row);
                if (typeof content == 'boolean') {
                    content = checkboxColumn(gridPath, column)(row, rowIndex);
                } else if (selected) {
                    content = ['input.grid-input', {
                        props: {
                            type: 'text',
                            value: content
                        },
                        on: {
                            change: evt => r.set([gridPath, 'items', rowIndex, column],
                                                 evt.target.value),
                            blur: _ => {
                                if (u.equals(gridState.selectedItem, [rowIndex, column]))
                                    r.set([gridPath, 'selectedItem'], null);
                            },
                            keyup: evt => {
                                switch (evt.key) {
                                    case 'Enter':
                                        evt.target.blur();
                                        break;
                                    case 'Escape':
                                        evt.target.value = u.get(column, row);
                                        evt.target.blur();
                                        break;
                                }
                            }
                        }}
                    ];
                }
            }
            const title = (validator ? validator(u.get(column, row), row) : null);
            return ['td' + (typeof column == 'function' ? '' : '.grid-col-' + column), {
                class: {
                    invalid: title
                },
                props: {
                    title: (title ? title : '')
                },
                on: {
                    click: evt => {
                        if (u.equals(gridState.selectedItem, [rowIndex, column]))
                            return;
                        r.set([gridPath, 'selectedItem'], [rowIndex, column]);
                        r.render();
                        if (evt.target.firstChild && evt.target.firstChild.focus)
                            evt.target.firstChild.focus();
                    }
                }},
                content];
        })]
    )];
}


export function tfoot(gridPath, colspan, newItem, csvColumns) {
    const itemsPath = [gridPath, 'items'];
    return ['tfoot',
        ['tr',
            ['td', {
                props: {
                    colSpan: colspan
                }},
                ['div',
                    ['button', {
                        on: {
                            click: () => r.change(itemsPath, u.append(newItem))
                        }},
                        ['span.fa.fa-plus'],
                        ' Add'
                    ],
                    ['span.spacer'],
                    (!csvColumns ?
                        [] :
                        [
                            ['button', {
                                on: {
                                    click: () => {
                                        importCsv(csvColumns, newItem).then(items => {
                                            r.change(itemsPath, state => state.concat(items));
                                        });
                                    }
                                }},
                                ['span.fa.fa-download'],
                                ' CSV Import'
                            ],
                            ['button', {
                                on: {
                                    click: () => exportCsv(r.get(itemsPath), csvColumns)
                                }},
                                ['span.fa.fa-upload'],
                                ' CSV Export'
                            ]
                        ]
                    )
                ]
            ]
        ]
    ];
}


export function createStringCsvColumns(...columns) {
    return u.pipe(
        u.map(i => [i, {
            toString: u.get(i),
            toItem: u.set(i)
        }]),
        u.fromPairs
    )(columns);
}


export function createBooleanCsvColumns(...columns) {
    return u.pipe(
        u.map(i => [i, {
            toString: u.pipe(u.get(i), x => x ? 'true' : 'false'),
            toItem: (x, acc) => u.set(i, x == 'true', acc)
        }]),
        u.fromPairs
    )(columns);
}


export function deleteColumn(gridPath, showUpDown, onDeleteCb) {
    const itemsPath = [gridPath, 'items'];
    return (i, index) => [
        (!showUpDown ? [] : [
            ['button', {
                on: {
                    click: () => {
                        const gridState = r.get(gridPath);
                        if (index < 1)
                            return;
                        r.change(itemsPath, u.pipe(
                            u.set(index, gridState.items[index-1]),
                            u.set(index-1, i)
                        ));
                    }
                }},
                ['span.fa.fa-arrow-up']
            ],
            ['button', {
                on: {
                    click: () => {
                        const gridState = r.get(gridPath);
                        if (index > gridState.items.length - 2)
                            return;
                        r.change(itemsPath, u.pipe(
                            u.set(index, gridState.items[index+1]),
                            u.set(index+1, i)
                        ));
                    }
                }},
                ['span.fa.fa-arrow-down']
            ]
        ]),
        ['button', {
            on: {
                click: () => {
                    const item = r.get(itemsPath, index);
                    r.change(itemsPath, u.omit(index));
                    if (onDeleteCb)
                        onDeleteCb(item);
                }
            }},
            ['span.fa.fa-minus']
        ]
    ];
}


export function checkboxColumn(gridPath, column) {
    return (i, index) => {
        const columnPath = [gridPath, 'items', index, column];
        return ['div', {
            props: {
                style: 'text-align: center'
            }},
            ['input', {
                props: {
                    type: 'checkbox',
                    checked: r.get(columnPath)
                },
                on: {
                    change: evt => r.set(columnPath, evt.target.checked)
                }}
            ]
        ];
    };
}


export function selectColumn(gridPath, column, values) {
    return (i, index) => {
        const columnPath = [gridPath, 'items', index, column];
        const selectedValue = r.get(columnPath);
        const invalid = values.find(
            i => u.equals(selectedValue, (u.isArray(i) ? i[0] : i))) === undefined;
        const allValues = (invalid ? u.append(selectedValue, values) : values);
        return ['select' + (invalid ? '.invalid' : ''), {
            class: {
                invalid: invalid
            },
            props: {
                title: (invalid ? 'invalid value' : ''),
                style: 'width: 100%'
            },
            on: {
                change: evt => r.set(columnPath, evt.target.value)
            }},
            allValues.map(i => {
                const value = (u.isArray(i) ? i[0] : i);
                const label = (u.isArray(i) ? i[1] : i);
                return ['option', {
                    selected: selectedValue == value,
                    value: value},
                    label
                ];
            })
        ];
    };
}


function importCsv(csvColumns, newItem) {
    return new Promise(resolve => {
        fs.loadText('csv').then(csvData => {
            const result = Papa.parse(csvData, {
                delimiter: ';',
                skipEmptyLines: true,
                header: true
            });
            const items = [];
            for (let i of result.data) {
                if (!Object.keys(i).every(k => u.contains(k, Object.keys(csvColumns))))
                    continue;
                const item = u.reduce(
                    (acc, [name, column]) => column.toItem(i[name], acc),
                    newItem,
                    u.toPairs(csvColumns));
                items.push(item);
            }
            resolve(items);
        });
    });
}


function exportCsv(items, csvColumns) {
    const csvData = Papa.unparse(
        items.map(item => u.map(column => column.toString(item))(csvColumns)), {
            delimiter: ';',
            skipEmptyLines: true,
            header: true});
    fs.saveText(csvData, 'data.csv');
}
