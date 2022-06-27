#ifndef OPCUT_H
#define OPCUT_H

#include <stddef.h>
#include <stdbool.h>

#define OPCUT_SUCCESS 0
#define OPCUT_ERROR 1
#define OPCUT_UNSOLVABLE 42

#define OPCUT_METHOD_GREEDY 0
#define OPCUT_METHOD_FORWARD_GREEDY 1

#ifdef __cplusplus
extern "C" {
#endif

typedef void *(*opcut_malloc_t)(size_t n);
typedef void (*opcut_free_t)(void *p);
typedef struct opcut_allocator_t opcut_allocator_t;

typedef struct opcut_panel_t {
    int id;
    double width;
    double height;

    // internal
    struct opcut_panel_t *next;
    double area;
} opcut_panel_t;

typedef struct opcut_item_t {
    int id;
    double width;
    double height;
    bool can_rotate;

    // internal
    struct opcut_item_t *next;
    double area;
} opcut_item_t;

typedef struct {
    double cut_width;
    bool min_initial_usage;
    opcut_panel_t *panels;
    opcut_item_t *items;

    // internal
    double panels_area;
} opcut_params_t;

typedef struct opcut_used_t {
    opcut_panel_t *panel;
    opcut_item_t *item;
    double x;
    double y;
    bool rotate;

    // internal
    struct opcut_used_t *next;
} opcut_used_t;

typedef struct opcut_unused_t {
    opcut_panel_t *panel;
    double width;
    double height;
    double x;
    double y;

    // internal
    struct opcut_unused_t *next;
    double area;
    bool initial;
} opcut_unused_t;

typedef struct {
    opcut_params_t *params;
    opcut_used_t *used;
    opcut_unused_t *unused;
} opcut_result_t;


opcut_allocator_t *opcut_allocator_create(opcut_malloc_t malloc,
                                          opcut_free_t free);
void opcut_allocator_destroy(opcut_allocator_t *a);

opcut_panel_t *opcut_panel_create(opcut_allocator_t *a, int id, double width,
                                  double height, opcut_panel_t *next);
opcut_item_t *opcut_item_create(opcut_allocator_t *a, int id, double width,
                                double height, bool can_rotate,
                                opcut_item_t *next);
opcut_params_t *opcut_params_create(opcut_allocator_t *a, double cut_width,
                                    bool min_initial_usage,
                                    opcut_panel_t *panels, opcut_item_t *items);

int opcut_calculate(opcut_allocator_t *a, int method, opcut_params_t *params,
                    opcut_result_t **result);

#ifdef __cplusplus
}
#endif

#endif
