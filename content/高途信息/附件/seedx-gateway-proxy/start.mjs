#!/usr/bin/env node
/**
 * start.mjs —— 一键启动：同时拉起「网关代理」+「cc-switch 同步(--watch)」，任一挂了自动重启。
 *
 *   node start.mjs          # 前台常驻，Ctrl+C 一起退出
 *
 * 两个子进程：
 *   seedx-gateway-proxy.mjs            常驻代理（每小时刷 act. 授权 + 每次现读 credentials.json）
 *   sync-ccswitch.mjs --watch          常驻同步 cc-switch 的 seedx网关 + 拉取模型清单
 *
 * 行为：
 *   - 子进程输出带 [proxy] / [sync] 前缀转发到本进程 stdout/stderr；
 *   - 任一子进程非主动退出 → 3 秒后重启（退出过快时退避到最长 30 秒，避免死循环刷屏）；
 *   - Ctrl+C / SIGTERM → 一并停掉两个子进程后退出，不再重启。
 *   - 传 SEEDX_PROXY_PORT / SEEDX_CREDENTIALS / SEEDX_SYNC_INTERVAL_S 等，会原样透传给两个子进程。
 */

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const DIR = dirname(fileURLToPath(import.meta.url));
let shuttingDown = false;
const children = new Set();

function run(name, file, args) {
  const tag = `[${name}]`;
  const child = spawn(process.execPath, [join(DIR, file), ...args], {
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, NODE_NO_WARNINGS: "1" },
  });
  children.add(child);
  const startedAt = Date.now();
  let restarts = 0;

  for (const [stream, out] of [
    [child.stdout, process.stdout],
    [child.stderr, process.stderr],
  ]) {
    let buf = "";
    stream.on("data", (d) => {
      buf += d.toString();
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        out.write(`${tag} ${buf.slice(0, i)}\n`);
        buf = buf.slice(i + 1);
      }
    });
    stream.on("end", () => {
      if (buf) out.write(`${tag} ${buf}\n`);
    });
  }

  child.on("error", (e) => console.error(`${tag} 启动失败: ${e.message}`));
  child.on("exit", (code, sig) => {
    children.delete(child);
    if (shuttingDown) return;
    // 秒退（启动即失败，如未登录/端口占用）→ 退避；正常长跑后退出 → 固定 3s
    const quick = Date.now() - startedAt < 5000;
    restarts = quick ? restarts + 1 : 0;
    const delay = Math.min(quick ? 3000 * 2 ** Math.min(restarts, 3) : 3000, 30000);
    console.log(`${tag} 退出(code=${code ?? "-"}, signal=${sig ?? "-"})，${delay / 1000}s 后重启`);
    setTimeout(() => {
      if (!shuttingDown) run(name, file, args);
    }, delay);
  });
}

function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log("\n正在停止全部子进程…");
  for (const c of children) {
    try {
      c.kill("SIGTERM");
    } catch {
      /* ignore */
    }
  }
  setTimeout(() => process.exit(0), 800);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

console.log("seedx 一键启动：网关代理 + cc-switch 同步（Ctrl+C 退出）");
run("proxy", "seedx-gateway-proxy.mjs", []);
run("sync", "sync-ccswitch.mjs", ["--watch"]);
