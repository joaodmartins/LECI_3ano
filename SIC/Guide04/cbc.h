void aes128_cbc_enc( void * ctx, const uint8_t * iv, const uint8_t * plaintext, const int plaintext_size, uint8_t * ciphertext );
void aes128_cbc_dec( void * ctx, const uint8_t * iv, const uint8_t * ciphertext, const int ciphertext_size, uint8_t * plaintext );

void aes128_block_enc(const void *ctx, const uint8_t *input, uint8_t *output);
void aes128_block_dec(const void *ctx, const uint8_t *input, uint8_t *output);
