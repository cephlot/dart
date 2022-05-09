#include <Adafruit_NeoPixel.h>

#define PIN 6

#define USE_PROTOTYPE
#ifdef USE_PROTOTYPE
#define NUM_PIXELS 16
#define COLOR_MODE NEO_GRB
#else
#define NUM_PIXELS 50
#define COLOR_MODE NEO_BRG
#endif

Adafruit_NeoPixel pixels(NUM_PIXELS, PIN, COLOR_MODE + NEO_KHZ800);

enum effect {clear, red, green, blue, white, rainbow, flash, loading};
effect current_effect;

unsigned long effect_change;

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
    case 'c':
      current_effect = clear;
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
      pixels.setBrightness(255);
      set_all_pixels(pixels.Color(255, 0, 0));
      break;
    case green:
      pixels.setBrightness(255);
      set_all_pixels(pixels.Color(0, 255, 0));
      break;
    case blue:
      pixels.setBrightness(255);
      set_all_pixels(pixels.Color(0, 0, 255));
      break;
    case white:
      pixels.setBrightness(255);
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
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(i, color);
  }
}

void update_rainbow(unsigned long since_effect_change) {
  uint16_t phase = since_effect_change * NUM_PIXELS * 3 % 65536;
  pixels.setBrightness(32);
  for (uint32_t i = 0; i < NUM_PIXELS; i++) {
    uint16_t hue = ((i * 65536 / NUM_PIXELS) - phase) % 65536;
    pixels.setPixelColor(i, pixels.ColorHSV(hue));
  }
}

void update_flash(unsigned long since_effect_change) {
  unsigned int secs = (since_effect_change / 500);
  uint8_t brightness = (secs % 2) * 255;
  pixels.setBrightness(brightness);
  set_all_pixels(pixels.Color(255, 0, 0));
}

void update_loading(unsigned long since_effect_change) {
  uint16_t phase = since_effect_change * 50 % 65536;
  uint16_t first_led = (uint32_t)phase * NUM_PIXELS / 65535;
  const uint16_t length = NUM_PIXELS / 4;
  pixels.setBrightness(32);
  pixels.clear();
  for (uint16_t i = first_led; i < first_led + length; i++) {
    pixels.setPixelColor(i % NUM_PIXELS, pixels.Color(255, 255, 0));
  }
}
