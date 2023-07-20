#include <SoftwareSerial.h>

SoftwareSerial bluetooth(10, 11); // RX, TX pins for Bluetooth module

void setup() {
  Serial.begin(9600); // Set the baud rate to match your serial monitor
  bluetooth.begin(9600); // Set the baud rate for Bluetooth communication
}

void loop() {
  // Send the desired string through the serial port
  bluetooth.println("S 02 10 19 19 19 19 19 19 19 19 19 19 19 19 19 19 19 0000 00");
  bluetooth.println("Um Segundo!");
  bluetooth.println("C 0A 0066 08 20 81 50 00 00 00 00 00");
  bluetooth.println("**  23/07/03  16:04  **");
  bluetooth.println("R 00 05 230703 16:04");
  bluetooth.println("C 0A 02B0 06 01 50 0C F3 19 00 00 00");
  bluetooth.println("D - Pede dados ID:2");
  bluetooth.println("C 0A 0066 08 20 41 51 00 00 00 00 00");
  bluetooth.println("C 0A 0066 08 20 41 51 00 00 00 00 00");
  bluetooth.println("C 0A 02B0 06 02 51 0C EF 19 00 00 00");
  bluetooth.println("D - Dados: Cell: 2 Tensao: 3311 V  Temp: 25 ºC");
  bluetooth.println("D - Pede dados ID:3");
  bluetooth.println("D - Pede Dados c: 3");
  bluetooth.println("P 01 01 00");
  bluetooth.println("D EstadoCarregador: 0");
  bluetooth.println("C 0A 0066 08 20 C1 52 00 00 00 00 00");
  bluetooth.println("C 0A 0066 08 20 C1 52 00 00 00 00 00");
  bluetooth.println("S 01 10 817E 8156 812E 814C 80FC 8142 7ED6 80AC 80DE 81A6 807A 80C0 8192 819C 80A2 80D4");
  bluetooth.println("C 0A 02B0 06 03 52 0C E9 19 00 00 00");

  delay(1000); // Delay for 1 second before sending again
}
