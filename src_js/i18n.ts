
const en = {
    server_error: 'Server error',
    invalid_cut_width: 'Invalid cut width',
    invalid_panel_name: 'Invalid panel name',
    invalid_item_name: 'Invalid item name',
    invalid_quantity: 'Invalid quantity',
    invalid_height: 'Invalid height',
    invalid_width: 'Invalid width',
    duplicate_name: 'Duplicate name',
    no_panels_defined: 'No panels defined',
    no_items_defined: 'No items defined',
    panel: 'Panel',
    item: 'Item',
    settings: 'Settings',
    source_code: 'Source code',
    method: 'Method',
    cut_width: 'Cut width',
    minimize_initial_panel_usage: 'Minimize initial panel usage',
    calculate: 'Calculate',
    quantity: 'Quantity',
    height: 'Height',
    width: 'Width',
    panel_name: 'Panel name',
    item_name: 'Item name',
    rotate: 'Rotate',
    add_panel: 'Add panel',
    add_item: 'Add item',
    csv_import: 'CSV import',
    csv_export: 'CSV export',
    export: 'Export',
    font_size: 'Font size',
    small: 'Small',
    medium: 'Medium',
    large: 'Large',
    show_names: 'Show names',
    show_dimensions: 'Show dimensions',
    cut_area: 'Cut area',
    version: 'Version',
    language: 'Language',
    result_colors: 'Result colors',
    cut: 'Cut',
    selected: 'Selected',
    unused: 'Unused',
    default_panel_values: 'Default panel values',
    default_item_values: 'Default item values',
    name: 'Name'
} as const;


const hr = {
    server_error: 'Pogreška poslužitelja',
    invalid_cut_width: 'Pogrešna širina reza',
    invalid_panel_name: 'Pogrešan naziv ploče',
    invalid_item_name: 'Pogrešan naziv elementa',
    invalid_quantity: 'Pogrešna količina',
    invalid_height: 'Pogrešna visina',
    invalid_width: 'Pogrešna širina',
    duplicate_name: 'Višestruko ime',
    no_panels_defined: 'Nepostojeće ploče',
    no_items_defined: 'Nepostojeći elementi',
    panel: 'Ploča',
    item: 'Element',
    settings: 'Postavke',
    source_code: 'Izvorni kod',
    method: 'Metoda',
    cut_width: 'Širina reza',
    minimize_initial_panel_usage: 'Optimiraj upotrebu početnih ploca',
    calculate: 'Izračunaj',
    quantity: 'Količina',
    height: 'Visina',
    width: 'Širina',
    panel_name: 'Naziv ploče',
    item_name: 'Naziv elementa',
    rotate: 'Zakreni',
    add_panel: 'Dodaj ploču',
    add_item: 'Dodaj element',
    csv_import: 'CSV uvoz',
    csv_export: 'CSV izvoz',
    export: 'Izvoz',
    font_size: 'Veličina slova',
    small: 'Mala',
    medium: 'Srednja',
    large: 'Velika',
    show_names: 'Prikaži nazive',
    show_dimensions: 'Prikaži veličine',
    cut_area: 'Površina reza',
    version: 'Inačica',
    language: 'Jezik',
    result_colors: 'Bojanje rezultata',
    cut: 'Rez',
    selected: 'Označen',
    unused: 'Nekorišten',
    default_panel_values: 'Inicijalne vrijednosti ploča',
    default_item_values: 'Inicijalne vrijednosti elemenata',
    name: 'Naziv'
} as const;


export const langs = {
    en: 'English',
    hr: 'Hrvatski'
} as const;

export type Lang = keyof (typeof langs);

export type Labels = (
    keyof (typeof en) |
    keyof (typeof hr)
);

export type Dict = Record<Labels, string>;

export const dicts: Record<Lang, Dict> = {
    en,
    hr
} as const;
