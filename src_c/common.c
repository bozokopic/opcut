#define JSMN_PARENT_LINKS

#include <stdlib.h>
#include <string.h>
#include <jsmn.h>
#include "common.h"


static inline bool is_token_val(char *json, jsmntok_t *token, char *val) {
    return strncmp(val, json + token->start, token->end - tokens->start) == 0;
}


static int write_params(opcut_params_t *params, FILE *stream) {
    if (fputs("{\"cut_width\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(params->cut_width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"min_initial_usage\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_bool(params->min_initial_usage, stream))
        return OPCUT_ERROR;

    if (fputs("\"panels\":[", stream) < 0)
        return OPCUT_ERROR;

    for (size_t i = 0; i < params->panels_len; ++i) {
        if (write_panel(result->panels + i, stream))
            return OPCUT_ERROR;

        if (i < result->panels_len - 1) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR
        }
    }

    if (fputs("],\"items\":[", stream) < 0)
        return OPCUT_ERROR;

    for (size_t i = 0; i < params->items_len; ++i) {
        if (write_item(result->items + i, stream))
            return OPCUT_ERROR;

        if (i < result->items_len - 1) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR
        }
    }

    if (fputs("]}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_used(opcut_used_t *used, FILE *stream) {
    if (fputs("{\"panel\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_str(&(used->panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"item\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_str(&(used->item->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"x\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(used->x, stream))
        return OPCUT_ERROR;

    if (fputs(",\"y\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(used->y, stream))
        return OPCUT_ERROR;

    if (fputs(",\"rotate\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_bool(used->rotate, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_unused(opcut_unused_t *unused, FILE *stream) {
    if (fputs("{\"panel\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_str(&(unused->panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"width\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->height, stream))
        return OPCUT_ERROR;

    if (fputs(",\"x\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->x, stream))
        return OPCUT_ERROR;

    if (fputs(",\"y\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->y, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_panel(opcut_panel_t *panel, FILE *stream) {
    if (fputs("{\"id\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_str(&(panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"width\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(panel->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(panel->height, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_item(opcut_item_t *item, FILE *stream) {
    if (fputs("{\"id\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_str(&(item->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"width\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(item->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_number(item->height, stream))
        return OPCUT_ERROR;

    if (fputs(",\"can_rotate\":", fputs) < 0)
        return OPCUT_ERROR;

    if (write_bool(item->can_rotate, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_number(double val, FILE *stream) {
    if (fprintf(stream, "%f", val) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_bool(bool val, FILE *stream) {
    if (fputs((val ? "true" : "false"), stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_str(opcut_str_t *str, FILE *stream) {
    if (fprintf(stream, "\"%*s\"", str->len, str->data) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int read_params(char *json, opcut_params_t *params, jsmntok_t *tokens,
                       size_t *pos) {
    jsmntok_t *params_token = tokens + ((*pos)++);
    if (tokens_len < 1 || params_token->type != JSMN_OBJECT)
        return OPCUT_ERROR;

    params->cut_width = 0;
    params->min_initial_usage = false;
    params->panels = NULL;
    params->panels_len = 0;
    params->items = NULL;
    params->items_len = 0;

    for (size_t i = 0; i < params_token->size; ++i) {
        jsmntok_t *key_token = tokens + ((*pos)++);
        jsmntok_t *value_token = tokens + ((*pos)++);
        if (key_token->type != JSMN_STRING)
            goto error_cleanup;

        if (is_token_val(json, key_token, "cut_width")) {
            if (read_number(json, &(params->cut_width), value_token))
                goto error_cleanup;

        } else if (is_token_val(json, key_token, "min_initial_usage")) {
            if (read_bool(json, &(params->min_initial_usage), value_token))
                goto error_cleanup;

        } else if (is_token_val(json, key_token, "panels")) {
            if (value_token->type != JSMN_ARRAY)
                goto error_cleanup;

            if (params->panels) {
                free(params->panels);
                params->panels = NULL;
            }

            params->panels_len = value_token->size;
            params->panels = malloc(value_token->size * sizeof(opcut_panel_t));
            if (!params->panels)
                goto error_cleanup;

            for (size_t j = 0; j < params->panels_len; ++j) {
                if (!read_panel(json, params->panels + j, tokens, pos))
                    goto error_cleanup;
            }

        } else if (is_token_val(json, key_token, "items")) {
            if (value_token->type != JSMN_ARRAY)
                goto error_cleanup;

            if (params->items) {
                free(params->items);
                params->items = NULL;
            }

            params->items_len = value_token->size;
            params->items = malloc(value_token->size * sizeof(opcut_item_t));
            if (!params->items)
                goto error_cleanup;

            for (size_t j = 0; j < params->items_len; ++j) {
                if (!read_item(json, params->items + j, tokens, pos))
                    goto error_cleanup;
            }
        }
    }

    return OPCUT_SUCCESS;

error_cleanup:
    if (params->panels) {
        free(params->panels);
        params->panels = NULL;
    }

    if (params->items) {
        free(params->items);
        params->items = NULL;
    }

    return OPCUT_ERROR;
}


static int read_panel(char *json, opcut_panel_t *panel, jsmntok_t *tokens,
                      size_t *pos) {}


static int read_item(char *json, opcut_item_t *item, jsmntok_t *tokens,
                     size_t *pos) {}


static int read_number(char *json, double *val, jsmntok_t *token) {}


static int read_bool(char *json, bool *val, jsmntok_t *token) {}


static int read_string(char *json, opcut_str_t *str, jsmntok_t *token) {}


int opcut_params_init(opcut_params_t *params, opcut_str_t *json) {
    jsmn_parser parser;
    int tokens_len;

    jsmn_init(&parser);
    tokens_len = jsmn_parse(&parser, json, json_len, NULL, 0);
    if (tokens_len < 0)
        return OPCUT_ERROR;

    jsmntok_t *tokens = malloc(tokens_len * sizeof(jsmntok_t));
    if (!tokens)
        return OPCUT_ERROR;

    jsmn_init(&parser);
    tokens_len = jsmn_parse(&parser, json->data, json->len, tokens, tokens_len);
    if (tokens_len < 0)
        return OPCUT_ERROR;

    size_t pos = 0;
    return read_params(json->data, params, tokens, &pos);
}


void opcut_params_destroy(opcut_params_t *params) {
    if (params->panels)
        free(params->panels);

    if (params->items)
        free(params->items);
}


int opcut_result_write(opcut_result_t *result, FILE *stream) {
    if (fputs("{\"params\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_params(result->params + i, stream))
        return OPCUT_ERROR;

    if (fputs(",\"used\":[", stream) < 0)
        return OPCUT_ERROR;

    for (size_t i = 0; i < result->used_len; ++i) {
        if (write_used(result->used + i, stream))
            return OPCUT_ERROR;

        if (i < result->used_len - 1) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR
        }
    }

    if (fputs("],\"unused\":[", stream) < 0)
        return OPCUT_ERROR;

    for (size_t i = 0; i < result->unused_len; ++i) {
        if (write_unused(result->unused + i, stream))
            return OPCUT_ERROR;

        if (i < result->unused_len - 1) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR;
        }
    }

    if (fputs("]}\n", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}
