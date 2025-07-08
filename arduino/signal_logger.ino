// signal_logger.ino
// Reads analog voltage from a plant electrode system and sends it via Serial

const int sensorPin = A0;         
const unsigned long sampleInterval = 10;  
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);          
  while (!Serial) {
    ; 
  }
  Serial.println("timestamp_ms,voltage_mv"); 

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastSampleTime >= sampleInterval) {
    lastSampleTime = currentTime;

    int rawValue = analogRead(sensorPin);            
    float voltage = (rawValue / 1023.0) * 5000.0;     
    Serial.print(currentTime);     
    Serial.print(",");
    Serial.println(voltage);       
  }
}
