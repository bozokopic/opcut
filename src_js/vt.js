import r from '@hat-open/renderer';
import * as u from '@hat-open/util';

import * as common from './common';
import * as dragger from './dragger';


export function main() {
    return ['div.main',
        leftPanel(),
        leftPanelResizer(),
        centerPanel(),
        rightPanelResizer(),
        rightPanel()
    ];
}


function leftPanelResizer() {
    return ['div.panel-resizer', {
        on: {
            mousedown: dragger.mouseDownHandler(evt => {
                const panel = evt.target.parentNode.querySelector('.left-panel');
                const width = panel.clientWidth;
                return (_, dx) => {
                    panel.style.width = `${width + dx}px`;
                };
            })
        }
    }];
}


function rightPanelResizer() {
    return ['div.panel-resizer', {
        on: {
            mousedown: dragger.mouseDownHandler(evt => {
                const panel = evt.target.parentNode.querySelector('.right-panel');
                const width = panel.clientWidth;
                return (_, dx) => {
                    panel.style.width = `${width - dx}px`;
                };
            })
        }
    }];
}


function leftPanel() {
    return ['div.left-panel',
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
            selectInput(r.get('form', 'method'),
                        [['forward_greedy', 'Forward greedy'],
                         ['greedy', 'Greedy']],
                        val => r.set(['form', 'method'], val)),
            ['label', 'Cut width'],
            numberInput(r.get('form', 'cut_width'),
                        u.isNumber,
                        val => r.set(['form', 'cut_width'], val)),
            ['label'],
            checkboxInput('Minimize initial panel usage',
                          r.get('form', 'min_initial_usage'),
                          val => r.set(['form', 'min_initial_usage'], val)),
            ['label'],
            checkboxInput('Use native implementation (experimental)',
                          r.get('form', 'native'),
                          val => r.set(['form', 'native'], val))
        ],
        ['div.content',
            leftPanelPanels(),
            leftPanelItems()
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


function leftPanelPanels() {
    const panelsPath = ['form', 'panels'];

    const panelNames = new Set();
    const nameValidator = name => {
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
                r.get(panelsPath).map((panel, index) => ['tr',
                    ['td.col-name',
                        ['div',
                            textInput(panel.name,
                                      nameValidator,
                                      val => r.set([panelsPath, index, 'name'], val))
                        ]
                    ],
                    ['td.col-quantity',
                        ['div',
                            numberInput(panel.quantity,
                                        u.isInteger,
                                        val => r.set([panelsPath, index, 'quantity'], val))
                        ]
                    ],
                    ['td.col-height',
                        ['div',
                            numberInput(panel.height,
                                        u.isNumber,
                                        val => r.set([panelsPath, index, 'height'], val))
                        ]
                    ],
                    ['td.col-width',
                        ['div',
                            numberInput(panel.width,
                                        u.isNumber,
                                        val => r.set([panelsPath, index, 'width'], val))
                        ]
                    ],
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: _ => r.change(panelsPath, u.omit(index))
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


function leftPanelItems() {
    const itemsPath = ['form', 'items'];

    const itemNames = new Set();
    const nameValidator = name => {
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
                r.get(itemsPath).map((item, index) => ['tr',
                    ['td.col-name',
                        ['div',
                            textInput(item.name,
                                      nameValidator,
                                      val => r.set([itemsPath, index, 'name'], val))
                        ]
                    ],
                    ['td.col-quantity',
                        ['div',
                            numberInput(item.quantity,
                                        u.isInteger,
                                        val => r.set([itemsPath, index, 'quantity'], val))
                        ]
                    ],
                    ['td.col-height',
                        ['div',
                            numberInput(item.height,
                                        u.isNumber,
                                        val => r.set([itemsPath, index, 'height'], val))
                        ]
                    ],
                    ['td.col-width',
                        ['div',
                            numberInput(item.width,
                                        u.isNumber,
                                        val => r.set([itemsPath, index, 'width'], val))
                        ]
                    ],
                    ['td.col-rotate',
                        ['div',
                            checkboxInput(null,
                                          item.can_rotate,
                                          val => r.set([itemsPath, index, 'can_rotate'], val))
                        ]
                    ],
                    ['td.col-delete',
                        ['button', {
                            on: {
                                click: _ => r.change(itemsPath, u.omit(index))
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


function rightPanel() {
    const result = r.get('result');
    return ['div.right-panel', (!result ?
        [] :
        [
            ['div.toolbar',
                ['button', {
                    on: {
                        click: common.generateOutput
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


function textInput(value, validator, onChange) {
    return ['input', {
        props: {
            type: 'text',
            value: value
        },
        class: {
            invalid: validator && !validator(value)
        },
        on: {
            change: evt => onChange(evt.target.value)
        }
    }];
}


function numberInput(value, validator, onChange) {

    return ['input', {
        props: {
            type: 'number',
            value: value
        },
        class: {
            invalid: validator && !validator(value)
        },
        on: {
            change: evt => onChange(evt.target.valueAsNumber)
        }
    }];
}


function checkboxInput(label, value, onChange) {
    const input = ['input', {
        props: {
            type: 'checkbox',
            checked: value
        },
        on: {
            change: evt => onChange(evt.target.checked)
        }
    }];

    if (!label)
        return input;

    return ['label',
        input,
        ` ${label}`
    ];
}


function selectInput(selected, values, onChange) {
    return ['select', {
        on: {
            change: evt => onChange(evt.target.value)
        }},
        values.map(([value, label]) => ['option', {
            props: {
                selected: value == selected,
                value: value
            }},
            label
        ])
    ];
}
