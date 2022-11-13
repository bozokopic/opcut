

export function load(ext: string): Promise<File | null> {
    const el = document.createElement('input');
    (el as any).style = 'display: none';
    el.type = 'file';
    el.accept = ext;
    document.body.appendChild(el);

    return new Promise<File | null>(resolve => {
        const listener = (evt: Event) => {
            const f = (evt.target as HTMLInputElement).files?.[0] ?? null;
            document.body.removeChild(el);
            resolve(f);
        };
        el.addEventListener('change', listener);
        // TODO blur not fired on close???
        el.addEventListener('blur', listener);
        el.click();
    });
}


export function save(f: File) {
    const a = document.createElement('a');
    a.download = f.name;
    a.rel = 'noopener';
    a.href = URL.createObjectURL(f);
    setTimeout(() => { URL.revokeObjectURL(a.href); }, 20000);
    setTimeout(() => { a.click(); }, 0);
}
