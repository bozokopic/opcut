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
        if (panel->area > pivot_first->area) {
            panel->next = left_first;
            left_first = panel;
        } else if (panel->area < pivot_first->area) {
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

        fitness->fitness +=
            (panel->area - used_areas) / result->params->panels_area;
        fitness->fitness -=
            FITNESS_K * min_used_area * max_unused_area /
            (result->params->panels_area * result->params->panels_area);
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


static inline bool item_fits_unused(opcut_item_t *item, opcut_unused_t *unused,
                                    bool rotate) {
    if (rotate && !item->can_rotate)
        return false;

    double item_width = (rotate ? item->height : item->width);
    double item_height = (rotate ? item->width : item->height);

    return unused->height >= item_height && unused->width >= item_width;
}


static int cut_item_from_unused(opcut_result_t *result, opcut_item_t *item,
                                opcut_unused_t *unused, bool rotate,
                                bool vertical) {
    double item_width = (rotate ? item->height : item->width);
    double item_height = (rotate ? item->width : item->height);
    if (unused->height < item_height || unused->width < item_width)
        return OPCUT_ERROR;

    opcut_used_t *used = opcut_pool_alloc(result->used_pool);
    if (!used)
        return OPCUT_ERROR;
    *used = (opcut_used_t){.panel = unused->panel,
                           .item = item,
                           .x = unused->x,
                           .y = unused->y,
                           .rotate = rotate,
                           .next = result->used};
    result->used = used;


    double width;
    double height;

    width = unused->width - item_width - result->params->cut_width;
    if (width > 0) {
        height = (vertical ? unused->height : item_height);
        opcut_unused_t *new_unused = opcut_pool_alloc(result->unused_pool);
        if (!new_unused)
            return OPCUT_ERROR;
        *new_unused = (opcut_unused_t){.panel = unused->panel,
                                       .width = width,
                                       .height = height,
                                       .x = unused->x + item_width +
                                            result->params->cut_width,
                                       .y = unused->y,
                                       .next = result->unused,
                                       .area = width * height,
                                       .initial = false};
        result->unused = new_unused;
    }

    height = unused->height - item_height - result->params->cut_width;
    if (height > 0) {
        width = (vertical ? item_width : unused->width);
        opcut_unused_t *new_unused = opcut_pool_alloc(result->unused_pool);
        if (!new_unused)
            return OPCUT_ERROR;
        *new_unused = (opcut_unused_t){.panel = unused->panel,
                                       .width = width,
                                       .height = height,
                                       .x = unused->x,
                                       .y = unused->y + item_height +
                                            result->params->cut_width,
                                       .next = result->unused,
                                       .area = width * height,
                                       .initial = false};
        result->unused = new_unused;
    }

    return OPCUT_SUCCESS;
}


static int copy_unused(opcut_result_t *result, opcut_unused_t *exclude) {
    opcut_unused_t *unused = NULL;
    for (opcut_unused_t *i = result->unused; i; i = i->next) {
        if (i == exclude)
            continue;

        opcut_unused_t *temp = opcut_pool_alloc(result->unused_pool);
        if (!temp)
            return OPCUT_ERROR;

        *temp = *i;
        temp->next = unused;
        unused = temp;
    }

    result->unused = NULL;
    while (unused) {
        opcut_unused_t *next = unused->next;
        unused->next = result->unused;
        result->unused = unused;
        unused = next;
    }

    return OPCUT_SUCCESS;
}


static void free_unused(opcut_result_t *result) {
    while (result->unused) {
        opcut_unused_t *next = result->unused->next;
        opcut_pool_free(result->unused_pool, result->unused);
        result->unused = next;
    }
}


static void free_last_used(opcut_result_t *result) {
    opcut_pool_free(result->used_pool, result->used);
}


static int calculate_greedy(opcut_result_t *result, opcut_item_t *items) {
    for (opcut_item_t *item = items; item; item = item->next) {
        opcut_result_t best_result;
        fitness_t best_fitness;
        bool solvable = false;

        for (opcut_unused_t *unused = result->unused; unused;
             unused = unused->next) {
            for (size_t rotate = 0; rotate < 2; ++rotate) {
                if (!item_fits_unused(item, unused, rotate))
                    continue;

                for (size_t vertical = 0; vertical < 2; ++vertical) {
                    opcut_result_t temp_result = *result;
                    if (copy_unused(&temp_result, unused))
                        return OPCUT_ERROR;

                    if (cut_item_from_unused(&temp_result, item, unused, rotate,
                                             vertical))
                        return OPCUT_ERROR;

                    fitness_t temp_fitness;
                    calculate_fitness(&temp_result, &temp_fitness);

                    if (!solvable) {
                        best_result = temp_result;
                        best_fitness = temp_fitness;
                        solvable = true;

                    } else if (compare_fitness(&temp_fitness, &best_fitness) <
                               0) {
                        free_last_used(&best_result);
                        free_unused(&best_result);
                        best_result = temp_result;
                        best_fitness = temp_fitness;

                    } else {
                        free_last_used(&temp_result);
                        free_unused(&temp_result);
                    }
                }
            }
        }

        if (!solvable)
            return OPCUT_UNSOLVABLE;

        free_unused(result);
        *result = best_result;
    }

    return OPCUT_SUCCESS;
}


static int calculate_forward_greedy(opcut_result_t *result,
                                    opcut_item_t *items) {
    for (opcut_item_t *item = items; item; item = item->next) {
    }

    return OPCUT_SUCCESS;
}


int opcut_calculate(opcut_pool_t *used_pool, opcut_pool_t *unused_pool,
                    opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result) {
    result->used_pool = used_pool;
    result->unused_pool = unused_pool;
    result->params = params;
    result->used = NULL;
    result->unused = NULL;

    sort_panels(&(params->panels), NULL);
    sort_items(&(params->items), NULL);

    for (opcut_panel_t *panel = params->panels; panel; panel = panel->next) {
        opcut_unused_t *unused = opcut_pool_alloc(unused_pool);
        if (!unused)
            return OPCUT_ERROR;

        *unused = (opcut_unused_t){.panel = panel,
                                   .width = panel->width,
                                   .height = panel->height,
                                   .x = 0,
                                   .y = 0,
                                   .next = result->unused,
                                   .area = panel->area,
                                   .initial = true};
        result->unused = unused;
    }

    if (method == OPCUT_METHOD_GREEDY)
        return calculate_greedy(result, params->items);

    if (method == OPCUT_METHOD_FORWARD_GREEDY)
        return calculate_forward_greedy(result, params->items);

    return OPCUT_ERROR;
}
