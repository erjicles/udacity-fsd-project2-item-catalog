from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

app = Flask(__name__)

APPLICATION_NAME = "Item Catalog Application"

# Landing page - show all categories and recent items
@app.route('/')
@app.route('/category/')
def showCategories():
    return render_template('main.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)