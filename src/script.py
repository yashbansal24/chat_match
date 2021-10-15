from flask import Flask  
  
app = Flask(__name__) #creating the Flask class object   
 
@app.route('/') #decorator drfines the   
def home():  
    return "hello, this is our first flask website";  
  

def about(name):  
    return ("This is %s about page" %name)

app.add_url_rule("/about/<name>", "about", about)  

if __name__ =='__main__':  
    app.run(host= '127.0.0.1', port='8000', debug = True)  #replace host with chatmatch.com