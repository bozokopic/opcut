// @ts-ignore
import Papa from 'papaparse';


export async function decode<TKey extends string>(
    blob: Blob,
    header: Record<TKey, (val: string) => any>
): Promise<Record<TKey, any>[]> {
    const data = await new Promise(resolve => {
        Papa.parse(blob, {
            header: true,
            complete: (result: any) => resolve(result.data)
        });
    }) as Record<string, string>[];

    const result: Record<TKey, any>[] = [];
    for (const i of data) {
        let element = {} as Record<TKey, any> | null;
        for (const [k, v] of Object.entries(header)) {
            if (!(k in i)) {
                element = null;
                break;
            }
            (element as any)[k] = (v as any)(i[k]);
        }
        if (element)
            result.push(element);
    }
    return result;
}


export function encode(data: Record<string, any>[]): Blob  {
    const csvData = Papa.unparse(data);
    return new Blob([csvData], {type: 'text/csv'});
}
