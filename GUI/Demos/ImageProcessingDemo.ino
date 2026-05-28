#include <Arduino.h>

namespace {

constexpr uint8_t kWidth = 20;
constexpr uint8_t kHeight = 20;
constexpr size_t kImageSize = static_cast<size_t>(kWidth) * kHeight;
constexpr size_t kCommandSize = 32;

enum class ProcessingMode : uint8_t {
  BlurLight,
  BlurHeavy,
  Sharpen,
};

uint8_t inputImage[kImageSize];
uint8_t outputImage[kImageSize];
char commandBuffer[kCommandSize];
size_t commandLength = 0;
size_t imageLength = 0;
bool readingImage = false;

uint8_t clampToByte(int value) {
  if (value < 0) {
    return 0;
  }

  if (value > 255) {
    return 255;
  }

  return static_cast<uint8_t>(value);
}

uint8_t getPixelClamped(const uint8_t *image, int x, int y) {
  if (x < 0) {
    x = 0;
  } else if (x >= kWidth) {
    x = kWidth - 1;
  }

  if (y < 0) {
    y = 0;
  } else if (y >= kHeight) {
    y = kHeight - 1;
  }

  return image[static_cast<size_t>(y) * kWidth + static_cast<size_t>(x)];
}

bool isCommandMatch(const char *command, const char *candidate) {
  return strcmp(command, candidate) == 0;
}

ProcessingMode parseProcessingMode(const char *command) {
  if (isCommandMatch(command, "BLUR_LIGHT")) {
    return ProcessingMode::BlurLight;
  }

  if (isCommandMatch(command, "BLUR_HEAVY")) {
    return ProcessingMode::BlurHeavy;
  }

  return ProcessingMode::Sharpen;
}

void processBlurLight() {
  static const int8_t kernel[3][3] = {
      {1, 1, 1},
      {1, 2, 1},
      {1, 1, 1},
  };

  for (int y = 0; y < kHeight; ++y) {
    for (int x = 0; x < kWidth; ++x) {
      int sum = 0;
      for (int ky = -1; ky <= 1; ++ky) {
        for (int kx = -1; kx <= 1; ++kx) {
          const uint8_t pixel = getPixelClamped(inputImage, x + kx, y + ky);
          sum += pixel * kernel[ky + 1][kx + 1];
        }
      }

      outputImage[static_cast<size_t>(y) * kWidth + static_cast<size_t>(x)] = clampToByte(sum / 10);
    }
  }
}

void processBlurHeavy() {
  for (int y = 0; y < kHeight; ++y) {
    for (int x = 0; x < kWidth; ++x) {
      int sum = 0;

      for (int ky = -2; ky <= 2; ++ky) {
        for (int kx = -2; kx <= 2; ++kx) {
          sum += getPixelClamped(inputImage, x + kx, y + ky);
        }
      }

      outputImage[static_cast<size_t>(y) * kWidth + static_cast<size_t>(x)] = clampToByte(sum / 25);
    }
  }
}

void processSharpen() {
  static const int8_t kernel[3][3] = {
      {0, -1, 0},
      {-1, 5, -1},
      {0, -1, 0},
  };

  for (int y = 0; y < kHeight; ++y) {
    for (int x = 0; x < kWidth; ++x) {
      int sum = 0;

      for (int ky = -1; ky <= 1; ++ky) {
        for (int kx = -1; kx <= 1; ++kx) {
          const uint8_t pixel = getPixelClamped(inputImage, x + kx, y + ky);
          sum += pixel * kernel[ky + 1][kx + 1];
        }
      }

      outputImage[static_cast<size_t>(y) * kWidth + static_cast<size_t>(x)] = clampToByte(sum);
    }
  }
}

void processImage(ProcessingMode mode) {
  switch (mode) {
    case ProcessingMode::BlurLight:
      processBlurLight();
      break;

    case ProcessingMode::BlurHeavy:
      processBlurHeavy();
      break;

    case ProcessingMode::Sharpen:
    default:
      processSharpen();
      break;
  }
}

void resetFrameState() {
  readingImage = false;
  commandLength = 0;
  imageLength = 0;
  commandBuffer[0] = '\0';
}

bool readCommandLine() {
  while (Serial.available() > 0) {
    const char incoming = static_cast<char>(Serial.read());

    if (incoming == '\r') {
      continue;
    }

    if (incoming == '\n') {
      commandBuffer[commandLength] = '\0';
      readingImage = true;
      imageLength = 0;
      return true;
    }

    if (commandLength + 1 >= kCommandSize) {
      resetFrameState();
      return false;
    }

    commandBuffer[commandLength++] = incoming;
  }

  return false;
}

bool readImageBytes() {
  while (Serial.available() > 0 && imageLength < kImageSize) {
    inputImage[imageLength++] = static_cast<uint8_t>(Serial.read());
  }

  return imageLength >= kImageSize;
}

void sendImageFrame() {
  Serial.println(F("OK|400"));
  Serial.write(outputImage, kImageSize);
}

}  // namespace

void setup() {
  Serial.begin(115200);
  resetFrameState();
}

void loop() {
  if (!readingImage) {
    readCommandLine();
    return;
  }

  if (!readImageBytes()) {
    return;
  }

  const ProcessingMode mode = parseProcessingMode(commandBuffer);
  processImage(mode);
  sendImageFrame();
  resetFrameState();
}