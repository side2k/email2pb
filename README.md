# Email 2 PushBullet

**Email to PushBullet notification**

This simple script allows to redirect mail input (from postfix, for example) to PushBullet notification. Useful to send pushes from sources which are able to send email only. It supports multipart emails with plaintext, html, and jpg parts. 

Note: This requires [pushbullet.py](https://github.com/rbrcsk/pushbullet.py).


## Example usage

Let's imagine that we want to redirect all emails sent to push@example.com to your PushBullet account (and therefore to your mobile devices, browser excensions, etc)
Keep in mind that instructions below were tested on Debian with Python 2.6 and Raspbian with Python 2.7. 

### Step 0: Setup and configure postfix for domain example.com and other prerequisites

[This tutorial](https://www.stewright.me/2012/09/tutorial-install-postfix-to-allow-outgoing-email-on-raspberry-pi/) is super short but a good place to get your feet wet if you are coming from nothing. 

[This tutorial](https://samhobbs.co.uk/2013/12/raspberry-pi-email-server-part-1-postfix) goes more in-depth. 

### Step 1: Create shell script

First, create shell script which will contain the email2pb call with any arguments you woud like. This is needed so the API key is not saved in the repository. 

Let's name it `/var/spool/postfix/email2pb/email2pb`.

Why there? Tested in Debian and Raspbian, and postfix's home dir is /var/spool/postfix.
Rememer, postfix should be able to acces your script.

The script will be something like this:

```
#!/bin/sh
/usr/bin/python /var/spool/postfix/email2pb/email2pb.py --key YOUR_PUSHBULLET_API_KEY --log_level 10 --log_file "/var/spool/postfix/email2pb/email2pb.log"
```
Feel free to change/remove `log_level` or `log_file` as needed.

Make the script executable:

```
chmod +x /var/spool/postfix/email2pb/email2pb
```

Make the log file writeable:

```
chmod +w /var/spool/postfix/email2pb/email2pb.log
```


### Step 2: Add mail alias

Open /etc/aliases file and append a line there:

```
push: |/var/spool/postfix/email2pb/email2pb
```
Save the file and execute `newaliases` command.


### Step 3: Test it

Send email to push@example.com and, if it didn't work, check /var/log/mail.log. If it did work you should receieve the push. 

That's it.
