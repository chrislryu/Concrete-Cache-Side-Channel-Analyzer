#include <openssl/evp.h>
#include <openssl/aes.h>
#include <unistd.h>

int main(int argc, char **argv) {
    EVP_CIPHER_CTX* en = EVP_CIPHER_CTX_new();
    unsigned int salt[] = {12345, 54321};
    unsigned char data[1] = {'a'};
    int dataLen = 1;
    unsigned char keyData[1] = {'a'};
    int keyDataLen = 1;

    int i, nrounds = 5;
    unsigned char key[32], iv[32];
    i = EVP_BytesToKey(EVP_aes_256_cbc(), EVP_sha1(), (unsigned char *) salt, key, keyDataLen, nrounds, key, iv);
    if (i != 32) {
        return -1;
    }
    EVP_CIPHER_CTX_init(en);
    EVP_EncryptInit_ex(en, EVP_aes_256_cbc(), NULL, key, iv);

    int c_len = dataLen + AES_BLOCK_SIZE, f_len = 0;
    unsigned char *ciphertext = (unsigned char *)malloc(c_len);
    EVP_EncryptInit_ex(en, NULL, NULL, NULL, NULL);
    EVP_EncryptUpdate(en, ciphertext, &c_len, data, dataLen);
    EVP_EncryptFinal_ex(en, ciphertext+c_len, &f_len);

    EVP_CIPHER_CTX_free(en);

    return 0;
}