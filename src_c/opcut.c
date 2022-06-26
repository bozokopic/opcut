#include "opcut.h"

#define PAGE_SIZE 4096
#define FITNESS_K 0.03


typedef struct mem_header_t {
    struct mem_header_t *next;
} mem_header_t;

typedef struct {
    opcut_malloc_t malloc;
    opcut_free_t free;
    size_t item_size;
    mem_header_t *blocks;
    mem_header_t *items;
} mem_pool_t;

struct opcut_allocator_t {
    opcut_free_t free;
    mem_pool_t *panel;
    mem_pool_t *item;
    mem_pool_t *params;
    mem_pool_t *used;
    mem_pool_t *unused;
    mem_pool_t *result;
};

typedef struct {
    size_t unused_initial_count;
    double fitness;
} fitness_t;


static void mem_pool_add_block(mem_pool_t *pool) {
    size_t items_per_block = (PAGE_SIZE - sizeof(mem_header_t)) /
                             (sizeof(mem_header_t) + pool->item_size);
    if (items_per_block < 1)
        items_per_block = 1;

    mem_header_t *block = pool->malloc(
        sizeof(mem_header_t) +
        items_per_block * (sizeof(mem_header_t) + pool->item_size));
    if (!block)
        return;
    block->next = pool->blocks;
    pool->blocks = block;

    for (size_t i = 0; i < items_per_block; ++i) {
        mem_header_t *header = (void *)block + sizeof(mem_header_t) +
                               i * (sizeof(mem_header_t) + pool->item_size);
        header->next = pool->items;
        pool->items = header;
    }
}


static mem_pool_t *mem_pool_create(opcut_malloc_t malloc, opcut_free_t free,
                                   size_t item_size) {
    mem_pool_t *pool = malloc(sizeof(mem_pool_t));
    if (!pool)
        return NULL;

    if (item_size % sizeof(void *) != 0)
        item_size += sizeof(void *) - (item_size % sizeof(void *));

    pool->malloc = malloc;
    pool->free = free;
    pool->item_size = item_size;
    pool->blocks = NULL;
    pool->items = NULL;

    return pool;
}


static void mem_pool_destroy(mem_pool_t *pool) {
    while (pool->blocks) {
        mem_header_t *block = pool->blocks;
        pool->blocks = block->next;
        pool->free(block);
    }
    pool->free(pool);
}


static void *mem_pool_alloc(mem_pool_t *pool) {
    if (!pool->items)
        mem_pool_add_block(pool);

    if (!pool->items)
        return NULL;

    mem_header_t *header = pool->items;
    pool->items = header->next;
    return header + 1;
}


