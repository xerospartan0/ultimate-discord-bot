from flask import Flask, render_template_string, request, redirect, url_for
import os, json

app = Flask(__name__)
data_file = os.path.join(os.getcwd(), 'data', 'dashboard.json')

@app.route('/')
def index():
    cfg = {}
    if os.path.exists(data_file):
        with open(data_file) as f:
            cfg = json.load(f)
    return render_template_string('''
        <h2>Ultimate Bot Dashboard (Template)</h2>
        <p>Use this lightweight dashboard to view and change simple settings.</p>
        <form method="post" action="/update">
        Prefix: <input name="prefix" value="{{cfg.get('prefix','!')}}"> <br/>
        Premium role: <input name="premium_role" value="{{cfg.get('premium_role','Premium')}}"> <br/>
        <button type="submit">Save</button>
        </form>
        ''', cfg=cfg)

@app.route('/update', methods=['POST'])
def update():
    cfg = {'prefix': request.form.get('prefix','!'), 'premium_role': request.form.get('premium_role','Premium')}
    with open(data_file, 'w') as f:
        json.dump(cfg, f)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
