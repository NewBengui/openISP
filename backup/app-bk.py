from flask import Flask, render_template, jsonify
import sftp_utils
import locale

app = Flask(__name__)

# Definindo a formatação local para português de Angola
locale.setlocale(locale.LC_ALL, 'pt_AO.UTF-8')

def format_currency(value):
    try:
        formatted_value = locale.currency(float(value), grouping=True)
        return formatted_value.replace('Kz', '').strip()  # Remove o símbolo de moeda e espaços em branco
    except ValueError:
        return value

def format_date(date_str):
    if len(date_str) == 14:
        return f"{date_str[6:8]}-{date_str[4:6]}-{date_str[:4]} {date_str[8:10]}:{date_str[10:12]}:{date_str[12:14]}"
    return date_str

app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['date'] = format_date

@app.route('/')
def index():
    files_data = sftp_utils.fetch_sftp_files()
    if not files_data:
        return render_template('index.html', error="Nenhum dado encontrado ou ocorreu um erro.")
    return render_template('index.html', files_data=files_data)

@app.route('/api/data')
def get_data():
    files_data = sftp_utils.fetch_sftp_files()
    if not files_data:
        return jsonify({"error": "Nenhum dado encontrado ou ocorreu um erro."}), 500
    return jsonify(files_data)

if __name__ == '__main__':
    app.run(debug=True)
