# scheduler_cli.py

from sql.models import *
import argparse
from main import load_course, load_room, prepare_courses, prepare_rooms, HybridScheduler, convert_to_schedules, get_session

def main(soft_constraints):
    """
    主函数，用于接收软约束列表并启动排课算法
    :param soft_constraints: 软约束列表，格式为 [(约束ID, 权重), ...]
    """
    try:
        # 加载原始数据
        raw_courses = load_course()
        raw_rooms = load_room()

        # 转换数据格式
        courses = prepare_courses(raw_courses)
        rooms = prepare_rooms(raw_rooms)

        print(f"\n=== 数据加载完成 ===")
        print(f"课程总数: {len(courses)}")
        print(f"教室总数: {len(rooms)}")

        # 使用混合排课算法
        print("\n=== 开始排课 ===")
        scheduler = HybridScheduler(courses, rooms, soft_constraints=soft_constraints)
        schedule, unscheduled = scheduler.solve()

        # 转换结果
        schedules = convert_to_schedules(schedule, courses)

        # 保存结果到数据库
        session = get_session()
        session.query(Schedule).delete()
        session.commit()
        session.add_all(schedules)
        session.commit()
        session.close()

        print("\n=== 排课完成 ===")
        print(f"排课记录总数: {len(schedules)}条")

    except Exception as e:
        print(f"排课失败: {e}")
    finally:
        print("\n排课程序结束")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="智能排课系统")
    parser.add_argument("--soft_constraints", type=str, help="软约束列表，格式为 '(id1,weight1),(id2,weight2)'")
    args = parser.parse_args()

    # 解析软约束
    soft_constraints = []
    if args.soft_constraints:
        try:
            # 将字符串解析为列表
            constraints_str = args.soft_constraints.strip("[]()")
            constraints_list = constraints_str.split("),(")
            for item in constraints_list:
                constraint = item.strip("()").split(",")
                if len(constraint) == 2:
                    soft_constraints.append((int(constraint[0]), int(constraint[1])))
            print(f"解析到的软约束: {soft_constraints}")
        except Exception as e:
            print(f"解析软约束失败: {e}")
            soft_constraints = []

    # 启动主函数
    main(soft_constraints)