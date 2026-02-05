from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'supersecurekey123'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User
class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# User Store
users = {
    'jami': User(id='jami', name='Jami Caloway', password='secure343')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

account_data = {
    'name': 'Jami Caloway',
    'balance': 149_993_380.00,
    'header': 'ACCOUNT STATEMENT – UPDATED ACTIVITY',

    'transactions': [
        # Newest transactions on top
        {'date': '2025-11-21', 'type': 'Deposit', 'amount': 100, 'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-11-21', 'type': 'Deposit', 'amount': 75,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-11-24', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-11-28', 'type': 'Deposit', 'amount': 150,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-1', 'type': 'Deposit', 'amount': 30,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-3', 'type': 'Deposit', 'amount': 370,  'note':'failed deposit code inactive'},
        {'date': '2025-12-3', 'type': 'Deposit', 'amount': 185,  'note':'Apple Giftcard Deposit'},
        {'date': '2025-12-5', 'type': 'Deposit', 'amount': 200,  'note':'Razer Gold Giftcard Deposit'},
        {'date': '2025-12-09', 'type': 'Deposit', 'amount': 45,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-13', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-15', 'type': 'Deposit', 'amount': 45,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-19', 'type': 'Deposit', 'amount': 20,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-19', 'type': 'Deposit', 'amount': 70,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-19', 'type': 'Deposit', 'amount': 450,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-12-23', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2026-01-02', 'type': 'Deposit', 'amount': 200,  'note':'Razer Gold Giftcard Deposit'},
        {'date': '2026-01-05', 'type': 'Deposit', 'amount': 75,  'note':'Razer Gold Giftcard Deposit'},
        {'date': '2025-01-06', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2026-01-10', 'type': 'Deposit', 'amount': 175,  'note':'Razer Gold Giftcard Deposit'},
        {'date': '2025-101-14', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2026-01-06', 'type': 'Deposit', 'amount': 60,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-01-20', 'type': 'Deposit', 'amount': 50,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-01-21', 'type': 'Deposit', 'amount': 10,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2026-01-23', 'type': 'Deposit', 'amount': 45,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2026-01-27', 'type': 'Deposit', 'amount': 45,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-01-30', 'type': 'Deposit', 'amount': 75,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-02-03', 'type': 'Deposit', 'amount': 465,  'note': 'Xbox Gift Card Deposit'},
        {'date': '2025-02-03', 'type': 'Deposit', 'amount': 200,  'note': 'Xbox Gift Card Deposit'},
        # Existing historical transactions
        {'date': '2025-10-18', 'type': 'Withdrawal', 'amount': -1600, 'note': 'Cash App Withdrawal'},
        {'date': '2025-10-18', 'type': 'Withdrawal', 'amount': -2000, 'note': 'Cash App Withdrawal'},
        {'date': '2025-10-17', 'type': 'Withdrawal', 'amount': -2500, 'note': 'Cash App Withdrawal'},
        {'date': '2025-10-17', 'type': 'Withdrawal', 'amount': -700,  'note': 'Cash App Withdrawal'},
        {'date': '2025-10-10', 'type': 'Deposit', 'amount': 100_000_000, 'note': 'Investment Funding'},
        {'date': '2025-10-10', 'type': 'Deposit', 'amount': 50_000_000,  'note': 'Initial Deposit'}
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
@app.route('/card-details')

@login_required
def card_details():
    card_info = {
        "holder": "Jami Caloway",
        "card_type": "Visa",
        "card_number": "**** **** **** 5432",
        "expiry": "06 / 30",
        "cvv": "***",
        "status": "Active",
        "linked_account": "Primary Checking",
        "bank": "Revolut",
        "issued": "2025-06-12"
    }
    return render_template('card_details.html', card=card_info)

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
    app.run(debug=True, port=3535)
