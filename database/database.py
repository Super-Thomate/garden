import os
import sqlite3
import sys
from core import logger

# get the path to project root
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
instance = sys.argv[1]
if not instance:
  path = dir_path + '../garden.db'
else:
  path = dir_path + '../garden_' + instance + '.db'
logger ("database", f"Database path: {path}")


def create_table():
  cnx = sqlite3.connect(path)
  cursor = cnx.cursor()
  try:
    ### INVITATION COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `invite_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `last_invite` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `invite_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `invite_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `galerie_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `galerie_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `galerie_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    ### NICKNAME COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `last_nickname` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last_change` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `nickname_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `nickname_current` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `nickname` VARCHAR(128) NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
    ### VOTE COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    # alter table vote_propositions add `ballot` integer not null default 0 ;
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_propositions` (`proposition` VARCHAR(512) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `proposition_id` INTEGER NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `ballot` INTEGER NOT NULL DEFAULT 0) ;')
    # cursor.execute('CREATE TABLE IF NOT EXISTS `vote_colors` (`color` VARCHAR(6) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_message` (`message_id` VARCHAR(256) NOT NULL, `channel_id` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `closed` INT NOT NULL default 0, `author_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `vote_type` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`)) ;')
    # alter table vote_time add `edit_ended_at` INTEGER ;
    # alter table vote_time rename `vote_closed_at` to `vote_ended_at` ;
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_time` (`message_id` VARCHAR(256) NOT NULL, `started_at` INTEGER, `proposition_ended_at` INTEGER, `edit_ended_at` INTEGER, `vote_ended_at` INTEGER, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `vote_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    ### WELCOME COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `welcome_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `welcome_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `welcome_message` (`message` TEXT NOT NULL, `role_id` integer not null, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
    """
    alter table welcome_message add `role_id` INTEGER not null default 0 ;
    alter table `welcome_message` rename to zob ;
    CREATE TABLE IF NOT EXISTS `welcome_message` (`message` TEXT NOT NULL, `role_id` integer not null, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;
    insert into welcome_message select message,role_id,guild_id from zob ;
    drop table zob ;
    """
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `welcome_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
    """
    alter table `welcome_role` rename to zob ;
    CREATE TABLE IF NOT EXISTS `welcome_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;
    insert into welcome_role select * from zob ;
    drop table zob ;
    """
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `welcome_user` (`user_id` VARCHAR(256) NOT NULL, `role_id` integer not null, `welcomed_at` INTEGER NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`user_id`, `role_id`, `guild_id`)) ;')
    """
    alter table welcome_user add `role_id` INTEGER not null default 0 ;
    alter table welcome_user rename to welcome_user_old ;
    CREATE TABLE IF NOT EXISTS `welcome_user` (`user_id` VARCHAR(256) NOT NULL, `role_id` integer not null, `welcomed_at` INTEGER NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`user_id`, `role_id`, `guild_id`)) ;
    INSERT INTO welcome_user SELECT `user_id`,`role_id`,`welcomed_at`,`guild_id` FROM welcome_user_old;
    drop table welcome_user_old ;
    """
    ### BANCOMMAND COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `ban_command_user_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `ban_command_user` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `user_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `ban_command_role_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `ban_command_role` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `role_id`, `guild_id`)) ;')
    ### ROLEDM COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `roledm_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `roledm_message` (`message` TEXT NOT NULL,`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
    ### SPY
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `spy_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    ### CONFIG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_role` (`role_id` VARCHAR(256) NOT NULL,`permission` INT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_prefix` (`prefix` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`prefix`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_url` (`url` VARCHAR(512) NOT NULL, `type_url` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_url`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_delay` (`delay` INTEGER NOT NULL, `type_delay` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_delay`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_do` (`do` INTEGER NOT NULL, `type_do` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_do`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_lang` (`language_code` VARCHAR(2) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `config_cog` (`cog` varchar(256) not null, `guild_id` int not null, `status` int not null, primary key (`cog`, `guild_id`)) ;')
    # UTIP COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_timer` (`user_id` VARCHAR(256) NOT NULL, `until` INTEGER NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`user_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_waiting` (`user_id` VARCHAR(256) NOT NULL, `status` INTEGER NOT NULL, `message_id` VARCHAR(256) NOT NULL, `valid_by` VARCHAR(256), `valid_at` INTEGER, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `utip_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    ### BIRTHDAY COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `birthday_user` (`user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `user_birthday` VARCHAR(5), `last_year_wished` VARCHAR(4), PRIMARY KEY (`user_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `birthday_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `birthday_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `birthday_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    ### SOURCE COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `source_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`channel_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `source_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `source_domain` (`domain` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`domain`, `guild_id`)) ;')
    ### RULES COG
    """
    alter table `rules_table` rename to zob ;
    CREATE TABLE IF NOT EXISTS `rules_table` (`rule` TEXT NOT NULL, `emoji_text` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`emoji_text`, `guild_id`)) ;
    insert into rules_table select rule,emoji_text,guild_id from zob ;
    drop table zob ;
    """
    """
    alter table `rules_table` rename to zob ;
    CREATE TABLE IF NOT EXISTS `rules_table` (`rule` TEXT NOT NULL, `emoji_text` VARCHAR(64), `emoji_id` VARCHAR(64), `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`emoji_text`, `emoji_id`, `guild_id`)) ;
    insert into rules_table (rule, emoji_text, guild_id) select rule,emoji_text,guild_id from zob ;
    drop table zob ;
    """
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `rules_table` (`rule` TEXT NOT NULL, `emoji_text` VARCHAR(64), `emoji_id` VARCHAR(64), `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`emoji_text`, `emoji_id`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `rules_message` (`message_id` TEXT NOT NULL, `emoji_text` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`, `emoji_text`, `guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `rules_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `pwet_reaction` (`emoji_text` VARCHAR(64), `emoji_id` VARCHAR(64), `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    
    ### Timer COG
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `timer_emoji` (`emoji` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `timer_end_message` (`end_message` VARCHAR(512) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    cursor.execute(
      'CREATE TABLE IF NOT EXISTS `timer_first_emoji` (`emoji` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
    # Save modifications
    cnx.commit()
    cursor.close()
  except Exception as e:
    cursor.close()
    print(f'ERROR: {type(e).__name__} - {e}')
  cnx.close()


def execute_order(sql, params=[]):
  cnx = sqlite3.connect(path)
  cursor = cnx.cursor()
  print(f"execute_order params: {params}")
  try:
    cursor.execute(sql, (params))
    cnx.commit()
    cursor.close()
  except Exception as e:
    cursor.close()
    print(f'execute_order ERROR: {type(e).__name__} - {e}')
    print(f'execute_order sql: {sql}')
  cnx.close()


def fetch_one_line(sql, params=[]):
  cnx = sqlite3.connect(path)
  cursor = cnx.cursor()
  line = None
  try:
    cursor.execute(sql, (params))
    line = cursor.fetchone()
    cursor.close()
  except Exception as e:
    cursor.close()
    print(f'fetch_one_line ERROR: {type(e).__name__} - {e}')
    print(f'fetch_one_line sql: {sql}')
  cnx.close()
  return line


def fetch_all_line(sql, params=[]):
  cnx = sqlite3.connect(path)
  cursor = cnx.cursor()
  lines = None
  try:
    cursor.execute(sql, (params))
    lines = cursor.fetchall()
    cursor.close()
  except Exception as e:
    cursor.close()
    print(f'fetch_all_line ERROR: {type(e).__name__} - {e} in \n{sql}')
  cnx.close()
  return lines


create_table()
