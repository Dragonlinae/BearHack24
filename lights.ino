#include <EEPROM.h>
#include <FastLED.h>

#define BUTTON_PIN 4
#define LED_PIN 3

#define BRIGHTNESS 10
#define NUM_LEDS 144
#define NUM_LEDS_PER_SEGMENT 4
#define LED_TYPE WS2812
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];
int ledsPerFrame = 1;

float r = 255;
float g = 255;
float b = 0;

char buffer[NUM_LEDS + 1];

int32_t currLED = 0;
int32_t maxLED = 0;

bool clicked = true;

int dir = 0;

CRGB red = CRGB(255, 0, 0);
CRGB green = CRGB(0, 255, 0);

void lightssetup() {
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setDither(0);

  pinMode(BUTTON_PIN, INPUT);

  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(0, 0, 0);
  }
  FastLED.show();

  maxLED = (int32_t)height * 1000 - 1;
}

void lightsloop() {

  int buttonState = digitalRead(BUTTON_PIN);
  pinMode(BUTTON_PIN, OUTPUT);
  digitalWrite(BUTTON_PIN, LOW);

  if (!moving) {
    currLED = -100;
    strcpy_P(buffer, (char *)pgm_read_ptr(&(color_table[0])));
    int color;
    for (int i = 0; i < NUM_LEDS; i++) {
      color = (uint8_t)buffer[i / NUM_LEDS_PER_SEGMENT];
      color -= 1;
      leds[i] = CRGB(color / 36 * 43, (color % 36) / 6 * 43, color % 6 * 43);
    }
    FastLED.show();
  }

  if (buttonState == HIGH || moving) {
    if (dir == 0) {
      if (acDir > 0) {
        dir = 1;
      } else {
        dir = -1;
      }
    } else {
      if (acDir > 0) {
        dir = 1;
      } else {
        dir = -1;
      }
      if (currLED == -100 && dir < 0 ) {
        currLED = maxLED;
      } else if (currLED == -100 && dir > 0) {
        currLED = 0;
      } else {
        currLED += dir * ((int32_t)acMag)/3;
      }
      if (currLED < 0) {
        currLED = 0;
        // currLED = maxLED + currLED % maxLED;
      } else if (currLED > maxLED) {
        currLED = maxLED;
        // currLED %= maxLED;
      }
    }
    Serial.println(currLED/10/height);
    // Serial.println(dir);
    strcpy_P(buffer, (char *)pgm_read_ptr(&(color_table[currLED / 1000])));

    int color = 0;

    if (dir == 1) {
      for (int i = 0; i < NUM_LEDS; i++) {
        color = (uint8_t)buffer[i / NUM_LEDS_PER_SEGMENT];
        color -= 1;
        leds[NUM_LEDS-1-i] = CRGB(color / 36 * 43, (color % 36) / 6 * 43, color % 6 * 43);
      }
    } else {
      for (int i = 0; i < NUM_LEDS; i++) {
        color = (uint8_t)buffer[i / NUM_LEDS_PER_SEGMENT];
        color -= 1;
        leds[NUM_LEDS-1-i] = CRGB(color / 36 * 43, (color % 36) / 6 * 43, color % 6 * 43);
      }
    }
    FastLED.show();
  } else {
    dir = 0;
    // for (int i = 0; i < NUM_LEDS; i++) {
    //   leds[i] = CRGB(0, 0, 0);
    // }
    // FastLED.show();
  }
}
