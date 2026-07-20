#!/usr/bin/env python3
"""Repair generic comic episode panels into concrete drawable manga beats.

This is a deterministic post-processor for projects whose panels contain vague template
phrases like “异常事件突然出现”. It rewrites **画面** and **构图** into concrete,
sequential, image-friendly descriptions while preserving Page/Panel structure, dialogue,
SFX, and mandatory fields.
"""
import argparse
import re
from pathlib import Path

PRESETS = {
    '雨夜外卖员': [
        ('雨夜的街边便利店外，陈野穿着湿透的黄色外卖雨衣，单手扶着电动车，外卖箱边缘滴水，霓虹灯倒映在积水里；他低头看手机，脸上是疲惫和想下班的表情。', '横向大格，远景建立场景，人物在画面右下，左侧留出雨夜街景和对白气泡空间。'),
        ('陈野手机屏幕特写：订单列表本来是空的，却突然跳出一单“热汤，送往旧楼天台”，时间显示 00:00；手机冷光照亮他惊讶的眼睛，外卖箱缝隙透出微弱白光。', '普通格，手机与眼睛双重特写，视觉焦点在异常订单和人物表情。'),
        ('陈野蹲下靠近外卖箱，手指停在拉链前不敢拉开；箱体自己轻轻震动，雨水沿箱盖滑落，背景街灯被压暗。', '竖向窄格，低角度近景，外卖箱在前景占大面积，人物脸在后景。'),
        ('旧楼门口出现一个半透明的中年男人身影，穿旧衬衫、神情焦急；陈野猛地回头，雨水从帽檐甩开，两人隔着雨幕对视。', '双人中景，过肩构图，陈野背影在前景，亡者身影在门洞光里。'),
        ('三连小格：第一格陈野盯着订单咽口水；第二格他拉紧雨衣拉链；第三格他的手抓起外卖箱提带，决定出发。', '三连小格，连续动作，视线从手机转到手部再到人物表情。'),
        ('旧楼楼梯间忽然被拉长成像没有尽头的竖井，楼层数字从 6 跳到 9 又跳回 4；陈野提着发光外卖箱站在楼梯口，显得很小。', '广角大场面，俯拍，楼梯旋转形成压迫感，人物小比例。'),
        ('天台铁门被风撞开，门后站着一个穿校服的女孩林遥，眼眶发红，手里攥着一张皱巴巴的旧照片；雨水把她的刘海贴在额头。', '半页大格，中景，天台门形成画框，女孩居中，天空和城市灯光在后方。'),
        ('陈野把热汤放到天台水泥台上，蒸汽在雨夜里升起；林遥低头看着汤盒，照片上父亲的笑脸与半透明父亲身影重叠。', '近景，汤盒和照片在前景，女孩与父亲虚影在后景，蒸汽引导视线。'),
        ('林遥背对天台边缘，肩膀颤抖；父亲虚影伸出手却碰不到她，只能停在半空。陈野站在旁边，欲言又止。', '横向大格，三人构图，天台栏杆横贯画面制造危险感。'),
        ('林遥突然转身大喊，眼泪和雨水混在一起；父亲虚影的表情从焦急变成愧疚，陈野握紧外卖箱带子。', '特写到中景，女孩脸部占主要画面，父亲虚影和陈野作背景反应。'),
        ('林遥打开热汤，汤盒盖内侧夹着父亲留下的纸条；纸条不用生成文字，只画成折叠白纸。父亲虚影低头，双手合十像是在道歉。', '物件特写，汤盒、白纸条、女孩颤抖的手为焦点，背景虚化。'),
        ('雨停一瞬，天台上方露出淡淡月光。林遥抱着热汤哭出来，父亲虚影在光里慢慢变淡；陈野站在天台门口，手机又轻轻亮起。', '结尾大格，远景，人物关系清晰，右下角手机亮光作为下集钩子。'),
    ],
    '猫咪便利侦探': [
        ('深夜便利店收银台前，年轻店员正打哈欠，一只橘猫从货架阴影里跳上柜台，嘴里叼着闪闪发亮的小物件。', '横向大格，远景建立便利店空间，收银台和橘猫是视觉焦点。'),
        ('橘猫把一枚戒指吐到收银台上，戒指滚到扫码枪旁边；店员瞪大眼睛，背景监控屏泛着冷光。', '物件特写，戒指在前景，店员惊讶表情在后景。'),
        ('便利店门外的雨夜街道空无一人，自动门却“叮”地打开一条缝，冷风吹动海报。', '低角度过肩，门缝和空街制造悬疑。'),
        ('橘猫用爪子拍打收银小票，小票上留下湿爪印；店员弯腰靠近，像在听猫说话。', '双人/人与猫中景，猫在桌面高位，人物在下方。'),
        ('监控画面里，一个戴帽子的黑影昨晚站在货架旁，橘猫的尾巴从画面边缘扫过。', '屏幕画面特写，监控边框清晰，黑影只保留轮廓。'),
        ('店员抱着橘猫冲进货架通道，猫忽然炸毛，盯着最底层泡面后面的黑色塑料袋。', '纵向窄格，货架形成纵深，塑料袋是焦点。'),
        ('黑色塑料袋被拉开，里面不是赃物，而是一张被撕开的照片和另一个猫铃铛。', '物件特写，照片碎片和铃铛占据中心。'),
        ('门口出现一位焦急的女孩，低头看见戒指时捂住嘴；橘猫跳到她脚边蹭了蹭。', '三人/一猫中景，女孩、店员、猫形成三角构图。'),
        ('女孩解释时，橘猫突然冲向门外，店员和女孩追出去，雨水溅起。', '动作格，斜向构图，奔跑方向从左下到右上。'),
        ('巷口垃圾桶旁，真正的小偷正翻找东西，看到橘猫扑来吓得后退。', '低角度动作格，猫在前景扑出，小偷在后景慌张。'),
        ('橘猫站在赃物袋上得意地抬头，店员撑着膝盖喘气，女孩抱着戒指哭笑不得。', '群像中景，猫居中高位，人物分列两侧。'),
        ('便利店清晨，橘猫趴在收银台睡觉，店门外贴着“猫咪侦探社”的手绘小牌，下一位顾客的影子停在门口。', '结尾横向大格，温暖日常光线，门口影子留悬念。'),
    ],
}

