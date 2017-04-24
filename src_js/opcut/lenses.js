import R from 'ramda';


export const index = R.lensIndex;

export const prop = R.lensProp;

export function path(...xs) {
    return R.reduce((acc, i) => R.compose(acc, pathParamToLens(i)),
                    R.identity, xs);
}

function pathParamToLens(x) {
    switch (typeof(x)) {
        case 'function': return x;
        case 'number': return index(x);
        case 'string': return prop(x);
        case 'object': if (Array.isArray(x)) return R.apply(path, x);
    }
    throw 'Invalid path parameter';
}
