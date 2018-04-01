#include <Adafruit_MotorShield.h>
#include <VarSpeedServo.h>
// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *motor1 = AFMS.getStepper(200, 1);
Adafruit_StepperMotor *motor2 = AFMS.getStepper(200, 2);

#define COMMAND_SIZE 128
#define PEN_UP 55
#define PEN_DOWN 70
VarSpeedServo servo;

char aWord[COMMAND_SIZE];
String command;
String command_part[6];
int part;
int last_space;
long serial_count;
char c;
long code;
char buf[16]; //
int x_new, y_new, z_new;
int x_curr, y_curr, z_curr;

void setup() {
  Serial.begin(2000000);

  x_curr = 0;
  y_curr = 0;
  z_curr = 1;
  AFMS.begin();
  motor1->setSpeed(12);
  motor2->setSpeed(12);
  motor1->release();
  motor2->release();
  servo.attach(10);
  servo.write(PEN_UP);
}

void loop()
{

  if (Serial.available() > 0) {
    // nächstes Zeichen
    //====================
    c = Serial.read();
    //no_data = 0;

    //==========================
    if (c != '\n') {
      aWord[serial_count] = c;
      serial_count++;
    }
  }

    if (serial_count && (c == '\n'))  {
      //no_data = 0;
      c = ' ';
      command=aWord;

      part=0;
      last_space= 0;

      for (int i=0; i < serial_count; i++){
        if (command.charAt(i) == ' ') {
          command_part[part] = command.substring(last_space,i);
          last_space=i+1;
          if (command_part[part].length() != 0) {
             part++;
          }
        }
      }
      command_part[part] = command.substring(last_space,serial_count);
      part++;

      if ((command_part[0] == "G01") || (command_part[0] == "g01") || (command_part[0] == "G1")) {
        extract_parameter();
        moveTo(x_new, y_new);
        Serial.println("OK");
      }
      else if ((command_part[0] == "G00") || (command_part[0] == "g00") || (command_part[0] == "G0")) {
        extract_parameter();
        if(z_new != z_curr) {
          if(z_new>0)
            servo.write(PEN_UP,50,true);
          else
            servo.write(PEN_DOWN,50,true);
        }
        z_curr = z_new;
        Serial.println("OK");
      }
      else if (command_part[0] == "M05") {
        motor1->release();
        motor2->release();
        servo.write(PEN_UP);
        Serial.println("OK");
      }
      else
        Serial.println("NOK");
      clear_process_string();
    }

}


void line(int x0, int y0, int x1, int y1)
{
  const int dx =  abs(x1-x0), sx = x0<x1 ? 1 : -1;  // 1 Forward -1 Backward
  const int dy = -abs(y1-y0), sy = y0<y1 ? 1 : -1;  //
  int err = dx+dy,  e2; /* error value e_xy */


  for(;;){  /* loop */

    if (x0==x1 && y0==y1) break;
    e2 = 2*err;
    if (e2 > dy) {
      err += dy; x0 += sx;
      if (sx == -1) {
        motor2->onestep(BACKWARD, MICROSTEP);
      }
      else {
        motor2->onestep(FORWARD, MICROSTEP);
      }
    }

    if (e2 < dx) {
      err += dx; y0 += sy;
      if (sy == -1) {
        motor1->onestep(BACKWARD, MICROSTEP);
      }
      else {
        motor1->onestep(FORWARD, MICROSTEP);
      }
    }
  }
}



void clear_process_string()
{
  // init

  for (byte i=0; i<COMMAND_SIZE; i++)
    aWord[i] = 0;
    serial_count = 0;
}

void moveTo(int x1, int y1)
{
  line (x_curr, y_curr, x1, y1);
  x_curr=x1;
  y_curr=y1;
}


void extract_parameter()
{
   if (command_part[1].startsWith("X")) {
        command_part[1] = command_part[1].substring(1, command_part[1].length()+1);
        command_part[1].toCharArray(buf,command_part[1].length()+1);

        x_new = atoi (buf);
      }
      if (command_part[2].startsWith("Y")) {
        command_part[2] = command_part[2].substring(1, command_part[2].length()+1);
        command_part[2].toCharArray(buf,command_part[2].length()+1);
        y_new = atoi (buf);
      }
      if (command_part[1].startsWith("Z")) {
        command_part[1] = command_part[1].substring(1, command_part[1].length()+1);
        command_part[1].toCharArray(buf,command_part[1].length()+1);
        z_new = atoi(buf);
      }

}
