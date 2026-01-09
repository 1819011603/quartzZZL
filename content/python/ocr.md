
ocr

https://catocr.com/#/

https://web.baimiaoapp.com/





#### macOS

使用 Homebrew 进行安装：


`brew install tesseract`


`brew install tesseract-lang # 安装语言包`

### 下载语言数据包

为了让 Tesseract 识别中文和英文，需要确保下载了相关的语言数据包。如果没有，可以从 [Tesseract 语言数据包](https://github.com/tesseract-ocr/tessdata) 下载 `chi_sim.traineddata` 和 `eng.traineddata`，并将其放置在 Tesseract 的 `tessdata` 目录中。
### 命令行使用

使用 Tesseract 识别包含中文和英文的图片，可以通过以下命令：

`tesseract input_image.png output_text -l chi_sim+eng --psm 6 --oem 1`

这个命令指定了 Tesseract 使用简体中文和英文语言模型来处理图片 `input_image.png`，识别结果会保存到 `output_text.txt` 文件中。
