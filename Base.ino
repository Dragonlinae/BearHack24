double yaw = 0, pitch = 0, roll = 0;
int acx = 0, acy = 0, acz = 0;
double acMag = 0;

void setup() {
  imusetup();
}

void loop() {
  imuloop();
  if (acMag > 1000) {
    Serial.println(acMag);
  }
}
