from flask import Flask, render_template, request, jsonify
import json
import os
import random
import time

app = Flask(__name__)

# ---------- 使用 /tmp 目录（Railway 可写） ----------
DATA_DIR = '/tmp/lottery_data'
os.makedirs(DATA_DIR, exist_ok=True)

STATE_FILE = os.path.join(DATA_DIR, 'state.json')

# ---------- 成员名单（36人）----------
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

TOTAL_MEMBERS = len(MEMBER_NAMES)
MAX_WINNERS = 8

# ---------- 状态管理 ----------
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'winners': [],
        'winner_indices': [],
        'remaining': MAX_WINNERS,
        'total': TOTAL_MEMBERS,
        'history': []
    }

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def reset_state():
    state = {
        'winners': [],
        'winner_indices': [],
        'remaining': MAX_WINNERS,
        'total': TOTAL_MEMBERS,
        'history': []
    }
    save_state(state)
    return state

def do_draw():
    lock_file = STATE_FILE + '.lock'
    start_time = time.time()
    while os.path.exists(lock_file):
        if time.time() - start_time > 3:
            return False, None, '系统繁忙，请稍后再试'
        time.sleep(0.1)

    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    try:
        state = load_state()
        if state['remaining'] <= 0:
            return False, None, '本周奖励名额已全部抽完！'

        winner_indices = set(state['winner_indices'])
        candidates = [i for i in range(TOTAL_MEMBERS) if i not in winner_indices]
        if not candidates:
            return False, None, '所有成员都已中奖！'

        chosen_idx = random.choice(candidates)
        chosen_name = MEMBER_NAMES[chosen_idx]

        state['winner_indices'].append(chosen_idx)
        state['winners'].append(chosen_name)
        state['history'].append(chosen_name)
        state['remaining'] -= 1
        save_state(state)
        return True, chosen_name, f'🎉 恭喜 {chosen_name} 获得本周奖励！'
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)

@app.route('/')
def index():
    state = load_state()
    return render_template('index.html',
                         members=MEMBER_NAMES,
                         winners=state['winners'],
                         remaining=state['remaining'],
                         total=TOTAL_MEMBERS,
                         history=state['history'])

@app.route('/api/draw', methods=['POST'])
def api_draw():
    success, name, message = do_draw()
    return jsonify({
        'success': success,
        'name': name,
        'message': message
    })

@app.route('/api/status')
def api_status():
    state = load_state()
    return jsonify({
        'remaining': state['remaining'],
        'winners': state['winners'],
        'history': state['history'],
        'total': TOTAL_MEMBERS
    })

@app.route('/api/reset', methods=['POST'])
def api_reset():
    reset_state()
    return jsonify({'success': True, 'message': '已重置，开始新一周！'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
