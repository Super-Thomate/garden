-- CONFIGURATION
CREATE TABLE IF NOT EXISTS config_lang (language_code TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS config_cog (cog_name TEXT NOT NULL, status BOOLEAN NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (cog_name, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_role (role_id INT NOT NULL, permission INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_prefix (prefix TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (prefix, guild_id)) ;
-- BANCOMMAND
CREATE TABLE IF NOT EXISTS bancommand_banned_user (command TEXT NOT NULL, ends_at INT, member_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (command, member_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS bancommand_banned_role (command TEXT NOT NULL, ends_at INT, role_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (command, role_id, guild_id)) ;
-- UTIP
CREATE TABLE IF NOT EXISTS utip_config (mod_channel_id INT, log_channel_id INT, role_id INT, delay INT, guild_id INT NOT NULL, PRIMARY KEY(guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_pending (member_id INT NOT NULL, message_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (message_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_timer (member_id INT NOT NULL, ends_at INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (member_id, guild_id)) ;
-- BIRTHDAY
CREATE TABLE IF NOT EXISTS birthday_config (bd_channel_id INT, message TEXT, timing INT, guild_id NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_user (member_id INT NOT NULL, birthday TEXT NOT NULL, last_year INT, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;