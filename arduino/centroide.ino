//=== Funcion de calculo del centroide ===
float calcularCentroide()
{
  float sumaPesos = 0;
  float sumaValores = 0;
  digitalWrite(IR_LEDON, HIGH);
  for(int i=0; i<8; i++)
  {
    if(i!=6)
    {
      int raw = analogRead(IR[i]);
      // normalizar
      float norm = (float)(raw - minVal[i]) / (maxVal[i] - minVal[i]);
      if(norm < 0) norm = 0;
      if(norm > 1) norm = 1;

      sumaPesos += norm * posiciones[i];
      sumaValores += norm;
    }
  }

  if(sumaValores == 0) {
    // línea perdida → devolver algo grande
    return 9999; 
  }
  return sumaPesos / sumaValores; // en milímetros
}