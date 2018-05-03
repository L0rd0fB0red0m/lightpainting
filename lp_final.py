from neopixel import *
import time
import ast
import RPi.GPIO as GPIO
import random
import os, fnmatch

#Button-config:
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()


def convert_image(image_path,image_path_new):
    with open(image_path,"r") as f:
        with open(image_path_new,"w") as k:
            #file1=f.readlines()
            #len_file = len(file1)-4
            len_file=191*3
            k.write(f.readline())
            k.write(f.readline())
            dims=f.readline()
            k.write(dims)
            file_len=int(dims[:dims.index(" ")])*int(dims[dims.index(" "):])
            k.write(f.readline())
            for i in range(int(file_len)):
                pixel = f.readline()[0:-1] + " " + f.readline()[0:-1] + " " + f.readline()
                k.write(pixel)
                
        k.close()
    f.close()
    
    
def show_picture(image_path_new):
    image_width=read_image(image_path_new)
    with open("transition.txt","r") as f:
        for i in range(image_width):
            for j in range(144):
                pixel_now=f.readline()
                pixel_now=ast.literal_eval(pixel_now)
                print(i,j,pixel_now[0],pixel_now[1],pixel_now[2])
                strip.setPixelColorRGB(j,pixel_now[0],pixel_now[1],pixel_now[2])
            strip.show()
            time.sleep(0.08)
            #print(i)


def clear_strip():
    for i in range(144):
        strip.setPixelColorRGB(i,0,0,0)


def read_image(image_path_new):
    with open(image_path_new,"r") as f:
        f.readline()
        f.readline()#remove if img file has no comment
        image_dims = f.readline()
        image_width=int(image_dims[0:image_dims.index(" ")])
        f.readline()
        columns=[]

        for i in range(image_width):
            for j in range(144):#height of image (should be 144)
                line=f.readline()
                if i==0:
                    columns.append([])
                columns[j].append(line)
    f.close()
    final_columns=[]

    for i in range(len(columns)):
        final_columns.append([])
        for j in range(len(columns[i])):
            final_columns[i].append([])
            columns[i][j]=columns[i][j][:-1]
            for k in range(2):
                final_columns[i][j].append(int(columns[i][j][:columns[i][j].index(" ")]))
                columns[i][j]=columns[i][j][columns[i][j].index(" ")+1:]
                #print(columns)
            final_columns[i][j].append(int(columns[i][j]))

    with open("transition.txt","w") as f:
        for i in final_columns:
            for j in i:
                f.write(str(j)+"\n")
    f.close()
    final_columns=[]
    return(image_width)


def main_loop(counterNOW):
    convert_image("images/"+image_old_list[counterNOW],"images/new/"+image_new_list[counterNOW])
    show_picture("images/new/"+image_new_list[counterNOW])


image_old_list = []
image_new_list=[]
button_counter=0

list_all = os.listdir('images')
pattern = "*.ppm"
for entry in list_all:  
    if fnmatch.fnmatch(entry, pattern):
            image_old_list.append(entry)

for j in image_old_list:
    image_new_list.append(j[:j.index(".ppm")]+"NEW.ppm")

print(image_new_list,image_old_list)
while True:
    print(button_counter)
    input_state = GPIO.input(25)
    if input_state == False:
        print("Button pressed")
        main_loop(button_counter)
        button_counter+=1
    time.sleep(0.2)
    if counter == len(image_new_list):
        counter = 0
