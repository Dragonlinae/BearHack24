double yaw = 0, pitch = 0, roll = 0;
double acx = 0, acy = 0, acz = 0;
double acMag = 0;
double acDir = 0;
bool moving = false;

void setup() {
  imusetup();
  lightssetup();
}

void loop() {
  imuloop();
  lightsloop();
  acMag = sqrt(acx * acx + acy * acy + acz * acz);
  Serial.println(acMag);
  if (acMag > 1000) {
    acDir = atan2(acx, acy) * 180 / M_PI;
    Serial.print(acDir);
    Serial.println(acMag);
    if (acMag > 3000) {
      moving = true;
    }
  } else {
    moving = false;
  }
}
