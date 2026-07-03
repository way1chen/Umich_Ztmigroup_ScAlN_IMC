#pragma once

#include <Arduino.h>
#include <stdint.h>
#include <string.h>

// MCU-side parser for the GUI serial protocol.
//
// Supported requests from GUI:
// 1) PROCESS\n<MODE>\n<400 raw grayscale bytes>
// 2) CLASSIFY\n<400 raw grayscale bytes>
//
// Expected responses to GUI:
// - Processing success: "OK|400\n" + 400 bytes payload
// - Classification success: "OK\n" + "v0,v1,...,v9\n"
// - Error: "ERROR:<message>\n"
class SerialManager {
public:
    static constexpr size_t kImageSize = 400;
    static constexpr size_t kMaxCommandLen = 32;
    static constexpr size_t kMaxModeLen = 32;
    static constexpr size_t kMaxClassifyCsvLen = 160;

    explicit SerialManager(char lineTerminator = '\n')
        : _state(State::AwaitCommand),
          _lineTerminator(lineTerminator),
          _lineIndex(0),
          _imageIndex(0) {
        _lineBuffer[0] = '\0';
        _processMode[0] = '\0';
    }

    void begin(unsigned long baudRate) {
        Serial.begin(baudRate);
        resetParser();
    }

    // Call frequently from loop(); this is non-blocking.
    void update() {
        while (Serial.available() > 0) {
            const uint8_t byteIn = static_cast<uint8_t>(Serial.read());

            if (_state == State::AwaitProcessPayload || _state == State::AwaitClassifyPayload) {
                consumeImageByte(byteIn);
            } else {
                consumeLineByte(byteIn);
            }
        }
    }

protected:
    // Override this to implement processing. Must write exactly 400 bytes to
    // outImage on success. Return true for success, false for protocol error.
    virtual bool onProcessImage(const char* mode, const uint8_t* inImage, uint8_t* outImage) {
        // Default behavior mirrors input to output to keep protocol testable.
        (void)mode;
        memcpy(outImage, inImage, kImageSize);
        return true;
    }

    // Optional mode-specific hooks. Override only what you need.
    virtual bool onBlurLight(const uint8_t* inImage, uint8_t* outImage) {
        memcpy(outImage, inImage, kImageSize);
        return true;
    }

    virtual bool onBlurHeavy(const uint8_t* inImage, uint8_t* outImage) {
        memcpy(outImage, inImage, kImageSize);
        return true;
    }

    virtual bool onSharpen(const uint8_t* inImage, uint8_t* outImage) {
        memcpy(outImage, inImage, kImageSize);
        return true;
    }

    // Override this to implement classification.
    // Write CSV with 10 floats ("p0,p1,...,p9") into outCsv.
    virtual bool onClassifyImage(const uint8_t* inImage, char* outCsv, size_t outCsvLen) {
        (void)inImage;
        if (outCsvLen == 0) {
            return false;
        }
        const char* defaultCsv = "0,0,0,0,0,0,0,0,0,0";
        if (strlen(defaultCsv) + 1 > outCsvLen) {
            return false;
        }
        strcpy(outCsv, defaultCsv);
        return true;
    }

    // Optional hook for unknown top-level commands.
    virtual void onUnknownCommand(const char* command) {
        sendError(String("Unknown command: ") + command);
    }

    // Optional hook for protocol errors (framing, invalid mode, etc.).
    virtual void onProtocolError(const char* message) {
        sendError(message);
    }

    // Helpers for derived classes when they want to send manual responses.
    void sendOk() {
        Serial.println("OK");
    }

    void sendError(const String& message) {
        Serial.print("ERROR:");
        Serial.println(message);
    }

    void sendProcessedImage(const uint8_t* image, size_t len = kImageSize) {
        if (len != kImageSize) {
            sendError("Internal error: invalid image length");
            return;
        }
        Serial.println("OK|400");
        Serial.write(image, kImageSize);
    }

