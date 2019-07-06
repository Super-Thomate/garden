import os
import sqlite3

class Database:
  def __init__ (self):
    self.cnx = sqlite3.connect('garden.db')
    self.create_table()
  def test(self, mot):
    print ("You said : "+mot)
  def create_table(self):
    cursor = self.cnx.cursor()
    try:
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `last_invite` (`member_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, last DATETIME NOT NULL, PRIMARY KEY (`member_id`, `guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `galerie_channel` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      cursor.execute('CREATE TABLE IF NOT EXISTS `invite_message` (`message` TEXT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;')
      # Save modifications
      self.cnx.commit()
      cursor.close()
    except Exception as e:
      cursor.close()
      print (f'ERROR: {type(e).__name__} - {e}')

  def execute_order (self, sql):
    cursor = self.cnx.cursor()
    try:
      cursor.execute(sql)
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
