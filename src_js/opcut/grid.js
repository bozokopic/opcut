import Papa from 'papaparse';

import r from 'opcut/renderer';
import * as u from 'opcut/util';
import * as ev from 'opcut/ev';


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
                        type: 'text',
                        'ev-change': (evt) => r.set([gridPath, 'items', rowIndex, column],
                                                    evt.target.value),
                        'ev-blur': _ => {
                            if (u.equals(gridState.selectedItem, [rowIndex, column]))
                                r.set([gridPath, 'selectedItem'], null);
                        },
                        'ev-keyup': (evt) => {
                            switch (evt.key) {
                                case 'Enter':
                                    evt.target.blur();
                                    break;
                                case 'Escape':
                                    evt.target.value = u.get(column, row);
                                    evt.target.blur();
                                    break;
                            }
                        },
                        value: content
                    }];
                }
            }
            const title = (validator ? validator(u.get(column, row), row) : null);
            return ['td' + (title ? '.invalid' : ''), {
                title: (title ? title : ''),
                'ev-click': evt => {
                    if (u.equals(gridState.selectedItem, [rowIndex, column]))
                        return;
                    ev.one(r, 'render', () => {
                        if (evt.target.firstChild && evt.target.firstChild.focus)
                            evt.target.firstChild.focus();
                    });
                    r.set([gridPath, 'selectedItem'], [rowIndex, column]);
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
                colSpan: colspan},
                ['div',
                    ['button', {
                        'ev-click': () => r.change(itemsPath, u.append(newItem))},
                        ['span.fa.fa-plus'],
                        ' Add'
                    ],
                    ['span.spacer'],
                    ['button', {
                        'ev-click': () => r.set(itemsPath, [])},
                        ['span.fa.fa-trash-o'],
                        ' Remove all'
                    ],
                    (!csvColumns ?
                        [] :
                        [
                            ['button', {
                                'ev-click': () => {
                                    const items = importCsv(csvColumns, newItem);
                                    if (!items)
                                        return;
                                    r.change(itemsPath, state => state.concat(items));
                                }},
                                ['span.fa.fa-download'],
                                ' Import from CSV'
                            ],
                            ['button', {
                                'ev-click': () => exportCsv(r.get(itemsPath), csvColumns)},
                                ['span.fa.fa-upload'],
                                ' Export to CSV'
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


export function deleteColumn(gridPath, showUpDown, onDeleteCb) {
    const itemsPath = [gridPath, 'items'];
    return (i, index) => [
        (!showUpDown ? [] : [
            ['button', {
                'ev-click': () => {
                    const gridState = r.get(gridPath);
                    if (index < 1)
                        return;
                    r.change(itemsPath, u.pipe(
                        u.set(index, gridState.items[index-1]),
                        u.set(index-1, i)
                    ));
                }},
                ['span.fa.fa-arrow-up']
            ],
            ['button', {
                'ev-click': () => {
                    const gridState = r.get(gridPath);
                    if (index > gridState.items.length - 2)
                        return;
                    r.change(itemsPath, u.pipe(
                        u.set(index, gridState.items[index+1]),
                        u.set(index+1, i)
                    ));
                }},
                ['span.fa.fa-arrow-down']
            ]
        ]),
        ['button', {
            'ev-click': () => {
                const item = r.get(itemsPath, index);
                r.change(itemsPath, u.omit(index));
                if (onDeleteCb)
                    onDeleteCb(item);
            }},
            ['span.fa.fa-minus']
        ]
    ];
}


export function checkboxColumn(gridPath, column) {
    return (i, index) => {
        const columnPath = [gridPath, 'items', index, column];
        return ['div', {
            style: 'text-align: center'},
            ['input', {
                type: 'checkbox',
                'ev-change': (evt) => r.set(columnPath, evt.target.checked),
                checked: r.get(columnPath)}
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
            title: (invalid ? 'invalid value' : ''),
            style: 'width: 100%',
            'ev-change': (evt) => r.set(columnPath, evt.target.value)},
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
        return items;
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
