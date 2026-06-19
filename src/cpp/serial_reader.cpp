#include "serial_reader.hpp"
#include <iostream>
#include <vector>
#include <sstream>

SerialReader::~SerialReader() {
    if (hSerial != INVALID_HANDLE_VALUE) {
        CloseHandle(hSerial);
    }
}

std::optional<std::string> SerialReader::find_available_port() {
    for (int i = 1; i <= 256; ++i) {
        std::string port_name = "COM" + std::to_string(i);
        std::string full_path = "\\\\.\\" + port_name;
        HANDLE hTest = CreateFileA(full_path.c_str(), GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
        if (hTest != INVALID_HANDLE_VALUE) {
            CloseHandle(hTest);
            return port_name;
        } else {
            DWORD err = GetLastError();
            if (err == ERROR_ACCESS_DENIED) {
                return port_name;
            }
        }
    }
    return std::nullopt;
}

bool SerialReader::connect_serial(const std::string& port, int baudrate, int timeout) {
    std::string full_path = "\\\\.\\" + port;
    hSerial = CreateFileA(full_path.c_str(), GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hSerial == INVALID_HANDLE_VALUE) {
        return false;
    }

    DCB dcbSerialParams = {0};
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
    if (!GetCommState(hSerial, &dcbSerialParams)) {
        CloseHandle(hSerial);
        hSerial = INVALID_HANDLE_VALUE;
        return false;
    }

    dcbSerialParams.BaudRate = baudrate;
    dcbSerialParams.ByteSize = 8;
    dcbSerialParams.StopBits = ONESTOPBIT;
    dcbSerialParams.Parity   = NOPARITY;
    if (!SetCommState(hSerial, &dcbSerialParams)) {
        CloseHandle(hSerial);
        hSerial = INVALID_HANDLE_VALUE;
        return false;
    }

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 50;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 50;
    timeouts.WriteTotalTimeoutMultiplier = 10;
    SetCommTimeouts(hSerial, &timeouts);

    PurgeComm(hSerial, PURGE_RXCLEAR | PURGE_TXCLEAR);
    Sleep(2000); 
    PurgeComm(hSerial, PURGE_RXCLEAR | PURGE_TXCLEAR);

    return true;
}

std::tuple<long long, std::vector<float>> SerialReader::read_line() {
    if (hSerial == INVALID_HANDLE_VALUE) {
        return {0, {}};
    }

    char buf[128];
    DWORD bytesRead;
    std::string current_line = "";

    while (true) {
        if (ReadFile(hSerial, buf, 1, &bytesRead, NULL) && bytesRead > 0) {
            char c = buf[0];
            if (c == '\n') {
                break;
            }
            if (c != '\r') {
                current_line += c;
            }
        } else {
            break;
        }
    }

    if (current_line.empty() || current_line.find("timestamp") != std::string::npos) {
        return {0, {}};
    }

    size_t comma_idx = current_line.find(',');
    if (comma_idx != std::string::npos) {
        try {
            std::string timestamp_str = current_line.substr(0, comma_idx);
            long long timestamp = std::stoll(timestamp_str);
            
            std::vector<float> voltages;
            std::stringstream ss(current_line.substr(comma_idx + 1));
            std::string item;
            while (std::getline(ss, item, ',')) {
                float v_mv = std::stof(item);
                voltages.push_back(v_mv / 1000.0f);
            }
            
            return {timestamp, voltages};
        } catch (...) {
            // parsing error
        }
    }
    
    return {0, {}};
}
