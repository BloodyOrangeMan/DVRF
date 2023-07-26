### write up

* 利用导航栏`firewall port-forward` 的 `name` 字段构造 xss,查看源码,可以发现存在一个showMessage.js文件，因此推出需要触发这个showMessage函数，注意过滤尖括号，输入`<svg onload=showMessage()//`可以绕过。

![](img/xss1.png)

![](img/xss2.png)

* 成功后将拿到下一题提示

![](img/success.png)

