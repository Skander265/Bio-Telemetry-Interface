#pragma once
#include <string>
#include <tuple>
#include <optional>
#include <vector>
#include <windows.h>

class SerialReader {
public:
    SerialReader() : hSerial(INVALID_HANDLE_VALUE) {}
    ~SerialReader();

    static std::optional<std::string> find_available_port();
    bool connect_serial(const std::string& port, int baudrate = 115200, int timeout = 1);
    std::tuple<long long, std::vector<float>> read_line();

private:
    HANDLE hSerial;
    std::string line_buffer;
};
