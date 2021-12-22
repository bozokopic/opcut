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
                      .panels_len = 0,                                         \
                      .items = NULL,                                           \
                      .items_len = 0})
#define OPCUT_RESULT_EMPTY                                                     \
    ((opcut_result_t){.params = NULL,                                          \
                      .used = NULL,                                            \
                      .used_len = 0,                                           \
                      .unused = NULL,                                          \
                      .unused_len = 0})

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
