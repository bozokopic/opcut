// @ts-ignore
import Papa from 'papaparse';


export async function decode<T extends Record<string, any>>(
    blob: Blob,
    header: {
        [TKey in keyof T]: (val: string) => T[TKey]
    }
): Promise<T[]> {
    const data = await new Promise(resolve => {
        Papa.parse(blob, {
            header: true,
            complete: (result: any) => resolve(result.data)
        });
    }) as Record<string, string>[];

    const decodeElement = (row: Record<string, string>) => {
        const element: any = {};
        for (const key in header) {
            if (!(key in row))
                return null;
            element[key] = header[key](row[key]);
        }
        return element as T;
    };

    const elements: T[] = [];
    for (const row of data) {
        const element = decodeElement(row);
        if (!element)
            continue;

        elements.push(element);
    }

    return elements;
}


export function encode(data: Record<string, any>[]): Blob  {
    const csvData = Papa.unparse(data);
    return new Blob([csvData], {type: 'text/csv'});
}
