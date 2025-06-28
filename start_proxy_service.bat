@echo off
setlocal

rem —— 激活 Conda 环境 —— 
call conda activate .\python3.10

rem —— 启动服务（直接运行 main.py）—— 
python main.py

endlocal
pause
