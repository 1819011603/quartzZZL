function download_vedio {
    # 最后一个参数是 URL，其他都是传给 yt-dlp 的额外参数
    if ($args.Count -eq 0) {
        Write-Host "Usage: download_vedio [yt-dlp options] <url>" -ForegroundColor Yellow
        Write-Host "Example: download_vedio 'https://youtube.com/watch?v=xxx'" -ForegroundColor Gray
        Write-Host "Example: download_vedio -F 'https://youtube.com/watch?v=xxx'" -ForegroundColor Gray
        Write-Host "Example: download_vedio -f 22 'https://youtube.com/watch?v=xxx'" -ForegroundColor Gray
        return
    }
    
    $url = $args[-1]
    $extraArgs = @()
    if ($args.Count -gt 1) {
        $extraArgs = $args[0..($args.Count - 2)]
    }
    
    cd E:\Download
    
    # 清理重复的 cookie 文件，只保留最新的
    $files = Get-ChildItem "yt-blp-cookie*.txt" -ErrorAction SilentlyContinue | Sort-Object { 
        if ($_.Name -match '\((\d+)\)') { [int]$matches[1] } else { 0 } 
    } -Descending
    
    if ($files.Count -gt 1) { 
        $files | Select-Object -Skip 1 | Remove-Item -Force 
    }
    
    if ($files.Count -gt 0) { 
        $keep = $files[0]
        if ($keep.Name -ne "yt-blp-cookie.txt") { 
            if (Test-Path "yt-blp-cookie.txt") { 
                Remove-Item "yt-blp-cookie.txt" -Force 
            }
            Rename-Item $keep.FullName "yt-blp-cookie.txt" 
        } 
    }
    
    # 使用 yt-dlp 下载视频
    if ($extraArgs.Count -gt 0) {
        # 有额外参数时，直接传递（比如 -F 只列出格式）
        yt-dlp --cookies yt-blp-cookie.txt @extraArgs $url
    } else {
        # 无额外参数时，使用默认下载设置
        # 优先选择 avc1(H.264) 编码的 1080p，兼容性最好，画质最佳
        # 回退顺序：avc1 1080p > 任意 1080p > best
        yt-dlp --cookies yt-blp-cookie.txt -f "bestvideo[height<=1080][vcodec^=avc1]+bestaudio/bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 --concurrent-fragments 16 -P "H:\Downloads" -r 20M $url
    }
}
