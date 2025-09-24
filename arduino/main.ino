#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

// === Constantes universales ===

// === Pines de salida ===
const int LED_INICIO = 14;
const int STBY = 19;
const int PWMA = 16;
const int AIN1 = 18;
const int AIN2 = 17;
const int PWMB = 23;
const int BIN1 = 21;
const int BIN2 = 22;
const int IR_LEDON = 27;

// === Pines de entrada (QTR8A) ===
const int IR[8] = {36,39,34,35,32,33,25,26};

// === Constantes de calibracion QTR8A
const float posiciones[8] = {-24.5, -17.5, -10.5, -3.5, 3.5, 10.5, 17.5, 24.5};

// ------------------------------------------------------------------------------

// === Variables universales ===

// === En calibración ===
unsigned long tiempo = 0;
unsigned long tiempoInicio = 0;
bool calFlag[8] = {0,0,0,0,0,0,0,0};
int sensores[8];
int minVal[8];
int maxVal[8];

// === Parámetros PID (Globales) ===
double Kp = 80.0;
double Ki = 0.05;
double Kd = 20.0;
double Ts = 0.01;
double error[3] = {0,0,0};
double q[3] = {0,0,0};
double salidaPID[2] = {0,0};

void setup() 
{
  // Inicialización de salidas
  pinMode(LED_INICIO, OUTPUT);
  pinMode(STBY,OUTPUT);
  pinMode(AIN1,OUTPUT);
  pinMode(AIN2,OUTPUT);
  pinMode(BIN1,OUTPUT);
  pinMode(BIN2,OUTPUT);
  pinMode(IR_LEDON,OUTPUT);

  // Salidas PWM
  ledcAttachChannel(PWMA, 5000, 8, 0);
  ledcAttachChannel(PWMB, 5000, 8, 1);

  // Inicialización de entradas
  for(int i=0; i<8; i++)
  {
    pinMode(IR[i], INPUT);
    minVal[i] = 4095;
    maxVal[i] = 0;
  }  

  Serial.begin(115200);
  
  // Inicializa constantes PID
  q[0] = Kp + Kd/Ts;
  q[1] = (-1) * (Kd/Ts);

  // Inicializa comunicación Serial BT
  SerialBT.begin("GREA Polaris");  // Nombre visible del dispositivo
}

bool cali = 0;
char mode = ' ';
float centroide = 0;
double u = 0;
double Vmax = 0.2;
double base = 0.0;
double dutyA;
double dutyB;
int pwma;
int pwmb;
int tiempoPID = 0;

void loop() {
  if (cali == 0)
  {
    calibracion();
    cali = 1;

    // === Imprimir valores máximos y mínimos ===
    Serial.println("Resultados de calibración:");
    for (int i = 0; i < 8; i++) {
      Serial.print("Sensor ");
      Serial.print(i+1);
      Serial.print(" -> Min: ");
      Serial.print(minVal[i]);
      Serial.print(" | Max: ");
      Serial.println(maxVal[i]);
    }
  }
  // Aqui debe imprimir todo
  tiempoInicio = millis();
  tiempoPID = millis();
  while(1)
  {   
    tiempo = millis();
    if(tiempo - tiempoPID >= Ts * 1000.0)
    {
      centroide = calcularCentroide();
      u = calcularPID(0,centroide);
      if(!is_valid_double(u)) u=0.0;
      Vmax = clampD(Vmax,0.0,1.0);
      base = Vmax * 255.0;
      dutyA = clampD(base + u,0.0,255.0);
      dutyB = clampD(base - u,0.0,255.0);
      
      pwma = (int)round(dutyA);
      pwmb = (int)round(dutyB);

      //digitalWrite(STBY,HIGH);
      marchaMotorA(1,pwma);
      marchaMotorB(1,pwmb);
    }
    if(tiempo - tiempoInicio >= 500)
    {
      Serial.print("Centroide: ");
      Serial.print(centroide);
      Serial.print(" mm - PID:");
      Serial.print(u);
      Serial.print(" - PWMA:");
      Serial.print(pwma);
      Serial.print(" - PWMB:");
      Serial.println(pwmb);
      tiempoInicio = millis();
    }
  }
}
