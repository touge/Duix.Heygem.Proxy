# Proxy Service 说明 / README

## 简介 / Overview
一个基于 FastAPI 的轻量级「局域网代理」服务  
A lightweight FastAPI “LAN proxy” that exposes local-only TTS-video synthesis endpoints to your LAN.  

- 将本机只能访问的合成接口`/easy/submit`、`/easy/query`对局域网开放  
- 额外提供带私钥保护的静态资源下载接口 `/resources/{filename}`  
- 支持音频文件上传或 Base64 数据  

---

## 项目结构 / Project Structure proxy/ 

├── proxy_service.py 
├── requirements.txt 
└── start_proxy_service.bat

---

修改DUIX.HEYGEM项目目录中deyloy目录下yml配置文件，如：

```docker-compose-lite```

修改字段：
```
services:
  heygem-gen-video:
    volumes:
      - d:/heygem_data/temp:/app/resources
```
在原volumes项目内新增映射，此目录为接口程序使用目录。
新增映射后重新启动docker。

---

启动 / Run 

Windows 下双击或在命令行执行：
```
start_proxy_service.bat
```

Linux / macOS

```
export RESOURCE_ACCESS_KEY="YourSecretKey"
uvicorn proxy_service:app --host 0.0.0.0 --port 8000
```

启动后可通过浏览器打开：
```http://<HOST_IP>:8000/docs```


