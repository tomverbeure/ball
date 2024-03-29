#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "MPU6050_6Axis_MotionApps_V6_12.h"

#include "mpu6050_drv.h"

MPU6050 mpu;

bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 gy;         // [x, y, z]            gyro sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector
float yaw, pitch, roll;

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

int mpu6050_init() {
    // Setup I2C pins
    i2c_init(i2c_default, 400 * 1000);
    gpio_set_function(21, GPIO_FUNC_I2C);
    gpio_set_function(20, GPIO_FUNC_I2C);
    gpio_pull_up(21);
    gpio_pull_up(20);
    
#if 0
    // setup blink led
    gpio_init(PICO_DEFAULT_LED_PIN);
	gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
	while (!stdio_usb_connected()) { // blink the pico's led until usb connection is established
		gpio_put(PICO_DEFAULT_LED_PIN, 1);
		sleep_ms(250);
		gpio_put(PICO_DEFAULT_LED_PIN, 0);
		sleep_ms(250);
	}
#endif

    // ================================================================
    // ===                      INITIAL SETUP                       ===
    // ================================================================
    mpu.initialize();
    devStatus = mpu.dmpInitialize();
    if (devStatus == 0) 
    {
        mpu.setDMPEnabled(true);                // turn on the DMP, now that it's ready
        mpuIntStatus = mpu.getIntStatus();
        dmpReady = true;                        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        packetSize = mpu.dmpGetFIFOPacketSize();      // get expected DMP packet size for later comparison
    } 
    else 
    {                                          
        // ERROR!        
        // 1 = initial memory load failed         
        // 2 = DMP configuration updates failed  (if it's going to break, usually the code will be 1)
        printf("DMP Initialization failed (code %d)", devStatus);
        sleep_ms(2000);
    }

    // Numbers determined by the calibration utility.
    mpu.setXGyroOffset(80);
    mpu.setYGyroOffset(-32);
    mpu.setZGyroOffset(14);
    mpu.setXAccelOffset(-1433);
    mpu.setYAccelOffset(-173);
    mpu.setZAccelOffset(1585);
}

t_vec prev_gravity;

t_vec mpu6050_gravity()
{
    int fifoCount = mpu.getFIFOCount();
    if (fifoCount < packetSize){
        return prev_gravity;
    }

//    printf("packetsize: %d\n", packetSize);
//    printf("fifoCount: %d\n", fifoCount);

    mpu.getFIFOBytes(fifoBuffer, packetSize);                             // read a packet from FIFO
    mpu.resetFIFO();
//    printf("fifoCount: %d\n", mpu.getFIFOCount());
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);

    t_vec g;
    g.x = gravity.x;
    g.y = gravity.y;
    g.z = gravity.z;
    g = vec_normalize(g);

//    printf("%f,%f,%f\n", gravity.x, gravity.y, gravity.z);
//    printf("%f,%f,%f\n", g.x, g.y, g.z);

    prev_gravity = g;
    return g;
}

#if 0
    yaw = 0.0;
    pitch = 0.0;
    roll = 0.0;

    // ================================================================
    // ===                    MAIN PROGRAM LOOP                     ===
    // ================================================================

    while(1){

        if (!dmpReady);                                                    // if programming failed, don't try to do anything
        mpuInterrupt = true;
        fifoCount = mpu.getFIFOCount();                                           // get current FIFO count
        if ((mpuIntStatus & 0x10) || fifoCount == 1024)                           // check for overflow (this should never happen unless our code is too inefficient)
        {
            mpu.resetFIFO();                                                      // reset so we can continue cleanly
            printf("FIFO overflow!");
        } 
        else if (mpuIntStatus & 0x01)                                             // otherwise, check for DMP data ready interrupt (this should happen frequently)
        {    
            while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();        // wait for correct available data length, should be a VERY short wait
            mpu.getFIFOBytes(fifoBuffer, packetSize);                             // read a packet from FIFO
            fifoCount -= packetSize;                                              // track FIFO count here in case there is > 1 packet available
            #ifdef OUTPUT_READABLE_YAWPITCHROLL                                               // display Euler angles in degrees
                mpu.dmpGetQuaternion(&q, fifoBuffer);
                mpu.dmpGetGravity(&gravity, &q);
                mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
                yaw = ypr[0] * 180 / PI;
                pitch = ypr[1] * 180 / PI;
                roll = ypr[2] * 180 / PI;
                printf("ypr: %f,\t %f,\t %f\n", yaw, pitch, roll);
            #endif
            #ifdef OUTPUT_READABLE_REALACCEL
                // display real acceleration, adjusted to remove gravity
                mpu.dmpGetQuaternion(&q, fifoBuffer);
                mpu.dmpGetAccel(&aa, fifoBuffer);
                mpu.dmpGetGravity(&gravity, &q);
                mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
                printf("areal: %d,\t %d,\t %d\n", aaReal.x, aaReal.y, aaReal.z);
            #endif
            #ifdef OUTPUT_READABLE_WORLDACCEL
                // display initial world-frame acceleration, adjusted to remove gravity
                // and rotated based on known orientation from quaternion
                mpu.dmpGetQuaternion(&q, fifoBuffer);
                mpu.dmpGetAccel(&aa, fifoBuffer);
                mpu.dmpGetGravity(&gravity, &q);
                mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
                mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
                printf("aworld: %d,\t %d,\t %d\n", aaWorld.x, aaWorld.y, aaWorld.z);
            #endif
            #ifdef OUTPUT_READABLE_CUSTOM
                mpu.dmpGetQuaternion(&q, fifoBuffer);
                printf("W: %f\t X: %f\t Y: %f\t Z: %f\n", q.w, q.x, q.y, q.z);
            #endif
                printf("G: %f\t%f\t%f\n", gravity.x, gravity.y, gravity.z);

            sleep_ms(1000);
        }
    }

    return 0;
}
#endif
