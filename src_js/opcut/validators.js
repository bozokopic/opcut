import * as u from '@hat-core/util';


export function notEmptyValidator(value) {
    if (!value)
        return 'invalid value';
}


export function floatValidator(value) {
    const floatValue = u.strictParseFloat(value);
    if (!Number.isFinite(floatValue))
        return 'not valid number';
}


export function integerValidator(value) {
    const intValue = u.strictParseInt(value);
    if (!Number.isFinite(intValue))
        return 'not valid number';
}


export function tcpPortValidator(value) {
    const intValue = u.strictParseInt(value);
    if (!Number.isFinite(intValue) || intValue < 0 || intValue > 0xFFFF)
        return 'not valid TCP port';
}


export function createChainValidator(...validators) {
    return value => {
        for (let validator of validators) {
            let result = validator(value);
            if (result)
                return result;
        }
    };
}


export function createUniqueValidator() {
    const values = new Set();
    return value => {
        if (values.has(value))
            return 'duplicate value';
        values.add(value);
    };
}


export function dimensionValidator(value) {
    const floatValue = u.strictParseFloat(value);
    if (!Number.isFinite(floatValue) || floatValue <= 0)
        return 'not valid dimension';
}


export function quantityValidator(value) {
    const intValue = u.strictParseInt(value);
    if (!Number.isFinite(intValue) || intValue < 1)
        return 'not valid quantity';
}