GENERIC_PATTERNS = [
    '普通日常场景', '异常事件突然出现', '主角靠近异常源', '关键配角登场',
    '连续观察、犹豫、伸手触碰', '世界观第一次展开', '规则第一次被验证',
    '主角做出第一次主动选择', '危机升级', '情感冲突爆发', '关键线索出现', '结尾钩子'
]


def detect_project(path: Path) -> str:
    for parent in [path.parent, *path.parents]:
        if parent.name in PRESETS:
            return parent.name
    # fallback by text title
    txt = path.read_text(encoding='utf-8', errors='ignore')
    for name in PRESETS:
        if name in txt:
            return name
    return ''


def rewrite_episode(path: Path) -> bool:
    txt = path.read_text(encoding='utf-8')
    project = detect_project(path)
    beats = PRESETS.get(project)
    if not beats:
        return False

    def repl_panel(m):
        num = int(m.group(1))
        body = m.group(2)
        if 1 <= num <= len(beats):
            visual, comp = beats[num-1]
            body = re.sub(r'\*\*画面\*\*[：:].*?(?=\n\*\*构图\*\*[：:])', f'**画面**：{visual}', body, flags=re.S)
            body = re.sub(r'\*\*构图\*\*[：:].*?(?=\n\s*\n\*\*气泡\*\*)', f'**构图**：{comp}', body, flags=re.S)
            # Replace positive prompt content between fences under AI prompt, keep style guide friendly and no text in art.
            prompt = 'black and white hand-drawn manga panel, clean ink line art, screentone shading, expressive characters, coherent sequential storytelling, commercial web manga style, no text, no letters, no watermark, clean empty speech-bubble space, ' + visual + ', ' + comp
            body = re.sub(r'(\*\*AI 提示词\*\*:\s*\n正向[：:]\s*\n```text\n).*?(\n```)', r'\1' + prompt + r'\2', body, flags=re.S)
            body = re.sub(r'(\*\*AI 提示词\*\*：\s*\n正向[：:]\s*\n```text\n).*?(\n```)', r'\1' + prompt + r'\2', body, flags=re.S)
        return f'### Panel {num}' + body

    new = re.sub(r'###\s+Panel\s+(\d+)(.*?)(?=\n---\n\n###\s+Panel\s+\d+|\n---\n\n##\s+Page|\n##\s+本集结尾钩子|\Z)', repl_panel, txt, flags=re.S)
    if new != txt:
        path.write_text(new, encoding='utf-8')
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episodes', nargs='+')
    args = ap.parse_args()
    changed=[]
    for p in args.episodes:
        path=Path(p)
        if rewrite_episode(path):
            changed.append(str(path))
    print({'changed': changed, 'count': len(changed)})

if __name__ == '__main__':
    main()
