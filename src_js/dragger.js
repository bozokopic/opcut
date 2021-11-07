

const draggers = [];


export function mouseDownHandler(createMoveHandlerCb) {
    return evt => {
        draggers.push({
            initX: evt.screenX,
            initY: evt.screenY,
            moveHandler: createMoveHandlerCb(evt)
        });
    };
}


document.addEventListener('mousemove', evt => {
    for (let dragger of draggers) {
        const dx = evt.screenX - dragger.initX;
        const dy = evt.screenY - dragger.initY;
        dragger.moveHandler(evt, dx, dy);
    }
});


document.addEventListener('mouseup', evt => {
    draggers.splice(0);
});
