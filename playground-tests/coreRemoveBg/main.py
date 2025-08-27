from rembg import remove
from PIL import Image

input_path = 'input.jpg'
output_path = 'output.png'


inp = Image.open(input_path)
out = remove(inp)   # background removed
out.save(output_path)