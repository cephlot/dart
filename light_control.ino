#include <Adafruit_NeoPixel.h>

#define PIN 6
#define NUM_PIXELS 50

Adafruit_NeoPixel pixels(NUM_PIXELS, PIN, NEO_BRG + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.clear();
  pixels.show();
  Serial.begin(115200);
}

void set_all_pixels(uint32_t color) {
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(i, color);
  }
}

void loop() {
  if (Serial.available() > 0) {
    int received_byte = Serial.read();
    if (received_byte >= 0) {
      char c = (char)received_byte;
      if (c == 'r') {
        set_all_pixels(pixels.Color(255, 0, 0));
      } else if (c == 'g') {
        set_all_pixels(pixels.Color(0, 255, 0));
      } else if (c == 'b') {
        set_all_pixels(pixels.Color(0, 0, 255));
      } else if (c == 'w') {
        set_all_pixels(pixels.Color(255, 255, 255));
      } else if (c == 'c') {
        pixels.clear();
      }
      pixels.show();
    }
  }
}
