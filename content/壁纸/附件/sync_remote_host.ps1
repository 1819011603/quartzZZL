# 用法: 第二参相对路径相对「脚本所在目录」（非当前工作目录）。
# 仅传 env：在脚本所在目录下扫描含 .idea 的一级子目录；无子工程则用脚本目录（需含 .idea）。
# 例: D:\resetIdea\sync_remote_host.ps1 test-eco-3
# 例: D:\resetIdea\sync_remote_host.ps1 test-eco-1 student-data
# 例: .\sync_remote_host.ps1 test-eco-1 "student-center,student-data" "student-center,student-data-dws"
# 第三参与第二参按顺序一一对应；单工程时第三参可为多个候选名（逗号分隔）。
# env 可逗号分隔多个；链文里应用名含 . 时与配置里 - 会对齐（如 gaotu100.com 与 gaotu100-com）。

$ErrorActionPreference = "Continue"

$ScriptBaseDir = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    (Resolve-Path -LiteralPath $PSScriptRoot).Path
} else {
    (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
}

$EurekaUrl = "https://test-eureka.baijia.com/"
$IntervalSec = 120
$PortVal = "28666"

if ($args.Count -lt 1) {
    Write-Host "用法: sync_remote_host.ps1 <env> [工程路径,逗号分隔] [Eureka服务名,逗号分隔]  （路径相对脚本所在目录）" -ForegroundColor Red
    exit 1
}
$EnvName = $args[0]
if ($args.Count -eq 1) {
    $ExtraServicesCsv = ""
    $auto = @()
    foreach ($child in Get-ChildItem -LiteralPath $ScriptBaseDir -Directory -ErrorAction SilentlyContinue) {
        $idea = Join-Path $child.FullName ".idea"
        if (Test-Path -LiteralPath $idea) { $auto += $child.Name }
    }
    if ($auto.Count -gt 0) {
        $ProjectsCsv = $auto -join ","
    }
    elseif (Test-Path -LiteralPath (Join-Path $ScriptBaseDir ".idea")) {
        $ProjectsCsv = "."
    }
    else {
        Write-Host "仅传 env 时：脚本目录下需有含 .idea 的一级子目录，或脚本目录本身为工程（含 .idea）: $ScriptBaseDir" -ForegroundColor Red
        exit 1
    }
}
else {
    $ProjectsCsv = $args[1]
    $ExtraServicesCsv = if ($args.Count -ge 3) { $args[2] } else { "" }
}

function Get-EurekaCsvForRoot {
    param(
        [string]$ProjRoot,
        [string]$BaseName,
        [System.Collections.Generic.List[string]]$ProjectRoots,
        [System.Collections.Generic.List[string]]$EurekaByPos
    )
    if ($null -eq $EurekaByPos -or $EurekaByPos.Count -eq 0) { return $BaseName }
    if ($ProjectRoots.Count -eq 1) {
        $parts = [System.Collections.Generic.List[string]]::new()
        foreach ($x in $EurekaByPos) {
            if ($x.Length -gt 0) { [void]$parts.Add($x) }
        }
        if ($parts.Count -gt 0) { return ($parts -join ',') }
        return $BaseName
    }
    $idx = -1
    for ($i = 0; $i -lt $ProjectRoots.Count; $i++) {
        if ($ProjectRoots[$i].Equals($ProjRoot, [StringComparison]::OrdinalIgnoreCase)) {
            $idx = $i
            break
        }
    }
    if ($idx -lt 0) { return $BaseName }
    if ($idx -lt $EurekaByPos.Count -and $EurekaByPos[$idx].Length -gt 0) { return $EurekaByPos[$idx] }
    return $BaseName
}

function Get-ProjectRootFromPatchFile {
    param([string]$Path)
    $d = Split-Path $Path -Parent
    if ((Split-Path $d -Leaf) -eq 'runConfigurations') {
        $d = Split-Path $d -Parent
    }
    Split-Path $d -Parent
}

function Find-PatchFilesUnderRoot {
    param([string]$RootDir)
    $set = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    if (-not (Test-Path -LiteralPath $RootDir)) { return @() }
    $direct = Join-Path $RootDir ".idea\workspace.xml"
    if (Test-Path -LiteralPath $direct) { [void]$set.Add((Resolve-Path $direct).Path) }
    Get-ChildItem -LiteralPath $RootDir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Name -eq 'workspace.xml' -and $_.Directory.Name.Equals('.idea', [StringComparison]::OrdinalIgnoreCase)) -or
            ($_.Directory.Name.Equals('runConfigurations', [StringComparison]::OrdinalIgnoreCase) -and
                $_.Directory.Parent.Name.Equals('.idea', [StringComparison]::OrdinalIgnoreCase) -and
                $_.Extension.Equals('.xml', [StringComparison]::OrdinalIgnoreCase)) -or
            ($_.Directory.Name.Equals('.run', [StringComparison]::OrdinalIgnoreCase) -and
                $_.Extension.Equals('.xml', [StringComparison]::OrdinalIgnoreCase))
        } |
        ForEach-Object { [void]$set.Add($_.FullName) }
    return @($set)
}

