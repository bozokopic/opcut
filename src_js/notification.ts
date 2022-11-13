import iziToast from 'izitoast';


export function show(type: string, message: string) {
    const fn = (type == 'success' ? iziToast.success : iziToast.error);
    fn.apply(iziToast, [{message: message}]);
}
