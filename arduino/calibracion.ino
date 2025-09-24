// === Función de calibración 
void calibracion()
{
  digitalWrite(IR_LEDON, HIGH);

  Serial.println("Inicio de la calibracion");

  // Reiniciar min y max
  for(int i=0; i<8; i++) {
    minVal[i] = 4095;  // valor máximo del ADC ESP32
    maxVal[i] = 0;
  }

  unsigned long tiempoInicio = millis();
  while((millis() - tiempoInicio) < 5000)
  {
    for(int i=0; i<8; i++)
    {
      int valor = analogRead(IR[i]);
      if(valor < minVal[i]) minVal[i] = valor;
      if(valor > maxVal[i]) maxVal[i] = valor;
    }
  }
  digitalWrite(IR_LEDON, LOW);
  Serial.println("Fin de calibracion");
}