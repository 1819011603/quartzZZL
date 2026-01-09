

#### reduce()

`reduce()` 是一种聚合操作，即将多个值经过特定的计算后获取到的单个值。像上面已经介绍了的 `count()` 、`max()` 、`min()` 等都是聚合操作。

1. **Optional reduce(BinaryOperator accumulator);**
		这个与其他两个相比，应该是最为常用的一个了。和上面几个聚合函数一样，该函数的返回值也是 Optional 对象，因为结果存在空指针的情况。
```java
    @Test
    public void test18(){
        int i = Stream.of(1, 2, 3, 4, 5, 6, 7, 18, 9, 10)
                .reduce((x, y) -> x + y)
                .get();
        System.out.println("i = " + i);		// i = 65
    }
```

2. **T reduce(T identity, BinaryOperator accumulator);**
	`T identity` 类似于是一个默认值，即当集合为空时，就返回这个默认值；当然如果集合不为空时，这个值也会参与到计算当中
```java
    @Test
    public void test19(){
        int i = Stream.of(1, 2, 3, 4, 5, 6, 7, 18, 9, 10)
                .reduce(0, (x, y) -> x + y);
        System.out.println("i = " + i);     // i = 65
    }

```

3. **U reduce(U identity, BiFunction<U, ? super T, U> accumulator, BinaryOperator combiner);**
	在方法中我们可以看到有两个泛型：**T** 和 **U** ，其中 **T** 是集合中的元素类型；而 **U** 是计算之后返回结果的类型，即 **U** 的类型是由第一个参数 identity 决定的

	**即该方法可以返回与集合中元素不同类型的值，而前两个方法则只能返回与集合中元素相同的值**
```java
    @Test
    public void test21(){
        List<Book> books = Stream.of(
                new Book("剑来", "烽火", 38, 100),
                new Book("斗破", "土豆", 34, 60),
                new Book("完美", "辰东", 37, 70)
        ).collect(Collectors.toList());

        List<Integer> reduce = books.stream().reduce(new ArrayList<Integer>(), new BiFunction<ArrayList<Integer>, Book, ArrayList<Integer>>() {
            @Override
            public ArrayList<Integer> apply(ArrayList<Integer> integers, Book book) {
                integers.add(book.getPrice());
                System.out.println("list = " + integers);
                System.out.println("bookPrice = " + book.getPrice());
                return integers;
            }
        }, new BinaryOperator<ArrayList<Integer>>() {
            @Override
            public ArrayList<Integer> apply(ArrayList<Integer> integers1, ArrayList<Integer> integers2) {
                integers1.addAll(integers2);
                System.out.println("integers1 = " + integers1);
                System.out.println("integers2 = " + integers2);
                return integers1;
            }
        });

        System.out.println("finalList = " + reduce);
    }
```
	那么为什么 `BinaryOperator` 没有执行呢？这是因为 Stream 是支持并发操作的，为了避免竞争，对于 reduce 这个方法，线程都会有独立的 result，**即 `BinaryOperator combiner` 的作用在于汇总所有线程的计算结果，从而得到一个最终的 result**

对于带有combiner的reduce操作，等价的代码段为：
U result = identity;
for (T element : this stream)
    result = accumulator.apply(result, element)
return result;
<mark class="hltr-yellow">其中，在并行流的情况下，combiner会被用于合并不同部分的结果。但是在单线程的情况下，combiner并不会被调用。</mark>

在Java中，对于使用Stream的reduce操作，如果你确定只会在单线程环境下进行操作，那么可以不提供combiner。在这种情况下，使用没有combiner的reduce操作是合适的。

由于在单线程环境下不需要并行执行和结果合并，因此省略combiner是可以接受的。然而，如果你的代码可能会在多线程或并行环境下执行，为了保证代码的健壮性，建议还是提供一个合适的combiner。

在并行流的情况下，combiner函数将会被用来合并不同部分的结果。因此，在编写通用的、可复用的代码时，最好还是考虑到多线程和并行执行的情况，以确保代码的鲁棒性。



####  allMatch() & anyMatch() & noneMatch()
- **allMatch()** 当流中的元素都按指定的规则匹配上，才会返回 true (即全部对才对)
- **anyMatch()** 当流中有任意元素满足指定的规则时，返回 true (即对一个就对了)
- **noneMatch()** 当流中所有元素都没有与指定的规则匹配上，才会返回 true (即全部错了才是对的)


#### flatMap()

**扁平化映射**，其实本质上与 map() 是一样的，都是对流中的元素进行一定的处理然后再返回出来

`flatMap`和`map`都是用于对Stream中的元素进行映射操作的方法，但它们之间有一些关键的区别：

- **map**：对Stream中的每个元素应用一个函数，并将返回的结果构成一个新的Stream。换句话说，map操作会对每个元素执行同一个函数，并将结果包装成一个新的Stream。
    
- **flatMap**：对Stream中的每个元素应用一个函数，将函数的返回值合并成一个新的Stream。与map不同，flatMap操作会将每个元素映射为一个流，然后将这些流扁平化（即合并）为一个单一的流。
    

换句话说，`map`操作是一对一的映射，而`flatMap`操作可以实现一对多的映射。通常情况下，当你需要对每个元素执行的函数返回一个流时，就会使用`flatMap`来展开这些流，而不是简单地使用`map`。

