#include <Adafruit_NeoPixel.h>

// The signal pin for the light strip
#define PIN 6
#define MAX_BRIGHTNESS 255

// Number of used pixels
#define NUM_PIXELS 24

Adafruit_NeoPixel pixels(NUM_PIXELS, PIN, NEO_BRG + NEO_KHZ800);

// The available effects
enum effect {clear, red, green, blue, white, rainbow, flash, loading};
effect current_effect;

// The last time the effect was changed
unsigned long effect_change;

void setup() {
  Serial.begin(115200);
  // Initialize light strip
  pixels.begin();
  pixels.clear();
  pixels.show();
  current_effect = clear;
  effect_change = millis();
}

void loop() {
  // Check for new command
  if (Serial.available() > 0) {
    const int received_byte = Serial.read();
    if (received_byte >= 0) {
      const char c = (char)received_byte;
      set_effect(c);
    }
  }
  update_effect();
}

void set_effect(char c) {
  unsigned long now = millis();
  switch (c) {
    case 'c':
      if (current_effect != clear) {
        current_effect = clear;
        effect_change = now;
      }
      break;
    case 'r':
      if (current_effect != red) {
        current_effect = red;
        effect_change = now;
      }
      break;
    case 'g':
      if (current_effect != green) {
        current_effect = green;
        effect_change = now;
      }
      break;
    case 'b':
      if (current_effect != blue) {
        current_effect = blue;
        effect_change = now;
      }
      break;
    case 'w':
      if (current_effect != white) {
        current_effect = white;
        effect_change = now;
      }
      break;
    case 'R':
      if (current_effect != rainbow) {
        current_effect = rainbow;
        effect_change = now;
      }
      break;
    case 'f':
      if (current_effect != flash) {
        current_effect = flash;
        effect_change = now;
      }
      break;
    case 'l':
      if (current_effect != loading) {
        current_effect = loading;
        effect_change = now;
      }
      break;
  }
}

void update_effect() {
  static unsigned long last_update = millis();
  const unsigned long now = millis();
  const unsigned long delta = now - last_update;
  last_update = now;
  const unsigned long since_effect_change = now - effect_change;

  switch (current_effect) {
    case red:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(255, 0, 0);
      break;
    case green:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(0, 255, 0);
      break;
    case blue:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(0, 0, 255);
      break;
    case white:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(255, 255, 255);
      break;
    case clear:
      pixels.clear();
      break;
    case rainbow:
      update_rainbow(since_effect_change);
      break;
    case flash:
      update_flash(since_effect_change);
      break;
    case loading:
      update_loading(since_effect_change);
      break;
  }
  pixels.show();
}

void set_all_pixels(uint8_t r, uint8_t g, uint8_t b) {
  pixels.clear();
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
}

void update_rainbow(unsigned long since_effect_change) {
  const int speed = 3;
  uint16_t phase = since_effect_change * speed % 65536; // Where in the loop to start
  pixels.setBrightness(MAX_BRIGHTNESS);
  for (uint16_t i = 0; i < NUM_PIXELS; i++) {
    uint16_t hue = (((uint32_t)i * 65536 / NUM_PIXELS) - phase * NUM_PIXELS) % 65536;
    pixels.setPixelColor(i, pixels.ColorHSV(hue));
  }
}

void update_flash(unsigned long since_effect_change) {
  const int speed = 1; // Flashes per second
  uint8_t brightness = ((since_effect_change * speed / 500) % 2); // 0 or 1
  pixels.setBrightness(brightness * MAX_BRIGHTNESS);
  set_all_pixels(255, 0, 0);
}

void update_loading(unsigned long since_effect_change) {
  const int speed = 50;
  uint16_t phase = since_effect_change * speed % 65536; // Where in the loop to start
  uint16_t position = (uint32_t)phase * NUM_PIXELS / 65535;
  const int length = NUM_PIXELS / 2; // Number of pixels used for the 'snake'
  pixels.setBrightness(MAX_BRIGHTNESS);
  pixels.clear();
  for (int i = 0; i < length; i++) {
    // Set pixels to yellow with varying intensities
    pixels.setPixelColor((position + i) % NUM_PIXELS, pixels.ColorHSV(10923, 255, pixels.gamma8(i * (255 / (length)))));
  }
}
