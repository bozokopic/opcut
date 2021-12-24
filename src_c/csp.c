#include "csp.h"


#define FITNESS_K 0.03


typedef struct {
    size_t unused_initial_count;
    double fitness;
} fitness_t;


static inline int compare_fitness(fitness_t *f1, fitness_t *f2) {
    return (f1->unused_initial_count == f2->unused_initial_count
                ? f1->fitness - f2->fitness
                : f1->unused_initial_count - f2->unused_initial_count);
}


static void calculate_fitness(opcut_result_t *result, fitness_t *fitness) {
    fitness->fitness = 0;

    for (size_t i = 0; i < result->params->panels_len; ++i) {
        opcut_panel_t *panel = result->params->panels + i;

        double min_used_area = 0;
        double used_areas = 0;
        for (size_t j = 0; j < result->used_len; ++j) {
            opcut_used_t *used = result->used + i;
            if (used->panel != panel)
                continue;
            if (min_used_area == 0 || used->item->area < min_used_area)
                min_used_area = used->item->area;
            used_areas = used->item->area;
        }

        double max_unused_area = 0;
        for (size_t j = 0; j < result->unused_len; ++j) {
            opcut_unused_t *unused = result->unused + i;
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
        for (size_t i = 0; i < result->unused_len; ++i) {
            opcut_unused_t *unused = result->unused + i;
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


int opcut_calculate(opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result) {

    result->params = params;
    result->used = NULL;
    result->used_len = 0;
    result->unused = NULL;
    result->unused_len = 0;
    result->panels_area = 0;

    return OPCUT_SUCCESS;
}
