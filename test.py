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


def convert_image(image_path):
    with open(image_path,"r") as f:
        new_image = []
        len_file=191*3
        new_image.append(f.readline())
        new_image.append(f.readline())
        dims=f.readline()
        new_image.append(dims)
        file_len=int(dims[:dims.index(" ")])*int(dims[dims.index(" "):])
        new_image.append(f.readline())
        for i in range(int(file_len)):
            pixel = f.readline()[0:-1] + " " + f.readline()[0:-1] + " " + f.readline()
            new_image.append(pixel)   
        f.close()
	return new_image
    

def read_image(image_path,number_of_image):
    converted_image = convert_image(image_path) 	#will be a list with 1 LE / 1ine
    converted_image = converted_image[2:]			#removes first 2 comment lines
    image_dims = converted_image[0]
    converted_image = converted_image[1:]
    image_width=int(image_dims[0:image_dims.index(" ")])
    converted_image = converted_image[1:]
    columns=[]
    for i in range(image_width):
        for j in range(144):#height of image (should be 144)
            line = converted_image[0]
	    converted_image = converted_image[1:]
	    if i==0:
	        columns.append([])
	        columns[j].append(line)
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

	with open("/images/new_format/transition"+number_of_image+".txt","w") as f:
                for i in final_columns:
                    for j in i:
                        f.write(str(j)+"\n")
	f.close()
	final_columns=[]
	width_of_each_image.append(image_width)
	image_as_txt_list.append("/images/new_format/transition"+number_of_image+".txt")

    
def show_picture(txt_path,image_width):
    with open(txt_path,"r") as f:
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



#Init. vars:
image_old_list = []
image_as_txt_list = []
width_of_each_image = []
button_counter=0
intermed_counter = 0


#show program start (not ready):
for _ in range(10):
     strip.setPixelColorRGB(_,200,0,0)
	
list_all = os.listdir('images')
pattern = "*.ppm"
for entry in list_all:  
    if fnmatch.fnmatch(entry, pattern):
         image_old_list.append(entry)
for _ in image_old_list:
    read_image("/images/"+_,intermed_counter)
    intermed_counter+=1

#show that ready:
for _ in range(10):
    strip.setPixelColorRGB(_,0,200,0)
	

while True:
    input_state = GPIO.input(25)
    if input_state == False:
        print("Button pressed")
        show_picture(image_as_txt_list[button_counter],width_of_each_image[button_counter])
        button_counter+=1
    time.sleep(0.2)
    if counter == len(image_new_list):
        counter = 0
