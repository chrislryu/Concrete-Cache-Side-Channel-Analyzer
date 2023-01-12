#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/bio.h>
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

    rsa = PEM_read_bio_RSA_PUBKEY(keybio, &rsa, NULL, NULL);

    return RSA_public_encrypt(dataLen, data, encrypted, rsa, padding);
}