function Get-NormEurekaSvcName {
    param([string]$s)
    return $s.ToLowerInvariant().Replace('.', '-')
}

function Test-EurekaRowHasEnv {
    param([string]$TextLower, [string[]]$EnvList)
    foreach ($e in $EnvList) {
        if ($TextLower.Contains('@' + $e)) { return $true }
    }
    return $false
}

function Test-EurekaRowMatchesService {
    param([string]$Text, [string]$Svc)
    $ns = Get-NormEurekaSvcName $Svc
    $m = [regex]::Match($Text, '^([^:]+):([^:]+):(\d+):')
    if ($m.Success) {
        if ((Get-NormEurekaSvcName $m.Groups[2].Value) -eq $ns) { return $true }
    }
    foreach ($part in $Text.Split(':')) {
        if ($part.Length -eq 0) { continue }
        if ($part -match '^\d+$') { continue }
        if ($part.StartsWith('@')) { continue }
        if ((Get-NormEurekaSvcName $part) -eq $ns) { return $true }
    }
    $tl = $Text.ToLowerInvariant().Replace('.', '-')
    $needle = (':' + $ns + ':')
    if ($tl.Contains($needle)) { return $true }
    return $false
}

function Extract-IpFromHtml {
    param([string]$HtmlPath, [string]$EnvTag, [string]$ServicesCsv)
    $services = @($ServicesCsv.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 })
    if ($services.Count -eq 0) { return $null }
    $envList = @($EnvTag.Split(',') | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_.Length -gt 0 })
    if ($envList.Count -eq 0) { return $null }

    $html = [IO.File]::ReadAllText($HtmlPath, [Text.UTF8Encoding]::new($false))
    $re = [regex]'<a\s+[^>]*href="https?://((?:\[[^\]]+\]|[^/":\s]+)):\d+[^"]*"[^>]*>([^<]*)</a>'
    foreach ($m in $re.Matches($html)) {
        $ip = $m.Groups[1].Value
        $text = $m.Groups[2].Value.Trim()
        $textL = $text.ToLowerInvariant()
        if (-not (Test-EurekaRowHasEnv -TextLower $textL -EnvList $envList)) { continue }
        foreach ($svc in $services) {
            if (Test-EurekaRowMatchesService -Text $text -Svc $svc) { return $ip }
        }
    }
    return $null
}

function Patch-IdeaXmlRemoteBlocks {
    param([string]$WsPath, [string]$NewHost, [string]$NewPort)
    $enc = New-Object System.Text.UTF8Encoding $false
    $xml = [IO.File]::ReadAllText($WsPath, $enc)
    $blockPat = '(<configuration\b(?=[^>]*(?:\btype="Remote[^"]*"|\bfactoryName="Remote"|factoryName="Remote JVM Debug"))[^>]*>)(.*?)(</configuration>)'
    $sb = New-Object System.Text.StringBuilder
    $last = 0
    foreach ($m in [regex]::Matches($xml, $blockPat, [System.Text.RegularExpressions.RegexOptions]::Singleline)) {
        [void]$sb.Append($xml.Substring($last, $m.Index - $last))
        $pre = $m.Groups[1].Value
        $body = $m.Groups[2].Value
        $post = $m.Groups[3].Value
        $body = $body -replace '(<option name="HOST" value=")[^"]*(")', "`$1$NewHost`$2"
        $body = $body -replace '(<option name="PORT" value=")[^"]*(")', "`$1$NewPort`$2"
        $body = $body -replace '(<option name="DEBUG_PORT" value=")[^"]*(")', "`$1$NewPort`$2"
        [void]$sb.Append($pre + $body + $post)
        $last = $m.Index + $m.Length
    }
    [void]$sb.Append($xml.Substring($last))
    [IO.File]::WriteAllText($WsPath, $sb.ToString(), $enc)
}

$ProjectRoots = [System.Collections.Generic.List[string]]::new()
foreach ($seg in $ProjectsCsv.Split(',')) {
    $p = $seg.Trim()
    if ($p.Length -eq 0) { continue }
    if (-not [IO.Path]::IsPathRooted($p)) {
        $p = Join-Path $ScriptBaseDir $p
    }
    if (-not (Test-Path -LiteralPath $p -PathType Container)) {
        Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: 不是目录，跳过: {1}" -f (Get-Date), $seg.Trim()) -ForegroundColor Yellow
        continue
    }
    $rp = (Resolve-Path -LiteralPath $p).Path
    [void]$ProjectRoots.Add($rp)
}

