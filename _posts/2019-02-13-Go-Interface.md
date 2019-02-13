---
layout: post
title:  "Golang  Interface"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 接口介绍
如果说gorountine和channel是支撑起Go语言的并发模型的基石，让Go语言在如今集群化与多核化的时代成为一道亮丽的风景，那么接口是Go语言整个类型系列的基石，让Go语言在基础编程哲学的探索上达到前所未有的高度。Go语言在编程哲学上是变革派，而不是改良派。这不是因为Go语言有gorountine和channel，而更重要的是因为Go语言的类型系统，更是因为Go语言的接口。Go语言的编程哲学因为有接口而趋于完美。C++,Java 使用"侵入式"接口，主要表现在实现类需要明确声明自己实现了某个接口。这种强制性的接口继承方式是面向对象编程思想发展过程中一个遭受相当多质疑的特性。Go语言采用的是“非侵入式接口",Go语言的接口有其独到之处：只要类型T的公开方法完全满足接口I的要求，就可以把类型T的对象用在需要接口I的地方，所谓类型T的公开方法完全满足接口I的要求，也即是类型T实现了接口I所规定的一组成员。这种做法的学名叫做Structural Typing，有人也把它看作是一种静态的Duck Typing。
    

要这个值实现了接口的方法。
```go
type Reader interface { 
 Read(p []byte) (n int, err os.Error) 
} 
  
// Writer 是包裹了基础 Write 方法的接口。 
type Writer interface { 
 Write(p []byte) (n int, err os.Error) 
} 
  
var r io.Reader 
r = os.Stdin 
r = bufio.NewReader(r) 
r = new(bytes.Buffer)
```
有一个事情是一定要明确的，不论 r 保存了什么值，r 的类型总是 io.Reader ,Go 是静态类型，而 r 的静态类型是 io.Reader。接口类型的一个极端重要的例子是空接口interface{},它表示空的方法集合，由于任何值都有零个或者多个方法，所以任何值都可以满足它。也有人说 Go 的接口是动态类型的，不过这是一种误解。 它们是静态类型的：接口类型的变量总是有着相同的静态类型，这个值总是满足空接口，只是存储在接口变量中的值运行时可能被改变。对于所有这些都必须严谨的对待，因为反射和接口密切相关。

### 接口类型内存布局
在类型中有一个重要的类别就是接口类型，表达了固定的一个方法集合。一个接口变量可以存储任意实际值（非接口），只要这个值实现了接口的方法。interface在内存上实际由两个成员组成，如下图，tab指向虚表，data则指向实际引用的数据。虚表描绘了实际的类型信息及该接口所需要的方法集。
```go
type Stringer interface { 
 String() string 
} 
  
type Binary uint64 
  
func (i Binary) String() string { 
 return strconv.FormatUint(i.Get(), 2) 
} 
  
func (i Binary) Get() uint64 { 
 return uint64(i) 
} 
  
func main() { 
 var b Binary = 32 
 s := Stringer(b) 
 fmt.Print(s.String()) 
}
```
![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/go_interface_memory_layout.png)


