#ifndef OPCUT_COMMON_H
#define OPCUT_COMMON_H

#include <stdbool.h>
#include <stdio.h>

#define OPCUT_SUCCESS 0
#define OPCUT_ERROR 1
#define OPCUT_UNSOLVABLE 2

#define OPCUT_STR_EMPTY ((opcut_str_t){.data = NULL, .len = 0})
#define OPCUT_PARAMS_EMPTY                                                     \
    ((opcut_params_t){.cut_width = 0,                                          \
                      .min_initial_usage = false,                              \
                      .panels = NULL,                                          \
                      .items = NULL})
#define OPCUT_RESULT_EMPTY                                                     \
    ((opcut_result_t){.params = NULL, .used = NULL, .unused = NULL})

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
    double panels_area;
} opcut_result_t;


int opcut_str_resize(opcut_str_t *str, size_t size);
int opcut_params_init(opcut_params_t *params, opcut_str_t *json);
int opcut_result_write(opcut_result_t *result, FILE *stream);

void opcut_str_destroy(opcut_str_t *str);
void opcut_params_destroy(opcut_params_t *params);
void opcut_result_destroy(opcut_result_t *result);

#ifdef __cplusplus
}
#endif

#endif
