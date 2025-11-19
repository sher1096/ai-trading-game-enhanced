#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update AI models to 2025 latest versions
"""
import sqlite3
import json
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def update_models_to_2025():
    """Update models field in providers table to 2025 latest models"""
    conn = sqlite3.connect('AITradeGame.db')
    cursor = conn.cursor()

    print("=" * 60)
    print("Updating AI models to 2025 latest versions...")
    print("=" * 60)

    # Get current providers
    cursor.execute('SELECT id, name, models FROM providers')
    providers = cursor.fetchall()

    if not providers:
        print("\n[X] No API providers in database")
        conn.close()
        return

    print(f"\nFound {len(providers)} API provider(s):\n")

    # 模型映射：旧模型名 -> 新模型名
    model_mapping = {
        # OpenAI
        'gpt-4o': 'gpt-5',
        'gpt-4o-mini': 'gpt-5-mini',
        'gpt-4-turbo': 'gpt-5',
        'gpt-4': 'gpt-5',
        'gpt-3.5-turbo': 'gpt-5-mini',

        # Claude
        'claude-3-5-sonnet-20241022': 'claude-sonnet-4-5',
        'claude-3-5-sonnet-20240620': 'claude-sonnet-4-5',
        'claude-3-opus-20240229': 'claude-opus-4-1',
        'claude-3-sonnet-20240229': 'claude-sonnet-4',
        'claude-3-haiku-20240307': 'claude-haiku-4-5',

        # DeepSeek (已经是最新，但标注版本)
        'deepseek-chat': 'deepseek-chat',  # V3.1
        'deepseek-coder': 'deepseek-chat',  # 统一使用chat
    }

    # 2025推荐模型列表
    recommended_models = {
        'openai': ['gpt-5', 'gpt-5-mini', 'gpt-5-nano'],
        'claude': ['claude-sonnet-4-5', 'claude-opus-4-1', 'claude-haiku-4-5'],
        'deepseek': ['deepseek-chat', 'deepseek-reasoner'],
        'qwen': ['qwen-plus', 'qwen-plus-latest', 'qwen-turbo', 'qwen-max-2025-01-25'],
        'anthropic': ['claude-sonnet-4-5', 'claude-opus-4-1', 'claude-haiku-4-5'],
    }

    updated_count = 0

    for provider_id, provider_name, models_str in providers:
        print(f"📋 提供商 #{provider_id}: {provider_name}")
        print(f"   原models字段: {models_str}")

        # 尝试解析models字段
        if not models_str:
            # 根据提供商名称推荐模型
            provider_name_lower = provider_name.lower()
            new_models = []

            if 'openai' in provider_name_lower or 'gpt' in provider_name_lower:
                new_models = recommended_models['openai']
            elif 'claude' in provider_name_lower or 'anthropic' in provider_name_lower:
                new_models = recommended_models['claude']
            elif 'deepseek' in provider_name_lower:
                new_models = recommended_models['deepseek']
            elif 'qwen' in provider_name_lower or 'alibaba' in provider_name_lower:
                new_models = recommended_models['qwen']
            else:
                print(f"   ⚠️  无法识别提供商类型，跳过")
                continue

            new_models_str = json.dumps(new_models)
            cursor.execute('UPDATE providers SET models = ? WHERE id = ?',
                         (new_models_str, provider_id))
            print(f"   ✅ 已添加推荐模型: {new_models}")
            updated_count += 1
            continue

        # 尝试解析为JSON
        try:
            models_list = json.loads(models_str)
        except:
            # 可能是逗号分隔的字符串
            models_list = [m.strip() for m in models_str.split(',') if m.strip()]

        # 更新模型名称
        new_models_list = []
        has_changes = False

        for model in models_list:
            if model in model_mapping:
                new_model = model_mapping[model]
                if new_model != model:
                    print(f"   🔄 {model} -> {new_model}")
                    has_changes = True
                new_models_list.append(new_model)
            else:
                # 保留未映射的模型
                new_models_list.append(model)

        # 去重
        new_models_list = list(dict.fromkeys(new_models_list))

        # 根据提供商添加新模型
        provider_name_lower = provider_name.lower()
        if 'openai' in provider_name_lower or 'gpt' in provider_name_lower:
            for model in recommended_models['openai']:
                if model not in new_models_list:
                    new_models_list.append(model)
                    has_changes = True
        elif 'claude' in provider_name_lower or 'anthropic' in provider_name_lower:
            for model in recommended_models['claude']:
                if model not in new_models_list:
                    new_models_list.append(model)
                    has_changes = True
        elif 'deepseek' in provider_name_lower:
            for model in recommended_models['deepseek']:
                if model not in new_models_list:
                    new_models_list.append(model)
                    has_changes = True
        elif 'qwen' in provider_name_lower or 'alibaba' in provider_name_lower:
            for model in recommended_models['qwen']:
                if model not in new_models_list:
                    new_models_list.append(model)
                    has_changes = True

        if has_changes:
            new_models_str = json.dumps(new_models_list)
            cursor.execute('UPDATE providers SET models = ? WHERE id = ?',
                         (new_models_str, provider_id))
            print(f"   ✅ 已更新为: {new_models_list}")
            updated_count += 1
        else:
            print(f"   ℹ️  无需更新")

    conn.commit()

    print(f"\n" + "=" * 60)
    print(f"✅ 更新完成！共更新了 {updated_count} 个API提供商")
    print("=" * 60)

    # 显示更新后的数据
    print("\n📊 更新后的提供商列表:\n")
    cursor.execute('SELECT id, name, models FROM providers')
    for provider_id, provider_name, models_str in cursor.fetchall():
        try:
            models_list = json.loads(models_str)
            print(f"#{provider_id} {provider_name}:")
            for model in models_list:
                print(f"  - {model}")
        except:
            print(f"#{provider_id} {provider_name}: {models_str}")

    conn.close()

    print("\n" + "=" * 60)
    print("🎉 所有AI模型已更新到2025最新版本！")
    print("请刷新浏览器页面查看更新")
    print("=" * 60)

if __name__ == '__main__':
    try:
        update_models_to_2025()
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
