from PIL import Image, ImageOps
import PySimpleGUI as sg
from io import StringIO

def Image_processing(inv, new_w, in_img, skip):
    # read width in mm and convert it to mm
    print("Creating grayscale inverted image...")
    new_w = int(new_w)
    new_w = new_w * 10
    skip = int(skip)
    img = Image.open(str(in_img)).convert('L')
    img_w = img.width
    img_h = img.height
    ratio = img_h / img_w
    new_h = round(new_w * ratio)
    img = img.resize((new_w, new_h), Image.ANTIALIAS)
    if inv is True:
        inverted_image = ImageOps.invert(img)
        inverted_image = ImageOps.mirror(inverted_image)
        img = inverted_image
    x = img.width
    y = img.height
    data = list(img.getdata())
    fil = StringIO()
    for k in range(y):
        for i in range(x):
            if data[i + (k * x)] >= skip:
                Row = data[i + (k * x)]
                fil.write(str(Row) + ",")
            else:
                fil.write(str(0) + ",")
            i += 1
        # file.write("\n")
        k += 1
    print("Image processing finished!")
    return x, y, fil

def view(inv, new_w, in_img):
    new_w = str(new_w)
    new_w = int(new_w)
    new_w = new_w * 10
    img = Image.open(str(in_img)).convert('L')
    img_w = img.width
    img_h = img.height
    ratio = img_h / img_w
    new_h = round(new_w * ratio)
    img = img.resize((new_w, new_h), Image.ANTIALIAS)
    if inv is True:
        inverted_image = ImageOps.invert(img)
        inverted_image = ImageOps.mirror(inverted_image)
        img = inverted_image
    img.show()
    return

def save(inv, new_w, in_img):
    new_w = str(new_w)
    new_w = int(new_w)
    new_w = new_w * 10
    img = Image.open(str(in_img)).convert('L')
    img_w = img.width
    img_h = img.height
    ratio = img_h / img_w
    new_h = round(new_w * ratio)
    img = img.resize((new_w, new_h), Image.ANTIALIAS)
    if inv is True:
        inverted_image = ImageOps.invert(img)
        inverted_image = ImageOps.mirror(inverted_image)
        img = inverted_image
    img.save('Output.png')
    return

def gcode_generator(data, w, h, powerh, t_speed, s_speed, startx, starty, filename):
    print("Generating G-code...")
    outfile = open(filename + '.gcode', 'w')
    #out = open(filename + '.txt', 'w')
    outfile.write\
(f""";Image width: {w} pix
;Image height: {h} pix
;Laser max power: {powerh} %
;Travel speed: {t_speed} mm/min
;Scan speed: {s_speed} mm/min
;X start position: {startx} mm
;Y start position: {starty} mm
G21 ; Units in mm
G90 ; Absolute positioning 
G28 X Y; Home X and Y axes 
G1 F{t_speed} X{startx} Y{starty}
G1 F{s_speed}
G91
M0 Start?
""")
    h = int(h)
    w = int(w)
    powerh = int(powerh)
    maps = data
    remap = maps.getvalue().split(",")
    for k in range(h):
        for i in range(w):
            pixel = remap[i + (k * w)]
            if int(k) > 0 and int(k) < (h-1):
                pixhelp5 = remap[(i+(k * w)) + 5]
                pixhelp4 = remap[(i+(k * w)) + 4]
                pixhelp3 = remap[(i+(k * w)) + 3]
                pixhelp2 = remap[(i+(k * w)) + 2]
                pixhelp1 = remap[(i+(k * w)) + 1]
                pixhelpm1 = remap[(i+(k * w)) - 1]
                pixhelpm2 = remap[(i+(k * w)) - 2]
            else:
                pixhelp1 = pixhelp2 = pixhelp3 = pixhelp4 = pixhelp5 = pixhelpm2 = pixhelpm1 = 1

            if int(pixhelp5) == 0 and int(pixhelp4) == 0 and int(pixhelp3) == 0 and int(pixhelp2) == 0 and int(pixhelp1) == 0 and int(pixhelpm1) == 0 and int(pixhelpm2) == 0:
                outfile.write\
(f"""
G1 F{t_speed}
M106 S{(str(round(float(pixel)*(powerh/100))))}
G1 X0.1
""")
            else:
                outfile.write\
(f"""
G1 F{s_speed}
M106 S{(str(round(float(pixel) * (powerh / 100))))}
G1 X0.1
""")

            i += 1
        outfile.write\
(f"""
M107
G4 P20
G1 F{t_speed} X-{str(w / 10)} Y0.1
G4 P20

G1 F{s_speed};
""")
        k += 1
    outfile.write\
(f"""
M107
G90
G1 F{t_speed} X0 Y235
M84
""")
    file.close()
    outfile.close()
    #out.close()
    print("Done!")
    return

sg.theme('DarkBrown1')

