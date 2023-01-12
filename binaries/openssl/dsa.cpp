#include <openssl/dsa.h>
#include <openssl/pem.h>
#include <unistd.h>

int main(int argc, char **argv) {
    int padding = RSA_PKCS1_PADDING;

    int dataLen = 20;
    unsigned char data[20];
    unsigned char encrypted[4096] {};
    char publicKey[426];

    read(0, data, 20);
    read(20, publicKey, 20);

    RSA *rsa;
    BIO *keybio;
    keybio = BIO_new_mem_buf(publicKey, -1);

    rsa = PEM_read_bio_RSAPrivateKey(keybio, &rsa, NULL, NULL);

    return RSA_private_decrypt(dataLen, data, encrypted, rsa, padding);
}