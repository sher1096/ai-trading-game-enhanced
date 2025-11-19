"""
生成所有模板的实际提示词示例
"""
from trading_knowledge_modules import (
    TradingKnowledgeManager,
    get_preset_template,
    get_all_templates
)

def generate_all_examples():
    """生成所有模板的提示词示例"""

    manager = TradingKnowledgeManager()
    templates = get_all_templates()

    print("=" * 80)
    print("开始生成所有模板的提示词示例...")
    print("=" * 80)
    print()

    # 1. 无模块配置
    print("[1/6] 生成无模块配置示例...")
    no_modules_prompt = manager.build_enhanced_prompt(
        enabled_modules=[],
        base_prompt=""
    )

    with open('prompt_example_no_modules.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("无模块配置 - 原始简单提示词\n")
        f.write("=" * 80 + "\n\n")
        f.write(no_modules_prompt)
        f.write(f"\n\n{'=' * 80}\n")
        f.write(f"提示词长度: {len(no_modules_prompt)} 字符\n")
        f.write(f"启用模块数: 0\n")

    print(f"  OK 无模块配置 - 长度: {len(no_modules_prompt)} 字符")

    # 2-6. 各个预设模板
    template_names = {
        'conservative': '保守型',
        'aggressive': '激进型',
        'balanced': '平衡型',
        'quantitative': '量化型',
        'trend_following': '趋势跟随型'
    }

    index = 2
    for template_id, template_cn_name in template_names.items():
        print(f"[{index}/6] 生成{template_cn_name}模板示例...")

        template = get_preset_template(template_id)
        prompt = manager.build_enhanced_prompt(
            enabled_modules=template['modules'],
            **template['params']
        )

        filename = f'prompt_example_{template_id}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"{template['name']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"说明: {template['description']}\n\n")
            f.write(f"启用模块 ({len(template['modules'])}个):\n")
            for module_id in template['modules']:
                module = manager.get_all_modules()[module_id]
                f.write(f"  - {module_id}: {module.name}\n")
            f.write(f"\n参数配置:\n")
            f.write(f"  - 最大仓位: {template['params']['max_position_size']*100:.0f}%\n")
            f.write(f"  - 止损: {template['params']['stop_loss_pct']*100:.1f}%\n")
            f.write(f"  - 止盈: {template['params']['take_profit_pct']*100:.1f}%\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("完整提示词内容:\n")
            f.write("=" * 80 + "\n\n")
            f.write(prompt)
            f.write(f"\n\n{'=' * 80}\n")
            f.write(f"提示词总长度: {len(prompt)} 字符\n")
            f.write(f"约 {len(prompt.split())} 个词\n")

        print(f"  OK {template_cn_name}模板 - 长度: {len(prompt)} 字符, 模块数: {len(template['modules'])}")
        index += 1

    # 7. 自定义配置示例
    print("[7/7] 生成自定义配置示例...")
    custom_modules = ['risk_management', 'psychology', 'market_cycle']
    custom_params = {
        'max_position_size': 0.25,
        'stop_loss_pct': 0.04,
        'take_profit_pct': 0.12
    }

    custom_prompt = manager.build_enhanced_prompt(
        enabled_modules=custom_modules,
        base_prompt="You are an expert crypto trader with 10 years of experience.",
        **custom_params
    )

    with open('prompt_example_custom.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("自定义配置示例\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"自定义启用模块 ({len(custom_modules)}个):\n")
        for module_id in custom_modules:
            module = manager.get_all_modules()[module_id]
            f.write(f"  - {module_id}: {module.name}\n")
        f.write(f"\n自定义参数:\n")
        f.write(f"  - 最大仓位: {custom_params['max_position_size']*100:.0f}%\n")
        f.write(f"  - 止损: {custom_params['stop_loss_pct']*100:.1f}%\n")
        f.write(f"  - 止盈: {custom_params['take_profit_pct']*100:.1f}%\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("完整提示词内容:\n")
        f.write("=" * 80 + "\n\n")
        f.write(custom_prompt)
        f.write(f"\n\n{'=' * 80}\n")
        f.write(f"提示词总长度: {len(custom_prompt)} 字符\n")

    print(f"  OK 自定义配置 - 长度: {len(custom_prompt)} 字符")

    # 生成对比总结
    print("\n生成对比总结...")
    comparison_data = []

    # 无模块
    comparison_data.append({
        'name': '无模块',
        'modules_count': 0,
        'length': len(no_modules_prompt),
        'max_position': '-',
        'stop_loss': '-',
        'take_profit': '-'
    })

    # 各预设模块
    for template_id, template_cn_name in template_names.items():
        template = get_preset_template(template_id)
        prompt = manager.build_enhanced_prompt(
            enabled_modules=template['modules'],
            **template['params']
        )
        comparison_data.append({
            'name': template_cn_name,
            'modules_count': len(template['modules']),
            'length': len(prompt),
            'max_position': f"{template['params']['max_position_size']*100:.0f}%",
            'stop_loss': f"{template['params']['stop_loss_pct']*100:.1f}%",
            'take_profit': f"{template['params']['take_profit_pct']*100:.1f}%"
        })

    # 自定义
    comparison_data.append({
        'name': '自定义示例',
        'modules_count': len(custom_modules),
        'length': len(custom_prompt),
        'max_position': f"{custom_params['max_position_size']*100:.0f}%",
        'stop_loss': f"{custom_params['stop_loss_pct']*100:.1f}%",
        'take_profit': f"{custom_params['take_profit_pct']*100:.1f}%"
    })

    with open('prompt_comparison_summary.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("所有模板对比总结\n")
        f.write("=" * 100 + "\n\n")

        # 表格头
        f.write(f"{'模板':<15} {'模块数':<8} {'提示词长度':<12} {'最大仓位':<10} {'止损':<8} {'止盈':<8}\n")
        f.write("-" * 100 + "\n")

        # 数据行
        for item in comparison_data:
            f.write(f"{item['name']:<15} {item['modules_count']:<8} "
                   f"{item['length']:<12} {item['max_position']:<10} "
                   f"{item['stop_loss']:<8} {item['take_profit']:<8}\n")

        f.write("\n" + "=" * 100 + "\n")
        f.write("关键观察:\n\n")
        f.write("1. 提示词长度对比:\n")
        f.write("   - 无模块: 非常短，缺乏专业知识\n")
        f.write("   - 保守型: 中等长度，专注风险管理\n")
        f.write("   - 激进型: 较长，丰富的技术分析知识\n")
        f.write("   - 平衡型: 最长，综合全面的交易知识\n")
        f.write("   - 量化型/趋势型: 长度适中，专注特定领域\n\n")
        f.write("2. 风险参数对比:\n")
        f.write("   - 保守型: 20%仓位, 3%止损, 10%止盈 (风险最低)\n")
        f.write("   - 激进型: 50%仓位, 8%止损, 25%止盈 (风险最高)\n")
        f.write("   - 平衡型: 30%仓位, 5%止损, 15%止盈 (推荐)\n\n")
        f.write("3. 模块组合策略:\n")
        f.write("   - 保守型: 全是风控和心理模块\n")
        f.write("   - 激进型: 全是技术分析模块\n")
        f.write("   - 平衡型: 风控+技术+心理，最全面\n")
        f.write("   - 量化型: 数据驱动，系统化\n")
        f.write("   - 趋势型: 专注趋势判断\n\n")
        f.write("4. 使用建议:\n")
        f.write("   - 新手: 从保守型开始\n")
        f.write("   - 进阶: 使用平衡型或量化型\n")
        f.write("   - 专家: 根据策略自定义组合\n")
        f.write("   - A/B测试: 对比不同配置的实际效果\n")

    print(f"  OK 对比总结已生成")

    print("\n" + "=" * 80)
    print("完成! 所有示例已生成")
    print("=" * 80)
    print("\n生成的文件:")
    print("  1. prompt_example_no_modules.txt      - 无模块配置")
    print("  2. prompt_example_conservative.txt    - 保守型模板")
    print("  3. prompt_example_aggressive.txt      - 激进型模板")
    print("  4. prompt_example_balanced.txt        - 平衡型模板")
    print("  5. prompt_example_quantitative.txt    - 量化型模板")
    print("  6. prompt_example_trend_following.txt - 趋势跟随型模板")
    print("  7. prompt_example_custom.txt          - 自定义配置")
    print("  8. prompt_comparison_summary.txt      - 对比总结")
    print("  9. prompt_examples_output.md          - 完整文档\n")


if __name__ == '__main__':
    generate_all_examples()
