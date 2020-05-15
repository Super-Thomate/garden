                                                             _       _                  
                                                            | |     (_)   ____    _ __  
                                                            | |     | |  / _//\  | '_ \ 
                                                            | |___  | | | (//) | | | | |
                                                            |_____| |_|  \//__/  |_| |_|

<!-- <img src="https://lion.fyi/lion_new.png" height="300" />-->

# Welcome to Liøn

Liøn is a Discord bot developed on [discord.py].  
It needs Python 3.8 and [Pipenv] to work.

# Installation and Run

First you need to install the virtual environment containing the python executable and dependencies. 
> pipenv install  

Then you'll have to create a `.env` file containing the project's environment variable.
**Do not push this file through VSC !**  
The `.env` file contains valuable informations about the project such as the bot's token, the path to the database 
and the name of the instance.  
Here's a default `.env` file :  
> INSTANCE=Lion  
DATABASE_PATH=Database_${INSTANCE}.db  
DATABASE_TABLE_PATH=data/database_table.sql  
LANGUAGE_FILE_PATH=data/language_files/  
BOT_ACTIVITY=Chewing Cables  
BOT_TOKEN=\<bot_token>  

The bot's token can be found in the bot section of your application in the [Discord Developer Portal]  
The last step is to actually run the bot using [Pipenv] as it automatically load the environment from the `.env` file:
> pipenv run lion

Which is an alias for `pipenv run "python Lion.py"`

# Working on the bot

So you are willing to work on Liøn eh ? I may know you or I may not.  
Anyway, you'll need to know how some of it's features work.  

## The database

Liøn uses **sqlite3**, a python basic module for simple database handling.  
The database is a `.db` file. It's name changes accordiing to the instance running.
The SQL statements handle two forms of parameter subsitution: `?` and `:name`.  

#### The `?` substitution

`?` works by passing a list to the function; each element of the list will 
replace a `?` in the SQL statement.  
> sql = "SELECT id FROM table WHERE firstname=? AND lastname=? ;"  
> fetch_one(sql, ['John', 'Doe'])  

Will replace the first `?` with **John** and the second `?` with **Doe**

#### The `:name` substitution

Useful when using the same element more than once.  
The `:name` substitution works by passing a *dict* to the function.  
Sqlite will then replace each occurence of each key by its value
> sql = "INSERT INTO table(id, firstname, lastname)  
>VALUES (:id, :fname, :lname)  
>ON CONFLICT(id) DO  
>UPDATE SET firstname=:fname, lastname=:lname WHERE id=:id ;"
>
> execute_order(sql, {'id': 42, 'fname': "John", 'lname': "Doe"})


## The Converters

[discord.py] proposes some [Discord Converters] used as type hints. 
It very practical to be sure to get what you want when a user writes a command.  
It's even possible to write [Custom Converters] (for example, they are used in the `Vote` cog).  
Here are some of the most used Converters in the program :  

### The [Message Converter]

`delete_message(ctx: command.Context, msg: discord.Message)`

Retrieve a **Message** object using three methods:

1. Lookup by “{channel ID}-{message ID}” (retrieved by shift-clicking on “Copy ID”)
2. Lookup by message ID (the message must be in the context channel)
3. Lookup by message URL

### The [Member Converter]

`ban_member(ctx: command.Context, member: discord.Member)`

Retrieve a **Member** object using five methods:

1. Lookup by ID.
2. Lookup by mention.
3. Lookup by name#discrim
4. Lookup by name
5. Lookup by nickname

### The [TextChannel Converter]

`set_log_channel(ctx: command.Context, channel: discord.TextChannel)`

Retrieve a **TextChannel** object using three methods:  

1. Lookup by ID.
2. Lookup by mention.
3. Lookup by name

### \[Custom] The EmojiOrUnicode Converter

`set_emoji(ctx: command.Context, emoji: utils.EmojiOrUnicodeConverter)`

Custom emoji converter that either retrieve an **Emoji** object or a string containing a Unicode emoji.  
Useful when you need to get and emoji that can be a server emoji (`<:RoF_ah:285095319086301184>`) or a simple Unicode emoji (`🐐`)

## The Special random format

The *special random format* allow to store a string in a special format. This format uses the following symbols :
> `{` : Indicate the beginning of the random part  
> `}` : Indicate the end of the random part  
> `|` : Separate the elements that are to be randomly chosen  
> `$member` : Is replaced by the **member_name** parameter of the _parse_string()_ function  

Example :  
> str = "Hello $member my {friend|enemy|Lord} !"  
> parsed = parse_string(str, member_name='John')  
> print(parsed)

Will randomly print :
> Hello John my friend !  
> Hello John my enemy !  
> Hello John my Lord !  


















[//]: #
   [discord.py]: <https://discordpy.readthedocs.io/en/latest/index.html>
   [Pipenv]: <https://pypi.org/project/pipenv/>
   [Discord Developer Portal]: <https://discord.com/developers/applications>
   [Discord Converters]: <https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#discord-converters>
   [Custom Converters]: <https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#advanced-converters>
   [Message Converter]: <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.MessageConverter>
   [Member Converter]: <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.MemberConverter>
   [TextChannel Converter]: <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.TextChannelConverter>