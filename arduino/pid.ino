// === Funcion PID ===

double calcularPID(double setpoint, double medida) {
  //error[2] = error[1];
  error[1] = error[0];
  error[0] = setpoint - medida;
  salidaPID[0] = q[0]*error[0] + q[1]*error[1]; //+ q[2]*error[2];
  salidaPID[1] = salidaPID[0];
  return salidaPID[0];
}

// === Funciones auxiliares clamp y anti NaN 

double clampD(double x, double lo, double hi)
{
  if(x < lo) return lo;
  if(x > hi) return hi;
  return x;
}

bool is_valid_double(double x)
{
  return !(isnan(x) || isinf(x));
}