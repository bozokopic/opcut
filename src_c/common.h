#ifndef OPCUT_COMMON_H
#define OPCUT_COMMON_H

#include <stdbool.h>
#include <stdio.h>
#include <hat/allocator.h>
#include "pool.h"

#define OPCUT_SUCCESS 0
#define OPCUT_ERROR 1
#define OPCUT_UNSOLVABLE 2

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    char *data;
    size_t len;
} opcut_str_t;

typedef struct opcut_panel_t {
    opcut_str_t id;
    double width;
    double height;

    // internal
    struct opcut_panel_t *next;
    double area;
} opcut_panel_t;

typedef struct opcut_item_t {
    opcut_str_t id;
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
    opcut_pool_t *panel_pool;
    opcut_pool_t *item_pool;
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

    // internal
    opcut_pool_t *used_pool;
    opcut_pool_t *unused_pool;
} opcut_result_t;


int opcut_params_init(hat_allocator_t *a, opcut_params_t *params,
                      opcut_pool_t *panel_pool, opcut_pool_t *item_pool,
                      opcut_str_t *json);
int opcut_result_write(opcut_result_t *result, FILE *stream);

#ifdef __cplusplus
}
#endif

#endif
