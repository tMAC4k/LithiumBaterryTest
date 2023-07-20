const int voltagePin1 = 9;    // Analog output pin for Power Supply 1 voltage
const int currentPin1 = 10;    // Analog output pin for Power Supply 1 current
const int voltagePin2 = 5;    // Analog output pin for Power Supply 2 voltage
const int currentPin2 = 6;    // Analog output pin for Power Supply 2 current

bool emergencyStop = false;    // Emergency stop flag

bool procedure = true;

float voltage1;
float current1;
float voltage2;
float current2;
float maxtemp;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Set analog pins as outputs
  pinMode(voltagePin1, OUTPUT);
  pinMode(currentPin1, OUTPUT);
  pinMode(voltagePin2, OUTPUT);
  pinMode(currentPin2, OUTPUT);

  Serial.print("Arduino Connected!");

  //Set all outputs to zero
  analogWrite(voltagePin1, 0);
  analogWrite(currentPin1, 0);
  analogWrite(voltagePin2, 0);
  analogWrite(currentPin2, 0);
}

void loop() {
  // Check if serial data is available
  if (Serial.available()) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove leading/trailing whitespaces

    // Process the command
    if (command.startsWith("SETV1-")) {
      // Set voltage for Power Supply 1
      command.remove(0, 6);  // Remove the command prefix
      voltage1 = command.toFloat();
      Serial.print("\nVoltage pin 1 set to: " + command + " V.");
    }
    
    else if (command.startsWith("SETC1-")) {
      // Set current for Power Supply 1
      command.remove(0, 6);  // Remove the command prefix
      current1 = command.toFloat();
      Serial.print("\nCurrent pin 1 set to: " + command + " A.");
    }
    
    else if (command.startsWith("SETV2-")) {
      // Set voltage for Power Supply 2
      command.remove(0, 6);  // Remove the command prefix
      voltage2 = command.toFloat();
      Serial.print("\nVoltage pin 2 set to: " + command + " V.");
    }
    
    else if (command.startsWith("SETC2-")) {
      // Set current for Power Supply 2
      command.remove(0, 6);  // Remove the command prefix
      current2 = command.toFloat();
      Serial.print("\nCurrent pin 2 set to: " + command + " A.");
    }

    else if (command.startsWith("SETMAXTEMP-")) {
      // Set current for Power Supply 2
      command.remove(0, 11);  // Remove the command prefix
      // current2 = command.toFloat();
      Serial.print("\nMax. Temperature set to: " + command + " *C.");
      //setTemp(currentPin2, current2);
    }

    else if (command == "START") {
      Serial.print("\nStarting.");
      if(procedure){
        startChargingTest();
      }
      else{
        startDischargingTest();
      }
     }

    else if (command == "PAUSE") {
      Serial.print("\nPausing.");
      stopPowerSupplies();
    }
    
    else if (command == "STOP") {
      Serial.print("\nStopping.");
      // Emergency stop - Set all values to zero
      emergencyStop = true;
      stopPowerSupplies();
    }
    
    else if (command == "Charging") {
      Serial.print("\nCharging Test Set...");
      // Start the test on Power Supply 1
      procedure = true;
    }

    else if (command == "Discharging") {
      Serial.print("\nDischarging Test Set...");
      // Start the test on Power Supply 1
      procedure = false;
    }
  }
}

void setVoltageFonte(int pin, float voltage) {
  // Convert the voltage value to the corresponding analog range
  int outputVoltage = map(voltage, 0, 160, 0, 255);
  analogWrite(pin, outputVoltage);
}

void setCurrentFonte(int pin, float current) {
  // Convert the current value to the corresponding analog range
  int outputCurrent = map(current, 0, 60, 0, 255);
  analogWrite(pin, outputCurrent);
}

void setVoltageCarga(int pin, float voltage) {
  // Convert the voltage value to the corresponding analog range
  int outputVoltage = map(voltage, 0, 360, 0, 255);
  analogWrite(pin, outputVoltage);
}

void setCurrentCarga(int pin, float current) {
  // Convert the current value to the corresponding analog range
  int outputCurrent = map(current, 0, 40, 0, 255);
  analogWrite(pin, outputCurrent);
}

void stopPowerSupplies() {
  // Set all power supply values to zero
  analogWrite(voltagePin1, 0);
  analogWrite(currentPin1, 0);
  analogWrite(voltagePin2, 0);
  analogWrite(currentPin2, 0);
}

void startChargingTest() {
  // Set voltage and current values for Power Supply 1 to charge Li-ion battery
  setVoltageFonte(voltagePin1, voltage1);
  setCurrentFonte(currentPin1, current1);  // Adjust the current value as needed
}

void startDischargingTest() {
  // Set voltage and current values for Power Supply 1 to charge Li-ion battery
  setVoltageCarga(voltagePin2, voltage2);
  setCurrentCarga(currentPin2, current2);  // Adjust the current value as needed
}
