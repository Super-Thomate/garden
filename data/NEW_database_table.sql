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
CREATE TABLE IF NOT EXISTS birthday_config (bd_channel_id INT, message TEXT, timing INT, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_user (member_id INT NOT NULL, birthday TEXT NOT NULL, last_year INT, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
-- TURING
CREATE TABLE IF NOT EXISTS turing_config (log_channel_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
-- WELCOME
CREATE TABLE IF NOT EXISTS welcome_public (role_id INT NOT NULL, channel_id INT NOT NULL, message TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_private (role_id INT NOT NULL, message TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_user (role_id INT NOT NULL, member_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (role_id, member_id, guild_id)) ;
-- PWET
CREATE TABLE IF NOT EXISTS pwet_table (emoji_id INT, emoji_str TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
-- RULES
CREATE TABLE IF NOT EXISTS rules_config (log_channel_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_table (emoji_id INT, emoji_str TEXT NOT NULL, rule TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (emoji_str, guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_warned (emoji_id INT, emoji_str TEXT NOT NULL, message_id INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (emoji_str, message_id, guild_id)) ;
-- VOTE
CREATE TABLE IF NOT EXISTS vote_table (vote_channel_id INT NOT NULL, vote_message_id INT NOT NULL, vote_name TEXT NOT NULL, end_role_id INT NOT NULL, end_channel_id INT NOT NULL, ends_at INT, guild_id INT NOT NULL, PRIMARY KEY (vote_name, guild_id)) ;
CREATE TABLE IF NOT EXISTS vote_proposition (emoji_id INT, emoji_str TEXT NOT NULL, proposition TEXT NOT NULL, vote_name TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (emoji_str, vote_name, guild_id)) ;
-- NICKNAME
CREATE TABLE IF NOT EXISTS nickname_table (nickname_delay INT, warning_nickname TEXT, guild_id INT NOT NULL, PRIMARY KEY(guild_id)) ;
CREATE TABLE IF NOT EXISTS nickname_user (member_id INT NOT NULL, nickname TEXT NOT NULL, last_change INT, guild_id INT NOT NULL, PRIMARY KEY(member_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS nickname_warning (member_id INT NOT NULL, warn_at INT, warned BOOLEAN NOT NULL, guild_id INT NOT NULL, PRIMARY KEY(member_id, guild_id)) ;



