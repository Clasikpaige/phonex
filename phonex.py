from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'supersecurekey123'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dummy User
class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# User Store
users = {
    'jami': User(id='jami', name='Jami Calloway', password='secure123')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Headless account data
account_data = {
    'name': 'Jami Calloway',
    'balance': 150_000_000.00,
    'transactions': [
        {'type': 'Deposit', 'amount': 50_000_000, 'note': 'Initial Deposit'},
        {'type': 'Deposit', 'amount': 100_000_000, 'note': 'Investment Funding'}
    ]
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    labels = [txn['note'] for txn in account_data['transactions']]
    data = [txn['amount'] for txn in account_data['transactions']]
    return render_template('index.html', account=account_data, chart_labels=labels, chart_data=data)

@app.route('/history')
@login_required
def history():
    return render_template('history.html', account=account_data)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    message = ''
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                message = 'Withdrawal must be greater than zero.'
            elif amount > account_data['balance']:
                message = 'Insufficient funds.'
            else:
                account_data['balance'] -= amount
                account_data['transactions'].append({
                    'type': 'Withdrawal',
                    'amount': -amount,
                    'note': 'Demo withdrawal'
                })
                message = f'Successfully withdrew ${amount:,.2f}'
        except ValueError:
            message = 'Invalid number format.'
    return render_template('withdraw.html', account=account_data, message=message)

if __name__ == '__main__':
    app.run(debug=True)
