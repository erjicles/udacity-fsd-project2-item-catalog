from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

app = Flask(__name__)

APPLICATION_NAME = "Item Catalog Application"

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello World"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)