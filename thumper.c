#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#define MAX_IP_LEN 16

void* ping_ip(void* arg) {
    char ip[MAX_IP_LEN];
    snprintf(ip, MAX_IP_LEN, "%s", (char*)arg);
    
    // Ping the IP
    char ping_command[50];
    snprintf(ping_command, 50, "ping -c 1 %s", ip);
    int result = system(ping_command);

    if (result == 0) {
        printf("%s is reachable\n", ip);
        pthread_exit(NULL);
    } else {
        printf("%s is unreachable\n", ip);
        pthread_exit(NULL);
    }
}

int main() {
    // List of IP addresses to ping
    char* ips[] = {"192.168.1.1", "192.168.1.2", "192.168.1.3"};

    // Number of IP addresses
    int num_ips = sizeof(ips) / sizeof(ips[0]);

    pthread_t threads[num_ips];

    // Create threads for each IP address
    for (int i = 0; i < num_ips; i++) {
        pthread_create(&threads[i], NULL, ping_ip, (void*)ips[i]);
    }

    // Wait for threads to finish
    for (int i = 0; i < num_ips; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
