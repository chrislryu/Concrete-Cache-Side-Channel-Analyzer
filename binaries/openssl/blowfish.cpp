#include <openssl/blowfish.h>
#include <unistd.h>
#include <cstdlib>
#include <iostream>

#define DATA_LENGTH 8
#define KEY_LENGTH 8

int main()
{
    unsigned char keyStr[KEY_LENGTH] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
    unsigned char in[DATA_LENGTH] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
    unsigned char out[DATA_LENGTH];

    std::cout << "reading key" << std::endl;

    read(0, keyStr, 8); //stdin

    std::cout << "allocating memory for key" << std::endl;

    BF_KEY *key = (BF_KEY*)malloc(sizeof(BF_KEY));

    std::cout << "setting up key" << std::endl;

    BF_set_key(key, KEY_LENGTH, keyStr);

    std::cout << "computing encryption" << std::endl;

    BF_ecb_encrypt(in, out, key, BF_ENCRYPT);

    std::cout << "finished encryption" << std::endl;
}
