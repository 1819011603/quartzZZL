#!/usr/bin/env bash
# 用法: ./sync_remote_host.sh <env> [工程路径,逗号分隔] [Eureka服务名,逗号分隔]
# 仅传 <env> 时：在「脚本所在目录」下扫描含 .idea 的一级子目录；若无子工程则把脚本所在目录当作工程（需含 .idea）。
# 第二参相对路径均相对「脚本所在目录」解析（非当前工作目录）；绝对路径仍按原样使用。
# 例: /path/to/sync_remote_host.sh test-eco-3
# 例: /path/to/sync_remote_host.sh test-eco-1 student-data
# 例: ./sync_remote_host.sh test-eco-1 "student-data,linkup" "student-data-dws,student-data-gps"
# 第三参与第二参按顺序一一对应：第 i 个工程只用第 i 个 Eureka 名查 IP（多工程不会共用一个服务名列表）。
# 仅 1 个工程时：第三参可写多个候选名（逗号分隔），按顺序尝试，仍不用目录名参与（除非某项留空）。
# 不传第三参时：各工程只用各自目录 basename。链接文案一般为 实例名:应用名:端口:@环境。
# <env> 可逗号分隔多个，任一出现在链文 @xxx 即算命中（如 default,test-crm-dev-4）。服务名匹配会将 . 与 - 归一（页上 gaotu100.com 可与配置 gaotu100-com 对上）。
# 内置: 每 120 秒一轮；PORT=28666；curl -k；EUREKA_URL 见下。

EUREKA_URL="https://test-eureka.baijia.com/"
INTERVAL=120
PORT_VAL=28666

SCRIPT_SOURCE="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd -P) || {
  echo "$(date '+%F %T') 异常: 无法解析脚本所在目录" >&2
  exit 1
}

