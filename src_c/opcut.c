#include "opcut.h"
#include <unistd.h>
#include <math.h>

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
    opcut_malloc_t malloc;
    opcut_free_t free;
    mem_pool_t *used;
    mem_pool_t *unused;
};

typedef struct {
    size_t unused_initial_count;
    double fitness;
} fitness_t;

typedef struct {
    opcut_used_t *used;
    opcut_unused_t *unused;
} result_t;


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
    if (!pool)
        return;

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


static void free_used_until(opcut_allocator_t *a, opcut_used_t *used,
                            opcut_used_t *last_used) {
    while (used && used != last_used) {
        opcut_used_t *next = used->next;
        mem_pool_free(a->used, used);
        used = next;
    }
}


static void free_unused_until(opcut_allocator_t *a, opcut_unused_t *unused,
                              opcut_unused_t *last_unused) {
    while (unused) {
        opcut_unused_t *next = unused->next;
        mem_pool_free(a->unused, unused);
        unused = next;
    }
}


static inline double compare_item(opcut_params_t *params, size_t id1, size_t id2) {
    return params->items[id1].area - params->items[id2].area;
}


static inline double compare_unused(opcut_unused_t *u1, opcut_unused_t *u2) {
    return u1->area - u2->area;
}


static inline double compare_fitness(fitness_t *f1, fitness_t *f2) {
    if (f1->unused_initial_count == f2->unused_initial_count)
        return f1->fitness - f2->fitness;
    return f1->unused_initial_count - f2->unused_initial_count;
}


static inline void swap_ids(size_t *ids, size_t pos1, size_t pos2) {
    size_t temp = ids[pos1];
    ids[pos1] = ids[pos2];
    ids[pos2] = temp;
}


static size_t partition_item_ids(opcut_params_t *params,
                            size_t *item_ids, ssize_t start, ssize_t stop) {
    ssize_t pivot = start - 1;
    for (size_t i = start; i < stop; ++i)
        if (compare_item(params, item_ids[i], item_ids[stop]) >= 0)
            swap_ids(item_ids, ++pivot, i);
    pivot += 1;
    swap_ids(item_ids, pivot, stop);
    return pivot;
}


static void sort_item_ids(opcut_params_t *params, size_t *item_ids,
                     ssize_t start, ssize_t stop) {
    if (start >= stop || stop < 0)
        return;

    ssize_t pivot = partition_item_ids(params, item_ids, start, stop);
    sort_item_ids(params, item_ids, start, pivot - 1);
    sort_item_ids(params, item_ids, pivot + 1, stop);
}


static int copy_unused_without(opcut_allocator_t *a, opcut_unused_t *exclude,
                               opcut_unused_t *src, opcut_unused_t **dst) {
    opcut_unused_t *unused = NULL;
    for (opcut_unused_t *i = src; i; i = i->next) {
        if (i == exclude)
            continue;

        opcut_unused_t *temp = mem_pool_alloc(a->unused);
        if (!temp)
            return OPCUT_ERROR;

        *temp = *i;
        temp->next = unused;
        unused = temp;
    }

    *dst = NULL;
    while (unused) {
        opcut_unused_t *next = unused->next;
        unused->next = *dst;
        *dst = unused;
        unused = next;
    }

    return OPCUT_SUCCESS;
}


static void insert_unused(opcut_unused_t **list, opcut_unused_t *el) {
    while (*list && compare_unused(*list, el) <= 0)
        list = &((*list)->next);

    el->next = *list;
    *list = el;
}



static size_t *create_initial_item_ids(opcut_allocator_t *a,
                                       opcut_params_t *params) {
    if (!params->items_len)
        return NULL;

    size_t *item_ids = a->malloc(params->items_len * sizeof(size_t));
    if (!item_ids)
        return NULL;

    for (size_t item_id = 0; item_id < params->items_len; ++item_id)
        item_ids[item_id] = item_id;

    sort_item_ids(params, item_ids, 0, params->items_len - 1);

    return item_ids;
}


