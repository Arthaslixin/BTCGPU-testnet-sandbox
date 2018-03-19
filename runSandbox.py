#coding=utf-8
import os
from flask import Flask, request, url_for, render_template, flash, redirect
import redis
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from requests import post
import sys

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='4HqpixKatu'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connectRPC():
    rpc_user='CHANGE_THIS_USERNAME'
    rpc_password='CHANGE_THIS_PASSWORD'

    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332"%(rpc_user, rpc_password))
    return rpc_connection

def get_balance():
    rpc_connection = connectRPC()
    commands = [['getbalance']]
    try:
        balance = rpc_connection.batch_(commands)
        balance = 'Balance:%s'%balance[0]
    except:
        balance = 'Load Wallet Fail.'
    return balance

@app.route('/')
def index():
    return render_template('index.html',balance = get_balance(), userIP=request.remote_addr)

@app.route('/sendtoaddress', methods=['POST'])
def sendtoaddress():
    reCAPTCHA_data = {'secret':'6LcYNEUUAAAAAAlBF51pojGTGogSLPfySrbBgAeh','response':request.form['g-recaptcha-response'],'remoteip':request.remote_addr}
    try:
        if 'proxy=yes' in sys.argv:
            proxies = {'https':'http://127.0.0.1:1087','http':'http://127.0.0.1:1087'}
            r = post('https://www.google.com/recaptcha/api/siteverify',data=reCAPTCHA_data,proxies=proxies)
        else:
            r = post('https://www.google.com/recaptcha/api/siteverify',data=reCAPTCHA_data)
        if r.text[15] == 'f':
            err = 'Validation Fail.'
            return render_template('index.html',err = err, balance=get_balance(), userIP=request.remote_addr)
    except:
        err = 'Get validation result fail.Please try again.'
        return render_template('index.html',err = err, balance=get_balance(), userIP=request.remote_addr)

    addr = request.form['address']
    rpc_connection = connectRPC()
    commands = [['sendtoaddress', addr, '0.1']]
    try:
        txid = rpc_connection.batch_(commands)
        txid = 'txid:%s'%txid[0]
        count = 0.1
        data={'txid':txid, 'addr':addr, 'count':count}
        return render_template('index.html',data = data, balance=get_balance(), userIP=request.remote_addr)
    except:
        err = 'Invalid Address!'
        return render_template('index.html',err = err, balance=get_balance(), userIP=request.remote_addr)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # CHANGE_THIS
