#pragma once
#include <thread>
#include <atomic>

class AudioSynthesizer {
public:
    AudioSynthesizer();
    ~AudioSynthesizer();

    void start();
    void stop();
    void update_voltage(float voltage);

private:
    void audio_loop();

    std::atomic<bool> active_{false};
    std::atomic<bool> running_{false};
    std::atomic<float> current_voltage_{0.5f};
    std::thread thread_;
};
