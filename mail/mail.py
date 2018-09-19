#!/usr/bin/python

import sys
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

def connect(host, port, tls = False):
    '''
    connect to smtp host, if succeed in 10 seconds, return a smtp object, otherwise Throw an Error and exit

    Arguments:
    host -- mail server host
    port -- connect port

    Returns:
    (status,description,smtp) -- send mail status, description of this operation, smtp object
    '''
    try:
        smtp = smtplib.SMTP(host,port,None,10)
    except BaseException,e:
        sys.stderr.write('*** CONNECT FAILURE ***\n%s\n'%str(e))
        return [False,str(e),None]
    else:
        if tls:
            smtp.starttls()
        return [True,None,smtp]
##-- test for connect --
#smtp = connect('smtp.office35.com',587)
#smtp = connect('smtp.office365.com', 587, True)
#-- end of test --

def login(smtp, user, password):
    '''
    login mail server with specify user and password

    Arguments:
    smtp -- smtp object
    user -- user name
    password -- password

    Returns:
    (status,description) -- send mail status, description of this operation
    '''
    try:
        smtp.login(user, password)
    except BaseException,e:
        sys.stderr.write('*** LOGIN FAILURE ***\n%s\n'%str(e))
        return (False,str(e))
    else:
        return (True,None)
##-- test for login --
#login(smtp,'chenshihong@genomics.cn','qwerty123456!')
#-- end of test --

def sendmail(smtp, from_addr, to_addrs, msg, mail_options=[], rcpt_options=[]):
    '''
    send mail by calling smtp.sendmail
    
    Arguments:
    smtp -- smtp object
    from_addr -- sender address
    to_addrs -- recipient addresses
    msg -- mail body text, should format by email
    mail_options -- mail options
    rcpt_options -- recept options

    Returns:
    (status,description) -- send mail status, description of this operation
    '''
    try:
        smtp.sendmail(from_addr, to_addrs, msg, mail_options, rcpt_options)
    except BaseException,e:
        sys.stderr.write('*** LOGIN FAILURE ***\n%s\n'%str(e))
        return (False,str(e))
    else:
        return (True,None)


def _format_addr(s):
    '''
    format e-mail address,
    if addr contains some chinese character, call this function make it display normally
    otherwise, using addr directly is okay

    Arguments:
    s -- address, should format as username<address@serveer.com> or only address.

    Returns:
    name,addr -- user name, address
    '''
    name,addr = parseaddr(s)
    return formataddr((Header(name,'utf-8').encode(), addr.encode('utf-8') if isinstance(addr,unicode) else addr))
## -- test for __format_addr
#print __format_addr('chenshihong<chenshihong@genimics.cn>')
#print __format_addr('chenshihong<chenshihong@genimics.cn>,chenshihong<chenshihong@genimics.cn>')
#-- end of test

def c_msg(From, To_s, subject, main_text, method = 'plain', attachments = []):
    '''
    construct a message for mail

    Arguments:
    From -- sender address
    To_s -- recipients addresses
    subject -- subject of this mail
    main_text -- mail body, a list of string, 0 => plain text, 1=> html text
    method -- mail format method, avaiable values => [plain, html, alternative]
    attachments --  attachment files list, each file is described as a tuple (path,type,format)

    Returns:
    msg -- mail message
    '''
    msg = None
    if method == 'alternative' or len(attachments) != 0:
        if method == 'alternative':
            msg = MIMEMultipart('alternative')
            msg.attach(MIMIText(main_text[0],'plain','utf-8'))
            msg.attach(MIMIText(main_text[1],'html','utf-8'))
        else:
            msg = MIMEMultipart()
    else:
        msg = MIMEText(main_text[0],method,'utf-8')
    msg['From'] = _format_addr(From)
    to_addr = ''
    for addr in To_s:
        if to_addr == '':
            to_addr += _format_addr(addr)
        else:
            to_addr += ','+_format_addr(addr)
    msg['To'] = to_addr
    msg['Subject'] = Header(subject,'utf-8').encode()
    
    for i in range(len(attachments)):
        pth,tp,fm = attachments[i]
        try:
            fhandle = open(pth,'rb')
        except:
            sys.stderr.write('Can\'t open %s\n'%pth)
            return None
        mime = MIMEBase(tp,fm,filename=fn)
        mime.add_header('Content-Disposition','attachment',filename=fn)
        mime.add_header('Content-ID','<'+str(i)+'>')
        mime.add_header('X-Attachment-Id',str(i))

        mime.set_payload(fhandle.read())

        encoders.encode_base64(mime)
        msg.attach(mime)
        fhandle.close()
    return msg

if __name__ == '__main__':
    print "connect to server ..."
    #server = connect('smtp.office365.com', 587, True)
    server = connect('smtp.genomics.cn', 587, True)
    if not server[0]:
        exit(159)
    print "login ..."
    #(s,d) = login(server[2],'chenshihong@genomics.cn','qwerty123456!')
    (s,d) = login(server[2],'bgi-Biosyn@genomics.cn','Synbio123456')
    print (s,d)
    if not s:
        exit(162)
    print "sending test mail ..."
    msg = c_msg('Administrator<bgi-Biosyn@genomics.cn>',['Shihong Chen<chenshihong@genomics.cn>'],'Test for sending email from python',['As the subject',None],'plain',[])
    print msg
    sendmail(server[2],'bgi-Biosyn@genomics.cn',['chenshihong@genomics.cn'],msg.as_string())
    server[2].quit()

