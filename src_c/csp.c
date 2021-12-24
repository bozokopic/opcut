#include "csp.h"


#define FITNESS_K 0.03


typedef struct {
    size_t unused_initial_count;
    double fitness;
} fitness_t;


static void sort_panels(opcut_panel_t **first, opcut_panel_t **last) {
    if (!*first) {
        if (last)
            *last = NULL;
        return;
    }

    opcut_panel_t *pivot_first = *first;
    opcut_panel_t *pivot_last = *first;
    opcut_panel_t *left_first = NULL;
    opcut_panel_t *right_first = NULL;

    for (opcut_panel_t *panel = (*first)->next; panel;) {
        opcut_panel_t *next = panel->next;
        if (panel->area < pivot_first->area) {
            panel->next = left_first;
            left_first = panel;
        } else if (panel->area > pivot_first->area) {
            panel->next = right_first;
            right_first = panel;
        } else {
            pivot_last->next = panel;
            pivot_last = panel;
        }
        panel = next;
    }

    opcut_panel_t *left_last;
    opcut_panel_t *right_last;
    sort_panels(&left_first, &left_last);
    sort_panels(&right_first, &right_last);

    *first = (left_first ? left_first : pivot_first);
    if (left_last)
        left_last->next = pivot_first;
    pivot_last->next = right_first;
    if (last)
        *last = (right_last ? right_last : pivot_last);
}


static void sort_items(opcut_item_t **first, opcut_item_t **last) {
    if (!*first) {
        if (last)
            *last = NULL;
        return;
    }

    opcut_item_t *pivot_first = *first;
    opcut_item_t *pivot_last = *first;
    opcut_item_t *left_first = NULL;
    opcut_item_t *right_first = NULL;

    for (opcut_item_t *item = (*first)->next; item;) {
        opcut_item_t *next = item->next;
        if (item->area > pivot_first->area) {
            item->next = left_first;
            left_first = item;
        } else if (item->area < pivot_first->area) {
            item->next = right_first;
            right_first = item;
        } else {
            pivot_last->next = item;
            pivot_last = item;
        }
        item = next;
    }

    opcut_item_t *left_last;
    opcut_item_t *right_last;
    sort_items(&left_first, &left_last);
    sort_items(&right_first, &right_last);

    *first = (left_first ? left_first : pivot_first);
    if (left_last)
        left_last->next = pivot_first;
    pivot_last->next = right_first;
    if (last)
        *last = (right_last ? right_last : pivot_last);
}


static inline int compare_fitness(fitness_t *f1, fitness_t *f2) {
    return (f1->unused_initial_count == f2->unused_initial_count
                ? f1->fitness - f2->fitness
                : f1->unused_initial_count - f2->unused_initial_count);
}


static void calculate_fitness(opcut_result_t *result, fitness_t *fitness) {
    fitness->fitness = 0;

    for (opcut_panel_t *panel = result->params->panels; panel;
         panel = panel->next) {
        double min_used_area = 0;
        double used_areas = 0;
        for (opcut_used_t *used = result->used; used; used = used->next) {
            if (used->panel != panel)
                continue;
            if (min_used_area == 0 || used->item->area < min_used_area)
                min_used_area = used->item->area;
            used_areas = used->item->area;
        }

        double max_unused_area = 0;
        for (opcut_unused_t *unused = result->unused; unused;
             unused = unused->next) {
            if (unused->panel != panel)
                continue;
            if (max_unused_area == 0 || unused->area > max_unused_area)
                max_unused_area = unused->area;
        }

        fitness->fitness += (panel->area - used_areas) / result->panels_area;
        fitness->fitness -= FITNESS_K * min_used_area * max_unused_area /
                            (result->panels_area * result->panels_area);
    }

    fitness->unused_initial_count = 0;
    if (result->params->min_initial_usage) {
        for (opcut_unused_t *unused = result->unused; unused;
             unused = unused->next) {
            if (unused->initial)
                fitness->unused_initial_count += 1;
        }
    }
}


static int cut_item_from_unused(opcut_item_t *item, opcut_unused_t *unused,
                                bool rotate, double cut_width, bool vertical,
                                opcut_used_t *new_used,
                                opcut_unused_t *new_unused,
                                size_t *new_unused_len) {
    double item_width = (rotate ? item->height : item->width);
    double item_height = (rotate ? item->width : item->height);
    if (unused->height < item_height || unused->width < item_width)
        return OPCUT_UNSOLVABLE;

    new_used->panel = unused->panel;
    new_used->item = item;
    new_used->x = unused->x;
    new_used->y = unused->y;
    new_used->rotate = rotate;

    double width;
    double height;
    *new_unused_len = 0;

    width = unused->width - item_width - cut_width;
    if (width > 0) {
        height = (vertical ? unused->height : item_height);
        new_unused[(*new_unused_len)++] =
            (opcut_unused_t){.panel = unused->panel,
                             .width = width,
                             .height = height,
                             .x = unused->x + item_width + cut_width,
                             .y = unused->y,
                             .area = width * height,
                             .initial = false};
    }

    height = unused->height - item_height - cut_width;
    if (height > 0) {
        width = (vertical ? item_width : unused->width);
        new_unused[(*new_unused_len)++] =
            (opcut_unused_t){.panel = unused->panel,
                             .width = width,
                             .height = height,
                             .x = unused->x,
                             .y = unused->y + item_height + cut_width,
                             .area = width * height,
                             .initial = false};
    }

    return OPCUT_SUCCESS;
}


void opcut_sort_params(opcut_params_t *params) {
    sort_panels(&(params->panels), NULL);
    sort_items(&(params->items), NULL);
}


int opcut_calculate(opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result) {

    result->params = params;
    result->used = NULL;
    result->unused = NULL;
    result->panels_area = 0;

    return OPCUT_SUCCESS;
}
