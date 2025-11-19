#!/bin/bash

# AITradeGame 一键部署脚本
# 使用方法: bash deploy.sh

set -e  # 遇到错误立即退出

echo "========================================="
echo "AITradeGame 服务器部署工具"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[提示] 某些操作可能需要sudo权限${NC}"
fi

# 1. 检查Docker是否安装
echo -e "${GREEN}[1/6] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker安装完成！${NC}"
else
    echo -e "${GREEN}Docker已安装 ✓${NC}"
fi

# 2. 检查Docker Compose
echo ""
echo -e "${GREEN}[2/6] 检查Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose未安装，正在安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose安装完成！${NC}"
else
    echo -e "${GREEN}Docker Compose已安装 ✓${NC}"
fi

# 3. 配置环境变量
echo ""
echo -e "${GREEN}[3/6] 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}未找到.env文件，从模板创建...${NC}"
    cp .env.example .env

    # 生成随机SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/请替换为随机字符串-使用openssl rand -hex 32生成/$SECRET_KEY/g" .env

    echo -e "${YELLOW}⚠️  请编辑 .env 文件并填入您的API密钥${NC}"
    echo -e "${YELLOW}   必填项: OPENAI_API_KEY 或 DEEPSEEK_API_KEY${NC}"
    echo ""
    read -p "是否现在编辑.env文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo -e "${GREEN}.env文件已存在 ✓${NC}"
fi

# 4. 创建必要的目录
echo ""
echo -e "${GREEN}[4/6] 创建数据目录...${NC}"
mkdir -p data logs logs/nginx
chmod 755 data logs logs/nginx
echo -e "${GREEN}目录创建完成 ✓${NC}"

# 5. 构建Docker镜像
echo ""
echo -e "${GREEN}[5/6] 构建Docker镜像...${NC}"
docker-compose build
echo -e "${GREEN}镜像构建完成 ✓${NC}"

# 6. 启动服务
echo ""
echo -e "${GREEN}[6/6] 启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo ""
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo ""
echo -e "${GREEN}检查服务状态...${NC}"
docker-compose ps

# 检查健康状态
echo ""
echo -e "${GREEN}检查应用健康状态...${NC}"
if curl -s http://localhost:80/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ 应用运行正常！${NC}"
else
    echo -e "${YELLOW}⚠️  应用可能需要更多时间启动，请稍后访问${NC}"
fi

# 完成信息
echo ""
echo "========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "========================================="
echo ""
echo "访问地址: http://$(hostname -I | awk '{print $1}'):80"
echo "或者: http://localhost:80"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  更新代码: git pull && docker-compose up -d --build"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "  1. 确保在.env中配置了API密钥"
echo "  2. 访问Web界面添加API提供方"
echo "  3. 创建AI交易模型开始测试"
echo ""
echo -e "${GREEN}祝您使用愉快！${NC}"