usage() {
  echo "用法: $0 <env[,env2,...]> [工程路径,逗号分隔] [Eureka服务名,逗号分隔]  （路径相对脚本所在目录）" >&2
  echo "例: (脚本同目录下含多个子工程) $0 test-eco-3" >&2
  echo "例: $0 test-eco-1 student-data  （目录名相对脚本所在路径）" >&2
  echo "例: $0 test-eco-1 \"student-center,student-data\" \"student-center,student-data-dws\"  （顺序对齐）" >&2
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
elif [[ $# -eq 1 ]]; then
  ENV_NAME="$1"
  EXTRA_SERVICES_CSV=""
  PROJECTS_CSV=""
  for _d in "$SCRIPT_DIR"/*; do
    [[ -d "$_d/.idea" ]] || continue
    _n=$(basename "$_d")
    PROJECTS_CSV="${PROJECTS_CSV:+$PROJECTS_CSV,}$_n"
  done
  if [[ -z "$PROJECTS_CSV" ]]; then
    if [[ -d "$SCRIPT_DIR/.idea" ]]; then
      PROJECTS_CSV="."
    else
      echo "$(date '+%F %T') 仅传 env 时：脚本目录下需有含 .idea 的一级子目录，或脚本目录本身为工程（含 .idea）: $SCRIPT_DIR" >&2
      usage
    fi
  fi
else
  ENV_NAME="$1"
  PROJECTS_CSV="$2"
  EXTRA_SERVICES_CSV="${3:-}"
fi

project_root_from_patch_file() {
  local f="$1"
  local d
  d=$(dirname "$f")
  if [[ "$(basename "$d")" == "runConfigurations" ]]; then
    d=$(dirname "$d")
  fi
  dirname "$d"
}

discover_patch_files_under() {
  local dir="$1"
  local tf
  tf=$(mktemp "${TMPDIR:-/tmp}/wslist.XXXXXX") || return 1
  # .run 下多为 *.run.xml（亦为 .xml）；两种 path 都写上以免个别 find 实现边界差异
  find "$dir" -type f \( -path '*/.idea/workspace.xml' -o -path '*/.idea/runConfigurations/*.xml' -o -path '*/.run/*.xml' -o -path '*/.run/*.run.xml' \) 2>/dev/null | sort -u >"$tf"
  if [[ -s "$tf" ]]; then
    cat "$tf"
    rm -f "$tf"
    return 0
  fi
  rm -f "$tf"
  return 1
}

extract_ip_from_eureka_html() {
  local html_file="$1"
  local env_tag="$2"
  local services_csv="$3"
  perl -CSD -e '
    use strict;
    use warnings;
    my ($path, $env, $csv) = @ARGV;
    my @services = grep { length } map {
      my $s = $_;
      $s =~ s/^\s+|\s+$//g;
      $s;
    } split /,/, $csv;
    die "no services\n" unless @services;
    my @envs = grep { length } map {
      my $e = $_;
      $e =~ s/^\s+|\s+$//g;
      lc $e;
    } split /,/, $env;
    die "no env\n" unless @envs;
    sub norm_svc {
      my ($s) = @_;
      $s = lc $s;
      $s =~ s/\./-/g;
      return $s;
    }
    sub row_has_env {
      my ($text_l, $envs_ref) = @_;
      for my $ex (@$envs_ref) {
        return 1 if index($text_l, "\@$ex") >= 0;
      }
      return 0;
    }
    sub row_matches_service {
      my ($text, $svc) = @_;
      my $ns = norm_svc($svc);
      if ($text =~ /^([^:]+):([^:]+):(\d+):/) {
        return 1 if norm_svc($2) eq $ns;
      }
      for my $part (split /:/, $text) {
        next unless length $part;
        next if $part =~ /^\d+$/;
        next if $part =~ /^@/;
        return 1 if norm_svc($part) eq $ns;
      }
      (my $tl = lc $text) =~ s/\./-/g;
      return 1 if index($tl, ":" . $ns . ":") >= 0;
      return 0;
    }
    open my $fh, "<:encoding(UTF-8)", $path or die "open html: $!\n";
    my $html = do { local $/; <$fh> };
    close $fh;
    while ($html =~ /<a\s+[^>]*href="https?:\/\/((?:\[[^\]]+\]|[^\/":\s]+)):\d+[^"]*"[^>]*>([^<]*)<\/a>/gi) {
      my ($ip, $text) = ($1, $2);
      $text =~ s/^\s+|\s+$//g;
      next unless row_has_env(lc $text, \@envs);
      for my $svc (@services) {
        next unless row_matches_service($text, $svc);
        print $ip;
        exit 0;
      }
    }
    exit 1;
  ' "$html_file" "$env_tag" "$services_csv"
}

patch_idea_xml_remote_blocks() {
  local target="$1"
  local new_host="$2"
  local new_port="$3"
  local out
  out=$(mktemp "${TMPDIR:-/tmp}/patchxml.XXXXXX") || return 1
  SYNC_NEW_HOST="$new_host" SYNC_REMOTE_PORT="$new_port" perl -CSD -0777 -e '
    use strict;
    use warnings;
    my $host = $ENV{SYNC_NEW_HOST} // die "SYNC_NEW_HOST\n";
    my $port = $ENV{SYNC_REMOTE_PORT} // die "SYNC_REMOTE_PORT\n";
    my $xml = do { local $/; <STDIN> };
    sub patch_block {
      my ($b) = @_;
      $b =~ s/(<option name="HOST" value=")[^"]*(")/$1$host$2/g;
      $b =~ s/(<option name="PORT" value=")[^"]*(")/$1$port$2/g;
      $b =~ s/(<option name="DEBUG_PORT" value=")[^"]*(")/$1$port$2/g;
      return $b;
    }
    # IDEA：type="Remote…" 或仅 factoryName="Remote" / "Remote JVM Debug"（.run/*.run.xml 常见）
    my $open = qr/<configuration\b(?=[^>]*(?:\btype="Remote[^"]*"|\bfactoryName="Remote"|factoryName="Remote JVM Debug"))[^>]*>/;
    $xml =~ s{($open)(.*?)(</configuration>)}{$1.patch_block($2).$3}gse;
    print $xml;
  ' <"$target" >"$out" || { rm -f "$out"; return 1; }
  mv "$out" "$target" || { rm -f "$out"; return 1; }
}

declare -a PROJECT_ROOTS=()
# 相对路径按脚本所在目录解析；已 / 或 Windows 盘符开头则视为绝对路径
resolve_project_dir() {
  local p="$1"
  if [[ "$p" == /* ]] || [[ "$p" == [A-Za-z]:[/\\]* ]]; then
    printf '%s' "$p"
  else
    printf '%s' "$SCRIPT_DIR/$p"
  fi
}

IFS=',' read -ra _raw_projects <<< "$PROJECTS_CSV"
for _p in "${_raw_projects[@]}"; do
  _p="${_p#"${_p%%[![:space:]]*}"}"
  _p="${_p%"${_p##*[![:space:]]}"}"
  [[ -z "$_p" ]] && continue
  _abs=$(resolve_project_dir "$_p")
  if [[ ! -d "$_abs" ]]; then
    echo "$(date '+%F %T') 异常: 不是目录，跳过: $_p （已解析为 $_abs）" >&2
    continue
  fi
  _rp=$(cd "$_abs" 2>/dev/null && pwd -P) || {
    echo "$(date '+%F %T') 异常: 无法进入目录: $_abs" >&2
    continue
  }
  PROJECT_ROOTS+=("$_rp")
done

if [[ ${#PROJECT_ROOTS[@]} -eq 0 ]]; then
  echo "$(date '+%F %T') 异常: 没有有效的工程路径" >&2
  exit 1
fi

declare -a EUREKA_BY_POS=()
if [[ -n "$EXTRA_SERVICES_CSV" ]]; then
  IFS=',' read -ra _raw_eureka <<< "$EXTRA_SERVICES_CSV"
  for _p in "${_raw_eureka[@]}"; do
    _p="${_p#"${_p%%[![:space:]]*}"}"
    _p="${_p%"${_p##*[![:space:]]}"}"
    EUREKA_BY_POS+=("$_p")
  done
fi

eureka_csv_for_patch_root() {
  local root="$1"
  local rp i base joined
  base=$(basename "$root")
  rp=$(cd "$root" 2>/dev/null && pwd -P) || rp="$root"

  if [[ ${#EUREKA_BY_POS[@]} -eq 0 ]]; then
    printf '%s' "$base"
    return
  fi

  if [[ ${#PROJECT_ROOTS[@]} -eq 1 ]]; then
    joined=""
    for i in "${!EUREKA_BY_POS[@]}"; do
      [[ -n "${EUREKA_BY_POS[$i]}" ]] || continue
      joined="${joined:+$joined,}${EUREKA_BY_POS[$i]}"
    done
    if [[ -n "$joined" ]]; then
      printf '%s' "$joined"
    else
      printf '%s' "$base"
    fi
    return
  fi

  for i in "${!PROJECT_ROOTS[@]}"; do
    if [[ "${PROJECT_ROOTS[$i]}" == "$rp" ]]; then
      if [[ $i -lt ${#EUREKA_BY_POS[@]} ]] && [[ -n "${EUREKA_BY_POS[$i]}" ]]; then
        printf '%s' "${EUREKA_BY_POS[$i]}"
      else
        printf '%s' "$base"
      fi
      return
    fi
  done

  printf '%s' "$base"
}

echo "$(date '+%F %T') 工程路径（${#PROJECT_ROOTS[@]} 个）:" >&2
for _p in "${PROJECT_ROOTS[@]}"; do
  echo "  - $_p" >&2
done
if [[ ${#EUREKA_BY_POS[@]} -gt 0 ]]; then
  echo "$(date '+%F %T') Eureka 服务名与工程顺序对齐:" >&2
  if [[ ${#PROJECT_ROOTS[@]} -eq 1 ]]; then
    echo "  （单工程）候选: $(eureka_csv_for_patch_root "${PROJECT_ROOTS[0]}")" >&2
  else
    if [[ ${#EUREKA_BY_POS[@]} -ne ${#PROJECT_ROOTS[@]} ]]; then
      echo "$(date '+%F %T') 警告: 工程数(${#PROJECT_ROOTS[@]})与第三参项数(${#EUREKA_BY_POS[@]})不一致；按索引对齐，缺项用目录名" >&2
    fi
    for i in "${!PROJECT_ROOTS[@]}"; do
      _bn=$(basename "${PROJECT_ROOTS[$i]}")
      if [[ $i -lt ${#EUREKA_BY_POS[@]} ]] && [[ -n "${EUREKA_BY_POS[$i]}" ]]; then
        echo "  $_bn -> ${EUREKA_BY_POS[$i]}" >&2
      else
        echo "  $_bn -> （目录名 $_bn）" >&2
      fi
    done
  fi
fi

sync_once() {
  local tmp listf any=0 ws_path root svc_csv new_host
  listf=$(mktemp "${TMPDIR:-/tmp}/wslist.XXXXXX") || return 0
  : >"$listf"
  for _root in "${PROJECT_ROOTS[@]}"; do
    discover_patch_files_under "$_root" >>"$listf" 2>/dev/null || true
  done
  sort -u "$listf" -o "$listf" 2>/dev/null || true

  if [[ ! -s "$listf" ]]; then
    echo "$(date '+%F %T') 异常: 在给定工程下未发现 workspace.xml / runConfigurations / .run" >&2
    rm -f "$listf"
    return 0
  fi

  tmp=$(mktemp "${TMPDIR:-/tmp}/eureka.XXXXXX") || { rm -f "$listf"; return 0; }
  if ! curl -fsS -L -k \
    -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -o "$tmp" \
    "$EUREKA_URL"; then
    echo "$(date '+%F %T') 异常: 拉取 Eureka 失败: $EUREKA_URL" >&2
    rm -f "$tmp" "$listf"
    return 0
  fi

  while IFS= read -r ws_path || [[ -n "$ws_path" ]]; do
    [[ -z "$ws_path" ]] && continue
    [[ -f "$ws_path" ]] || continue
    if ! grep -qE 'type="Remote|factoryName="Remote"|factoryName="Remote JVM Debug"' "$ws_path" 2>/dev/null; then
      echo "$(date '+%F %T') 跳过（文件中无 Remote 运行配置）| $ws_path" >&2
      continue
    fi
    root=$(project_root_from_patch_file "$ws_path")
    if [[ -z "$root" ]]; then
      echo "$(date '+%F %T') 异常: 无法解析工程根: $ws_path" >&2
      continue
    fi
    svc_csv=$(eureka_csv_for_patch_root "$root")
    new_host=$(extract_ip_from_eureka_html "$tmp" "$ENV_NAME" "$svc_csv") || {
      echo "$(date '+%F %T') 跳过 Eureka 无匹配 env=$ENV_NAME services=[$svc_csv] | $ws_path" >&2
      continue
    }
    if ! patch_idea_xml_remote_blocks "$ws_path" "$new_host" "$PORT_VAL"; then
      echo "$(date '+%F %T') 异常: 写入失败 $ws_path" >&2
      continue
    fi
    echo "$(date '+%F %T') 已更新 [$(basename "$root")] HOST=$new_host PORT=$PORT_VAL ($svc_csv) $ws_path"
    any=1
  done <"$listf"

  rm -f "$tmp" "$listf"
  if [[ "$any" -eq 0 ]]; then
    echo "$(date '+%F %T') 本轮无文件被更新" >&2
  fi
  return 0
}

while true; do
  sync_once || true
  sleep "$INTERVAL"
done
