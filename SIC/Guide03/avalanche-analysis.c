#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <memory.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <assert.h>

// gcc -O2 -Wall avalanche-analysis.c -o avalanche-analysis -lcrypto

#include <openssl/types.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/sha.h>

#ifndef MAX
#define MAX(x,y) (x > y ? x : y)
#endif

#define HASH_OUTPUT_MAX_BYTES   MAX( MD5_DIGEST_LENGTH, SHA256_DIGEST_LENGTH )
#define HASH_OUTPUT_MAX_BITS    (8 * HASH_OUTPUT_MAX_BYTES)
#define HASH_OUTPUT_BLOCK_SIZE  HASH_OUTPUT_MAX_BYTES

int bad_usage(const char *p) {
    fprintf(stderr, "Usage:\n\t%s M N\n\n"
                    "\tM: the size in bytes of the initial source message\n"
                    "\tN: the number of one-bit altered messages\n\n", p);
    return -2;
}

static int ones[16] = {
    0, 1, 1, 2,
    1, 2, 2, 3,
    1, 2, 2, 3,
    2, 3, 3, 4
};

// Count number of 1s in a byte
int count_1s(uint8_t c) {
    return ones[c & 0xF] + ones[c >> 4];
}

// Count differing bits between h1 and h2 over `size` bytes
int count_diff_bits(const uint8_t *h1, const uint8_t *h2, const uint32_t size) {
    int n = 0;
    for (int i = 0; i < size; i++) {
        n += count_1s(h1[i] ^ h2[i]);
    }
    assert(n <= 8 * size);
    return n;
}

// Modify a single random bit that hasn't been flipped yet
void change_me_a_bit(const uint8_t *source, const uint32_t source_size,
                     uint8_t *track_mods, uint8_t *working_buf)
{
    memcpy(working_buf, source, source_size);

    uint32_t bit_idx = rand() % (source_size * 8);
    uint32_t byte_idx = bit_idx / 8;
    uint32_t bit_offset = bit_idx % 8;
    uint8_t bit_mask = 1 << bit_offset;

    uint32_t tries = 0;
    while (track_mods[byte_idx] & bit_mask) {
        tries++;
        assert(tries < source_size * 8);
        bit_idx = (bit_idx + 1) % (source_size * 8);
        byte_idx = bit_idx / 8;
        bit_offset = bit_idx % 8;
        bit_mask = 1 << bit_offset;
    }

    working_buf[byte_idx] ^= bit_mask;
    track_mods[byte_idx] |= bit_mask;

    assert(count_diff_bits(source, working_buf, source_size) == 1);
}

// Modify a single random byte that hasn't been flipped yet
void change_me_a_byte(const uint8_t *source, const uint32_t source_size,
                      uint8_t *track_mods, uint8_t *working_buf)
{
    memcpy(working_buf, source, source_size);

    uint32_t byte_idx = rand() % source_size;
    uint32_t tries = 0;

    while (track_mods[byte_idx]) {
        tries++;
        assert(tries < source_size);
        byte_idx = (byte_idx + 1) % source_size;
    }

    working_buf[byte_idx] ^= 0xFF; // flip all bits in the byte
    track_mods[byte_idx] = 1;

    uint32_t diff_count = 0;
    for (uint32_t i = 0; i < source_size; i++) {
        if (source[i] != working_buf[i]) diff_count++;
    }
    assert(diff_count == 1);
}

// Generate SHA-256 hash
void sha256(const uint8_t *data, const uint32_t data_size, uint8_t *output_hash)
{
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit(ctx, EVP_sha256());
    EVP_DigestUpdate(ctx, data, data_size);
    EVP_DigestFinal(ctx, output_hash, NULL);
    EVP_MD_CTX_free(ctx);
}

// Generate MD5 hash
void md5(const uint8_t *data, const uint32_t data_size, uint8_t *output_hash)
{
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit(ctx, EVP_md5());
    EVP_DigestUpdate(ctx, data, data_size);
    EVP_DigestFinal(ctx, output_hash, NULL);
    EVP_MD_CTX_free(ctx);
}

int main(int argc, char *argv[])
{
    if (argc != 3)
        return bad_usage(argv[0]);

    uint32_t source_size, n_variations;
    assert(sscanf(argv[1], "%d", &source_size));
    assert(sscanf(argv[2], "%d", &n_variations));

    fprintf(stderr, "Working with M=%d and N=%d...\n", source_size, n_variations);
    assert(n_variations <= source_size * 8);

    // Seed rand()
    srand(time(NULL));

    uint32_t histogram[HASH_OUTPUT_MAX_BITS + 1] = {0};

    // Allocate buffers
    uint8_t *source = malloc(source_size);
    uint8_t *bit_mod = malloc(source_size);
    uint8_t *track_mods = calloc(source_size, 1); // bit-level for bits

    assert(source && bit_mod && track_mods);

    // Fill `source` with random bytes
    int fd = open("/dev/urandom", O_RDONLY);
    assert(fd >= 0);
    assert(read(fd, source, source_size) == source_size);
    close(fd);

    uint8_t source_hash[HASH_OUTPUT_BLOCK_SIZE];
    uint8_t bit_mod_hash[HASH_OUTPUT_BLOCK_SIZE];
    const int size_of_hash = SHA256_DIGEST_LENGTH;

    sha256(source, source_size, source_hash);

    // Generate N variations and collect avalanche statistics
    for (uint32_t i = 0; i < n_variations; i++) {
        change_me_a_bit(source, source_size, track_mods, bit_mod);
        sha256(bit_mod, source_size, bit_mod_hash);

        int diff = count_diff_bits(source_hash, bit_mod_hash, size_of_hash);
        histogram[diff]++;
    }

    printf("The results are...\n");
    for (int i = 0; i <= size_of_hash * 8; i++) {
        if (histogram[i] > 0)
            printf("%3d %d\n", i, histogram[i]);
    }

    free(source);
    free(bit_mod);
    free(track_mods);

    return 0;
}
