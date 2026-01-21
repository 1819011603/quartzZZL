
### C盘清理

# SpaceSniffer(磁盘空间分析工具)

https://soft.3dmgame.com/down/200352.html
http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-07-14/7b5f1f3d157c5071201c2be7f40ac1f3/spacesniffer1302.zip

### 软件卸载

https://geekuninstaller.pro/download/

http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-07-14/bd73b1a5ea526e29680282637258df25/geek.zip



截屏

**`Win + Shift + S`**


| 功能     | macOS                | <br><br>Windows  |
| ------ | -------------------- | ---------------- |
| 查看所有桌面 | Ctrl + ↑             | Win + Tab        |
| 切换桌面   | Ctrl + ←/→           | Win + Ctrl + ←/→ |
| 新建桌面   | Mission Control 中点 + | Win + Ctrl + D   |

Win + Tab  可以新建桌面和删除桌面
![[../壁纸/附件/Pasted image 20260109232708.png]]




### windows创建脚本命令 

```
# ===== 一键创建 history_clear 命令 =====

# 1. 创建脚本目录
$scriptDir = "$env:USERPROFILE\PowerShellScripts"
New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null

# 2. 创建脚本文件
$scriptPath = "$scriptDir\history_clear.ps1"

$scriptContent = @'
$historyFile = (Get-PSReadLineOption).HistorySavePath

if (!(Test-Path $historyFile)) {
    Write-Host "历史文件不存在" -ForegroundColor Yellow
    exit
}

$history = Get-Content $historyFile
$beforeCount = $history.Count

$cleanHistory = $history | Where-Object {
    $cmd = $_.Trim()
    $cmd.Length -ge 3 -and $cmd -notmatch "^(ls|ll|cd|cls|clear|pwd|exit|quit|q|c|dir|echo)$"
}

$uniqueClean = @()
$seen = @{}

for ($i = $cleanHistory.Count - 1; $i -ge 0; $i--) {
    $cmd = $cleanHistory[$i].Trim()
    if ($cmd -and !$seen.ContainsKey($cmd)) {
        $seen[$cmd] = $true
        $uniqueClean = @($cmd) + $uniqueClean
    }
}

Copy-Item $historyFile "$historyFile.bak" -Force
$uniqueClean | Set-Content $historyFile

Write-Host "✅ 清理完成！移除 $($beforeCount - $uniqueClean.Count) 条" -ForegroundColor Green
'@

$scriptContent | Set-Content -Path $scriptPath -Encoding UTF8 -Force

# 3. 添加到 PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$scriptDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$scriptDir", "User")
    $env:Path += ";$scriptDir"
}

# 4. 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "===== 安装完成！ =====" -ForegroundColor Green
Write-Host "脚本位置: $scriptPath" -ForegroundColor White
Write-Host ""
Write-Host "现在可以直接使用命令：" -ForegroundColor Cyan
Write-Host "  history_clear" -ForegroundColor Yellow
Write-Host ""
Write-Host "测试一下：" -ForegroundColor Gray
history_clear
```


# Tabby的使用

![[../壁纸/附件/Pasted image 20260121223725.png]]


```

$exePath = "C:\Users\Administrator\scoop\shims\oh-my-posh.exe"

$themesPath = "C:\Users\Administrator\AppData\Local\Programs\oh-my-posh\themes"


Get-ChildItem "$themesPath\*.omp.json" | Select-Object -ExpandProperty BaseName | Sort-Object


Write-Host "`n===== tokyo =====" -ForegroundColor Cyan

& $exePath init pwsh --config "$themesPath\tokyo.omp.json" | Invoke-Expression





# 👇 把这里改成你选的主题名
$themeName = "atomic"

$exePath = "C:\Users\Administrator\scoop\shims\oh-my-posh.exe"
$themesPath = "C:\Users\Administrator\AppData\Local\Programs\oh-my-posh\themes"

$config = @"
# ===== Oh My Posh 配置 =====
`$exePath = "$exePath"
`$themesPath = "$themesPath"
`$env:POSH_THEMES_PATH = `$themesPath
& `$exePath init pwsh --config "`$themesPath\$themeName.omp.json" | Invoke-Expression
"@

$config | Set-Content $PROFILE -Force
Write-Host "✅ 已保存主题: $themeName" -ForegroundColor Green
Write-Host "重启 Tabby 永久生效！" -ForegroundColor Cyan


```


```

# ===== 配置命令历史和智能提示 =====

# 历史记录配置
$historyConfig = @"

# ===== 命令历史配置 =====
# 历史记录文件路径
`$historyFile = "`$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"

# 设置历史记录保存数量（保存最近 10000 条）
Set-PSReadLineOption -MaximumHistoryCount 10000

