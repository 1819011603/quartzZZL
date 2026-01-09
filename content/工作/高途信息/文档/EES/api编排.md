

无sudo权限安装nodejs


```

# 1️⃣ 下载 nvm 安装脚本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# 2️⃣ 刷新环境变量
source ~/.bashrc   # 或者 ~/.bash_profile，看你系统用哪个

# 3️⃣ 验证 nvm 是否安装成功
nvm --version


# 安装适配旧系统的 Node 版本（比如 v10 或 v12）
nvm install 12
nvm use 12


# 4️⃣ 查看可安装的 Node.js 版本
# nvm ls-remote

# 5️⃣ 安装 Node.js（例如最新的长期支持版）
nvm install --lts

# 6️⃣ 验证 Node.js 安装成功
node -v
npm -v
```


#### **方案 2：使用编译好的“兼容包”（Node for CentOS 7）**

Node 官方在部分发行版上提供了针对老 glibc 的构建：

```
curl -O https://unofficial-builds.nodejs.org/download/release/v18.17.1/node-v18.17.1-linux-x64-glibc-217.tar.gz
tar -xzf node-v18.17.1-linux-x64-glibc-217.tar.gz -C ~/
echo 'export PATH=$HOME/node-v18.17.1-linux-x64-glibc-217/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

node -v
npm -v

```

> 🔹 这个包是 **专门为 GLIBC 2.17（CentOS 7）** 编译的兼容版本。

好的！我来为您整理前端和后端的启动命令。

[1 tool called]

## 📚 前端和后端启动命令总结

---

```
export MYSQL_ENABLED=true
export MYSQL_HOST=gaotu-polar-test02.rwlb.rds.aliyuncs.com
export MYSQL_USER=gaotu_test_rw
export MYSQL_PASSWORD=gaotu@test2020
export MYSQL_DATABASE=ees_data
```
## 🔧 后端启动

### 开发模式
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main

cd test-api/backend/
conda activate R
nohup python -m  app.main > output.log 2>&1 &
```

### 生产模式
```bash
cd backend
source venv/bin/activate
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🎨 前端启动

#### **方案3：彻底清理 node_modules 并重装**

最干净的方式（适合多文件冲突时）：

```
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

```

### 开发模式
```bash
cd frontend
npm install 或者 npm install --force
npm run dev


cd test-api/frontend/
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run dev -- --host 0.0.0.0


# 这个不行 还是会被关闭 
nohup npm run dev -- --host 0.0.0.0 > front.log  2>&1 &

pm2 start npm --name "my-frontend-app" -- run dev -- --host 0.0.0.0




```

### 生产模式

### ## 原因分析 & 思路

1. **SIGHUP 信号**: 当您关闭一个终端或断开 SSH 连接时，Shell 会向该会话启动的所有进程发送一个 `SIGHUP` (Hangup) 信号，这个信号的默认行为是终止进程。
2. **`nohup` 的作用**: `nohup` 命令的作用是拦截 `SIGHUP` 信号，使其包裹的命令（在这里是 `npm`）不会因为这个信号而退出。同时，它会将标准输出和标准错误重定向到 `nohup.out` 文件或您指定的文件（如 `front.log`）。
3. **问题的关键 - 进程树**: `npm run dev` 命令本身并不是最终运行的开发服务器。`npm` 进程会读取 `package.json` 文件，然后启动一个新的子进程来执行 `dev` 脚本中定义的命令（例如 `vite`, `webpack-dev-server` 或 `next dev`）。这就形成了一个进程树：`Shell -> nohup -> npm -> node (dev server)`。
    - `nohup` 保护了 `npm` 进程。
    - 但是，当 `npm` 进程退出或被其他信号杀死时，它可能会（也常常会）把它启动的子进程也一并终止。
    - 某些开发服务器本身可能设计为交互式的，没有正确处理作为后台守护进程运行的情况，导致其在父进程 `npm` 失去终端后也随之退出。


```
# 1. 全局安装 PM2 (如果尚未安装)
npm install pm2 -g

# 2. 进入您的项目目录
cd /path/to/your/frontend

# 3. 使用 PM2 启动您的应用
# --name "my-frontend-app" : 给你的应用起一个易于识别的名字
# -- : 这是关键，它告诉 pm2 后面的所有参数都应该传递给 npm run dev 脚本
#    而不是 pm2 命令本身。
pm2 start npm --name "my-frontend-app" -- run dev -- --host 0.0.0.0

# --- PM2 常用管理命令 ---

# 查看所有正在运行的应用的状态
pm2 list

# 查看指定应用的实时日志
pm2 logs my-frontend-app

# 停止应用
pm2 stop my-frontend-app

# 重启应用
pm2 restart my-frontend-app

# 删除应用
pm2 delete my-frontend-app

```

```bash
cd frontend
npm install
npm run build
npm run preview
```

---

## 🚀 一键启动（推荐）

```bash
# 使用启动脚本
chmod +x start.sh
./start.sh
```

---

## 🐳 Docker部署

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 🎉 项目完成

**API自动化编排平台 v1.3.0**

- **功能完成度**: 100%
- **文件数量**: 80+
- **代码行数**: 16000+
- **文档数量**: 18个

**访问**：http://localhost:5173

**所有功能已就绪，祝使用愉快！** 🚀