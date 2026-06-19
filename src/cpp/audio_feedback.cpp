#include "audio_feedback.hpp"
#include <windows.h>
#include <iostream>

AudioSynthesizer::AudioSynthesizer() {
}

AudioSynthesizer::~AudioSynthesizer() {
    stop();
}

void AudioSynthesizer::start() {
    if (!active_) {
        active_ = true;
        running_ = true;
        thread_ = std::thread(&AudioSynthesizer::audio_loop, this);
        std::cout << "Audio Engine Started\n";
    }
}

void AudioSynthesizer::stop() {
    running_ = false;
    active_ = false;
    if (thread_.joinable()) {
        thread_.join();
    }
}

void AudioSynthesizer::update_voltage(float voltage) {
    current_voltage_ = voltage;
}

void AudioSynthesizer::audio_loop() {
    while (running_) {
        float voltage = current_voltage_.load();
        int target_freq = static_cast<int>(100.0f + (voltage * 300.0f));
        
        if (target_freq < 40) target_freq = 40;
        if (target_freq > 5000) target_freq = 5000;
        
        Beep(target_freq, 100);
        
        // Minor sleep to prevent thread thrashing if Beep returns immediately or to space them
        Sleep(10);
    }
}