static opcut_unused_t *create_initial_unused(opcut_allocator_t *a,
                                             opcut_params_t *params) {
    if (!params->panels_len)
        return NULL;

    opcut_unused_t *unused = NULL;
    for (size_t panel_id = 0; panel_id < params->panels_len; ++panel_id) {
        opcut_panel_t *panel = params->panels + panel_id;

        opcut_unused_t *temp = mem_pool_alloc(a->unused);
        if (!temp) {
            free_unused_until(a, unused, NULL);
            unused = NULL;
            break;
        }

        *temp = (opcut_unused_t){.panel_id = panel_id,
                                 .width = panel->width,
                                 .height = panel->height,
                                 .x = 0,
                                 .y = 0,
                                 .next = unused,
                                 .area = panel->area,
                                 .initial = true};
        insert_unused(&unused, temp);
    }

    return unused;
}


static void calculate_fitness(opcut_params_t *params, result_t *result,
                              fitness_t *fitness) {
    fitness->fitness = 0;

    for (size_t panel_id = 0; panel_id < params->panels_len; ++panel_id) {
        double min_used_area = 0;
        double used_areas = 0;
        for (opcut_used_t *used = result->used; used; used = used->next) {
            if (used->panel_id != panel_id)
                continue;
            opcut_item_t *item = params->items + used->item_id;
            if (min_used_area == 0 || item->area < min_used_area)
                min_used_area = item->area;
            used_areas = item->area;
        }

        double max_unused_area = 0;
        for (opcut_unused_t *unused = result->unused; unused;
             unused = unused->next) {
            if (unused->panel_id != panel_id)
                continue;
            if (max_unused_area == 0 || unused->area > max_unused_area)
                max_unused_area = unused->area;
        }

        opcut_panel_t *panel = params->panels + panel_id;
        fitness->fitness += (panel->area - used_areas) / params->panels_area;
        fitness->fitness -= FITNESS_K * min_used_area * max_unused_area /
                            (params->panels_area * params->panels_area);
    }

    fitness->unused_initial_count = 0;
    if (params->min_initial_usage) {
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


static int cut_item_from_unused(opcut_allocator_t *a, opcut_params_t *params,
                                result_t *result, size_t item_id,
                                opcut_unused_t *unused, bool rotate,
                                bool vertical) {
    opcut_item_t *item = params->items + item_id;
    double item_width = (rotate ? item->height : item->width);
    double item_height = (rotate ? item->width : item->height);
    if (unused->height < item_height || unused->width < item_width)
        return OPCUT_ERROR;

    opcut_used_t *used = mem_pool_alloc(a->used);
    if (!used)
        return OPCUT_ERROR;
    *used = (opcut_used_t){.panel_id = unused->panel_id,
                           .item_id = item_id,
                           .x = unused->x,
                           .y = unused->y,
                           .rotate = rotate,
                           .next = result->used};
    result->used = used;


    double width;
    double height;

    width = unused->width - item_width - params->cut_width;
    if (width > 0) {
        height = (vertical ? unused->height : item_height);
        opcut_unused_t *new_unused = mem_pool_alloc(a->unused);
        if (!new_unused)
            return OPCUT_ERROR;
        *new_unused =
            (opcut_unused_t){.panel_id = unused->panel_id,
                             .width = width,
                             .height = height,
                             .x = unused->x + item_width + params->cut_width,
                             .y = unused->y,
                             .next = result->unused,
                             .area = width * height,
                             .initial = false};
        insert_unused(&(result->unused), new_unused);
    }

    height = unused->height - item_height - params->cut_width;
    if (height > 0) {
        width = (vertical ? item_width : unused->width);
        opcut_unused_t *new_unused = mem_pool_alloc(a->unused);
        if (!new_unused)
            return OPCUT_ERROR;
        *new_unused =
            (opcut_unused_t){.panel_id = unused->panel_id,
                             .width = width,
                             .height = height,
                             .x = unused->x,
                             .y = unused->y + item_height + params->cut_width,
                             .next = result->unused,
                             .area = width * height,
                             .initial = false};
        insert_unused(&(result->unused), new_unused);
    }

    return OPCUT_SUCCESS;
}


static int calculate_greedy(opcut_allocator_t *a, opcut_params_t *params,
                            result_t *result, size_t *item_ids,
                            size_t item_ids_len, bool forward_greedy) {
    for (size_t i = 0; i < item_ids_len; ++i) {
        result_t best_result;
        fitness_t best_fitness;
        bool solvable = false;
        size_t item_id = item_ids[i];
        opcut_item_t *item = params->items + item_id;

        for (opcut_unused_t *unused = result->unused; unused;
             unused = unused->next) {
            for (size_t rotate = 0; rotate < 2; ++rotate) {
                if (!item_fits_unused(item, unused, rotate))
                    continue;

                for (size_t vertical = 0; vertical < 2; ++vertical) {
                    result_t temp_result = {.used = result->used,
                                            .unused = NULL};
                    if (copy_unused_without(a, unused, result->unused,
                                            &(temp_result.unused)))
                        return OPCUT_ERROR;

                    if (cut_item_from_unused(a, params, &temp_result, item_id,
                                             unused, rotate, vertical))
                        return OPCUT_ERROR;

                    fitness_t temp_fitness;
                    if (!forward_greedy) {
                        calculate_fitness(params, &temp_result, &temp_fitness);

                    } else {
                        result_t greedy_result = {.used = temp_result.used,
                                                  .unused = NULL};
                        if (copy_unused_without(a, temp_result.unused,
                                                temp_result.unused,
                                                &(greedy_result.unused)))
                            return OPCUT_ERROR;

                        int err = calculate_greedy(a, params, &greedy_result,
                                                   item_ids + i + 1,
                                                   item_ids_len - i - 1, false);

                        if (!err) {
                            calculate_fitness(params, &greedy_result,
                                              &temp_fitness);
                            free_used_until(a, greedy_result.used,
                                            temp_result.used);
                            free_unused_until(a, greedy_result.unused, NULL);


                        } else if (err == OPCUT_UNSOLVABLE) {
                            free_used_until(a, greedy_result.used,
                                            temp_result.used);
                            free_used_until(a, temp_result.used, result->used);
                            free_unused_until(a, greedy_result.unused, NULL);
                            free_unused_until(a, temp_result.unused, NULL);
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
                        free_used_until(a, best_result.used, result->used);
                        free_unused_until(a, best_result.unused, NULL);
                        best_result = temp_result;
                        best_fitness = temp_fitness;

                    } else {
                        free_used_until(a, temp_result.used, result->used);
                        free_unused_until(a, temp_result.unused, NULL);
                    }
                }
            }
        }

        if (!solvable)
            return OPCUT_UNSOLVABLE;

        free_unused_until(a, result->unused, NULL);
        *result = best_result;
    }

    return OPCUT_SUCCESS;
}


opcut_allocator_t *opcut_allocator_create(opcut_malloc_t malloc,
                                          opcut_free_t free) {
    opcut_allocator_t *a = malloc(sizeof(opcut_allocator_t));
    if (!a)
        return NULL;

    *a = (opcut_allocator_t){
        .malloc = malloc, .free = free, .used = NULL, .unused = NULL};

    a->used = mem_pool_create(malloc, free, sizeof(opcut_used_t));
    if (!a->used)
        goto error_cleanup;

    a->unused = mem_pool_create(malloc, free, sizeof(opcut_unused_t));
    if (!a->unused)
        goto error_cleanup;

    return a;

error_cleanup:
    opcut_allocator_destroy(a);
    return NULL;
}


void opcut_allocator_destroy(opcut_allocator_t *a) {
    if (!a)
        return;

    mem_pool_destroy(a->used);
    mem_pool_destroy(a->unused);
    a->free(a);
}


int opcut_calculate(opcut_allocator_t *a, int method, opcut_params_t *params,
                    opcut_used_t **used, opcut_unused_t **unused) {
    int ret = OPCUT_ERROR;
    result_t result = (result_t){.used = NULL, .unused = NULL};

    size_t *item_ids = create_initial_item_ids(a, params);
    if (params->items_len && !item_ids)
        goto cleanup;

    result.unused = create_initial_unused(a, params);
    if (params->panels_len && !result.unused)
        goto cleanup;

    if (method == OPCUT_METHOD_GREEDY) {
        ret = calculate_greedy(a, params, &result, item_ids, params->items_len,
                               false);

    } else if (method == OPCUT_METHOD_FORWARD_GREEDY) {
        ret = calculate_greedy(a, params, &result, item_ids, params->items_len,
                               true);
    }

cleanup:
    if (item_ids)
        a->free(item_ids);

    *used = result.used;
    *unused = result.unused;
    return ret;
}
