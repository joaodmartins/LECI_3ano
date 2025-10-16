// Helper file for SIC Lab on Symmetric Cryptography

#include <stdint.h>
#include <memory.h>
#include <assert.h>

#include "aes.h"
#include "cbc.h"

void
aes128_cbc_enc( void * ctx, const uint8_t * iv, const uint8_t * plaintext, const int plain_size, uint8_t * ciphertext )
{
    assert( ctx != 0 && iv != 0 && plaintext != 0 && ciphertext != 0);
    assert( plain_size % 16 == 0 );
// TODO: add your code here
    uint8_t prev_block[16];
    memcpy(prev_block, iv, 16);

    for (int i = 0; i < plain_size; i += 16)
    {
        uint8_t block[16];

        for (int j = 0; j < 16; j++) {
            block[j] = plaintext[i + j] ^ prev_block[j];
        }

        aes128_block_enc(ctx, block, ciphertext + i);

        memcpy(prev_block, ciphertext +i, 16);
    }
// until here
}

void
aes128_cbc_dec( void * ctx, const uint8_t * iv, const uint8_t * ciphertext, const int cipher_size, uint8_t * plaintext )
{
    assert( ctx != 0 && iv != 0 && plaintext != 0 && ciphertext != 0);
    assert( cipher_size % 16 == 0);
// TODO: add your code here
    uint8_t prev_block[16];
    memcpy(prev_block, iv, 16);

    for (int i = 0; i < cipher_size; i += 16)
    {
        uint8_t block[16];

        aes128_block_dec(ctx, block, plaintext + i);

        for (int j = 0; j < 16; j++) {
            plaintext[i + j] = block[j] ^ prev_block[j];
        }

        memcpy(prev_block, ciphertext +i, 16);
    }
// until here
}
