import flask
webApp = flask.Flask(__name__)

@webApp.route('/')  #need to put our url here
def hello_world():
    return "NOT Hello, World!"

if __name__ == '__main__':  #if we do not give an url, run it and go to url localhost:5000 on browser
    webApp.run(debug=True)