filename = "image.png"

from PIL import Image

def resize_image(filename, new_width):
  img = Image.open(filename)
  width, height = img.size
  new_height = int(new_width * height / width)
  new_height = min(new_height, 200)
  img = img.resize((new_width, new_height))
  img.save(filename.replace(".png", "_small.png"))
  return img

def generate_code(img):
  with open("aparams.ino", "w") as f:
    f.write("const int height = " + str(img.height) + ";\n")
    for y in range(0, img.height):
      print("Row", y)
      # const char string_0[] PROGMEM = "String 0";
      f.write("const char color_" + str(y) + "[] PROGMEM = {")
      for x in range(0, img.width):
        r, g, b = img.getpixel((x, y))
        r = r // 43
        g = g // 43
        b = b // 43
        f.write(str(r*36 + g*6 + b + 1) + ", ")
      f.write("0};\n")

      # const char * const string_table[] PROGMEM = {string_0, string_1, string_2};
    f.write("const char * const color_table[] PROGMEM = {")
    for y in range(0, img.height):
      f.write("color_" + str(y) + ", ")

    f.write("};\n")

img = resize_image(filename, int(144/4))
generate_code(img)