
https://tech.baijia.com/

![[../../壁纸/附件/Pasted image 20260806144621.png]]

```

curl -sf http://localhost:3000/internal/git-credential | grep '^password=' | cut -d= -f2 | base64





git clone http://oauth:VGNdatQ3oghxWHjp7P1-@git.baijia.com/gaotu/user.git


⚠️ 这条会把 token 写进 .git/config，用完记得 git remote set-url origin http://git.baijia.com/gaotu/user.git 清掉。

```