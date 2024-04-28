double yaw = 0, pitch = 0, roll = 0;
double oldyaw = 0, oldpitch = 0, oldroll = 0;
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
  acMag = sqrt(acx * acx + acy * acy + acz * acz);
  acMag = abs(yaw - oldyaw) * 3000;
  if (yaw > oldyaw) {
    acDir = 1;
  } else {
    acDir = -1;
  }
  if (acMag == 0) {
    return;
  }
  oldyaw = yaw;
  Serial.println(acMag);
  if (acMag > 200) {
    // acDir = atan2(acx, acy) * 180 / M_PI;
    // Serial.print(acDir);
    // Serial.println(acMag);
    if (acMag > 1000) {
      moving = true;
    }
  } else {
    moving = false;
  }
  lightsloop();
}
