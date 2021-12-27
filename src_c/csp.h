#ifndef OPCUT_CSP_H
#define OPCUT_CSP_H

#include <stddef.h>
#include "common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    OPCUT_METHOD_GREEDY,
    OPCUT_METHOD_FORWARD_GREEDY
} opcut_method_t;


int opcut_calculate(opcut_pool_t *used_pool, opcut_pool_t *unused_pool,
                    opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result);

#ifdef __cplusplus
}
#endif

#endif
