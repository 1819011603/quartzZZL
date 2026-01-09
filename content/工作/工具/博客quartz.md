


### 拉下来

https://github.com/1819011603/quartzZZL


content 目录下就是网页的内容  

需要手动创建 index.md


 vim content/index.md



```

---                                                                                                                                                                                     

title: 首页                                                                                                                                                                             

---                                                                                                                                                                                     

# 欢迎来到我的笔记                                                                                                                                                                      

这是我的 Quartz 知识库首页。                                                                                                                                                            

## 目录                                                                                                                                                                                 

- [[生活]]                                                                                                                                                                              

- [[工作]]
```


### 用 nvm 安装 Node 22
1. curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
2. source ~/.zshrc
3. nvm --version
4. nvm install 22
5. nvm use 22



### 本地构建

```
npx quartz build --serve


```

| 步骤  | 功能                          |
| --- | --------------------------- |
| 1   | 找 >25MB 文件，去重添加到 .gitignore |
| 2   | 检查 ./ 开头的行，删除不存在的文件         |

```

find ./content -type f -size +25M -not -path "./.git/*" | while read file; do
  grep -qxF "$file" .gitignore || { echo "$file" >> .gitignore; echo "✅ 已添加: $file"; }
done && while IFS= read -r line; do
  if [[ "$line" == ./* ]]; then
    [ -e "$line" ] && echo "$line" || echo "🗑️  已删除: $line" >&2
  else
    echo "$line"
  fi
done < .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore

```

	