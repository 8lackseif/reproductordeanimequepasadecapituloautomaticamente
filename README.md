# **reproductordeanimequepasadecapituloautomaticamente**

> reproductor de anime que pasa de capitulo automaticamente en segundo plano

> anime reproducer that change to next episode automatically when finish one side by side



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
  pyinstaller --onefile --noconsole --hidden-import=lxml --add-data "venv/Lib/site-packages/lxml-4.9.2.dist-info;lxml-4.9.2.dist-info" src/main.py
  
  ```
  5. Move the main.exe where you want.
  6. Make sure you have mpv installed in your terminal or put mpv.exe on the same directory with the main.exe.
  
## Showcase
  - start scrapping
  
  ![imagen](https://user-images.githubusercontent.com/108239975/227037679-fafe9c48-03e7-4ca8-9618-5885a81f7457.png)
  ---
  - finishes scrapping, opening a mpv to play the anime
  
  ![imagen](https://user-images.githubusercontent.com/108239975/227038069-b718a801-5d5f-48cb-83a1-42e8b91156b5.png)
  ---
  - change your episode with the mpv next video option or just wait, it will start next video automatically when previous one finish. 
  
  ![imagen](https://user-images.githubusercontent.com/108239975/227038471-18bbb5e4-9bb1-4d2c-a3ad-fba14f378dd8.png)



