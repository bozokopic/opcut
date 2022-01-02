#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <argparse.h>
#include "csp.h"


typedef struct {
    opcut_method_t method;
    char *input_path;
    char *output_path;
} args_t;


static int parse_args(args_t *args, int argc, char **argv) {
    char *method = NULL;
    char *output_path = NULL;

    char *usages[] = {
        "opcut-calculate [options] [[--] -|path]",
        NULL,
    };

    struct argparse_option options[] = {
        OPT_HELP(), OPT_STRING(0, "method", &method, "calculate method"),
        OPT_STRING(0, "output", &output_path, "output path"), OPT_END()};

    struct argparse argparse;
    argparse_init(&argparse, options, (const char *const *)usages, 0);
    argc = argparse_parse(&argparse, argc, (const char **)argv);

    if (method && strcmp(method, "greedy") == 0) {
        args->method = OPCUT_METHOD_GREEDY;
    } else if (method && strcmp(method, "forward_greedy") == 0) {
        args->method = OPCUT_METHOD_FORWARD_GREEDY;
    } else {
        return OPCUT_ERROR;
    }

    if (!argc) {
        args->input_path = NULL;
    } else if (argc == 1) {
        if (strcmp(argv[0], "-") == 0) {
            args->input_path = NULL;
        } else {
            args->input_path = argv[0];
        }
    } else {
        return OPCUT_ERROR;
    }

    if (output_path && strcmp(output_path, "-") == 0) {
        args->output_path = NULL;
    } else {
        args->output_path = output_path;
    }

    return OPCUT_SUCCESS;
}


static int read_stream(hat_allocator_t *a, FILE *stream, opcut_str_t *json) {
    size_t size = 0;

    while (!(json->len < size)) {
        size += 4096;
        char *data = hat_allocator_alloc(a, size, json->data);
        if (!data)
            return OPCUT_ERROR;

        json->data = data;
        json->len += fread(json->data + json->len, 1, size - json->len, stream);
    }

    return OPCUT_SUCCESS;
}


int main(int argc, char **argv) {
    hat_allocator_t *a = &hat_allocator_libc;
    opcut_pool_t *panel_pool = opcut_pool_create(a, sizeof(opcut_panel_t));
    opcut_pool_t *item_pool = opcut_pool_create(a, sizeof(opcut_item_t));
    opcut_pool_t *used_pool = opcut_pool_create(a, sizeof(opcut_used_t));
    opcut_pool_t *unused_pool = opcut_pool_create(a, sizeof(opcut_unused_t));

    args_t args;
    FILE *input_stream = NULL;
    FILE *output_stream = NULL;
    opcut_str_t json = {.data = NULL, .len = 0};
    opcut_params_t params;
    opcut_result_t result;
    int exit_code;

    if (!panel_pool || !item_pool || !used_pool || !unused_pool) {
        fprintf(stderr, "error creating memory pools\n");
        goto cleanup;
    }

    exit_code = parse_args(&args, argc, argv);
    if (exit_code) {
        fprintf(stderr, "error parsing command line arguments\n");
        goto cleanup;
    }

    input_stream = (args.input_path ? fopen(args.input_path, "r") : stdin);
    if (!input_stream) {
        fprintf(stderr, "error opening input stream\n");
        exit_code = OPCUT_ERROR;
        goto cleanup;
    }

    output_stream = (args.output_path ? fopen(args.output_path, "w") : stdout);
    if (!output_stream) {
        fprintf(stderr, "error opening output stream\n");
        exit_code = OPCUT_ERROR;
        goto cleanup;
    }

    exit_code = read_stream(a, input_stream, &json);
    if (exit_code) {
        fprintf(stderr, "error reading input stream\n");
        goto cleanup;
    }

    exit_code = opcut_params_init(a, &params, panel_pool, item_pool, &json);
    if (exit_code) {
        fprintf(stderr, "error parsing calculation parameters\n");
        goto cleanup;
    }

    exit_code =
        opcut_calculate(used_pool, unused_pool, args.method, &params, &result);
    if (exit_code) {
        fprintf(stderr, "calculation error\n");
        goto cleanup;
    }

    exit_code = opcut_result_write(&result, output_stream);

cleanup:

    if (json.data)
        hat_allocator_free(a, json.data);
    if (output_stream)
        fclose(output_stream);
    if (input_stream)
        fclose(input_stream);
    if (unused_pool)
        opcut_pool_destroy(unused_pool);
    if (used_pool)
        opcut_pool_destroy(used_pool);
    if (item_pool)
        opcut_pool_destroy(item_pool);
    if (panel_pool)
        opcut_pool_destroy(panel_pool);

    return exit_code;
}
