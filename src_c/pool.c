#include <stdlib.h>
#include "pool.h"


#define PAGE_SIZE 4096


typedef struct header_t {
    struct header_t *next;
} header_t;


struct opcut_pool_t {
    hat_allocator_t *a;
    size_t item_size;
    header_t *blocks;
    header_t *items;
};


static void allocate_block(opcut_pool_t *pool) {
    size_t items_per_block =
        (PAGE_SIZE - sizeof(header_t)) / (sizeof(header_t) + pool->item_size);
    if (items_per_block < 1)
        items_per_block = 1;

    header_t *block = hat_allocator_alloc(
        pool->a, sizeof(header_t) +
                     items_per_block * (sizeof(header_t) + pool->item_size));
    if (!block)
        return;
    block->next = pool->blocks;
    pool->blocks = block;

    for (size_t i = 0; i < items_per_block; ++i) {
        header_t *header = (void *)block + sizeof(header_t) +
                           i * (sizeof(header_t) + pool->item_size);
        header->next = pool->items;
        pool->items = header;
    }
}


opcut_pool_t *opcut_pool_create(hat_allocator_t *a, size_t item_size) {
    opcut_pool_t *pool = hat_allocator_alloc(a, sizeof(opcut_pool_t));
    if (!pool)
        return NULL;

    if (item_size % sizeof(void *) != 0)
        item_size += sizeof(void *) - (item_size % sizeof(void *));

    pool->a = a;
    pool->item_size = item_size;
    pool->blocks = NULL;
    pool->items = NULL;

    return pool;
}


void opcut_pool_destroy(opcut_pool_t *pool) {
    while (pool->blocks) {
        header_t *block = pool->blocks;
        pool->blocks = block->next;
        hat_allocator_free(pool->a, block);
    }
    hat_allocator_free(pool->a, pool);
}


void *opcut_pool_alloc(opcut_pool_t *pool) {
    if (!pool->items)
        allocate_block(pool);

    if (!pool->items)
        return NULL;

    header_t *header = pool->items;
    pool->items = header->next;
    return header + 1;
}


void opcut_pool_free(opcut_pool_t *pool, void *item) {
    header_t *header = (header_t *)item - 1;
    header->next = pool->items;
    pool->items = header;
}
