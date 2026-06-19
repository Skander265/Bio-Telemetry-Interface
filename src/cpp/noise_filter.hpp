#pragma once
#include <deque>
#include <numeric>

class MovingAverageFilter {
public:
    MovingAverageFilter(int window_size = 5) : window_size_(window_size) {}

    float apply(float value) {
        if (buffer_.size() >= window_size_) {
            buffer_.pop_front();
        }
        buffer_.push_back(value);
        
        float sum = std::accumulate(buffer_.begin(), buffer_.end(), 0.0f);
        return sum / buffer_.size();
    }

private:
    int window_size_;
    std::deque<float> buffer_;
};
