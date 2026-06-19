#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "noise_filter.hpp"
#include "serial_reader.hpp"
#include "audio_feedback.hpp"
#include "signal_analyst.hpp"

namespace py = pybind11;

PYBIND11_MODULE(bio_core_cpp, m) {
    m.doc() = "C++ Core Modules for Bio-Telemetry Interface"; // optional module docstring

    py::class_<MovingAverageFilter>(m, "MovingAverageFilter")
        .def(py::init<int>(), py::arg("window_size") = 5)
        .def("apply", &MovingAverageFilter::apply);

    py::class_<SerialReader>(m, "SerialReader")
        .def(py::init<>())
        .def_static("find_available_port", []() -> py::object {
            auto port = SerialReader::find_available_port();
            if (port) {
                return py::str(*port);
            }
            return py::none();
        })
        .def("connect_serial", &SerialReader::connect_serial, 
             py::arg("port"), py::arg("baudrate") = 115200, py::arg("timeout") = 1)
        .def("read_line", [](SerialReader& self) -> py::object {
            auto [t, v] = self.read_line();
            if (t == 0) {
                return py::make_tuple(py::none(), py::none());
            }
            return py::make_tuple(t, v);
        });

    py::class_<AudioSynthesizer>(m, "AudioSynthesizer")
        .def(py::init<>())
        .def("start", &AudioSynthesizer::start)
        .def("stop", &AudioSynthesizer::stop)
        .def("update_voltage", &AudioSynthesizer::update_voltage);

    py::class_<SignalAnalyst>(m, "SignalAnalyst")
        .def(py::init<const std::string&>(), py::arg("sensor_id") = "default")
        .def("update", [](SignalAnalyst& self, float voltage) -> py::dict {
            auto result_map = self.update(voltage);
            py::dict d;
            for (const auto& kv : result_map) {
                if (std::holds_alternative<std::string>(kv.second)) {
                    d[kv.first.c_str()] = std::get<std::string>(kv.second);
                } else if (std::holds_alternative<float>(kv.second)) {
                    d[kv.first.c_str()] = std::get<float>(kv.second);
                } else if (std::holds_alternative<int>(kv.second)) {
                    d[kv.first.c_str()] = std::get<int>(kv.second);
                }
            }
            return d;
        });
}
