
https://blog.csdn.net/monkey_win/article/details/103303174  包含有空格的命令执行会报错。

``` markdown
Java的`ProcessBuilder`并不是不支持空格，而是在使用`ProcessBuilder`时需要格外小心处理参数。当你将命令和参数作为一个字符串列表传递给`ProcessBuilder`时，每个元素都应该独立表示命令或参数，并且不要手动添加额外的引号。

例如，如果你想运行`/bin/echo`命令并传递一个带有空格的参数"hello world"，你应该这样做：

java复制代码

`ProcessBuilder processBuilder = new ProcessBuilder("/bin/echo", "hello world");`

这样会确保`ProcessBuilder`正确解析参数，并且可以正确地执行带有空格的命仮。

如果你将命令和参数作为单个字符串传递给`ProcessBuilder`，那么空格可能会导致参数被错误地分割。因此，最佳实践是将每个命令和参数分别作为`ProcessBuilder`构造函数的参数。
```