from neopixel import *
import time
import json
import RPi.GPIO as GPIO
import os, fnmatch



class Image_Handler():

    # Create image files which will be displayed
    def __init__(self):

        # Shows that the program is still computing
        for p in range(144):
             strip.setPixelColorRGB(p,200,0,0)
        strip.show()

        # Raw input images
        self.list_images_unparsed = []

        # Finished and ready to be displayed images
        self.list_images_parsed = []

        # Store only .ppm files
        for entry in os.listdir("images"):
            if fnmatch.fnmatch(entry, "*.ppm"):
                 self.list_images_unparsed.append(entry)

        # Store only .json files
        for entry in os.listdir("images/new_format"):
            if fnmatch.fnmatch(entry, "*.json"):
                 self.list_images_parsed.append(entry)

        # If an image has already been converted, skip it (saves a whole lot of time when repeating the process, especially when you start using a lot of pictures (or very large ones))
        for image_unparsed in self.list_images_unparsed:
            if (image_unparsed[:image_unparsed.index(".ppm")] + ".json") not in self.list_images_parsed:
                self.read_image("images/"+image_unparsed)

        # Turn off red LEDs
        self.clear_strip()

        # Shows that you're ready to go:
        for p in range(144):
            strip.setPixelColorRGB(p,0,200,0)
        strip.show()

        time.sleep(2)


    def read_image(self, image_unparsed_path):

        reconstructed_image = self.reconstruct_image(image_unparsed_path)
        # Recover image width
        image_width = reconstructed_image[0]
        # Remove image width from list
        reconstructed_image = reconstructed_image[1:]
        # Prepare final list --> pixels' arrangement: From left to right, From top to bottom | pixels' needed arrangement: From top to bottom, From left to right
        # Why? Because you display column after coloumn and not row after row
        inverted_list = [[] for _ in range(image_width)]
        reconstructed_image_index = 0

        # Fill inverted_list, sublists contain columns
        # Iterate ROWS (Always 144 = amount of pixels the LED strip possesses)
        for i in range(144):
            # Iterate COLUMNS (= amount of pixels in one row)
            for j in range(image_width):
                inverted_list[j].append(reconstructed_image[reconstructed_image_index])
                reconstructed_image_index += 1

        # Write this list to a json file with the same name stored in image/new_format
        with open("images/new_format/" + image_unparsed_path[image_unparsed_path.rfind("/"):image_unparsed_path.index(".ppm")] + ".json","w") as f:
            # Simply dump the resulting list into the file
            json.dump(inverted_list, f)
            f.close()

        # Delete list?
        #del inverted_list
        # Add file to list
        self.list_images_parsed.append("images/new_format/" + image_unparsed_path[image_unparsed_path.rfind("/")+1:image_unparsed_path.index(".ppm")] + ".json")


    # Reconstructs and stores the image's pixels in a list
    def reconstruct_image(self, image_unparsed_path):
        with open(image_unparsed_path,"r") as f:
            reconstructed_image = []
            # Skip title and file type
            f.readline()
            f.readline()
            # Store image width and height
            dims = f.readline()
            # Store total amount of pixels
            file_len = int(dims[:dims.index(" ")]) * int(dims[dims.index(" "):])
            # Store image width
            reconstructed_image.append(int(dims[:dims.index(" ")]))
            # Skip comment?
            f.readline()
            # Solely a single pixel color per line --> pixel distributed across 3 lines
            for i in range(file_len):
                # [:-1] to get rid of "\n" (newline, which is stored as a string in the file)
                r = int(f.readline()[:-1])
                g = int(f.readline()[:-1])
                b = int(f.readline()[:-1])
                #pixel = [r,g,b]
                reconstructed_image.append([r,g,b])

            f.close()

        return reconstructed_image


    # Aaaaaaannnd... ACTION!
    def display_picture(self, image_parsed_path):

        with open(image_parsed_path,"r") as f:
            # Load json file's content into variable
            pixels = json.load(f)
            f.close()

        for w in range(len(pixels)):
            for h in range(len(pixels[w])): # len(pixel[w]) immer 144 oder?
                temp_pixel = pixels[w][h]
                # Allocate each column's pixel to the strip
                """IF WISHING DO DEBUG  ON NON-RPI SYSTEMS"""
                #print(LED_COUNT-1-h,temp_pixel[0],temp_pixel[1],temp_pixel[2])
                strip.setPixelColorRGB(LED_COUNT-1-h,temp_pixel[0],temp_pixel[1],temp_pixel[2])
            # Show after the column has been completely filled
            ##strip.show()
            # As it is pretty perilous running around with an LED strip and since the results are not that good either, reduce the display frequency
            time.sleep(0.08)

    # Clear the strip
    def clear_strip(self):

        for p in range(144):
            strip.setPixelColorRGB(p, 0, 0, 0)

        strip.show()


if __name__ == "__main__":

    # Button configuration (GPIO pin 25)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # LED strip configuration:

    LED_COUNT	   = 144	    # Number of LED pixels

    LED_PIN		   = 18	        # GPIO pin connected to the strip (18 uses PWM!)
    LED_FREQ_HZ	   = 800000     # LED signal frequency in hertz (usually 800khz)
    LED_DMA		   = 5	        # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 50	        # Set to 0 for darkest and 255 for brightest
    LED_INVERT	   = False      # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL	   = 0	        # set to '1' for GPIOs 13, 19, 41, 45 or 53
    LED_STRIP	   = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

    # Object with which you control which LEDs are illuminated with which color
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Unlock strip's receipt of commands
    strip.begin()

    perfect_image_handler = Image_Handler()

    # Counts how many times the button has been clicked
    button_counter = 0
    #
    first_iteration = True

    # Launch main loop
    while True:

        # Show which image is about to be displayed
    	if first_iteration:
    		print(perfect_image_handler.list_images_parsed[button_counter] + " is next on the list.")

        # To prevent the while loop from displaying the above-mentioned message
    	first_iteration = False
        # Check button's input state
    	input_state = GPIO.input(25)
        #input_state = bool(input("TEST")) """DEBUGGING"""

        # If button clicked
    	if input_state == False:
            # Delay to let some scope for an eventual second button press
            time.sleep(0.3)
            # As an image will be displayed, the message shall tell us which one comes next
            first_iteration = True
            # Store time in order to work with time intervals
            start_time = time.time()
            # Visual help for the user
            print("Press now to skip to the next image")
            delta_t = True
            # While loop loops until the button is either clicked or left unpressed for 0.5s
            while delta_t:

                # If the image is clicked, skip the actual image
                input_state = GPIO.input(25)
                #input_state = bool(input("TEST")) """DEBUGGING""")

                if input_state == False:
                    delta_t = False
                    print("Button pressed twice")

                # Computes the actual time each while-loop-iteration and compares it to the precedently stored time
                if time.time() - start_time >= 0.5:
                    print(perfect_image_handler.list_images_parsed[button_counter] + " is being displayed now.")
                    perfect_image_handler.display_picture("images/new_format/"+perfect_image_handler.list_images_parsed[button_counter])
                    delta_t = False

            # Independently from your decision, jump to the subsequent image
            button_counter += 1

            #Better tha last if statement:
            button_counter = button_counter%len(perfect_image_handler.list_images_parsed)

        # Clear the srip after an image has been completely dis
        perfect_image_handler.clear_strip()
        time.sleep(0.2)

        """
        # Reset button_counter if it has reached the last image stored in perfect_image_handler.list_images_parsed
    	if button_counter == len(perfect_image_handler.list_images_parsed):
    		button_counter = 0
        """
