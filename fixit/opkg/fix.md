## 修改方法

该[commit](https://git.openwrt.org/?p=project/opkg-lede.git;a=commitdiff;h=c09fe2098718807ddbca13ee36e3e38801822946;hp=80d161eb5b95ceb51db989196405eaa00950e03b)修正了在解析校验和时跳过前导空白而导致能随意伪造软件包的问题，

对`checksum_hex2bin`函数进行了修改，调整了变量`s`的初始化位置，将其从函数开始部分移动到了循环开始部分。

```c
@@ -235,7 +235,7 @@ char *checksum_hex2bin(const char *src, size_t *len)
 {
        size_t slen;
        unsigned char *p;
-       const unsigned char *s = (unsigned char *)src;
+       const unsigned char *s;
        static unsigned char buf[32];

        if (!src) {
@@ -253,7 +253,7 @@ char *checksum_hex2bin(const char *src, size_t *len)
                return NULL;
        }

-       for (p = buf, *len = 0;
+       for (s = (unsigned char *)src, p = buf, *len = 0;
             slen > 0 && isxdigit(s[0]) && isxdigit(s[1]);
             slen--, s += 2, (*len)++)
                *p++ = hex2bin(s[0]) * 16 + hex2bin(s[1]);

```

