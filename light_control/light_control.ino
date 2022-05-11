#include <Adafruit_NeoPixel.h>

#define PIN 6
#define MAX_BRIGHTNESS 255

#define TOTAL_PIXELS 50 /* Total number of connected pixels */
#define NUM_PIXELS 25 /* Number of used pixels */
#define FIRST_PIXEL 4 /* First used pixel */
#define COLOR_MODE NEO_BRG

Adafruit_NeoPixel pixels(TOTAL_PIXELS, PIN, COLOR_MODE + NEO_KHZ800);

// The available effects
enum effect {clear, red, green, blue, white, rainbow, flash, loading};
effect current_effect;
unsigned long effect_change; // The last time the effect was changed

void setup() {
  Serial.begin(115200);
  pixels.begin();
  pixels.clear();
  pixels.show();
  current_effect = clear;
  effect_change = millis();
}

void loop() {
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
  effect_change = millis();
  switch (c) {
    case 'c':
      current_effect = clear;
      break;
    case 'r':
      current_effect = red;
      break;
    case 'g':
      current_effect = green;
      break;
    case 'b':
      current_effect = blue;
      break;
    case 'w':
      current_effect = white;
      break;
    case 'R':
      current_effect = rainbow;
      break;
    case 'f':
      current_effect = flash;
      break;
    case 'l':
      current_effect = loading;
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
      set_all_pixels(pixels.Color(255, 0, 0));
      break;
    case green:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(pixels.Color(0, 255, 0));
      break;
    case blue:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(pixels.Color(0, 0, 255));
      break;
    case white:
      pixels.setBrightness(MAX_BRIGHTNESS);
      set_all_pixels(pixels.Color(255, 255, 255));
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

void set_all_pixels(uint32_t color) {
  pixels.clear();
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(FIRST_PIXEL + i, color);
  }
}

void update_rainbow(unsigned long since_effect_change) {
  const int speed = 3;
  uint16_t phase = since_effect_change * speed % 65536; // Where in the loop to start
  pixels.setBrightness(MAX_BRIGHTNESS);
  for (uint16_t i = 0; i < NUM_PIXELS; i++) {
    uint16_t hue = (((uint32_t)i * 65536 / NUM_PIXELS) - phase * NUM_PIXELS) % 65536;
    pixels.setPixelColor(FIRST_PIXEL + i, pixels.ColorHSV(hue));
  }
}

void update_flash(unsigned long since_effect_change) {
  const int speed = 1; // Flashes per second
  uint8_t brightness = ((since_effect_change * speed / 500) % 2); // 0 or 1
  pixels.setBrightness(brightness * MAX_BRIGHTNESS);
  set_all_pixels(pixels.Color(255, 0, 0));
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
    pixels.setPixelColor(FIRST_PIXEL + ((position + i) % NUM_PIXELS),
                         pixels.ColorHSV(10923, 255,
                                         pixels.gamma8(i * (255 / (length)))));
  }
}
