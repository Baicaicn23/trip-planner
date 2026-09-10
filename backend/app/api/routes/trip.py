"""旅行规划API路由 —— 核心接单窗口（Controller层）

【使命】对外只露一个主接口 POST /api/trip/plan：收 TripRequest → 调车间主任 → 回 TripPlanResponse 信封。
【类比】苍穹外卖的 EmployeeController：接DTO、调Service、回Result，三段式一模一样。
"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """生成旅行计划 —— 全站最核心的接口

    【干什么用】打收单日志 → 拿车间主任单例 → plan_trip()干活 → 成功装信封返回；
    异常则打完整堆栈转成HTTP 500（兜底计划在主任内部已处理过，走到这里的是真塌房）。
    【类比】@PostMapping("/login") 那套：参数绑定DTO → service处理 → Result.success()。

    Args:

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查 —— 会真的唤醒车间主任（首次调用会启动MCP进程），报告Agent名和工具数"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()

        # 修复bug：原代码写 agent.agent（该属性不存在，是早期版本残留），
        # 现按真实结构报告四位专员及其工具数
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agents": [
                agent.attraction_agent.name,
                agent.weather_agent.name,
                agent.hotel_agent.name,
                agent.planner_agent.name,
            ],
            "tools_count": len(agent.attraction_agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

