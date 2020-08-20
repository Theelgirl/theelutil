# TheelUtil (fork of DueUtil at https://github.com/MacDue/DueUtil)
### The questing and fun discord bot!

#### Running the bot
(more detailed setup / install script later -- maybe)

Requirements:
* Python 3.8 + (may work on 3.5.4-3.7, but I haven't tried)
* The packages in requirements.txt (`pip install -r requirements.txt`)
* MongoDB  (https://docs.mongodb.com/manual/installation/)
* PHP & Apache (if you really want to run the site too)

##### Setup the DB
1. Install mongodb on your VPS: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
2. Enter the mongo shell by typing `mongo` into the command line.
3. Create an account that can create & update databases (admin will do):

2a.
```
use admin
```

2b.
```
db.createUser(
  {
    user: "dueutil",
    pwd: "<choose a secure one>",
    roles: [ { role: "root", db: "admin" } ]
  }
);
```

4. Put the account details in `dbconfig.json`

```json
{
    "host":"localhost",
    "user": "dueutil",
    "pwd": "<enter your password from 2b here>"
}
```
(the host will probably be localhost)

##### Configure TheelUtil
Create a file `dueutil.json` in the same folder as `run.py` (the root).
```json
{
   "botToken":"[DISCORD BOT TOKEN]",
   "owner":"[OWNER DISCORD ID]",
   "shardCount":1,
   "shardNames":[
      "Clone DueUtil: shard 1"
   ],
   "logChannel": "[SERVER ID]/[CHANNEL ID]",
   "errorChannel": "[SERVER ID]/[CHANNEL ID]",
   "feedbackChannel": "[SERVER ID]/[CHANNEL ID]",
   "bugChannel": "[SERVER ID]/[CHANNEL ID]",
   "announcementsChannel":"[SERVER ID]/[CHANNEL ID]",
   "carbonKey":"[https://www.carbonitex.net key you won't have]",
   "discordBotsOrgKey":"https://discordbots.org/ key you also won't have",
   "discordBotsKey": "https://bots.discord.pw/ key you also also won't have",
   "discoinKey":"http://discoin.sidetrip.xyz/ you will never get",
   "sentryAuth": "[SENTRY AUTH]"
}
```
The logging channels are currenly needed (the bot may not work properly without them), the bot probably can run without the other keys.

##### Restoring the database

1. Download the database dump from the last release (TheelUtil data coming soon)
2. Extract that zip into folder called `database`
    ```
    database
    `-- dueutil
        |-- award_stats.bson
        |-- award_stats.metadata.json
        |-- _CacheStats.bson
        ...
    ```
    Your file tree should look like this
 3. Use mongorestore
    ``mongorestore  --username your_use --password "your_pass" --authenticationDatabase admin ./database``

##### Run TheelUtil!

TheelUtil can be run from an open terminal with: `python3 run.py`.
To run it in the background, do:
1. `cd` (to get you to the home directory)
2. `cd /root/TheelUtil` (to put you inside the theelutil folder)
3. `chmod u+x ./start_fixed.sh` (the x lets you execute the start_fixed.sh file)`
4. `nohup /root/TheelUtil/start_fixed.sh &` (run it in the background, so you can close the terminal`

### Can't run the bot?!
If you're having any difficulties, contact me at Theelx#4980 and I'll try and help you.

### Contribute
No need to contribute, not even to clean up code. I'll be cleaning up code over the next few months, and I hope to release a cleaner version by the 3rd anniversary of the original PyDue's death in January 2021. 
