---
layout: post
title:  "Golang Josn Parser"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 处理Json

上干货
1. 一个结构体正常序列化
```c
package main
import (
    "encoding/json"
    "fmt"
)

// Product 商品信息
type Product struct {
    Name      string
    ProductID int64
    Number    int
    Price     float64
    IsOnSale  bool
}

func main() {
    p := &Product{}
    p.Name = "Xiao mi 6"
    p.IsOnSale = true
    p.Number = 10000
    p.Price = 2499.00
    p.ProductID = 1
    data, _ := json.Marshal(p)
    fmt.Println(string(data))
}


//结果
{"Name":"Xiao mi 6","ProductID":1,"Number":10000,"Price":2499,"IsOnSale":true}
```

2. 给结构体的每个字段打上一个标签(tag)，标签冒号前是类型，后面是标签名
```c
// Product 商品信息
type Product struct {
    Name      string `json:"name"`
    ProductID int64 `json:"-"`
    Number    int `json:"number"`
    Price     float64 `json:"price"`
    IsOnSale  bool `json:"is_on_sale,string"`
}
// 序列化过后，可以看见
{"name":"Xiao mi 6","number":10000,"price":2499,"is_on_sale":"false"}

```

3. omitempty，tag里面加上omitempy，可以在序列化的时候忽略0值或者空值
```c
package main

import (
"encoding/json"
"fmt"
)

// Product _
type Product struct {
Name string json:"name"
ProductID int64 json:"product_id,omitempty"
Number int json:"number"
Price float64 json:"price"
IsOnSale bool json:"is_on_sale,omitempty"
}

func main() {
p := &Product{}
p.Name = "Xiao mi 6"
p.IsOnSale = false
p.Number = 10000
p.Price = 2499.00
p.ProductID = 0

 data, _ := json.Marshal(p)
 fmt.Println(string(data))
}
// 结果
{"name":"Xiao mi 6","number":10000,"price":2499}
```

4. type，有些时候，我们在序列化或者反序列化的时候，可能结构体类型和需要的类型不一致，这个时候可以指定,支持string,number和boolean

```c
package main

import (
"encoding/json"
"fmt"
)

// Product _
type Product struct {
Name string json:"name"
ProductID int64 json:"product_id,string"
Number int json:"number,string"
Price float64 json:"price,string"
IsOnSale bool json:"is_on_sale,string"
}

func main() {

 var data = `{"name":"Xiao mi 6","product_id":"10","number":"10000","price":"2499","is_on_sale":"true"}`
 p := &Product{}
 err := json.Unmarshal([]byte(data), p)
 fmt.Println(err)
 fmt.Printf("%#v", p)
}

// 结果
main.Product{Name:"Xiao mi 6", ProductID:10, Number:10000, Price:2499, IsOnSale:true}
```
