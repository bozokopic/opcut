#define JSMN_PARENT_LINKS

#include <stdlib.h>
#include <string.h>
#include <jsmn.h>
#include "common.h"


static inline bool is_token_val(char *json, jsmntok_t *token, char *val) {
    return strncmp(val, json + token->start, token->end - token->start) == 0;
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
    if (fprintf(stream, "\"%.*s\"", str->len, str->data) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_panel(opcut_panel_t *panel, FILE *stream) {
    if (write_str(&(panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(":{\"width\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(panel->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(panel->height, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_item(opcut_item_t *item, FILE *stream) {
    if (write_str(&(item->id), stream))
        return OPCUT_ERROR;

    if (fputs(":{\"width\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(item->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(item->height, stream))
        return OPCUT_ERROR;

    if (fputs(",\"can_rotate\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_bool(item->can_rotate, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_params(opcut_params_t *params, FILE *stream) {
    if (fputs("{\"cut_width\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(params->cut_width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"min_initial_usage\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_bool(params->min_initial_usage, stream))
        return OPCUT_ERROR;

    if (fputs(",\"panels\":{", stream) < 0)
        return OPCUT_ERROR;

    for (opcut_panel_t *panel = params->panels; panel; panel = panel->next) {
        if (write_panel(panel, stream))
            return OPCUT_ERROR;

        if (panel->next) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR;
        }
    }

    if (fputs("},\"items\":{", stream) < 0)
        return OPCUT_ERROR;

    for (opcut_item_t *item = params->items; item; item = item->next) {
        if (write_item(item, stream))
            return OPCUT_ERROR;

        if (item->next) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR;
        }
    }

    if (fputs("}}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_used(opcut_used_t *used, FILE *stream) {
    if (fputs("{\"panel\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_str(&(used->panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"item\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_str(&(used->item->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"x\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(used->x, stream))
        return OPCUT_ERROR;

    if (fputs(",\"y\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(used->y, stream))
        return OPCUT_ERROR;

    if (fputs(",\"rotate\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_bool(used->rotate, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int write_unused(opcut_unused_t *unused, FILE *stream) {
    if (fputs("{\"panel\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_str(&(unused->panel->id), stream))
        return OPCUT_ERROR;

    if (fputs(",\"width\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->width, stream))
        return OPCUT_ERROR;

    if (fputs(",\"height\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->height, stream))
        return OPCUT_ERROR;

    if (fputs(",\"x\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->x, stream))
        return OPCUT_ERROR;

    if (fputs(",\"y\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_number(unused->y, stream))
        return OPCUT_ERROR;

    if (fputs("}", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int read_number(char *json, double *val, jsmntok_t *token) {
    if (token->type != JSMN_PRIMITIVE)
        return OPCUT_ERROR;

    if (sscanf(json + token->start, "%lf", val) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}


static int read_bool(char *json, bool *val, jsmntok_t *token) {
    if (token->type != JSMN_PRIMITIVE)
        return OPCUT_ERROR;

    if (json[token->start] == 't') {
        *val = true;
        return OPCUT_SUCCESS;
    }

    if (json[token->start] == 'f') {
        *val = false;
        return OPCUT_SUCCESS;
    }

    return OPCUT_ERROR;
}


static int read_string(char *json, opcut_str_t *str, jsmntok_t *token) {
    if (token->type != JSMN_STRING)
        return OPCUT_ERROR;

    str->data = json + token->start;
    str->len = token->end - token->start;
    return OPCUT_SUCCESS;
}


static int read_panel(char *json, opcut_panel_t *panel, jsmntok_t *tokens,
                      size_t *pos) {
    jsmntok_t *id_token = tokens + ((*pos)++);
    jsmntok_t *panel_token = tokens + ((*pos)++);
    if (panel_token->type != JSMN_OBJECT)
        return OPCUT_ERROR;

    if (read_string(json, &(panel->id), id_token))
        return OPCUT_ERROR;

    panel->width = 0;
    panel->height = 0;

    for (size_t i = 0; i < panel_token->size; ++i) {
        jsmntok_t *key_token = tokens + ((*pos)++);
        jsmntok_t *value_token = tokens + ((*pos)++);
        if (key_token->type != JSMN_STRING)
            return OPCUT_ERROR;

        if (is_token_val(json, key_token, "width")) {
            if (read_number(json, &(panel->width), value_token))
                return OPCUT_ERROR;

        } else if (is_token_val(json, key_token, "height")) {
            if (read_number(json, &(panel->height), value_token))
                return OPCUT_ERROR;
        }
    }

    if (panel->width <= 0 || panel->height <= 0)
        return OPCUT_ERROR;
    panel->area = panel->width * panel->height;

    return OPCUT_SUCCESS;
}


static int read_item(char *json, opcut_item_t *item, jsmntok_t *tokens,
                     size_t *pos) {
    jsmntok_t *id_token = tokens + ((*pos)++);
    jsmntok_t *item_token = tokens + ((*pos)++);
    if (item_token->type != JSMN_OBJECT)
        return OPCUT_ERROR;

    if (read_string(json, &(item->id), id_token))
        return OPCUT_ERROR;

    item->width = 0;
    item->height = 0;
    item->can_rotate = false;

    for (size_t i = 0; i < item_token->size; ++i) {
        jsmntok_t *key_token = tokens + ((*pos)++);
        jsmntok_t *value_token = tokens + ((*pos)++);
        if (key_token->type != JSMN_STRING)
            return OPCUT_ERROR;

        if (is_token_val(json, key_token, "width")) {
            if (read_number(json, &(item->width), value_token))
                return OPCUT_ERROR;

        } else if (is_token_val(json, key_token, "height")) {
            if (read_number(json, &(item->height), value_token))
                return OPCUT_ERROR;

        } else if (is_token_val(json, key_token, "can_rotate")) {
            if (read_bool(json, &(item->can_rotate), value_token))
                return OPCUT_ERROR;
        }
    }

    if (item->width <= 0 || item->height <= 0)
        return OPCUT_ERROR;
    item->area = item->width * item->height;

    return OPCUT_SUCCESS;
}


static int read_params(opcut_params_t *params, char *json, jsmntok_t *tokens,
                       size_t *pos) {
    jsmntok_t *params_token = tokens + ((*pos)++);
    if (params_token->type != JSMN_OBJECT)
        return OPCUT_ERROR;

    params->cut_width = 0;
    params->min_initial_usage = false;
    params->panels = NULL;
    params->items = NULL;
    params->panels_area = 0;

    for (size_t i = 0; i < params_token->size; ++i) {
        jsmntok_t *key_token = tokens + ((*pos)++);
        jsmntok_t *value_token = tokens + ((*pos)++);
        if (key_token->type != JSMN_STRING)
            return OPCUT_ERROR;

        if (is_token_val(json, key_token, "cut_width")) {
            if (read_number(json, &(params->cut_width), value_token))
                return OPCUT_ERROR;

        } else if (is_token_val(json, key_token, "min_initial_usage")) {
            if (read_bool(json, &(params->min_initial_usage), value_token))
                return OPCUT_ERROR;

        } else if (is_token_val(json, key_token, "panels")) {
            if (value_token->type != JSMN_OBJECT)
                return OPCUT_ERROR;

            for (size_t j = 0; j < value_token->size; ++j) {
                opcut_panel_t *panel = opcut_pool_alloc(params->panel_pool);
                if (!panel)
                    return OPCUT_ERROR;

                if (read_panel(json, panel, tokens, pos))
                    return OPCUT_ERROR;

                panel->next = params->panels;
                params->panels = panel;
                params->panels_area += panel->area;
            }

        } else if (is_token_val(json, key_token, "items")) {
            if (value_token->type != JSMN_OBJECT)
                return OPCUT_ERROR;

            for (size_t j = 0; j < value_token->size; ++j) {
                opcut_item_t *item = opcut_pool_alloc(params->item_pool);
                if (!item)
                    return OPCUT_ERROR;

                if (read_item(json, item, tokens, pos))
                    return OPCUT_ERROR;

                item->next = params->items;
                params->items = item;
            }
        }
    }

    return OPCUT_SUCCESS;
}


int opcut_params_init(hat_allocator_t *a, opcut_params_t *params,
                      opcut_pool_t *panel_pool, opcut_pool_t *item_pool,
                      opcut_str_t *json) {
    params->panel_pool = panel_pool;
    params->item_pool = item_pool;

    jsmn_parser parser;
    int tokens_len;

    jsmn_init(&parser);
    tokens_len = jsmn_parse(&parser, json->data, json->len, NULL, 0);
    if (tokens_len < 0)
        return OPCUT_ERROR;

    jsmntok_t *tokens =
        hat_allocator_alloc(a, tokens_len * sizeof(jsmntok_t), NULL);
    if (!tokens)
        return OPCUT_ERROR;

    jsmn_init(&parser);
    tokens_len = jsmn_parse(&parser, json->data, json->len, tokens, tokens_len);
    if (tokens_len < 0) {
        hat_allocator_free(a, tokens);
        return OPCUT_ERROR;
    }

    size_t pos = 0;
    int err = read_params(params, json->data, tokens, &pos);

    hat_allocator_free(a, tokens);
    return err;
}


int opcut_result_write(opcut_result_t *result, FILE *stream) {
    if (fputs("{\"params\":", stream) < 0)
        return OPCUT_ERROR;

    if (write_params(result->params, stream))
        return OPCUT_ERROR;

    if (fputs(",\"used\":[", stream) < 0)
        return OPCUT_ERROR;

    for (opcut_used_t *used; used; used = used->next) {
        if (write_used(used, stream))
            return OPCUT_ERROR;

        if (used->next) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR;
        }
    }

    if (fputs("],\"unused\":[", stream) < 0)
        return OPCUT_ERROR;

    for (opcut_unused_t *unused; unused; unused = unused->next) {
        if (write_unused(unused, stream))
            return OPCUT_ERROR;

        if (unused->next) {
            if (fputs(",", stream) < 0)
                return OPCUT_ERROR;
        }
    }

    if (fputs("]}\n", stream) < 0)
        return OPCUT_ERROR;

    return OPCUT_SUCCESS;
}
