

如果是 I/O 密集型，且 I/O 请求比较耗时的话，使用协程。  
如果是 I/O 密集型，且 I/O 请求比较快的话，使用多线程。  
如果是 计算 密集型，考虑可以使用多核 CPU，使用多进程。


https://zhuanlan.zhihu.com/p/56352731


### **multiprocessing开销比较大，原因就在于：主进程和子进程之间通信，必须进行序列化和反序列化的操作**

```
ProcessPoolExecutor类会利用multiprocessing模块所提供的底层机制，以例2作为例子描述下


多进程执行流程：

（1）把urllist列表中的每一项输入数据都传给map

（2）用pickle模块对数据进行序列化，将其变成二进制形式

（3）通过本地套接字，将序列化之后的数据从解释器所在的进程发送到子解释器所在的进程

（4）在子进程中，用pickle对二进制数据进行反序列化，将其还原成python对象

（5）引入包含download函数的python模块

（6）各个子进程并行的对各自的输入数据进行计算

（7）对运行的结果进行序列化操作，将其转变成字节

（8）将这些字节通过socket复制到主进程之中

（9）主进程对这些字节执行反序列化操作，将其还原成python对象

（10）最后把每个子进程所求出的计算结果合并到一份列表之中，并返回给调用者。
```


# Python全局解释器锁GIL（Global Interpreter Lock）

简单来说，Python全局解释器锁([Global Interpreter Lock](https://link.zhihu.com/?target=https%3A//wiki.python.org/moin/GlobalInterpreterLock))或[GIL](https://link.zhihu.com/?target=https%3A//wiki.python.org/moin/GlobalInterpreterLock)是一个互斥锁，它只允许一个线程来控制Python解释器。

这意味着在任何时间点只有一个线程可以处于执行状态。执行单线程程序的开发人员感受不到GIL的影响，但它可能是CPU限制型和多线程代码中的性能瓶颈。

由于即使在具有多个CPU核心的多线程架构中，GIL一次只允许一个线程执行，因此GIL已经成为Python“臭名昭着”的特性。


**多进程与多线程：**最流行的方法是使用多方法，使用多个进程而不是线程。每个Python进程都有自己的Python解释器和内存空间，因此GIL不会成为问题。Python有一个[multiprocessing](https://link.zhihu.com/?target=https%3A//docs.python.org/2/library/multiprocessing.html)模块，可以让我们像这样轻松地创建流程：


```python
from multiprocessing import Pool
import time
COUNT = 50000000
def countdown(n):
    while n>0:
        n -= 1
if __name__ == '__main__':
    pool = Pool(processes=2)
    start = time.time()
    r1 = pool.apply_async(countdown, [COUNT//2])
    r2 = pool.apply_async(countdown, [COUNT//2])
    pool.close()
    pool.join()
    end = time.time()
    print('Time taken in seconds -', end - start)
```

Python中的多线程由于Global Interpreter Lock （GIL）的存在，同一时间只允许一个线程执行Python字节码。即便在多核处理器上，Python的多线程也无法利用多核的优势。因此，对于CPU密集型任务，多线程并不能提高运行速度，甚至因为线程切换的开销而导致运行速度下降。  
  
然而，对于IO密集型任务，如文件操作、网络访问等，由于这类任务的主要时间花费在等待IO操作，而不是CPU计算，因此多线程能有效提升程序的运行效率，实现任务的并行处理。  
  
如果你在Python中执行的任务大部分为CPU密集型任务，可能会发现100个线程和1个线程花费的时间相差无几，这正是由于GIL的影响。如果想充分利用多核进行并行计算，可以考虑使用`multiprocessing`库进行多进程编程，或者使用其他支持真正意义上多线程的语言进行编程。


#  所有代码必须代码在if __name__ == '__main__':中，全局变量可声明在外面

```python
if __name__ == '__main__':
	from multiprocessing import Pool  
	with Pool(processes=30) as pool:  
	results = pool.map(find, contents)  
	for result in results:  
	if result is not None:  
	res.append(result)
```

