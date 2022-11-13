
type MouseHandler = (evt: MouseEvent) => void;

type MoveHandler = (evt: MouseEvent, dx: number, dy: number) => void;

type CreateMoveHandler = (evt: MouseEvent) => MoveHandler;

type Dragger = {
    initX: number,
    initY: number,
    moveHandler: MoveHandler;
}


const draggers: Dragger[] = [];


export function mouseDownHandler(
    createMoveHandlerCb: CreateMoveHandler
): MouseHandler {
    return evt => {
        draggers.push({
            initX: evt.screenX,
            initY: evt.screenY,
            moveHandler: createMoveHandlerCb(evt)
        });
    };
}


document.addEventListener('mousemove', evt => {
    for (const dragger of draggers) {
        const dx = evt.screenX - dragger.initX;
        const dy = evt.screenY - dragger.initY;
        dragger.moveHandler(evt, dx, dy);
    }
});


document.addEventListener('mouseup', () => {
    draggers.splice(0);
});
