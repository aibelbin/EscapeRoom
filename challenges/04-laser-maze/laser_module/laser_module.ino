const int LDR = 2;

void setup() {
  pinMode(LDR, INPUT);
  Serial.begin(9600);
}

void loop() {
  int sensor = digitalRead(LDR);

  // Adjust this if your module behaves opposite
  int tripwire = (sensor == HIGH) ? 1 : 0;

  Serial.println(tripwire);

  delay(20);
}