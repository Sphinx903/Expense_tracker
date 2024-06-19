import os

# Set Matplotlib cache directory before importing matplotlib
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_cache')

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import openpyxl

app = Flask(__name__)
app.secret_key = app.secret_key = b'%\x14\xd8\x91\xb1\x13G\x19\x80y\xffVK\xaaNl\xfd\xf7,\x8ei\xa6w\x84' # Replace with your secret key

# Initialize the DataFrame to store expenses
categories = ['Salaries', 'Utilities', 'Maintenance', 'Supplies', 'Transportation', 'Miscellaneous']
expenses = pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description'])

# Flask-Login initialization
login_manager = LoginManager()
login_manager.init_app(app)

# Example user database (replace with your actual user model and database)
users = {
    '1': {'id': '1', 'username': 'user1', 'password': 'password1'},
    '2': {'id': '2', 'username': 'user2', 'password': 'password2'}
}

# User class for Flask-Login (replace with your actual User model)
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        user = User()
        user.id = user_id
        return user
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', expenses=expenses.to_dict('records'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = None
        
        # Example authentication logic (replace with your actual authentication logic)
        for user_id, data in users.items():
            if data['username'] == username and data['password'] == password:
                user = User()
                user.id = user_id
                login_user(user)
                return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        
        global expenses
        new_expense = pd.DataFrame({'Date': [date], 'Amount': [amount], 'Category': [category], 'Description': [description]})
        expenses = pd.concat([expenses, new_expense], ignore_index=True)
        
        return redirect(url_for('index'))
    
    return render_template('add.html', categories=categories)

@app.route('/plot')
@login_required
def plot_expenses():
    # Bar Chart
    fig, ax = plt.subplots()
    expenses.groupby('Category')['Amount'].sum().plot(kind='bar', ax=ax, title='Total Expenses by Category')
    ax.set_ylabel('Total Amount')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    bar_plot_url = base64.b64encode(img.getvalue()).decode()
    
    # Pie Chart
    fig, ax = plt.subplots()
    expenses.groupby('Category')['Amount'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%', title='Expense Distribution')
    ax.set_ylabel('')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    pie_plot_url = base64.b64encode(img.getvalue()).decode()

    # Histogram
    fig, ax = plt.subplots()
    expenses['Amount'].plot(kind='hist', ax=ax, bins=10, title='Expense Distribution')
    ax.set_xlabel('Amount')
    ax.set_ylabel('Frequency')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    hist_plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('plot.html', bar_plot_url=bar_plot_url, pie_plot_url=pie_plot_url, hist_plot_url=hist_plot_url)

@app.route('/report')
@login_required
def generate_report():
    # Save the expenses DataFrame to an Excel file
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expense_report.xlsx')
    with pd.ExcelWriter(report_file) as writer:
        expenses.to_excel(writer, index=False, sheet_name='Expenses')
        summary = expenses.groupby('Category')['Amount'].sum()
        summary.to_excel(writer, sheet_name='Summary')
    
    return send_file(report_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
