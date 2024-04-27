#include <EEPROM.h>
#include <FastLED.h>

#define BUTTON_PIN 4
#define LED_PIN 3

#define BRIGHTNESS 10
#define NUM_LEDS 144
#define LED_TYPE WS2812
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];
int ledsPerFrame = 1;

float r = 255;
float g = 255;
float b = 0;

char redbuffer[NUM_LEDS + 1];
char greenbuffer[NUM_LEDS + 1];
char bluebuffer[NUM_LEDS + 1];

int currLED = 0;

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
}

void lightsloop() {

  int buttonState = digitalRead(BUTTON_PIN);
  pinMode(BUTTON_PIN, OUTPUT);
  digitalWrite(BUTTON_PIN, LOW);

  if (buttonState == HIGH && moving) {
    if (dir == 0) {
      if (acDir > 0) {
        dir = 1;
      } else {
        dir = -1;
      }
    }
    if (dir == 1) {
      for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = red;
      }
    } else {
      for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = green;
      }
    }
    FastLED.show();
  } else {
    dir = 0;
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB(0, 0, 0);
    }
    FastLED.show();
  }
}
