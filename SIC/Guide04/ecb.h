void aes128_ecb_enc ( const void * ctx, const uint8_t * plaintext, const int plain_size, uint8_t * ciphertext );
void aes128_ecb_dec ( const void * ctx, const uint8_t * ciphertext, const int cipher_size, uint8_t * plaintext );

void aes128_encrypt_block(const void *ctx, const uint8_t *input, uint8_t *output);
void aes128_decrypt_block(const void *ctx, const uint8_t *input, uint8_t *output);
