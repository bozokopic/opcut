#ifndef OPCUT_POOL_H
#define OPCUT_POOL_H

#include <stddef.h>
#include "common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    OPCUT_METHOD_GREEDY,
    OPCUT_METHOD_FORWARD_GREEDY
} opcut_method_t;

void opcut_sort_params(opcut_params_t *params);
int opcut_calculate(opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result);

#ifdef __cplusplus
}
#endif

#endif
