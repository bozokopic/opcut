import * as u from '@hat-open/util';


export function text(
    value: string,
    validator: ((val: string) => boolean) | null,
    onChange: (val: string) => void
): u.VNode {
    return ['input', {
        props: {
            type: 'text',
            value: value
        },
        class: {
            invalid: validator && !validator(value)
        },
        on: {
            change: (evt: Event) => onChange((evt.target as HTMLInputElement).value)
        }
    }];
}


export function number(
    value: number,
    validator: ((val: number) => boolean) | null,
    onChange: (val: number) => void
): u.VNode {
    return ['input', {
        props: {
            type: 'number',
            value: value
        },
        class: {
            invalid: validator && !validator(value)
        },
        on: {
            change: (evt: Event) => onChange((evt.target as HTMLInputElement).valueAsNumber)
        }
    }];
}


export function checkbox(
    label: string | null,
    value: boolean,
    onChange: (val: boolean) => void
): u.VNode {
    const input: u.VNode = ['input', {
        props: {
            type: 'checkbox',
            checked: value
        },
        on: {
            change: (evt: Event) => onChange((evt.target as HTMLInputElement).checked)
        }
    }];

    if (!label)
        return input;

    return ['label',
        input,
        ` ${label}`
    ];
}


export function select(
    selected: string,
    values: [string, string][],
    onChange: (val: string) => void
): u.VNode {
    return ['select', {
        on: {
            change: (evt: Event) => onChange((evt.target as HTMLSelectElement).value)
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


export function color(
    value: string,
    onChange: (val: string) => void
): u.VNode {
    return ['input', {
        props: {
            type: 'color',
            value: value
        },
        on: {
            change: (evt: Event) => onChange((evt.target as HTMLInputElement).value)
        }
    }];
}
