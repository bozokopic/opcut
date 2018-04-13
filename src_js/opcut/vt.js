import r from 'opcut/renderer';

import * as common from 'opcut/common';


export function main() {
    return ['div.window',
        leftPanel(),
        ['div.center-panel'],
        ['div.right-panel']
    ];
}


function leftPanel() {
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
                            selected: r.get('form', 'method') == method
                        }},
                        method
                    ])
            ]
        ],
        ['div.group',
            ['label', 'Cut width'],
            ['input', {
                props: {
                    value: r.get('form', 'cut_width')
                },
                on: {
                    change: evt => r.set(['form', 'cut_width'], evt.target.value)
                }}
            ]
        ],
        ['div.list',
            ['label', 'Panels'],
            ['div.content',
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br']
            ],
            ['button.add', {
                on: {
                    click: common.addPanel
                }},
                ['span.fa.fa-plus'],
                ' Add panel'
            ]
        ],
        ['div.list',
            ['label', 'Items'],
            ['div.content',
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br'],
                'sdfsdfssfd', ['br']
            ],
            ['button.add', {
                on: {
                    click: common.addItem
                }},
                ['span.fa.fa-plus'],
                ' Add item'
            ]
        ],
        ['button.submit', {
            on: {
                click: common.submit
            }},
            'Calculate'
        ]
    ];
}
