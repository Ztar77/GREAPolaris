// === Funcion mando Motor A
void marchaMotorA(int mode, int pwma)
{
  analogWrite(PWMA,pwma);
  if(pwma > 0 && mode == 1)
  {
    
    digitalWrite(AIN1,HIGH);
    digitalWrite(AIN2,LOW);
    digitalWrite(LED_INICIO,HIGH);
  }
  else if(pwma < 0 && mode == 1)
  {
    digitalWrite(AIN1,LOW);
    digitalWrite(AIN2,HIGH);
    digitalWrite(LED_INICIO,HIGH);
  }
  else
  {
    digitalWrite(AIN1,LOW);
    digitalWrite(AIN2,LOW);
    digitalWrite(LED_INICIO,LOW);
  }
}

// === Funcion mando Motor B
void marchaMotorB(int mode, int pwmb)
{
  analogWrite(PWMB,pwmb);
  if(pwmb > 0 && mode == 1)
  {
    
    digitalWrite(BIN1,HIGH);
    digitalWrite(BIN2,LOW);
    digitalWrite(LED_INICIO,HIGH);
  }
  else if(pwma < 0 && mode == 1)
  {
    digitalWrite(BIN1,LOW);
    digitalWrite(BIN2,HIGH);
    digitalWrite(LED_INICIO,HIGH);
  }
  else
  {
    digitalWrite(BIN1,LOW);
    digitalWrite(BIN2,LOW);
    digitalWrite(LED_INICIO,LOW);
  }
}