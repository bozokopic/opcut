#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <argparse.h>
#include "common.h"
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


static int read_stream(FILE *stream, opcut_str_t *json) {
    size_t size = 0;

    while (!(json->len < size)) {
        size += 4096;
        if (opcut_str_resize(json, size))
            return OPCUT_ERROR;

        json->len += fread(json->data + json->len, 1, size - json->len, stream);
    }

    return OPCUT_SUCCESS;
}


int main(int argc, char **argv) {
    args_t args;
    FILE *input_stream = NULL;
    FILE *output_stream = NULL;
    opcut_str_t json = OPCUT_STR_EMPTY;
    opcut_params_t params = OPCUT_PARAMS_EMPTY;
    opcut_result_t result = OPCUT_RESULT_EMPTY;
    int exit_code;

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

    exit_code = read_stream(input_stream, &json);
    if (exit_code) {
        fprintf(stderr, "error reading input stream\n");
        goto cleanup;
    }

    exit_code = opcut_params_init(&params, &json);
    if (exit_code) {
        fprintf(stderr, "error parsing calculation parameters\n");
        goto cleanup;
    }

    exit_code = opcut_calculate(args.method, &params, &result);
    if (exit_code) {
        fprintf(stderr, "calculation error\n");
        goto cleanup;
    }

    exit_code = opcut_result_write(&result, output_stream);

cleanup:

    opcut_result_destroy(&result);
    opcut_params_destroy(&params);
    opcut_str_destroy(&json);
    if (output_stream)
        fclose(output_stream);
    if (input_stream)
        fclose(input_stream);

    return exit_code;
}
