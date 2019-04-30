String readString;
#include <Servo.h>
Servo servoaz;
Servo servoel;
void setup (){  
 servoaz.attach(9);
 servoel.attach(3);
 Serial.begin(9600); 
}
void loop () {
 char c;
 
 while(c != ';') {
   while ( !Serial.available() ){}
   while ( Serial.available()){
     c = Serial.read();
     if (c != ';')
     readString += c ;
     }
   }
Serial.println("the message was: "+ readString);
int delimiterpos =readString.indexOf(',');
int  length= readString.length();
String azstr=readString.substring(0,delimiterpos);
String elstr=readString.substring(delimiterpos+1, length);
int az = azstr.toInt();
int el = elstr.toInt();
Serial.println(az+el);
Serial.flush(); 
el = el+90;
servoaz.write(az);
servoel.write(el);
readString ="";
}

