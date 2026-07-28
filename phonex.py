from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from markupsafe import escape
from datetime import datetime
import uuid
from flask import Flask, request, jsonify
app = Flask(__name__)
app.secret_key = 'supersecurekey123'

# ---------------- LOGIN SETUP ---------------- #
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access the dashboard."
login_manager.login_message_category = "info"


class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


users = {
    'jami': User('jami', 'Jami Caloway', 'secure123'),
    'richard': User('richard', 'Richard Admin', 'admin2026')
}

user_roles = {
    "jami": "user",
    "richard": "admin"
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# ---------------- HELPERS ---------------- #
def sort_transactions(txns):
    return sorted(
        txns,
        key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"),
        reverse=True
    )


def add_running_balance(txns):
    running = 0
    for txn in reversed(txns):
        running += txn['amount']
        txn['running_balance'] = running
    return list(reversed(txns))


def format_balance(amount):
    return "${:,.2f}".format(amount)


# ---------------- ACCOUNT DATA (MANUAL BALANCE) ---------------- #
MANUAL_BALANCE = 143787523.00

account_data = {
    'bank_name': 'Phoenix Bank',
    'bank_tagline': 'Advanced Elite Banking Service',
    'name': 'Jami Caloway',
    'header': 'ACCOUNT STATEMENT – PREMIUM ACTIVITY SUMMARY',

    'balance': MANUAL_BALANCE,
    'formatted_balance': format_balance(MANUAL_BALANCE),

    'profile_locked': True,
    'offline_only': True,

    'transactions': [
        {
            'id': str(uuid.uuid4()),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'Withdrawal',
            'category': 'Court Order',
            'amount': -6000000,
            'note': 'Court Mandated Payment',
            'description': 'Bank executed court order payment'
        },
        {
            'id': str(uuid.uuid4()),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'Fee',
            'category': 'Service Charge',
            'amount': -6000,
            'note': 'Court Order Processing Fee',
            'description': 'Service charge for court execution'
        },
                {
            'id': str(uuid.uuid4()),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'Fee',
            'category': 'levy',
            'amount': 650,
            'note': 'Court Order Processing Fee',
            'description': 'Service charge for court execution'
        },
        {
            'id': str(uuid.uuid4()),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'Withdrawal',
            'category': 'Wire Transfer',
            'amount': -200000,
            'note': 'Unauthorized Transfer',
            'description': 'Security flagged transaction'
        },
        {
            'id': str(uuid.uuid4()),
            'date': '2026-03-21',
            'type': 'Deposit',
            'category': 'Levy',
            'amount': 300,
            'note': 'Levy Deposit',
            'description': 'Completed deposit'
        },
                {
            'id': str(uuid.uuid4()),
            'date': '2026-06-28',
            'type': 'Deposit',
            'category': 'Levy',
            'amount': 2050,
            'note': 'credit charge deposit',
            'description': 'Completed deposit'
        },
        {
            'id': str(uuid.uuid4()),
            'date': '2026-03-15',
            'type': 'Deposit',
            'category': 'Digital Assets',
            'amount': 345,
            'note': 'Razer Gold',
            'description': 'Giftcard conversion'
        }
    ]
}

# process transactions ONLY (balance stays manual)
account_data['transactions'] = sort_transactions(account_data['transactions'])
account_data['transactions'] = add_running_balance(account_data['transactions'])


# ---------------- ROUTES ---------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form.get('username', ''))
        password = request.form.get('password', '')

        user = users.get(username)

        if user and user.password == password:
            login_user(user)

            role = user_roles.get(user.id, "user")

            next_page = request.args.get('next')

            if role == "admin":
                return redirect(url_for("admin_chat"))
            else:
                return redirect(next_page if next_page and next_page.startswith('/') else url_for("dashboard"))

        flash('Invalid credentials. Try again.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    labels = [txn['note'] for txn in account_data['transactions'][:8]]
    data = [txn['amount'] for txn in account_data['transactions'][:8]]

    return render_template(
        'index.html',
        account=account_data,
        chart_labels=labels,
        chart_data=data
    )


@app.route('/history')
@login_required
def history():

    labels = [txn['note'] for txn in account_data['transactions'][:8]]
    data = [txn['amount'] for txn in account_data['transactions'][:8]]

    return render_template(
        'history.html',
        account=account_data,
        chart_labels=labels,
        chart_data=data
    )
    
chats = []


@app.route("/chat/send", methods=["POST"])
@login_required
def send_chat():
    data = request.get_json()

    message = (data.get("message") or "").strip()
    sender = data.get("from")  # This will be "user" or "admin"

    if not message:
        return jsonify({"ok": False, "error": "empty message"}), 400

    # Determine sender
    if sender == "admin" and current_user.id == "richard":
        from_field = "admin"
        user_name = "Admin"
    else:
        from_field = "user"
        user_name = current_user.name

    chats.append({
        "id": str(uuid.uuid4()),
        "user": user_name,
        "user_id": current_user.id,
        "from": from_field,          # ← This is the fix
        "message": message,
        "reply": "",
        "time": datetime.now().isoformat()
    })

    return jsonify({"ok": True})
    
@app.route("/chat/feed", methods=["GET"])
@login_required
def chat_feed():
    return jsonify({
        "chats": chats[-100:]   # last 100 messages
    })
    
@app.route('/card-details')
@login_required
def card_details():
    card_info = {
        "holder": "Jami Caloway",
        "card_type": "Mastercard",
        "card_number": "**** **** **** 9659",
        "expiry": "06 / 29",
        "cvv": "***",
        "status": "Active",
        "linked_account": "Phoenix Elite Savings",
        "bank": "Phoenix Bank",
        "issued": "2025-06-12"
    }
    return render_template('card_details.html', card=card_info)


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
                new_txn = {
                    'id': str(uuid.uuid4()),
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'type': 'Withdrawal',
                    'category': 'Wire Transfer',
                    'amount': -amount,
                    'note': 'Manual Withdrawal',
                    'description': 'User initiated withdrawal'
                }

                account_data['transactions'].append(new_txn)
                account_data['transactions'] = sort_transactions(account_data['transactions'])
                account_data['transactions'] = add_running_balance(account_data['transactions'])

                # IMPORTANT: manual balance does NOT auto-change
                message = f'Successfully processed withdrawal request of ${amount:,.2f}'

        except ValueError:
            message = 'Invalid number format.'

    return render_template('withdraw.html', account=account_data, message=message)

@app.route("/support/chat")   # ✅ changed from /admin/chat
@login_required
def admin_chat():
    if current_user.id != "richard":
        return redirect(url_for("dashboard"))




    return render_template("support.html")
# ---------------- RUN ---------------- #
if __name__ == '__main__':
    app.run(debug=True, port=3535)
