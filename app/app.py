import os

# Set Matplotlib cache directory before importing matplotlib
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_cache')

from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import openpyxl

app = Flask(__name__)

# Initialize the DataFrame to store expenses
categories = ['Salaries', 'Utilities', 'Maintenance', 'Supplies', 'Transportation', 'Miscellaneous']
expenses = pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description'])

@app.route('/')
def index():
    return render_template('index.html', expenses=expenses.to_dict('records'))

@app.route('/add', methods=['GET', 'POST'])
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

