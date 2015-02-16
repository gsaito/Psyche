/* pcrypt.c */
// gcc cipher.c -o a.out -lsocket -L /usr/lib/happycoders/

#include <stdlib.h>
#include <string.h>

#include <stdio.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define BUFFER_SIZE 256

#define PKEY_SIZE 29

static const char encrypt_key[PKEY_SIZE + 1] = "Poshel-ka ti na hui drug aver";
static const char decrypt_key[PKEY_SIZE + 1] = "reva gurd iuh an it ak-lehsoP";

static void pcrypt_block(const char key[], char block[]) {
  size_t i;
  unsigned char t;

  /* xor */
  for(i = 0; i < PKEY_SIZE; i++) block[i] ^= key[i];

  /* rot */
  for(i = 0; i < PKEY_SIZE / 2; i++) {
    t = block[i];
    block[i] = block[PKEY_SIZE - 1 - i];
    block[PKEY_SIZE - 1 - i] = t;
  }

} /* crypt_block */

static void pcrypt(const char key[], char *buf, size_t size) {
  size_t i, off;

  for(off = 0; off + PKEY_SIZE < size; off += PKEY_SIZE) {
    pcrypt_block(key, &buf[off]);

    /* neg */
    if(off & 1)
      for(i = 0; i < PKEY_SIZE; i++) {
        buf[off + i] ^= 0xff;
      }
  }

  if((size %= PKEY_SIZE))
    for(i = 0; i < size; i++) {
      //printf("[*] buf[%lu] = %d = %c\n", off+i, buf[off+i] ^ 0xff, buf[off+i] ^ 0xff);
      buf[off + i] ^= 0xff;
    }

} /* pcrypt */

void pencrypt(char *buf, size_t size) {
  pcrypt(encrypt_key, buf, size);
} /* pencrypt */

void pdecrypt(char *buf, size_t size) {
  pcrypt(decrypt_key, buf, size);
} /* pdecrypt */


int main() {
    // IP address, port, socket
    char destination[80];
    unsigned short port = 9876;
    int dstSocket;

    // Socket addr structure
    struct sockaddr_in dstAddr;

    // Parameters
    int status;
    int numsnt;

    // Enter target address
    //printf("Connect to ? (name or IP address) > ");
    //scanf("%s", destination);
    strcpy(destination, "127.0.0.1");

    // Set socket addr structure
    memset(&dstAddr, 0, sizeof(dstAddr));
    dstAddr.sin_port = htons(port);
    dstAddr.sin_family = AF_INET;
    dstAddr.sin_addr.s_addr = inet_addr(destination);

    // Create socket
    dstSocket = socket(AF_INET, SOCK_STREAM, 0);

    // Connect
    printf("[*] Trying to connect to %s:9876\n", destination);
    connect(dstSocket, (struct sockaddr *) &dstAddr, sizeof(dstAddr));

    // Message
    //char *message = malloc(sizeof(char) * 128);
    //strcpy(message, "Richard Of York Gave Battle In Vain");
    char message[256];
    printf("[*] Enter message to encrypt and send > ");
    scanf("%[^\n]", message);
    size_t message_len = strlen(message);
    pencrypt(message, message_len);
    //printf("Encrypted message:\n%s\n", message);
    //pdecrypt(message, message_len);
    //printf("Decrypted message:\n%s\n", message);

    // Send packet
    printf("[*] Sending...\n");
    send(dstSocket, message, message_len, 0);
    sleep(1);

    // Close socket
    close(dstSocket);

    return 0;
}