    void sendClassificationCsv(const char* csv) {
        Serial.println("OK");
        Serial.println(csv);
    }

private:
    enum class State {
        AwaitCommand,
        AwaitProcessMode,
        AwaitProcessPayload,
        AwaitClassifyPayload,
    };

    State _state;
    char _lineTerminator;

    char _lineBuffer[kMaxCommandLen + 1];
    size_t _lineIndex;

    char _processMode[kMaxModeLen + 1];

    uint8_t _imageBuffer[kImageSize];
    size_t _imageIndex;

    static bool equalsNoCase(const char* a, const char* b) {
        while (*a != '\0' && *b != '\0') {
            const char ca = static_cast<char>(toupper(*a));
            const char cb = static_cast<char>(toupper(*b));
            if (ca != cb) {
                return false;
            }
            ++a;
            ++b;
        }
        return *a == '\0' && *b == '\0';
    }

    void resetLineBuffer() {
        _lineIndex = 0;
        _lineBuffer[0] = '\0';
    }

    void resetParser() {
        _state = State::AwaitCommand;
        _imageIndex = 0;
        _processMode[0] = '\0';
        resetLineBuffer();
    }

    void consumeLineByte(uint8_t byteIn) {
        if (byteIn == '\r') {
            return;
        }

        if (byteIn == static_cast<uint8_t>(_lineTerminator)) {
            _lineBuffer[_lineIndex] = '\0';
            handleLine(_lineBuffer);
            resetLineBuffer();
            return;
        }

        if (_lineIndex < kMaxCommandLen) {
            _lineBuffer[_lineIndex++] = static_cast<char>(byteIn);
        } else {
            onProtocolError("Command line too long");
            resetParser();
        }
    }

    void consumeImageByte(uint8_t byteIn) {
        _imageBuffer[_imageIndex++] = byteIn;
        if (_imageIndex < kImageSize) {
            return;
        }

        _imageIndex = 0;

        if (_state == State::AwaitProcessPayload) {
            executeProcess();
        } else if (_state == State::AwaitClassifyPayload) {
            executeClassify();
        }

        _state = State::AwaitCommand;
    }

    void handleLine(const char* line) {
        if (line[0] == '\0') {
            return;
        }

        if (_state == State::AwaitCommand) {
            if (equalsNoCase(line, "PROCESS")) {
                _state = State::AwaitProcessMode;
                return;
            }

            if (equalsNoCase(line, "CLASSIFY")) {
                _state = State::AwaitClassifyPayload;
                return;
            }

            onUnknownCommand(line);
            return;
        }

        if (_state == State::AwaitProcessMode) {
            if (strlen(line) > kMaxModeLen) {
                onProtocolError("Processing mode too long");
                resetParser();
                return;
            }

            strcpy(_processMode, line);
            _state = State::AwaitProcessPayload;
            return;
        }

        onProtocolError("Unexpected text while waiting for payload");
        resetParser();
    }

    void executeProcess() {
        uint8_t outImage[kImageSize];
        bool ok = false;

        if (equalsNoCase(_processMode, "BLUR_LIGHT")) {
            ok = onBlurLight(_imageBuffer, outImage);
        } else if (equalsNoCase(_processMode, "BLUR_HEAVY")) {
            ok = onBlurHeavy(_imageBuffer, outImage);
        } else if (equalsNoCase(_processMode, "SHARPEN")) {
            ok = onSharpen(_imageBuffer, outImage);
        } else {
            ok = onProcessImage(_processMode, _imageBuffer, outImage);
        }

        if (!ok) {
            onProtocolError("PROCESS handler failed");
            return;
        }

        sendProcessedImage(outImage, kImageSize);
    }

    void executeClassify() {
        char csv[kMaxClassifyCsvLen] = {0};
        const bool ok = onClassifyImage(_imageBuffer, csv, sizeof(csv));
        if (!ok) {
            onProtocolError("CLASSIFY handler failed");
            return;
        }

        sendClassificationCsv(csv);
    }
};