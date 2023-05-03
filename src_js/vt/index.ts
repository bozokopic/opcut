import * as u from '@hat-open/util';

import * as params from './params';
import * as result from './result';
import * as svg from './svg';


export function main(): u.VNode {
    return ['div.main',
        ['div.left-panel', params.main()],
        leftPanelResizer(),
        ['div.center-panel', svg.main() ?? []],
        rightPanelResizer(),
        ['div.right-panel', result.main()]
    ];
}


function leftPanelResizer(): u.VNode {
    return ['div.panel-resizer', {
        on: {
            mousedown: u.draggerMouseDownHandler(evt => {
                const panel = (evt.target as HTMLElement).parentNode?.querySelector('.left-panel') as HTMLElement | null;
                if (panel == null)
                    return () => {};  // eslint-disable-line
                const width = panel.clientWidth;
                return (_, dx) => {
                    panel.style.width = `${width + dx}px`;
                };
            })
        }
    }];
}


function rightPanelResizer(): u.VNode {
    return ['div.panel-resizer', {
        on: {
            mousedown: u.draggerMouseDownHandler(evt => {
                const panel = (evt.target as HTMLElement).parentNode?.querySelector('.right-panel') as HTMLElement | null;
                if (panel == null)
                    return () => {};  // eslint-disable-line
                const width = panel.clientWidth;
                return (_, dx) => {
                    panel.style.width = `${width - dx}px`;
                };
            })
        }
    }];
}
