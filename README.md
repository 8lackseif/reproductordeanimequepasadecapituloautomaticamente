# **reproductordeanimequepasadecapituloautomaticamente**

> reproductor de anime que pasa de capitulo automaticamente en segundo plano

> anime reproducer that change to next episode automatically when finish one side by side

---
## Install

### Option 1 :
  1. Download release zip file.
  2. Extract to a directory.
  3. Open the main.exe.

### Option 2 :
  1. Make sure you have python installed.
  2. Clone the proyect.
  3. Go to the proyect directory, in terminal ` pip install -r requirements.txt `.
  4. Generate the .exe file with,
  ``` 
  pyinstaller --onefile --noconsole --hidden-import=lxml --add-data "venv/Lib/site-packages/lxml-4.9.2.dist-info;lxml-4.9.2.dist-info" src/main.py `
  
  ```
  5. Move the main.exe where you want.
  6. Make sure you have mpv installed in your terminal or put mpv.exe on the same directory with the main.exe.
  

