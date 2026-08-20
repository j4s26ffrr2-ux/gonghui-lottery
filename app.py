from flask import Flask, render_template, request, jsonify
import json
import os
import random

app = Flask(__name__)

# ---------- 使用 /tmp 目录 ----------
DATA_DIR = '/tmp/lottery_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, 'state.json')

# ---------- 成员名单 ----------
MEMBER_NAMES = [
    '很润', '范清川', '两只小鼠', 'AeoI菜鸟', '蓝月亮',
    '别卷了呗', '玩家25192586', '京城安少', '駶八戒', '慢慢。',
    '有点强啊我', '呆瓜王子', '昨日公园', 'KEIZUKO', '万野',
    '鱼刺！', 'mmg', '多可悲zZ', '骗氪特攻队', '辰',
    '热烈个温', '山海', '吻开', '充沛的小米', 'LLL',
    '武庸y', 'stan096712', '完美小遗忘', '178文艺青年', '秀芹。',
    '鱼仔啵啵', 'Shopt', '守护她一辈子', 'tt打怪兽', '飞鼠。',
    '楽曲'
]

MAX_WINNERS = 8

def load_state():
    # 如果文件不存在，返回默认状态
    if not os.path.exists(DATA_FILE):
        return {'winners': [], 'remaining': MAX_WINNERS}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'winners': [], 'remaining': MAX_WINNERS}

def save_state(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except:
        pass

@app.route('/')
def index():
    state = load_state()
    return render_template('index.html', 
                         members=MEMBER_NAMES,
                         winners=state.get('winners', []),
                         remaining=state.get('remaining', MAX_WINNERS),
                         total=len(MEMBER_NAMES),
                         history=state.get('winners', []))

@app.route('/api/draw', methods=['POST'])
def draw():
    state = load_state()
    if state['remaining'] <= 0:
        return jsonify({'success': False, 'message': '本周奖励名额已全部抽完！'})
    
    available = [m for m in MEMBER_NAMES if m not in state['winners']]
    if not available:
        return jsonify({'success': False, 'message': '所有成员都已中奖！'})
    
    chosen = random.choice(available)
    state['winners'].append(chosen)
    state['remaining'] -= 1
    save_state(state)
    return jsonify({'success': True, 'name': chosen, 'message': f'🎉 恭喜 {chosen} 获得本周奖励！'})

@app.route('/api/status')
def status():
    state = load_state()
    return jsonify({
        'remaining': state.get('remaining', MAX_WINNERS),
        'winners': state.get('winners', []),
        'total': len(MEMBER_NAMES),
        'history': state.get('winners', [])
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    save_state({'winners': [], 'remaining': MAX_WINNERS})
    return jsonify({'success': True, 'message': '已重置，开始新一周！'})

if __name__ == '__main__':
    # 确保数据目录存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    # 如果状态文件不存在，创建默认
    if not os.path.exists(DATA_FILE):
        save_state({'winners': [], 'remaining': MAX_WINNERS})
    app.run(host='0.0.0.0', port=5000, debug=False)