观察itable的结构，首先是描述type信息的一些元数据，然后是满足Stringger接口的函数指针列表（注意，这里不是实际类型Binary的函数指针集哦）。因此我们如果通过接口进行函数调用，实际的操作其实就是s.tab->fun[0](s.data) 。是不是和C++的虚表很像？但是他们有本质的区别。先看C++，它为每个类创建了一个方法集即虚表，当子类重写父类的虚函数时，就将表中的相应函数指针改为子类自己实现的函数，如果没有则指向父类的实现，当面临多继承时，C++对象结构里就会存在多个虚表指针，每个虚表指针指向该方法集的不同部分。我们再来看golang的实现方式，同C++一样，golang也为每种类型创建了一个方法集，不同的是接口的虚表是在运行时专门生成的，而c++的虚表是在编译时生成的（但是c++虚函数表表现出的多态是在运行时决定的).例如，当例子中当首次遇见s := Stringer(b)这样的语句时，golang会生成Stringer接口对应于Binary类型的虚表，并将其缓存。那么为什么go不采用c++的方式来实现呢？这根c++和golang的对象内存布局是有关系的。
首先c++的动态多态是以继承为基础的，在对象构造初始化的时首先会初始化父类，其次是子类，也就是说一个对象的内存布局是虚表，父类部分，子类部分（编译器不同可能会有差异），当一个父类指针指向子类时，会发生内存的截断，截断子类部分(内存地址偏移)，但是此时子类的虚表中的函数指针实际上还是指向了自己的实现，所以此时的指针才会调用到子类的虚函数，如果不是虚函数，因为内存已经截断没有子类的非虚函数信息了，所以只能调用父类的了，这种继承关系让c++的虚表的初始化非常清晰，在一个对象初始化时先调用父类的构造此时虚表跟父类是一样的，接下来初始化子类，此时编译器就会去识别子类有没有覆盖父类的虚函数，如果有则虚表中相应的函数指针改成自己的虚函数实现指针。
那么go有什么不同呢，首先我们很清楚go是没有严格意义上的继承的，go的接口不存在继承关系，只要实现了接口定义的方法都可以成为接口类型，这给go的虚表初始化带来很大的麻烦，到底有多少类型实现了这个接口，一个类型到底实现了多少接口这让编译器很confused。举个例子，某个类型有m个方法，某接口有n个方法，则很容易知道这种判定的时间复杂度为O(mXn)，不过可以使用预先排序的方式进行优化，实际的时间复杂度为O(m+n)这样看来其实还行那为什么要在运行时生成虚表呢，这不是会拖慢程序的运行速度吗，注意我们这里是某个类型，某个接口，是1对1的关系，如果有n个类型，n个接口呢，编译器难道要把之间所有的关系都理清吗？退一步说就算编译器任劳任怨把这事干了，可是你在写过程中你本来就不想实现那个接口，而你无意中给这个类型实现的方法中包含了某些接口的方法，你根本不需要这个接口(况且go的接口机制会导致很多这种无意义的接口实现)，你欺负编译器就行了，这也太欺负人了吧。如果我们放到运行时呢，我们只要在需要接口的去分析一下类型是否实现了接口的所有方法就行了很简单的一件事。

### 空接口
接口类型的一个极端重要的例子是空接口：interface{} ,它表示空的方法集合，由于任何值都有零个或者多个方法，所以任何值都可以满足它。

> 注意，*[]T不能直接赋值给[]interface{}*
```go
//t := []int{1, 2, 3, 4} wrong 
//var s []interface{} = t 
t := []int{1, 2, 3, 4} //right 
s := make([]interface{}, len(t)) 
for i, v := range t { 
 s[i] = v 
}
```
```go
str, ok := value.(string) 
if ok { 
 fmt.Printf("string value is: %q\n", str) 
} else { 
 fmt.Printf("value is not a string\n") 
}
```
在Go语言中，我们可以使用type switch语句查询接口变量的真实数据类型，语法如下：

```go
type Stringer interface { 
  String() string 
} 
  
var value interface{} // Value provided by caller. 
switch str := value.(type) { 
case string: 
  return str //type of str is string 
case Stringer: //type of str is Stringer 
  return str.String() 
}
```
也可以使用“comma, ok”的习惯用法来安全地测试值是否为一个字符串：
```go
str, ok := value.(string) 
if ok { 
  fmt.Printf("string value is: %q\n", str) 
} else { 
  fmt.Printf("value is not a string\n") 
}
```
### 接口赋值
```go
package main 
  
import ( 
"fmt" 
) 
  
type LesssAdder interface { 
  Less(b Integer) bool 
  Add(b Integer) 
} 
  
type Integer int 
  
func (a Integer) Less(b Integer) bool { 
  return a < b 
} 
  
func (a *Integer) Add(b Integer) { 
  *a += b 
} 
  
func main() { 
  
  var a Integer = 1 
  var b LesssAdder = &a 
  fmt.Println(b) 
  
  //var c LesssAdder = a 
  //Error:Integer does not implement LesssAdder  
  //(Add method has pointer receiver) 
}
```
go语言可以根据下面的函数:

