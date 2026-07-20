#!/usr/bin/env python3
"""将轻小说章节转换为短剧分镜脚本

用法:
  python3 convert_to_script.py <项目名> --chapter <ln编号> [--output <输出文件名>]
  python3 convert_to_script.py <项目名> --all          # 转换所有章节

输出: projects/<项目名>/scripts/sdXXX_<章名>.md
"""

import os, sys, re, json, argparse
from pathlib import Path

PROJECTS_ROOT = Path(os.environ.get('COMIC_PROJECTS_ROOT', os.path.expanduser('~/comic-projects/projects')))

# 短剧分镜模板
def make_script(chapter_title, scene_setting, characters, shots):
    """生成短剧分镜脚本"""
    lines = [f'# {chapter_title}', '', f'**场景**：{scene_setting}', f'**人物**：{characters}', '', '---', '']
    for i, shot in enumerate(shots, 1):
        lines.append(f'### 镜头 {i}')
        lines.append(f'**画面**：{shot.get("画面", "")}')
        if shot.get('对白'):
            lines.append(f'**对白**：')
            for line in shot['对白']:
                lines.append(f'- {line}')
        else:
            lines.append(f'**对白**：无')
        lines.append(f'**时长**：{shot.get("时长", "3秒")}')
        lines.append(f'**转场**：{shot.get("转场", "切")}')
        lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('*本场完*')
    return '\n'.join(lines)

def list_ln_chapters(project_name):
    """列出项目的小说章节"""
    proj = PROJECTS_ROOT / project_name
    if not proj.exists():
        return []
    ln_dir = proj / 'light_novel'
    if not ln_dir.exists():
        return []
    chapters = []
    for f in sorted(ln_dir.glob('ln*.md')):
        match = re.match(r'ln(\d+)_(.+)\.md', f.name)
        if match:
            num = int(match.group(1))
            title = match.group(2)
            chapters.append({'num': num, 'title': title, 'file': f})
    return chapters

def chapter_exists(project_name, ln_num):
    """检查是否已有对应脚本"""
    scripts_dir = PROJECTS_ROOT / project_name / 'scripts'
    if not scripts_dir.exists():
        return False
    for f in scripts_dir.glob(f'sd{ln_num:03d}_*.md'):
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='转换小说章节为短剧分镜')
    parser.add_argument('project', help='项目名')
    parser.add_argument('--chapter', '-c', type=int, help='ln编号（如 1 对应 ln001）')
    parser.add_argument('--all', '-a', action='store_true', help='转换所有未转换的章节')
    parser.add_argument('--force', '-f', action='store_true', help='强制覆盖已有脚本')
    args = parser.parse_args()

    chapters = list_ln_chapters(args.project)
    if not chapters:
        print(f'❌ 项目 "{args.project}" 没有小说章节')
        sys.exit(1)

    if args.all:
        todo = [c for c in chapters if args.force or not chapter_exists(args.project, c['num'])]
        if not todo:
            print(f'✅ 所有章节已转换，无需操作')
            return
        print(f'📋 找到 {len(todo)} 个待转换章节：')
        for c in todo:
            print(f'  ln{c["num"]:03d}  {c["title"]}')
        print(f'\n💡 请用 Hermes agent 逐章调用 LLM 生成脚本内容后写入：')
        print(f'   projects/{args.project}/scripts/sdXXX_<章名>.md')
        print(f'\n或者手动创建脚本文件，参考格式：')
        print(f'   python3 -c "import convert_to_script; print(convert_to_script.make_script(...))"')
        return

    if args.chapter:
        match = [c for c in chapters if c['num'] == args.chapter]
        if not match:
            print(f'❌ 未找到 ln{args.chapter:03d}')
            sys.exit(1)
        c = match[0]
        output_name = f'sd{c["num"]:03d}_{c["title"]}.md'
        scripts_dir = PROJECTS_ROOT / args.project / 'scripts'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        output_path = scripts_dir / output_name
        if output_path.exists() and not args.force:
            print(f'⚠ 已存在: {output_name} (使用 --force 覆盖)')
            return
        print(f'📄 输出路径: {output_path}')
        print(f'📖 源文件: {c["file"]}')
        print(f'\n💡 请用 Hermes agent 读取源文件后生成短剧分镜脚本并写入：')
        print(f'   write_file(path="{output_path}", content=...)')
        return

if __name__ == '__main__':
    main()