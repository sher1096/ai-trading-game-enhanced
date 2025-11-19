"""
测试交易知识模块系统 - 展示不同配置的效果
"""
from trading_knowledge_modules import (
    TradingKnowledgeManager,
    get_preset_template,
    get_all_templates
)

def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def demo_1_list_all_modules():
    """示例1：查看所有可用模块"""
    print_separator("示例1：查看所有可用的交易知识模块")

    manager = TradingKnowledgeManager()
    modules = manager.get_module_list_for_ui()

    # 按类别分组
    categories = {}
    for module in modules:
        cat = module['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(module)

    for category, mods in categories.items():
        print(f"📁 {category}类模块：")
        for mod in mods:
            print(f"  ✓ {mod['id']}: {mod['name']}")
            print(f"    {mod['description']}")
        print()


def demo_2_no_modules():
    """示例2：不使用知识模块（原始方式）"""
    print_separator("示例2：不使用知识模块 - 原始简单提示词")

    manager = TradingKnowledgeManager()

    # 不启用任何模块
    prompt = manager.build_enhanced_prompt(
        enabled_modules=[],
        base_prompt=""
    )

    print("生成的提示词：")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    print(f"提示词长度: {len(prompt)} 字符")


def demo_3_conservative_template():
    """示例3：保守型模板（重风控）"""
    print_separator("示例3：保守型模板 - 适合稳健投资者")

    template = get_preset_template('conservative')

    print(f"模板名称: {template['name']}")
    print(f"说明: {template['description']}")
    print(f"启用的模块: {', '.join(template['modules'])}")
    print(f"参数配置: {template['params']}")
    print()

    manager = TradingKnowledgeManager()
    prompt = manager.build_enhanced_prompt(
        enabled_modules=template['modules'],
        **template['params']
    )

    print("生成的提示词（前1500字符）：")
    print("-" * 80)
    print(prompt[:1500])
    print("...")
    print("-" * 80)
    print(f"完整提示词长度: {len(prompt)} 字符")


def demo_4_aggressive_template():
    """示例4：激进型模板（高收益）"""
    print_separator("示例4：激进型模板 - 适合追求高收益")

    template = get_preset_template('aggressive')

    print(f"模板名称: {template['name']}")
    print(f"说明: {template['description']}")
    print(f"启用的模块: {', '.join(template['modules'])}")
    print(f"参数配置: {template['params']}")
    print()

    manager = TradingKnowledgeManager()
    prompt = manager.build_enhanced_prompt(
        enabled_modules=template['modules'],
        **template['params']
    )

    print("生成的提示词（前1500字符）：")
    print("-" * 80)
    print(prompt[:1500])
    print("...")
    print("-" * 80)
    print(f"完整提示词长度: {len(prompt)} 字符")


def demo_5_balanced_template():
    """示例5：平衡型模板（推荐）"""
    print_separator("示例5：平衡型模板 - 推荐配置")

    template = get_preset_template('balanced')

    print(f"模板名称: {template['name']}")
    print(f"说明: {template['description']}")
    print(f"启用的模块: {', '.join(template['modules'])}")
    print(f"参数配置: {template['params']}")
    print()

    manager = TradingKnowledgeManager()
    prompt = manager.build_enhanced_prompt(
        enabled_modules=template['modules'],
        **template['params']
    )

    print("生成的提示词（前1500字符）：")
    print("-" * 80)
    print(prompt[:1500])
    print("...")
    print("-" * 80)
    print(f"完整提示词长度: {len(prompt)} 字符")


def demo_6_custom_config():
    """示例6：自定义配置"""
    print_separator("示例6：自定义配置 - 只选择3个模块")

    # 自定义选择
    custom_modules = ['risk_management', 'psychology', 'market_cycle']
    custom_params = {
        'max_position_size': 0.25,
        'stop_loss_pct': 0.04,
        'take_profit_pct': 0.12
    }

    print(f"自定义启用的模块: {', '.join(custom_modules)}")
    print(f"自定义参数: {custom_params}")
    print()

    manager = TradingKnowledgeManager()
    prompt = manager.build_enhanced_prompt(
        enabled_modules=custom_modules,
        base_prompt="You are an expert crypto trader with 10 years of experience.",
        **custom_params
    )

    print("生成的提示词（前1500字符）：")
    print("-" * 80)
    print(prompt[:1500])
    print("...")
    print("-" * 80)
    print(f"完整提示词长度: {len(prompt)} 字符")


def demo_7_compare_templates():
    """示例7：对比所有模板"""
    print_separator("示例7：对比所有预设模板")

    templates = get_all_templates()
    manager = TradingKnowledgeManager()

    comparison = []

    for template_id, template in templates.items():
        prompt = manager.build_enhanced_prompt(
            enabled_modules=template['modules'],
            **template['params']
        )

        comparison.append({
            'id': template_id,
            'name': template['name'],
            'modules_count': len(template['modules']),
            'prompt_length': len(prompt),
            'max_position': template['params']['max_position_size'],
            'stop_loss': template['params']['stop_loss_pct'],
            'take_profit': template['params']['take_profit_pct']
        })

    print("模板对比表：")
    print()
    print(f"{'模板':<20} {'模块数':<8} {'提示词长度':<12} {'最大仓位':<10} {'止损':<8} {'止盈':<8}")
    print("-" * 80)

    for item in comparison:
        print(f"{item['name']:<20} {item['modules_count']:<8} "
              f"{item['prompt_length']:<12} {item['max_position']*100:.0f}%{'':<6} "
              f"{item['stop_loss']*100:.1f}%{'':<3} {item['take_profit']*100:.1f}%")

    print()
    print("观察：")
    print("  • 保守型：模块最少，但都是风控相关")
    print("  • 激进型：专注技术分析，仓位和止盈目标更高")
    print("  • 平衡型：综合考虑，模块最多")
    print("  • 量化型：重视数据和指标")
    print("  • 趋势型：专注于趋势判断")


def demo_8_full_prompt_example():
    """示例8：完整提示词示例"""
    print_separator("示例8：完整提示词示例 - 平衡型模板")

    template = get_preset_template('balanced')
    manager = TradingKnowledgeManager()

    prompt = manager.build_enhanced_prompt(
        enabled_modules=template['modules'],
        **template['params']
    )

    print("【完整提示词内容】")
    print("="*80)
    print(prompt)
    print("="*80)
    print()
    print(f"总长度: {len(prompt)} 字符")
    print(f"约 {len(prompt.split())} 个词")
    print()
    print("这个提示词包含了：")
    print("  ✓ 风险管理原则（止损、止盈、仓位控制）")
    print("  ✓ 技术分析理论（道氏理论、趋势、支撑阻力）")
    print("  ✓ 市场周期认知（牛熊市特征和应对）")
    print("  ✓ 交易心理学（避免常见陷阱）")
    print("  ✓ 指标组合共振（多指标验证）")


def demo_9_minimal_vs_full():
    """示例9：最小配置 vs 完整配置对比"""
    print_separator("示例9：最小配置 vs 完整配置效果对比")

    manager = TradingKnowledgeManager()

    # 最小配置
    minimal_prompt = manager.build_enhanced_prompt(
        enabled_modules=[],
        base_prompt="You are a crypto trader."
    )

    # 完整配置
    full_modules = list(manager.get_all_modules().keys())
    full_prompt = manager.build_enhanced_prompt(
        enabled_modules=full_modules,
        base_prompt="You are a crypto trader.",
        max_position_size=0.3,
        stop_loss_pct=0.05,
        take_profit_pct=0.15
    )

    print("最小配置（无知识模块）：")
    print(f"  提示词: {minimal_prompt}")
    print(f"  长度: {len(minimal_prompt)} 字符")
    print()

    print("完整配置（所有11个模块）：")
    print(f"  启用模块: {len(full_modules)} 个")
    print(f"  提示词长度: {len(full_prompt)} 字符")
    print(f"  是最小配置的 {len(full_prompt) / len(minimal_prompt):.1f} 倍")
    print()

    print("前500字符对比：")
    print()
    print("【最小配置】")
    print("-" * 80)
    print(minimal_prompt[:500])
    print()

    print("【完整配置】")
    print("-" * 80)
    print(full_prompt[:500])
    print("...")


def run_all_demos():
    """运行所有演示"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "AI交易知识模块系统 - 效果演示" + " "*20 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    demos = [
        demo_1_list_all_modules,
        demo_2_no_modules,
        demo_3_conservative_template,
        demo_4_aggressive_template,
        demo_5_balanced_template,
        demo_6_custom_config,
        demo_7_compare_templates,
        demo_8_full_prompt_example,
        demo_9_minimal_vs_full,
    ]

    for i, demo in enumerate(demos, 1):
        try:
            demo()
            input(f"\n按回车继续查看下一个示例... ({i}/{len(demos)})")
        except KeyboardInterrupt:
            print("\n\n演示已中断。")
            break
        except Exception as e:
            print(f"\n❌ 运行示例时出错: {e}")
            import traceback
            traceback.print_exc()

    print_separator("演示完成")
    print("您已经看到了交易知识模块系统的强大功能！")
    print()
    print("总结：")
    print("  ✓ 11个专业交易知识模块可选")
    print("  ✓ 5个预设模板适合不同风格")
    print("  ✓ 完全可配置的参数")
    print("  ✓ 从简单到复杂的灵活性")
    print()
    print("下一步：选择一个模板，开始您的AI交易之旅！")


if __name__ == '__main__':
    run_all_demos()
