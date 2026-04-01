# Sec-Skills
网络安全相关的大模型skill

后续有的新的Skill也会在该项目中更新，喜欢的可以点一个star哦。

- web-feature-search 访问网站，分析网站特征，生成FOFA、Hunter和谷歌搜索语法。
- flutter-ssl-analysis 调用ida-pro-mcp，分析libflutter.so，获取ssl_write和ssl_read地址，生成Frida抓包命令。
- dirsearch-command-generator dirsearch命令生成

其他好用的skills

- Java Audit Skills https://github.com/RuoJi6/java-audit-skills

## 使用
### web-feature-search
```
/web-feature-analyzer https://xxx.com/login
```

### flutter-ssl-analysis
**获取 ssl_write 和 ssl_read**
```
/flutter-ssl-analysis 调用ida-pro-mcp分析libflutter.so
或者
/flutter-ssl-analysis Locating SSL_write/SSL_read Functions
```

**生成 frida SSL bypass**
```
/flutter-ssl-analysis SSL Bypass Script Generation
```

### dirsearch-command-generator
获取网站特征后，给出需求+字典地址
```
/dirsearch-command-generator 网站是用XX语言写的，文件后缀有JS、html、jsp、xxx，给出dirsearch命令。
```

联动web-feature-search使用
```
/web-feature-search https://xxx.com/login
/dirsearch-command-generator 根据上述skill返回的网站特征给出dirsearch命令 
```

