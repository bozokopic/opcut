#ifndef OPCUT_POOL_H
#define OPCUT_POOL_H

#include <stddef.h>
#include <hat/allocator.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct opcut_pool_t opcut_pool_t;

opcut_pool_t *opcut_pool_create(hat_allocator_t *a, size_t item_size);
void opcut_pool_destroy(opcut_pool_t *pool);
void *opcut_pool_alloc(opcut_pool_t *pool);
void opcut_pool_free(opcut_pool_t *pool, void *item);

#ifdef __cplusplus
}
#endif

#endif
