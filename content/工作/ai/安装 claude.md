


# 强制修改 npm 配置

配置没生效，我们直接手动改配置文件。

---

## 按顺序执行

### 第一步：创建目录和配置文件

```bash
# 创建目录
mkdir -p ~/.npm-global

# 直接写入配置文件（覆盖）
echo "prefix=${HOME}/.npm-global" > ~/.npmrc

# 验证配置文件内容
cat ~/.npmrc
```

### 第二步：验证配置生效

```bash
npm config get prefix
```

现在应该显示：`/Users/gaotu/.npm-global`

### 第三步：配置 PATH 并安装

```bash
# 添加到 PATH
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 安装（不用 sudo）
npm install -g @anthropic-ai/claude-code

# 验证
claude --version
```

---

## 一键执行

```bash
mkdir -p ~/.npm-global && \
echo "prefix=${HOME}/.npm-global" > ~/.npmrc && \
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc && \
source ~/.zshrc && \
npm config get prefix && \
npm install -g @anthropic-ai/claude-code && \
claude --version
```

---

如果还是不行，检查是否有系统级配置覆盖：

```bash
# 查看所有 npm 配置来源
npm config list

# 查看是否有系统级配置
cat /usr/local/etc/npmrc 2>/dev/null
```



配置

https://claude-code-router.baijia.com

sk--A_poOtprtGJA00Z2V9G8A