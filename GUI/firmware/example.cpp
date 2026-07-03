#include <Arduino.h>
#include "serial_manager.h"

namespace {

uint8_t clampToByte(int value) {
    if (value < 0) {
        return 0;
    }
    if (value > 255) {
        return 255;
    }
    return static_cast<uint8_t>(value);
}

class ExampleSerialManager : public SerialManager {
protected:
    bool onBlurLight(const uint8_t* inImage, uint8_t* outImage) override {
        // 3-tap horizontal box blur: average left, center, right.
        for (int y = 0; y < 20; ++y) {
            for (int x = 0; x < 20; ++x) {
                const int idx = (y * 20) + x;
                const int leftIdx = (y * 20) + (x > 0 ? x - 1 : x);
                const int rightIdx = (y * 20) + (x < 19 ? x + 1 : x);
                const int sum = inImage[leftIdx] + inImage[idx] + inImage[rightIdx];
                outImage[idx] = static_cast<uint8_t>(sum / 3);
            }
        }
        return true;
    }

    bool onBlurHeavy(const uint8_t* inImage, uint8_t* outImage) override {
        // 5-tap horizontal box blur for a stronger effect.
        for (int y = 0; y < 20; ++y) {
            for (int x = 0; x < 20; ++x) {
                int sum = 0;
                for (int dx = -2; dx <= 2; ++dx) {
                    int xx = x + dx;
                    if (xx < 0) {
                        xx = 0;
                    } else if (xx > 19) {
                        xx = 19;
                    }
                    sum += inImage[(y * 20) + xx];
                }
                outImage[(y * 20) + x] = static_cast<uint8_t>(sum / 5);
            }
        }
        return true;
    }

    bool onSharpen(const uint8_t* inImage, uint8_t* outImage) override {
        // Simple unsharp-like operation: center*2 - average(left,right).
        for (int y = 0; y < 20; ++y) {
            for (int x = 0; x < 20; ++x) {
                const int idx = (y * 20) + x;
                const int leftIdx = (y * 20) + (x > 0 ? x - 1 : x);
                const int rightIdx = (y * 20) + (x < 19 ? x + 1 : x);
                const int neighborAvg = (inImage[leftIdx] + inImage[rightIdx]) / 2;
                const int sharpened = (2 * static_cast<int>(inImage[idx])) - neighborAvg;
                outImage[idx] = clampToByte(sharpened);
            }
        }
        return true;
    }

    bool onProcessImage(const char* mode, const uint8_t* inImage, uint8_t* outImage) override {
        // Fallback for custom/unknown modes: just pass image through.
        (void)mode;
        memcpy(outImage, inImage, kImageSize);
        return true;
    }

    bool onClassifyImage(const uint8_t* inImage, char* outCsv, size_t outCsvLen) override {
        // Demo classifier: map average brightness to one "most likely" bucket.
        uint32_t sum = 0;
        for (size_t i = 0; i < kImageSize; ++i) {
            sum += inImage[i];
        }

        const uint8_t mean = static_cast<uint8_t>(sum / kImageSize);
        int predicted = (mean * 10) / 256;
        if (predicted > 9) {
            predicted = 9;
        }

        const float high = 0.70f;
        const float low = (1.0f - high) / 9.0f;

        size_t used = 0;
        for (int i = 0; i < 10; ++i) {
            const float score = (i == predicted) ? high : low;
            const int written = snprintf(
                outCsv + used,
                outCsvLen - used,
                (i < 9) ? "%.4f," : "%.4f",
                static_cast<double>(score)
            );

            if (written < 0 || static_cast<size_t>(written) >= (outCsvLen - used)) {
                return false;
            }
            used += static_cast<size_t>(written);
        }

        return true;
    }

    void onUnknownCommand(const char* command) override {
        sendError(String("Unsupported command in example: ") + command);
    }
};

ExampleSerialManager gSerialManager;

}  // namespace

void setup() {
    gSerialManager.begin(115200);
    Serial.println("Example serial manager ready");
}

void loop() {
    gSerialManager.update();
}