```java
/*
当你有一个嵌套的数据结构，例如列表的列表时，你可能希望将其扁平化为一个单一的列表。这就是`flatMap`方法发挥作用的场景之一。

假设我们有一个列表，其中包含多个单词的列表，而我们想要将所有这些单词合并到一个单独的列表中。在这种情况下，我们可以使用`flatMap`来实现这个需求。
*/
List<List<String>> nestedWords = Arrays.asList(
    Arrays.asList("Hello", "World"),
    Arrays.asList("Welcome", "to", "Java")
);

List<String> flattenedList = nestedWords.stream()
                                        .flatMap(List::stream)  // 使用flatMap将嵌套列表展开
                                        .collect(Collectors.toList());

System.out.println(flattenedList);  // 输出：[Hello, World, Welcome, to, Java]

/*
在这个例子中，我们使用`flatMap`操作将嵌套的列表展开为一个单一的列表。这意味着每个内部列表都会被展开为其包含的所有元素，并最终形成一个单一的列表。
*/

```


####  collect

这段代码使用了`collect`方法，它的作用是将Stream中的元素收集到一个结果容器中。在这里，`stringStream`是一个Stream对象，我们对它调用`collect`方法来进行元素的收集。

具体来说，`collect(ArrayList::new, ArrayList::add, ArrayList::addAll)`中的三个参数分别代表了：

1. Supplier：`ArrayList::new`表示创建一个空的ArrayList作为最终的结果容器。
2. Accumulator：`ArrayList::add`表示如何将Stream中的元素一个一个地添加到结果容器中。
3. Combiner：`ArrayList::addAll`表示如何将并行执行时不同部分的结果合并起来（在单线程情况下一般不会被调用）。

因此，整个`collect`方法的作用是将Stream中的元素收集到一个ArrayList中。首先创建一个新的ArrayList作为结果容器，然后逐个将Stream中的元素添加到这个ArrayList中，最后如果有并行操作需要合并不同部分的结果，就会调用`ArrayList::addAll`来进行合并。


```java
public interface Collector<T, A, R> {
	
	/**
	 *该方法将返回一个类型为A的Supplier，该方法会创建一个元素容器，该容器在accumulator()方法中将会被用到，主要用于收集累加器计算的数据结果
	 */
	Supplier<A> supplier();
	/**
	 *累加器方法是比较关键的方法，该方法会部分（在并行流中）运算或者全部计算（在串行流中）Stream流经的元素，并且将其存入supplier方法构造出来的容器中。
	 */
	BiConsumer<A, T> accumulator();
	/**
	 *该方法主要用于在并行流中进行结果的整合操作，在并行流中，每一个子线程都在执行部分数据的累加器方法，最后的结果该如何自处呢？当然是需要将其进行整合（分而治之，Fork Join的思想），那么该方法的泛型参数与supplier（）方法一致也就很容易理解了。
	 */
	BinaryOperator<A> combiner();
	/**
	 * 当所有的计算完成之后，该方法将被用于做进一步的transformation操作，比如将int类型转换为long类型，同时该方法也是整个Collector接口在Stream collect操作中最后一个被调用的方法。
	 */
	Function<A, R> finisher();
	/**
	 * 该方法主要用于定义Collector的特征值，包含了CONCURRENT、UNORDERED和IDENTITY_FINISH三个类型
	 */
	Set<Characteristics> characteristics();
}

```


  Collector接口方法在串行流中的执行过程，如下：

![[../../壁纸/附件/Pasted image 20240724170641.png]]  如上图所示，在串行流中，其中combiner方法将不会被使用到，因为不存在子线程子任务数据的合并动作，所有的操作将直接由单线程来完成。


![[../../壁纸/附件/Pasted image 20240724170850.png]]

如上图所示，和串行流相比，在这里当分支流程执行完成后，需要调用combiner方法进行结果的合并，然后再调用finisher方法返回结果。


### mapping
Collectors.mapping是不是先map后collect

您的理解非常准确。Collectors.mapping 确实可以被看作是先 map 然后 collect 的组合操作。让我详细解释一下：

1. 概念上的等价性：  
    Collectors.mapping(mapper, downstream) 在概念上等同于先进行 map 操作，然后再进行 collect 操作。
    
2. 实现方式：  
    虽然在概念上类似，但 Collectors.mapping 是作为一个单一的收集器实现的，而不是实际的两步操作。这种实现方式通常更高效。
    
3. 示例比较：
    
     
    
    使用 Collectors.mapping:
    
    ```java
    List<String> result = list.stream()
        .collect(Collectors.mapping(
            String::toUpperCase, 
            Collectors.toList()
        ));
    ```
    
    等价的 map + collect 操作：
    
    ```java
    List<String> result = list.stream()
        .map(String::toUpperCase)
        .collect(Collectors.toList());
    ```

1. 优势：
    
    - 性能：Collectors.mapping 可能比分离的 map 和 collect 操作更高效，因为它避免了创建中间流。
    - 灵活性：允许在更复杂的收集操作中嵌入映射逻辑。
    - 组合性：可以轻松地与其他收集器组合使用。
2. 使用场景：
    
    - 当需要在收集过程中转换元素，并且这个转换是收集操作的一部分时。
    - 在复杂的分组或多级收集操作中特别有用。
1. 例子：
    
    ```java
    Map<Department, List<String>> employeeNamesByDept = employees.stream()
        .collect(Collectors.groupingBy(
            Employee::getDepartment,
            Collectors.mapping(
                Employee::getName,
                Collectors.toList()
            )
        ));
    ```
    
    这里，mapping 被嵌入到 groupingBy 操作中。
总之，您的理解是正确的。Collectors.mapping 确实提供了一种优雅的方式来组合映射和收集操作，使得代码更加简洁和高效。它在概念上等同于先 map 后 collect，但在实现上可能更优化。