```go
func (a Integer) Less(b Integer) bool
```
自动生成一个新的Less()方法
```go
func (a *Integer) Less(b Integer) bool
```
这样，类型*Integer就既存在Less()方法，也存在Add()方法，满足LessAdder接口。 而根据
```go
func (a *Integer) Add(b Integer)
```
这个函数无法生成以下成员方法：
```go
func(a Integer) Add(b Integer) { 
  （&a).Add(b) 
}
```
因为(&a).Add()改变的只是函数参数a,对外部实际要操作的对象并无影响(值传递)，这不符合用户的预期。所以Go语言不会自动为其生成该函数。因此类型Integer只存在Less()方法，缺少Add()方法，不满足LessAddr接口。（可以这样去理解：指针类型的对象函数是可读可写的，非指针类型的对象函数是只读的）将一个接口赋值给另外一个接口 在Go语言中，只要两个接口拥有相同的方法列表(次序不同不要紧),那么它们就等同的，可以相互赋值。 如果A接口的方法列表时接口B的方法列表的子集，那么接口B可以赋值给接口A，但是反过来是不行的，无法通过编译。

### 接口查询
接口查询是否成功，要在运行期才能够确定。他不像接口的赋值，编译器只需要通过静态类型检查即可判断赋值是否可行。
```go
var file1 Writer = ...
if file5,ok := file1.(two.IStream);ok {
...
}
```
这个if语句检查file1接口指向的对象实例是否实现了two.IStream接口，如果实现了，则执行特定的代码。

在Go语言中，你可以询问它指向的对象是否是某个类型，比如，
```go
var file1 Writer = File{}
if file6,ok := file1.(*File);ok {
...
}
```
这个if语句判断file1接口指向的对象实例是否是*File类型，如果是则执行特定的代码。
> Note, 判断类型一定使用`*`，否则，函数将认为File为一个接口，判断file1是否是File接口

```go
slice := make([]int, 0)
slice = append(slice, 1, 2, 3)
 
var I interface{} = slice
 
 
if res, ok := I.([]int)；ok {
  fmt.Println(res) //[1 2 3]
}
```
这个if语句判断接口I所指向的对象是否是[]int类型，如果是的话输出切片中的元素。

```go
func Sort(array interface{}, traveser Traveser) error {
 
  if array == nil {
    return errors.New("nil pointer")
  }
  var length int //数组的长度
  switch array.(type) {
  case []int:
    length = len(array.([]int))
  case []string:
    length = len(array.([]string))
  case []float32:
    length = len(array.([]float32))
 
  default:
    return errors.New("error type")
  }
 
  if length == 0 {
    return errors.New("len is zero.")
  }
 
  traveser(array)
 
  return nil
}
```

通过使用.(type)方法可以利用switch来判断接口存储的类型。

小结: 查询接口所指向的对象是否为某个类型的这种用法可以认为是接口查询的一个特例。接口是对一组类型的公共特性的抽象，所以查询接口与查询具体类型区别好比是下面这两句问话的区别:

你是医生么？
是。
你是莫莫莫
是
第一句问话查询的是一个群体，是查询接口；而第二个问句已经到了具体的个体，是查询具体类型。

除此之外利用反射也可以进行类型查询，会在反射中做详细介绍。

总结

以上就是这篇文章的全部内容了，希望本文的内容对大家的学习或者工作具有一定的参考学习价值，如果有疑问大家可以留言交流，谢谢大家对脚本之家的支持。
