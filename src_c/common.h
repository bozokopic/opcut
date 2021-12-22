#ifndef OPCUT_COMMON_H
#define OPCUT_COMMON_H

#include <stdbool.h>
#include <stdio.h>

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

typedef struct {
    opcut_str_t id;
    double width;
    double height;
} opcut_panel_t;

typedef struct {
    opcut_str_t id;
    double width;
    double height;
    bool can_rotate;
} opcut_item_t;

typedef struct {
    double cut_width;
    bool min_initial_usage;
    opcut_panel_t *panels;
    size_t panels_len;
    opcut_item_t *items;
    size_t items_len;
} opcut_params_t;

typedef struct {
    opcut_panel_t *panel;
    opcut_item_t *item;
    double x;
    double y;
    bool rotate;
} opcut_used_t;

typedef struct {
    opcut_panel_t *panel;
    double width;
    double height;
    double x;
    double y;
} opcut_unused_t;

typedef struct {
    opcut_params_t *params;
    opcut_used_t *used;
    size_t used_len;
    opcut_unused_t *unused;
    size_t unused_len;
} opcut_result_t;


int opcut_params_init(opcut_params_t *params, opcut_str_t *json);
void opcut_params_destroy(opcut_params_t *params);
int opcut_result_write(opcut_result_t *result, FILE *stream);

#ifdef __cplusplus
}
#endif

#endif