# 历史记录保存到文件
Set-PSReadLineOption -HistorySavePath `$historyFile
Set-PSReadLineOption -HistorySaveStyle SaveIncrementally

# ===== 智能提示配置 =====
# 开启基于历史的智能提示
Set-PSReadLineOption -PredictionSource History

# 提示显示样式：ListView（列表）或 InlineView（行内）
Set-PSReadLineOption -PredictionViewStyle ListView

# 提示颜色
Set-PSReadLineOption -Colors @{
    InlinePrediction = 'DarkGray'
    ListPrediction = 'DarkGray'
    ListPredictionSelected = 'DarkYellow'
}

# ===== 快捷键配置 =====
# 上下箭头搜索历史
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

# Tab 补全显示菜单
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete

# Ctrl+R 搜索历史
Set-PSReadLineKeyHandler -Key Ctrl+r -Function ReverseSearchHistory

# Ctrl+D 退出（像 Linux）
Set-PSReadLineKeyHandler -Key Ctrl+d -Function DeleteCharOrExit

"@

# 读取现有配置
$existingContent = ""
if (Test-Path $PROFILE) {
    $existingContent = Get-Content $PROFILE -Raw
    # 移除旧的历史配置
    $existingContent = $existingContent -replace "(?s)# ===== 命令历史配置 =====.*?# ===== 快捷键配置 =====.*?DeleteCharOrExit[`"']?\s*\)", ""
}

# 添加新配置
if ($existingContent -notmatch "命令历史配置") {
    Add-Content -Path $PROFILE -Value $historyConfig
    Write-Host "✅ 历史记录配置已添加！" -ForegroundColor Green
} else {
    Write-Host "⚠️ 配置已存在" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "功能说明：" -ForegroundColor Cyan
Write-Host "  📝 命令历史自动保存，重启不丢失" -ForegroundColor White
Write-Host "  💡 输入时显示历史命令提示（灰色）" -ForegroundColor White
Write-Host "  ⬆️  上箭头：搜索以当前输入开头的历史命令" -ForegroundColor White
Write-Host "  ⬇️  下箭头：向下搜索历史" -ForegroundColor White
Write-Host "  🔍 Ctrl+R：交互式搜索历史" -ForegroundColor White
Write-Host "  📋 Tab：显示补全菜单" -ForegroundColor White
Write-Host ""
Write-Host "重启 Tabby 生效！" -ForegroundColor Yellow
```

### 完整配置文件示例

# 查看当前配置文件

notepad $PROFILE

完整配置应该像这样：

```

# ===== Oh My Posh 配置 =====
$exePath = "C:\Users\Administrator\scoop\shims\oh-my-posh.exe"
$themesPath = "C:\Users\Administrator\AppData\Local\Programs\oh-my-posh\themes"
$env:POSH_THEMES_PATH = $themesPath
& $exePath init pwsh --config "$themesPath\atomic.omp.json" | Invoke-Expression

# ===== 命令历史配置 =====
Set-PSReadLineOption -MaximumHistoryCount 10000
Set-PSReadLineOption -HistorySaveStyle SaveIncrementally
Set-PSReadLineOption -PredictionSource History
Set-PSReadLineOption -PredictionViewStyle ListView
Set-PSReadLineOption -Colors @{
    InlinePrediction = 'DarkGray'
    ListPrediction = 'DarkGray'
}

# ===== 快捷键配置 =====
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadLineKeyHandler -Key Ctrl+r -Function ReverseSearchHistory
```


```
# 获取历史文件路径
$historyFile = (Get-PSReadLineOption).HistorySavePath

# 读取历史记录
$history = Get-Content $historyFile

# 统计去重前数量
$beforeCount = $history.Count

# 去重（保留最后一次出现的，即最新的）
$uniqueHistory = @()
$seen = @{}

# 从后往前遍历，保留最新的
for ($i = $history.Count - 1; $i -ge 0; $i--) {
    $cmd = $history[$i].Trim()
    if ($cmd -and !$seen.ContainsKey($cmd)) {
        $seen[$cmd] = $true
        $uniqueHistory = @($cmd) + $uniqueHistory
    }
}

# 备份原文件
Copy-Item $historyFile "$historyFile.bak" -Force

# 写入去重后的历史
$uniqueHistory | Set-Content $historyFile

# 统计结果
$afterCount = $uniqueHistory.Count
$removed = $beforeCount - $afterCount

Write-Host "✅ 去重完成！" -ForegroundColor Green
Write-Host "   去重前: $beforeCount 条" -ForegroundColor White
Write-Host "   去重后: $afterCount 条" -ForegroundColor White
Write-Host "   移除重复: $removed 条" -ForegroundColor Yellow
Write-Host "   备份文件: $historyFile.bak" -ForegroundColor Gray

 $historyFile = (Get-PSReadLineOption).HistorySavePath

    if (!(Test-Path $historyFile)) {

        Write-Host "历史文件不存在" -ForegroundColor Yellow

        return

    }

    $history = Get-Content $historyFile

    $beforeCount = $history.Count

    $cleanHistory = $history | Where-Object {

        $cmd = $_.Trim()

        $cmd.Length -ge 3 -and $cmd -notmatch "^(ls|ll|cd|cls|clear|pwd|exit|quit|q|c|dir)$"

    }

    $uniqueClean = @()

    $seen = @{}

    for ($i = $cleanHistory.Count - 1; $i -ge 0; $i--) {

        $cmd = $cleanHistory[$i].Trim()

        if ($cmd -and !$seen.ContainsKey($cmd)) {

            $seen[$cmd] = $true

            $uniqueClean = @($cmd) + $uniqueClean

        }

    }

    Copy-Item $historyFile "$historyFile.bak" -Force

    $uniqueClean | Set-Content $historyFile

    Write-Host "清理完成！移除 $($beforeCount - $uniqueClean.Count) 条" -ForegroundColor Green
```