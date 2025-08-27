from nicegui import ui, app
from fastapi import UploadFile
import threading
import time
import cv2
import numpy as np
import os

from rembg import remove
from PIL import Image

class UiGen:
    def __init__(self):
        self.status_label = None
        self.processed_path = "processed.png"
        self.spawnGui()

    def run(self):
        self.t = threading.Thread(target=self.host, daemon=True)
        self.t.start()

    def host(self):
        ui.run(reload=False, show=False)

    def spawnGui(self):
        ui.dark_mode().enable()
        ui.label("Upload an image").classes("text-xl")

        self.status_label = ui.label("Idle")



        ui.upload(
            label="Upload Image",
            auto_upload=True,
            on_upload=self.on_upload,
            max_file_size=10_000_000,
        ).props('accept=image/*')

        base64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        self.outputImage = ui.image(base64)




    def on_upload(self, e):
        # Set status to "processing"
        self.status_label.set_text("Processing...")

        # Save uploaded file temporarily
        input_path = "input.png"
        with open(input_path, "wb") as f:
            f.write(e.content.read())   # <-- use .files[0].content

        # Start background worker
        threading.Thread(
            target=self.process_image,
            args=(input_path, self.processed_path),
            daemon=True
        ).start()

    def process_image(self, input_path, output_path):
        import cv2
        

        img = cv2.imread(input_path)
        if img is not None:
            out = remove(img)
            cv2.imwrite(output_path, out)
            out = cv2.cvtColor(out, cv2.COLOR_RGB2BGR)
            self.outputImage.set_source(Image.fromarray(out))


        self.status_label.set_text("finished")

if __name__ == "__main__":
    ug = UiGen()
    ug.run()
    while True:
        time.sleep(1)