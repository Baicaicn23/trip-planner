"""启动脚本 —— 后端的"点火钥匙"

【干什么用】读配置(端口/日志级别)后拉起 uvicorn 服务器；reload=True 表示改代码自动重启(开发模式)。
【类比】等于 SpringBoot 项目的 main 方法：真正的应用装配在 app.api.main:app 里，这里只负责点火。
"""

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )

