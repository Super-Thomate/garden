
       _____               _            
      / ____|             | |           
     | |  __  __ _ _ __ __| | ___ _ __  
     | | |_ |/ _` | '__/ _` |/ _ \ '_ \
     | |__| | (_| | | | (_| |  __/ | | |
      \_____|\__,_|_|  \__,_|\___|_| |_|



Garden is a multifunction bot designed for Realms of Fantasy.
This bot needs Python 3.5.3 or higher.
API doc : <https://discordpy.readthedocs.io/en/latest/>

# Installation

```
python3 -m pip install -U -r requirements.txt
```

# Launch Garden

Garden expects an instance name, which is linked to a bot's token in `config.json`.
To launch Garden you must run in command line:
`/usr/bin/python3 /home/garden/bot.py :instance:`
You must replace `/home/garden/` with the actual path to Garden's directory.

# Initialization

In order to initialize Garden, you must load cogs using
```
<p>load cogs_name
```
Where `<p>` is your prefix and `cogs_name` is a valid cog's name.

Prefixes can be set in `config.json` (an example is provided).

# Autostart Garden using systemd on Linux
Create a new service file:
`/etc/systemd/system/garden@.service`

Paste the following and replace all instances of `:username:` with the username your bot is running under (hopefully not root):

```
    [Unit]
    Description=Garden bot for %I
    After=multi-user.target

    [Service]
    ExecStart=/usr/bin/python3 /home/garden/bot.py %I
    User=:username:
    Group=:username:
    Type=idle
    Restart=always
    RestartSec=15
    RestartPreventExitStatus=0
    TimeoutStopSec=10

    [Install]
    WantedBy=multi-user.target
```
You must replace `/home/garden/` with the actual path to Garden's directory.
This same file can be used to start as many instances of the bot as you wish, without creating more service files, just start and enable more services and add any bot instance name after the **@**

To start the bot, run the service and add the instance name after the **@**:
`sudo systemctl start garden@instancename`

To set the bot to start on boot, you must enable the service, again adding the instance name after the **@**:
`sudo systemctl enable garden@instancename`

To stop the bot, run the following command still by adding the instance name after the **@**:
`sudo systemctl stop garden@instancename`

To view Garden's log, you can acccess through journalctl:
`sudo journalctl -u garden@instancename`