if ($ProjectRoots.Count -eq 0) {
    Write-Host "没有有效的工程路径" -ForegroundColor Red
    exit 1
}

Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 工程路径（{1} 个）:" -f (Get-Date), $ProjectRoots.Count)
foreach ($r in $ProjectRoots) { Write-Host "  - $r" }

$EurekaByPos = [System.Collections.Generic.List[string]]::new()
if ($ExtraServicesCsv) {
    foreach ($p in $ExtraServicesCsv.Split(',')) {
        [void]$EurekaByPos.Add($p.Trim())
    }
}
if ($EurekaByPos.Count -gt 0) {
    Write-Host ("{0:yyyy-MM-dd HH:mm:ss} Eureka 服务名与工程顺序对齐:" -f (Get-Date))
    if ($ProjectRoots.Count -eq 1) {
        $bn0 = Split-Path $ProjectRoots[0] -Leaf
        $cand = Get-EurekaCsvForRoot -ProjRoot $ProjectRoots[0] -BaseName $bn0 -ProjectRoots $ProjectRoots -EurekaByPos $EurekaByPos
        Write-Host ("  （单工程）候选: {0}" -f $cand)
    }
    else {
        if ($EurekaByPos.Count -ne $ProjectRoots.Count) {
            Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 警告: 工程数({1})与第三参项数({2})不一致；按索引对齐，缺项用目录名" -f (Get-Date), $ProjectRoots.Count, $EurekaByPos.Count) -ForegroundColor Yellow
        }
        for ($i = 0; $i -lt $ProjectRoots.Count; $i++) {
            $bn = Split-Path $ProjectRoots[$i] -Leaf
            if ($i -lt $EurekaByPos.Count -and $EurekaByPos[$i].Length -gt 0) {
                Write-Host ("  {0} -> {1}" -f $bn, $EurekaByPos[$i])
            }
            else {
                Write-Host ("  {0} -> （目录名 {0}）" -f $bn)
            }
        }
    }
}

function Sync-Once {
    $allFiles = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($r in $ProjectRoots) {
        foreach ($f in (Find-PatchFilesUnderRoot -RootDir $r)) {
            [void]$allFiles.Add($f)
        }
    }
    if ($allFiles.Count -eq 0) {
        Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: 在给定工程下未发现 workspace / runConfigurations / .run" -f (Get-Date)) -ForegroundColor Yellow
        return
    }

    $tmp = [IO.Path]::GetTempFileName()
    try {
        $curlArgs = @("-fsS", "-L", "-k", "-o", $tmp,
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            $EurekaUrl)
        & curl.exe @curlArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: 拉取 Eureka 失败" -f (Get-Date)) -ForegroundColor Yellow
            return
        }

        $any = $false
        foreach ($ws in $allFiles) {
            try {
                $raw = [IO.File]::ReadAllText($ws, [Text.UTF8Encoding]::new($false))
            }
            catch { continue }
            if ($raw -notmatch 'type="Remote' -and $raw -notmatch 'factoryName="Remote"' -and $raw -notmatch 'factoryName="Remote JVM Debug"') {
                Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 跳过（文件中无 Remote 运行配置）| {1}" -f (Get-Date), $ws) -ForegroundColor DarkGray
                continue
            }

            $projRoot = Get-ProjectRootFromPatchFile -Path $ws
            if ([string]::IsNullOrWhiteSpace($projRoot)) {
                Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: 无法解析工程根: {1}" -f (Get-Date), $ws) -ForegroundColor Yellow
                continue
            }

            $base = Split-Path $projRoot -Leaf
            $svcCsv = Get-EurekaCsvForRoot -ProjRoot $projRoot -BaseName $base -ProjectRoots $ProjectRoots -EurekaByPos $EurekaByPos
            $newHost = Extract-IpFromHtml -HtmlPath $tmp -EnvTag $EnvName -ServicesCsv $svcCsv
            if (-not $newHost) {
                Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 跳过 Eureka 无匹配 env={1} services=[{2}] | {3}" -f (Get-Date), $EnvName, $svcCsv, $ws) -ForegroundColor Yellow
                continue
            }
            try {
                Patch-IdeaXmlRemoteBlocks -WsPath $ws -NewHost $newHost -NewPort $PortVal
                Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 已更新 [{1}] HOST={2} PORT={3} ({4}) {5}" -f (Get-Date), $base, $newHost, $PortVal, $svcCsv, $ws)
                $any = $true
            }
            catch {
                Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: 写入失败 {1} {2}" -f (Get-Date), $ws, $_) -ForegroundColor Red
            }
        }

        if (-not $any) {
            Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 本轮无文件被更新" -f (Get-Date)) -ForegroundColor Yellow
        }
    }
    finally {
        if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    }
}

while ($true) {
    try { Sync-Once } catch { Write-Host ("{0:yyyy-MM-dd HH:mm:ss} 异常: {1}" -f (Get-Date), $_) -ForegroundColor Red }
    Start-Sleep -Seconds $IntervalSec
}
