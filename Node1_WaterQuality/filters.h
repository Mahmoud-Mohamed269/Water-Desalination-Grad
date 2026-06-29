#ifndef FILTERS_H
#define FILTERS_H

#include <Arduino.h>

// ============================================================
// 1D Kalman Filter
// ============================================================
class KalmanFilter {
private:
    float _q; // Process noise covariance
    float _r; // Measurement noise covariance
    float _x; // Value
    float _p; // Estimation error covariance
    float _k; // Kalman gain

public:
    KalmanFilter(float q, float r, float p, float intial_value) {
        _q = q;
        _r = r;
        _p = p;
        _x = intial_value;
    }

    float update(float measurement) {
        // Prediction update
        _p = _p + _q;

        // Measurement update
        _k = _p / (_p + _r);
        _x = _x + _k * (measurement - _x);
        _p = (1 - _k) * _p;

        return _x;
    }
    
    void setInitial(float value) {
        _x = value;
    }
};

// ============================================================
// Moving Average Filter
// ============================================================
class MovingAverage {
private:
    float* _buffer;
    uint8_t _windowSize;
    uint8_t _index;
    uint8_t _count;
    float _sum;

public:
    MovingAverage(uint8_t windowSize) {
        _windowSize = windowSize;
        _buffer = new float[windowSize];
        _index = 0;
        _count = 0;
        _sum = 0;
    }

    ~MovingAverage() {
        delete[] _buffer;
    }

    float update(float measurement) {
        if (_count < _windowSize) {
            _count++;
        } else {
            _sum -= _buffer[_index];
        }

        _buffer[_index] = measurement;
        _sum += measurement;
        
        _index = (_index + 1) % _windowSize;

        return _sum / _count;
    }
    
    void reset() {
        _count = 0;
        _index = 0;
        _sum = 0;
    }
};

// ============================================================
// Median Filter (5-sample)
// ============================================================
class MedianFilter {
private:
    float _buffer[5];
    uint8_t _index;

    void sort(float* arr, uint8_t n) {
        for (uint8_t i = 1; i < n; i++) {
            float key = arr[i];
            int8_t j = i - 1;
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j = j - 1;
            }
            arr[j + 1] = key;
        }
    }

public:
    MedianFilter() {
        _index = 0;
        for(int i=0; i<5; i++) _buffer[i] = 0;
    }

    float update(float measurement) {
        _buffer[_index] = measurement;
        _index = (_index + 1) % 5;

        float sorted[5];
        for (uint8_t i = 0; i < 5; i++) {
            sorted[i] = _buffer[i];
        }

        sort(sorted, 5);
        return sorted[2]; // Return median
    }
};

#endif // FILTERS_H
