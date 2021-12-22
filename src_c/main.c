#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "common.h"


static int read_stdin(opcut_str_t *json) {
    size_t json_data_size = 0;
    json->data = NULL;
    json->len = 0;

    while (!(json->len < json_data_size)) {
        char *old_json_data = json->data;
        json_data_size += 4096;
        json->data = realloc(json->data, json_data_size);
        if (!json->data) {
            free(old_json_data);
            return OPCUT_ERROR;
        }
        json->len +=
            fread(json->data + json->len, 1, json_data_size - json->len, stdin);
    }

    return OPCUT_SUCCESS;
}


int main(int argc, char **argv) {
    char *method = NULL;
    for (size_t i = 1; i < argc - 1; ++i) {
        if (strcmp("--method", argv[i]) == 0)
            method = argv[++i];
    }

    opcut_str_t json;
    if (!read_stdin(&json))
        return OPCUT_ERROR;

    opcut_params_t params;
    if (!opcut_params_init(&params, &json)) {
        free(json.data);
        return OPCUT_ERROR;
    }

    opcut_result_t result = {.params = &params,
                             .used = NULL,
                             .used_len = 0,
                             .unused = NULL,
                             .unused_len = 0};

    size_t res = opcut_result_write(&result, stdout);

    opcut_params_destroy(&params);
    free(json.data);

    return res;
}
