function download_vedio {
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
    
    $files = Get-ChildItem "yt-blp-cookie*.txt" -ErrorAction SilentlyContinue | Sort-Object { if ($_.Name -match '\((\d+)\)') { [int]$matches[1] } else { 0 } } -Descending
    
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

    cd H:\Software\bin
    
    $isListFormats = $extraArgs -contains "-F" -or $extraArgs -contains "--list-formats"
    $beforeDownload = Get-Date
    
    if ($isListFormats) {
        ./yt-dlp.exe --cookies E:\Download\yt-blp-cookie.txt @extraArgs $url
        return
    }
    
    if ($extraArgs.Count -gt 0) {
        ./yt-dlp.exe --cookies E:\Download\yt-blp-cookie.txt -f "bestvideo[height<=1080][vcodec^=avc1]+bestaudio/bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 --concurrent-fragments 4 -P "H:\Downloads" -r 20M @extraArgs $url
    } else {
        ./yt-dlp.exe --cookies E:\Download\yt-blp-cookie.txt -f "bestvideo[height<=1080][vcodec^=avc1]+bestaudio/bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 --concurrent-fragments 4 -P "H:\Downloads" -r 20M $url
    }
    
    # 下载完成后打开最新的视频文件
    if ($LASTEXITCODE -eq 0) {
        Start-Sleep -Seconds 1
        $latestFile = Get-ChildItem "H:\Downloads\*.mp4" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $beforeDownload } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latestFile) {
            Write-Host "`nOpening: $($latestFile.FullName)" -ForegroundColor Green
            Start-Process $latestFile.FullName
        }
    }
}
