import h from 'hyperscript';
import FileSaver from 'file-saver';

import * as u from '@hat-core/util';


export function loadText(ext) {
    const el = h('input', {
        style: 'display: none',
        type: 'file',
        accept: ext});
    const promise = new Promise(resolve => {
        el.addEventListener('change', evt => {
            const file = u.get(['files', 0], evt.target);
            if (!file)
                return;
            const fileReader = new FileReader();
            fileReader.onload = () => {
                const data = fileReader.result;
                resolve(data);
            };
            fileReader.readAsText(file);
        });
        el.click();
    });
    return promise;
}


export function saveText(text, fileName) {
    const blob = stringToBlob(text);
    FileSaver.saveAs(blob, fileName);
}


export function saveB64Data(b64Data, fileName) {
    const blob = b64ToBlob(b64Data);
    FileSaver.saveAs(blob, fileName);
}


function stringToBlob(strData, contentType) {
    contentType = contentType || '';
    return new Blob([strData], {type: contentType});
}


// http://stackoverflow.com/a/16245768
function b64ToBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}
