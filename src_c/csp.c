#include "csp.h"


int opcut_calculate(opcut_method_t method, opcut_params_t *params,
                    opcut_result_t *result) {

    result->params = params;
    result->used = NULL;
    result->used_len = 0;
    result->unused = NULL;
    result->unused_len = 0;

    return OPCUT_SUCCESS;
}
