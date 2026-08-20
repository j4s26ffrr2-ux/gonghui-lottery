from flask import Flask, render_template, request, jsonify
import json
import os
import random

app = Flask(__name__)

DATA_FILE = '/tmp/state.json'

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
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'winners': [], 'remaining': MAX_WINNERS}

def save_state(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    state = load_state()
    return render_template('index.html', members=MEMBER_NAMES, 
                         winners=state['winners'], remaining=state['remaining'],
                         total=len(MEMBER_NAMES), history=state['winners'])

@app.route('/api/draw', methods=['POST'])
def draw():
    state = load_state()
    if state['remaining'] <= 0:
        return jsonify({'success': False, 'message': '已抽完'})
    
    available = [m for m in MEMBER_NAMES if m not in state['winners']]
    if not available:
        return jsonify({'success': False, 'message': '全员已中奖'})
    
    chosen = random.choice(available)
    state['winners'].append(chosen)
    state['remaining'] -= 1
    save_state(state)
    return jsonify({'success': True, 'name': chosen, 'message': f'恭喜 {chosen} 中奖！'})

@app.route('/api/status')
def status():
    state = load_state()
    return jsonify(state)

@app.route('/api/reset', methods=['POST'])
def reset():
    save_state({'winners': [], 'remaining': MAX_WINNERS})
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
