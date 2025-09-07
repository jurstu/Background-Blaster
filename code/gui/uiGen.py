from nicegui import ui, app
from fastapi import UploadFile
from fastapi import Response
import threading
import time
import cv2
import numpy as np
import os
import shutil

from rembg import remove
from PIL import Image

class UiGen:
    def __init__(self):
        self.inputImageSrc =  np.empty((480, 720, 3))
        self.outputImageSrc = np.empty((480, 720, 3)) + 255

        self.prepareFs()

        self.spawnGui()

    def prepareFs(self):
        self.path = "/tmp/BackgroundBlaster"
        self.inputPath = os.path.join(self.path, "input.png")        
        self.processedPath = os.path.join(self.path, "processed.png")        

        # If the directory exists, remove it completely
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

        # Recreate the empty directory
        os.makedirs(self.path, exist_ok=True)

        print(f"Directory prepared: {self.path}")

    def run(self):
        self.t = threading.Thread(target=self.host, daemon=True)
        self.t.start()

    def host(self):
        ui.run(reload=False, show=False)

    def spawnGui(self):
        ui.dark_mode().enable()
        with ui.column():
            with ui.row():
                with ui.card().classes("w-full shadow-lg bg-gray-400").style("height: 480px; width: 720px"):
                    self.inputImage = ui.interactive_image(f'/video/source?{time.time()}') \
                        .classes('w-full h-full object-contain')
                    
                with ui.card().classes("w-full shadow-lg bg-gray-400").style("height: 480px; width: 720px"):
                    self.outputImage = ui.interactive_image(f'/video/processed?{time.time()}') \
                        .classes('w-full h-full object-contain')
            
        
            ui.upload(
                label="Upload Image",
                auto_upload=True,
                on_upload=self.on_upload,
                max_file_size=10_000_000,
            ).props('accept=image/*')

        ui.timer(interval=0.3, callback=lambda: self.outputImage.set_source(f'/video/processed?{time.time()}'))
        ui.timer(interval=0.3, callback=lambda: self.inputImage.set_source(f'/video/source?{time.time()}'))


        @app.get("/video/source", response_class=Response)
        def grabVideoFrame() -> Response:
            _, raw = cv2.imencode(".png", self.inputImageSrc)
            return Response(content=raw.tobytes(), media_type="image/png") 

        @app.get("/video/processed", response_class=Response)
        def grabVideoFrame() -> Response:
            _, raw = cv2.imencode(".png", self.outputImageSrc)
            return Response(content=raw.tobytes(), media_type="image/png") 

    def on_upload(self, e):
        # Set status to "processing"
        # Save uploaded file temporarily
        with open(self.inputPath, "wb") as f:
            f.write(e.content.read())   # <-- use .files[0].content

        self.inputImageSrc = cv2.imread(self.inputPath)
        # Start background worker
        threading.Thread(
            target=self.process_image,
            args=(self.inputPath, self.processedPath),
            daemon=True
        ).start()

    def process_image(self, input_path, output_path):
        import cv2
        img = cv2.imread(input_path)
        if img is not None:
            out = remove(img)
            cv2.imwrite(output_path, out)
            self.outputImageSrc = out       
            print("file processed")

   

if __name__ == "__main__":
    ug = UiGen()
    ug.run()
    while True:
        time.sleep(1)