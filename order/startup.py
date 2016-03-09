from order import webapp

if __name__ == '__main__':
    webapp.setup()
    webapp.app.run(host='0.0.0.0', port=5000)
