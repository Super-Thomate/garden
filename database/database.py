import sqlite3
import sys
import os


class Database:
  def __init__ (self):
    # get the path to project root
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
    instance = sys.argv[1]
    if not instance:
      #self.cnx = sqlite3.connect(dir_path+'../garden.db')
      self.path = dir_path+'../garden.db'
    else:
      #self.cnx = sqlite3.connect(dir_path+'../garden_'+instance+'.db')
      self.path = dir_path+'../garden_'+instance+'.db'
    print (self.path)
    self.create_table()

  def create_table(self):
    cnx = sqlite3.connect (self.path)
    cursor = cnx.cursor()
    try:
      ### INVITATION COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `last_invite` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      ### NICKNAME COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `last_nickname` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last_change` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `nickname_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `nickname_current` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `nickname` VARCHAR(128) NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      ### VOTE COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      # alter table vote_propositions add `ballot` integer not null default 0 ;
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_propositions` (`proposition` VARCHAR(512) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `proposition_id` INTEGER NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `ballot` INTEGER NOT NULL DEFAULT 0) ;')
      #cursor.execute('CREATE TABLE IF NOT EXISTS `vote_colors` (`color` VARCHAR(6) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_message` (`message_id` VARCHAR(256) NOT NULL, `channel_id` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `closed` INT NOT NULL default 0, `author_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `vote_type` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`)) ;')
      # alter table vote_time add `edit_ended_at` INTEGER ;
      # alter table vote_time rename `vote_closed_at` to `vote_ended_at` ;
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_time` (`message_id` VARCHAR(256) NOT NULL, `started_at` INTEGER, `proposition_ended_at` INTEGER, `edit_ended_at` INTEGER, `vote_ended_at` INTEGER, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      ### WELCOME COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `welcome_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `welcome_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `welcome_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `welcome_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `welcome_user` (`user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `welcomed_at` INTEGER NOT NULL, PRIMARY KEY (`user_id`, `guild_id`)) ;')
      # alter table welcome_user rename to welcome_user_old ;
      # CREATE TABLE IF NOT EXISTS `welcome_user` (`user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `welcomed_at` INTEGER NOT NULL, PRIMARY KEY (`user_id`, `guild_id`)) ;
      # INSERT INTO welcome_user SELECT * FROM welcome_user_old;
      ### BANCOMMAND COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `ban_command_user_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `ban_command_user` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `user_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `ban_command_role_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`))  ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `ban_command_role` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `role_id`, `guild_id`)) ;')
      ### ROLEDM COG
      cursor.execute('CREATE TABLE IF NOT EXISTS `roledm_role` (`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `roledm_message` (`message` TEXT NOT NULL,`role_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`, `guild_id`)) ;')
      ### SPY 
      cursor.execute('CREATE TABLE IF NOT EXISTS `spy_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      ### CONFIG
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_role` (`role_id` VARCHAR(256) NOT NULL,`permission` INT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_prefix` (`prefix` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`prefix`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_url` (`url` VARCHAR(512) NOT NULL, `type_url` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_url`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_delay` (`delay` INTEGER NOT NULL, `type_delay` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_delay`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_do` (`do` INTEGER NOT NULL, `type_do` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_delay`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `config_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      # Save modifications
      cnx.commit()
      cursor.close()

    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')
    cnx.close()

  def execute_order (self, sql, params=[]):
    cnx = sqlite3.connect (self.path)
    cursor = cnx.cursor()
    print (f"params: {params}")
    try:
      cursor.execute(sql, (params))
      cnx.commit()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')
    cnx.close()

  def fetch_one_line (self, sql, params=[]):
    cnx = sqlite3.connect (self.path)
    cursor = cnx.cursor()
    line = None
    try:
      cursor.execute(sql, (params))
      line = cursor.fetchone()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')
    cnx.close()
    return line

  def fetch_all_line (self, sql):
    cnx = sqlite3.connect (self.path)
    cursor = cnx.cursor()
    lines = None
    try:
      cursor.execute(sql)
      lines = cursor.fetchall()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')
    cnx.close()
    return lines
