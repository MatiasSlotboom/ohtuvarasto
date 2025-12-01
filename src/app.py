from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses
warehouses = {}


@app.route('/')
def index():
    return render_template('index.html', warehouses=warehouses)


@app.route('/add_warehouse', methods=['POST'])
def add_warehouse():
    name = request.form.get('name', '').strip()
    try:
        tilavuus = float(request.form.get('tilavuus', 0))
    except ValueError:
        tilavuus = 0
    try:
        alku_saldo = float(request.form.get('alku_saldo', 0))
    except ValueError:
        alku_saldo = 0

    if name and tilavuus > 0:
        warehouses[name] = Varasto(tilavuus, alku_saldo)

    return redirect(url_for('index'))


@app.route('/remove_warehouse/<name>', methods=['POST'])
def remove_warehouse(name):
    if name in warehouses:
        del warehouses[name]
    return redirect(url_for('index'))


@app.route('/warehouse/<name>')
def view_warehouse(name):
    if name not in warehouses:
        return redirect(url_for('index'))
    warehouse = warehouses[name]
    return render_template('warehouse.html', name=name, warehouse=warehouse)


@app.route('/warehouse/<name>/add', methods=['POST'])
def add_to_warehouse(name):
    if name in warehouses:
        try:
            amount = float(request.form.get('amount', 0))
        except ValueError:
            amount = 0
        if amount > 0:
            warehouses[name].lisaa_varastoon(amount)
        return redirect(url_for('view_warehouse', name=name))
    return redirect(url_for('index'))


@app.route('/warehouse/<name>/remove', methods=['POST'])
def remove_from_warehouse(name):
    if name in warehouses:
        try:
            amount = float(request.form.get('amount', 0))
        except ValueError:
            amount = 0
        if amount > 0:
            warehouses[name].ota_varastosta(amount)
        return redirect(url_for('view_warehouse', name=name))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
