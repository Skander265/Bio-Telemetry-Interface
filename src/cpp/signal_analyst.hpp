#pragma once
#include <string>
#include <vector>
#include <map>
#include <variant>

struct AnalystResult {
    std::string type;
    std::string message;
    float peak;
    int duration;
};

class SignalAnalyst {
public:
    SignalAnalyst(const std::string& sensor_id = "default");

    std::map<std::string, std::variant<std::string, float, int>> update(float voltage);

private:
    std::string sensor_id_;
    std::string model_filename_;
    
    float threshold_;
    int min_samples_;
    
    bool recording_;
    std::vector<float> buffer_;
    
    bool is_calibrated_;
    std::vector<std::vector<float>> calibration_data_;
    
    // Statistical model params
    std::vector<float> feature_means_;
    std::vector<float> feature_stds_;

    std::map<std::string, std::variant<std::string, float, int>> process_event(const std::vector<float>& raw_signal);
    std::vector<float> extract_features(const std::vector<float>& signal);
    
    void fit_model();
    void save_model();
    bool load_model();
};
