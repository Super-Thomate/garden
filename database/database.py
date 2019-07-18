import sqlite3
import sys
import os


class Database:
  def __init__ (self):
    # get the path to project root
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
    print (dir_path)
    self.cnx = sqlite3.connect(dir_path+'../garden.db')
    self.create_table()

  def create_table(self):
    cursor = self.cnx.cursor()
    try:
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `last_invite` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `last_nickname` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, `last_change` DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `nickname_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_propositions` (`proposition` VARCHAR(512) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_colors` (`color` VARCHAR(6) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `vote_message` (`message_id` VARCHAR(256) NOT NULL, `channel_id` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`, `month`, `year`)) ;')
      # Save modifications
      self.cnx.commit()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')

  def execute_order (self, sql, params):
    cursor = self.cnx.cursor()
    print (f"params: {params}")
    try:
      cursor.execute(sql, (params))
      self.cnx.commit()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')

  def fetch_one_line (self, sql):
    cursor = self.cnx.cursor()
    line = None
    try:
      cursor.execute(sql)
      line = cursor.fetchone()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')
    return line
