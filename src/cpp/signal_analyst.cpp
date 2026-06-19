#include "signal_analyst.hpp"
#include <iostream>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <fstream>

SignalAnalyst::SignalAnalyst(const std::string& sensor_id) 
    : sensor_id_(sensor_id), 
      threshold_(0.8f), 
      min_samples_(15), 
      recording_(false), 
      is_calibrated_(false) 
{
    model_filename_ = "models/model_" + sensor_id_ + ".txt"; // Using text file instead of pkl
    
    if (load_model()) {
        std::cout << "[" << sensor_id_ << "] System Startup: Loading statistical model from disk...\n";
        is_calibrated_ = true;
    } else {
        std::cout << "[" << sensor_id_ << "] System Startup: No existing model found. initializing new statistical baseline.\n";
        is_calibrated_ = false;
    }
}

std::map<std::string, std::variant<std::string, float, int>> SignalAnalyst::update(float voltage) {
    if (!recording_) {
        if (voltage > threshold_) {
            recording_ = true;
            buffer_.clear();
            buffer_.push_back(voltage);
            return {{"type", "Recording"}};
        }
        return {{"type", "Scanning"}};
    } else {
        buffer_.push_back(voltage);
        
        bool signal_drop = (buffer_.size() > 10 && voltage < threshold_);
        bool timeout = buffer_.size() > 100;
        
        if (signal_drop || timeout) {
            auto result = process_event(buffer_);
            recording_ = false;
            buffer_.clear();
            return result;
        }
        
        return {{"type", "Recording"}};
    }
}

std::vector<float> SignalAnalyst::extract_features(const std::vector<float>& signal) {
    if (signal.empty()) return {0.0f, 0.0f, 0.0f};

    float peak = *std::max_element(signal.begin(), signal.end());
    
    float energy = 0.0f;
    for (float v : signal) {
        energy += v * v;
    }
    
    auto peak_it = std::max_element(signal.begin(), signal.end());
    int peak_index = std::distance(signal.begin(), peak_it);
    float rise_time = peak_index > 0 ? static_cast<float>(peak_index) : 1.0f;
    
    return {peak, energy, rise_time};
}

std::map<std::string, std::variant<std::string, float, int>> SignalAnalyst::process_event(const std::vector<float>& raw_signal) {
    std::vector<float> features = extract_features(raw_signal);
    
    if (!is_calibrated_) {
        calibration_data_.push_back(features);
        int samples_remaining = min_samples_ - calibration_data_.size();
        
        if (samples_remaining <= 0) {
            std::cout << "[" << sensor_id_ << "] Calibration Limit Reached. Fitting model to baseline data...\n";
            fit_model();
            save_model();
            
            return {
                {"type", "CALIBRATION_COMPLETE"},
                {"peak", features[0]},
                {"duration", static_cast<int>(raw_signal.size())}
            };
        }
        
        return {
            {"type", "CALIBRATING"},
            {"message", "Acquiring Baseline"},
            {"peak", features[0]},
            {"duration", static_cast<int>(raw_signal.size())}
        };
    } else {
        // INFERENCE: Statistical Z-score approach
        float max_z_score = 0.0f;
        for (size_t i = 0; i < features.size() && i < feature_means_.size(); ++i) {
            float mean = feature_means_[i];
            float std = feature_stds_[i] > 0.0001f ? feature_stds_[i] : 0.0001f;
            float z = std::abs(features[i] - mean) / std;
            if (z > max_z_score) {
                max_z_score = z;
            }
        }
        
        // Z-score > 3.0 is a common threshold for anomalies
        if (max_z_score > 3.0f) {
            return {
                {"type", "ALARM"},
                {"message", "Anomaly Detected (Score: " + std::to_string(max_z_score) + ")"},
                {"peak", features[0]},
                {"duration", static_cast<int>(raw_signal.size())}
            };
        } else {
            return {
                {"type", "IGNORE"},
                {"message", "Baseline Signal"},
                {"peak", features[0]},
                {"duration", static_cast<int>(raw_signal.size())}
            };
        }
    }
}

void SignalAnalyst::fit_model() {
    if (calibration_data_.empty()) return;
    
    int num_features = calibration_data_[0].size();
    feature_means_.assign(num_features, 0.0f);
    feature_stds_.assign(num_features, 0.0f);
    
    int n = calibration_data_.size();
    
    // Mean
    for (const auto& row : calibration_data_) {
        for (int i = 0; i < num_features; ++i) {
            feature_means_[i] += row[i];
        }
    }
    for (int i = 0; i < num_features; ++i) {
        feature_means_[i] /= n;
    }
    
    // Std Dev
    for (const auto& row : calibration_data_) {
        for (int i = 0; i < num_features; ++i) {
            float diff = row[i] - feature_means_[i];
            feature_stds_[i] += diff * diff;
        }
    }
    for (int i = 0; i < num_features; ++i) {
        feature_stds_[i] = std::sqrt(feature_stds_[i] / n);
    }
    
    is_calibrated_ = true;
}

void SignalAnalyst::save_model() {
    std::ofstream out(model_filename_);
    if (out.is_open() && !feature_means_.empty()) {
        for (float m : feature_means_) out << m << " ";
        out << "\n";
        for (float s : feature_stds_) out << s << " ";
        out << "\n";
        std::cout << "[" << sensor_id_ << "] Model Serialized to " << model_filename_ << "\n";
    }
}

bool SignalAnalyst::load_model() {
    std::ifstream in(model_filename_);
    if (!in.is_open()) return false;
    
    feature_means_.clear();
    feature_stds_.clear();
    
    std::string line;
    if (std::getline(in, line)) {
        size_t pos = 0;
        while (pos < line.length()) {
            size_t next_space = line.find(' ', pos);
            if (next_space == std::string::npos) next_space = line.length();
            if (next_space > pos) {
                feature_means_.push_back(std::stof(line.substr(pos, next_space - pos)));
            }
            pos = next_space + 1;
        }
    }
    
    if (std::getline(in, line)) {
        size_t pos = 0;
        while (pos < line.length()) {
            size_t next_space = line.find(' ', pos);
            if (next_space == std::string::npos) next_space = line.length();
            if (next_space > pos) {
                feature_stds_.push_back(std::stof(line.substr(pos, next_space - pos)));
            }
            pos = next_space + 1;
        }
    }
    
    return feature_means_.size() == 3 && feature_stds_.size() == 3;
}