layout = [[sg.Input(key='_FILEBROWSE_', enable_events=True, visible=False)],
          [sg.Text("Select image", size=(30, 1)), sg.Output(size=(50, 2)), sg.FileBrowse(target='_FILEBROWSE_')],
          [sg.Text("Set width (height autocalculated)[mm]: ", size=(30, 1)), sg.Input(key='_WIDTH_', size=(10, 1))],
          [sg.Checkbox('Invert image colours', key='_INV_', default=True)],
          [sg.Text("Skip under values [0-255]: ", size=(30, 1)), sg.Input(key='_SKIP_', size=(10, 1), default_text=40)],
          [sg.Text("Set max power [%]:", size=(30, 1)), sg.Input(key='_POWERH_', size=(10, 1), default_text=50)],
          [sg.Text("Travel speed [mm/min]:", size=(30, 1)), sg.Input(key='_TRAVELSPEED_', size=(10, 1), default_text=10000)],
          [sg.Text("Scan speed [mm/min]:", size=(30, 1)), sg.Input(key='_SCANSPEED_', size=(10, 1), default_text=50)],
          [sg.Text("Start X position [mm]:", size=(30, 1)), sg.Input(key='_STARTX_', size=(10, 1), default_text=50)],
          [sg.Text("Start Y position [mm]:", size=(30, 1)), sg.Input(key='_STARTY_', size=(10, 1), default_text=30)],
          [sg.Text("Output filename:", size=(30, 1)), sg.Input(key='_FILENAME_', size=(30, 1))],
          [sg.Button('View grayscale', size=(15, 1)), sg.Button('Save grayscale', size=(15, 1)),
           sg.Button('Generate', size=(15, 1)), sg.Button('Exit', size=(15, 1))],
          [sg.Text("This script generates Gcode for Marlin flavoured 3D printers from an image. \nThe higher the "
                   "brightness of the pixel,the higher the power of the laser.\n\n"
                   "Help:\n\n"
                   "Select image: Select a picture from Your computer\n\n"
                   "Set width...: Set the width of picture in mm. Resolution will be 0.1mm/pixel. Ratio will be maintained.\n\n"
                   "Invert image colours: If Your images' background is too dark, inverting is recommended (use the \n"
                   "'View Grayscale' button to inspect processed image. Remember, brighter pixels will be darker).\n\n"
                   "Skip under values: This value is for filter the pixels which have too low intensity according to Your laser.\n\n"
                   "Set max power: Adjusts the maximum power of the laser (100% = 255).\n\n"
                   "Travel speed: Set the travel speed in mm/min.\n\n"
                   "Scan speed: Set the cutting (engraving) speed in mm/min.\n\n"
                   "Start X and Y position: Set X and Y offset.\n\n"
                   "Output filename: Type the filename you want to save."
                   )]]

window = sg.Window('IMG2Gcode').Layout(layout)

while True:  # Event Loop
    event, values = window.Read()
    print(values['_FILEBROWSE_'])

    if event is None or event is 'Exit':
        window.close()
        break

    if event is "Generate":

        if len(values['_FILEBROWSE_']) == 0:
            print("No file selected!")
        elif len(values['_WIDTH_']) == 0:
            print("Width data incorrect!")
        elif len(values['_SKIP_']) == 0:
            print("Skip data incorrect!")
        elif len(values['_POWERH_']) == 0:
            print("Power data incorrect!")
        elif len(values['_TRAVELSPEED_']) == 0:
            print("Travel speed data incorrect!")
        elif len(values['_SCANSPEED_']) == 0:
            print("Scan speed data incorrect!")
        elif len(values['_STARTX_']) == 0:
            print("X start position incorrect!")
        elif len(values['_STARTY_']) == 0:
            print("Y start position incorrect!")
        elif len(values['_FILENAME_']) == 0:
            print("Filename incorrect!")
        else:
            x, y, file = Image_processing(values['_INV_'], values['_WIDTH_'], values['_FILEBROWSE_'], values['_SKIP_'])
            gcode_generator(file, str(x), str(y), values['_POWERH_'], values['_TRAVELSPEED_'], values['_SCANSPEED_'],
                            values['_STARTX_'], values['_STARTY_'], values['_FILENAME_'])

    if event is "View grayscale":

        if len(values['_FILEBROWSE_']) == 0:
            print("No file selected!")
        elif len(values['_WIDTH_']) == 0:
            print("Width data incorrect!")
        else:
            view(values['_INV_'], values['_WIDTH_'], values['_FILEBROWSE_'])

    if event is "Save grayscale":

        if len(values['_FILEBROWSE_']) == 0:
            print("No file selected!")
        elif len(values['_WIDTH_']) == 0:
            print("Width data incorrect!")
        else:
            save(values['_INV_'], values['_WIDTH_'], values['_FILEBROWSE_'])