static void mem_pool_free(mem_pool_t *pool, void *item) {
    mem_header_t *header = (mem_header_t *)item - 1;
    header->next = pool->items;
    pool->items = header;
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


static void sort_unused(opcut_unused_t **first, opcut_unused_t **last) {
    if (!*first) {
        if (last)
            *last = NULL;
        return;
    }

    opcut_unused_t *pivot_first = *first;
    opcut_unused_t *pivot_last = *first;
    opcut_unused_t *left_first = NULL;
    opcut_unused_t *right_first = NULL;

    for (opcut_unused_t *unused = (*first)->next; unused;) {
        opcut_unused_t *next = unused->next;
        if (unused->area > pivot_first->area) {
            unused->next = left_first;
            left_first = unused;
        } else if (unused->area < pivot_first->area) {
            unused->next = right_first;
            right_first = unused;
        } else {
            pivot_last->next = unused;
            pivot_last = unused;
        }
        unused = next;
    }

    opcut_unused_t *left_last;
    opcut_unused_t *right_last;
    sort_unused(&left_first, &left_last);
    sort_unused(&right_first, &right_last);

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


static int cut_item_from_unused(opcut_allocator_t *a, opcut_result_t *result,
                                opcut_item_t *item, opcut_unused_t *unused,
                                bool rotate, bool vertical) {
    double item_width = (rotate ? item->height : item->width);
    double item_height = (rotate ? item->width : item->height);
    if (unused->height < item_height || unused->width < item_width)
        return OPCUT_ERROR;

    opcut_used_t *used = mem_pool_alloc(a->used);
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
        opcut_unused_t *new_unused = mem_pool_alloc(a->unused);
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
        opcut_unused_t *new_unused = mem_pool_alloc(a->unused);
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


static int copy_unused(opcut_allocator_t *a, opcut_result_t *result,
                       opcut_unused_t *exclude) {
    opcut_unused_t *unused = NULL;
    for (opcut_unused_t *i = result->unused; i; i = i->next) {
        if (i == exclude)
            continue;

        opcut_unused_t *temp = mem_pool_alloc(a->unused);
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


static void free_unused(opcut_allocator_t *a, opcut_result_t *result) {
    while (result->unused) {
        opcut_unused_t *next = result->unused->next;
        mem_pool_free(a->unused, result->unused);
        result->unused = next;
    }
}


static void free_used(opcut_allocator_t *a, opcut_result_t *result,
                      opcut_used_t *last_used) {
    while (result->used && result->used != last_used) {
        opcut_used_t *next = result->used->next;
        mem_pool_free(a->used, result->used);
        result->used = next;
    }
}


static int calculate_greedy(opcut_allocator_t *a, opcut_result_t *result,
                            opcut_item_t *items, bool forward_greedy) {
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
                    if (copy_unused(a, &temp_result, unused))
                        return OPCUT_ERROR;

                    if (cut_item_from_unused(a, &temp_result, item, unused,
                                             rotate, vertical))
                        return OPCUT_ERROR;

                    fitness_t temp_fitness;
                    if (!forward_greedy) {
                        calculate_fitness(&temp_result, &temp_fitness);

                    } else {
                        opcut_result_t greedy_result = temp_result;
                        if (copy_unused(a, &greedy_result, temp_result.unused))
                            return OPCUT_ERROR;

                        int err = calculate_greedy(a, &greedy_result,
                                                   item->next, false);

                        if (!err) {
                            calculate_fitness(&greedy_result, &temp_fitness);
                            free_used(a, &greedy_result, temp_result.used);
                            free_unused(a, &greedy_result);

                        } else if (err == OPCUT_UNSOLVABLE) {
                            free_used(a, &greedy_result, temp_result.used);
                            free_used(a, &temp_result, result->used);
                            free_unused(a, &greedy_result);
                            free_unused(a, &temp_result);
                            continue;

                        } else {
                            return err;
                        }
                    }

                    if (!solvable) {
                        best_result = temp_result;
                        best_fitness = temp_fitness;
                        solvable = true;

                    } else if (compare_fitness(&temp_fitness, &best_fitness) <
                               0) {
                        free_used(a, &best_result, result->used);
                        free_unused(a, &best_result);
                        best_result = temp_result;
                        best_fitness = temp_fitness;

                    } else {
                        free_used(a, &temp_result, result->used);
                        free_unused(a, &temp_result);
                    }
                }
            }
        }

        if (!solvable)
            return OPCUT_UNSOLVABLE;

        free_unused(a, result);
        *result = best_result;
    }

    return OPCUT_SUCCESS;
}


opcut_allocator_t *opcut_allocator_create(opcut_malloc_t malloc,
                                          opcut_free_t free) {
    opcut_allocator_t *a = malloc(sizeof(opcut_allocator_t));
    if (!a)
        return NULL;

    a->free = free;
    a->panel = NULL;
    a->item = NULL;
    a->params = NULL;
    a->used = NULL;
    a->unused = NULL;
    a->result = NULL;

    a->panel = mem_pool_create(malloc, free, sizeof(opcut_panel_t));
    if (!a->panel)
        goto error_cleanup;

    a->item = mem_pool_create(malloc, free, sizeof(opcut_item_t));
    if (!a->item)
        goto error_cleanup;

    a->params = mem_pool_create(malloc, free, sizeof(opcut_params_t));
    if (!a->params)
        goto error_cleanup;

    a->used = mem_pool_create(malloc, free, sizeof(opcut_used_t));
    if (!a->used)
        goto error_cleanup;

    a->unused = mem_pool_create(malloc, free, sizeof(opcut_unused_t));
    if (!a->unused)
        goto error_cleanup;

    a->result = mem_pool_create(malloc, free, sizeof(opcut_result_t));
    if (!a->result)
        goto error_cleanup;

    return a;

error_cleanup:
    opcut_allocator_destroy(a);
    return NULL;
}


void opcut_allocator_destroy(opcut_allocator_t *a) {
    if (a->panel)
        a->free(a->panel);

    if (a->item)
        a->free(a->item);

    if (a->params)
        a->free(a->params);

    if (a->used)
        a->free(a->used);

    if (a->unused)
        a->free(a->unused);

    if (a->result)
        a->free(a->result);

    a->free(a);
}


opcut_panel_t *opcut_panel_create(opcut_allocator_t *a, char *id, double width,
                                  double height, opcut_panel_t *next) {
    opcut_panel_t *panel = mem_pool_alloc(a->panel);
    if (!panel)
        return NULL;

    panel->id = id;
    panel->width = width;
    panel->height = height;
    panel->next = next;
    panel->area = width * height;

    return panel;
}


opcut_item_t *opcut_item_create(opcut_allocator_t *a, char *id, double width,
                                double height, bool can_rotate,
                                opcut_item_t *next) {
    opcut_item_t *item = mem_pool_alloc(a->item);
    if (!item)
        return NULL;

    item->id = id;
    item->width = width;
    item->height = height;
    item->can_rotate = can_rotate;
    item->next = next;
    item->area = width * height;

    return item;
}


opcut_params_t *opcut_params_create(opcut_allocator_t *a, double cut_width,
                                    bool min_initial_usage,
                                    opcut_panel_t *panels,
                                    opcut_item_t *items) {
    opcut_params_t *params = mem_pool_alloc(a->params);
    if (!params)
        return NULL;

    params->cut_width = cut_width;
    params->min_initial_usage = min_initial_usage;
    params->panels = panels;
    params->items = items;
    params->panels_area = 0;

    for (opcut_panel_t *panel = params->panels; panel; panel = panel->next)
        params->panels_area += panel->area;

    return params;
}


opcut_used_t *opcut_used_create(opcut_allocator_t *a, opcut_panel_t *panel,
                                opcut_item_t *item, double x, double y,
                                bool rotate, opcut_used_t *next) {
    opcut_used_t *used = mem_pool_alloc(a->used);
    if (!used)
        return NULL;

    used->panel = panel;
    used->item = item;
    used->x = x;
    used->y = y;
    used->rotate = rotate;
    used->next = next;

    return used;
}


opcut_unused_t *opcut_unused_create(opcut_allocator_t *a, opcut_panel_t *panel,
                                    double width, double height, double x,
                                    double y, bool rotate,
                                    opcut_unused_t *next) {
    opcut_unused_t *unused = mem_pool_alloc(a->unused);
    if (!unused)
        return NULL;

    unused->panel = panel;
    unused->width = width;
    unused->height = height;
    unused->x = x;
    unused->y = y;
    unused->next = next;
    unused->area = width * height;
    unused->initial = true;

    return unused;
}


opcut_result_t *opcut_result_create(opcut_allocator_t *a,
                                    opcut_params_t *params, opcut_used_t *used,
                                    opcut_unused_t *unused) {
    opcut_result_t *result = mem_pool_alloc(a->result);
    if (!result)
        return NULL;

    result->params = params;
    result->used = used;
    result->unused = unused;

    return result;
}


int opcut_calculate(opcut_allocator_t *a, int method, opcut_result_t *result) {
    opcut_item_t *used_items = NULL;
    opcut_item_t *unused_items = NULL;

    for (opcut_item_t *item = result->params->items; item;) {
        bool is_used = false;
        opcut_item_t *next = item->next;

        for (opcut_used_t *used = result->used; used && !is_used;
             used = used->next)
            is_used = used->item == item;

        if (is_used) {
            item->next = used_items;
            used_items = item;

        } else {
            item->next = unused_items;
            unused_items = item;
        }

        item = next;
    }

    sort_items(&used_items, NULL);
    sort_items(&unused_items, NULL);

    result->params->items = used_items;
    for (opcut_item_t *item = result->params->items; item; item = item->next) {
        if (!item->next) {
            item->next = unused_items;
            break;
        }
    }

    sort_unused(&(result->unused), NULL);

    if (method == OPCUT_METHOD_GREEDY)
        return calculate_greedy(a, result, unused_items, false);

    if (method == OPCUT_METHOD_FORWARD_GREEDY)
        return calculate_greedy(a, result, unused_items, true);

    return OPCUT_ERROR;
}
