
### safari 不支持无头模式

![[../壁纸/附件/Pasted image 20240705131730.png]]

- **macOS 环境**：Safari 浏览器和 Remote Automation 功能仅在 macOS 系统上可用。
- 1. **启用 Remote Automation**：在 Safari 浏览器的菜单栏中，选择 “Preferences” -> “Advanced”，并勾选 “Show Develop menu in menu bar”。然后在菜单栏中选择 “Develop” -> “Allow Remote Automation”。
- **系统权限**：确保 `safaridriver` 具有执行权限。在终端中运行以下命令：
	- sudo safaridriver --enable
- 确保没有其他 `safaridriver` 进程在运行。你可以使用以下命令来查看并终止所有 `safaridriver` 进程：
	- pkill safaridrive
- sudo mkdir /Users/gaotu/.cache/selenium
- sudo chmod a+w /Users/gaotu/.cache/selenium


```python
def get_safari_driver():  
    from selenium import webdriver  
    from selenium.webdriver.safari.options import Options  
    # 创建 Safari 选项  
    options = Options()  
    options.add_argument(  
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")  
    # option.add_argument("--headless")  
  
    # 返回配置了选项的 Safari WebDriver 对象  
    return webdriver.Safari(options=options)
driver = get_safari_driver()  
# 打开目标页面  
driver.get('https://www.baidu.com')  
  
# 获取页面标题  
print(driver.title)  
time.sleep(1000)  
driver.close()
```

