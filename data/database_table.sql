-- BANCOMMAND
CREATE TABLE IF NOT EXISTS ban_command_role (command VARCHAR(256) NOT NULL, until INTEGER, role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (command, role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS ban_command_role_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS ban_command_user (command VARCHAR(256) NOT NULL, until INTEGER, user_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (command, user_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS ban_command_user_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- BIRTHDAY
CREATE TABLE IF NOT EXISTS birthday_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_message (message TEXT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_time(time VARCHAR(32) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS birthday_user(user_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, user_birthday VARCHAR(5), last_year_wished VARCHAR(4), PRIMARY KEY (user_id, guild_id)) ;
-- CONFIGURATION
CREATE TABLE IF NOT EXISTS config_cog (cog varchar(256) not null, guild_id int not null, status int not null, primary key (cog, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_delay (delay INTEGER NOT NULL, type_delay VARCHAR(128) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (type_delay, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_do(do INTEGER NOT NULL, type_do VARCHAR(128) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (type_do, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_lang(language_code VARCHAR(2) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS config_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS config_prefix(prefix VARCHAR(64) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (prefix, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_role(role_id VARCHAR(256) NOT NULL,permission INT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id)) ;
CREATE TABLE IF NOT EXISTS config_url (url VARCHAR(512) NOT NULL, type_url VARCHAR(128) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (type_url, guild_id)) ;
-- GALLERY
CREATE TABLE IF NOT EXISTS galerie_channel(channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS galerie_log(channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS galerie_message(message TEXT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- INVITATION
CREATE TABLE IF NOT EXISTS invite_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS invite_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS invite_message (message TEXT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS last_invite (member_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, last DATETIME NOT NULL, PRIMARY KEY (member_id, guild_id)) ;
-- NICKNAME
CREATE TABLE IF NOT EXISTS last_nickname (member_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, last_change DATETIME NOT NULL, PRIMARY KEY (member_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS nickname_current (member_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, nickname VARCHAR(128) NOT NULL, PRIMARY KEY (member_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS nickname_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- PWET
CREATE TABLE IF NOT EXISTS pwet_reaction (emoji_text VARCHAR(64), emoji_id VARCHAR(64), guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- ROLEDM
CREATE TABLE IF NOT EXISTS roledm_message (message TEXT NOT NULL,role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS roledm_role (role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
-- RULES
CREATE TABLE IF NOT EXISTS rules_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_message (message_id TEXT NOT NULL, emoji_text VARCHAR(64) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (message_id, emoji_text, guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_table (rule TEXT NOT NULL, emoji_text VARCHAR(64) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (emoji_text, guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_table (rule TEXT NOT NULL, emoji_text VARCHAR(64), emoji_id VARCHAR(64), guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (emoji_text, emoji_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS rules_table (rule TEXT NOT NULL, emoji_text VARCHAR(64), emoji_id VARCHAR(64), guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (emoji_text, emoji_id, guild_id)) ;
-- SOURCE
CREATE TABLE IF NOT EXISTS source_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (channel_id)) ;
CREATE TABLE IF NOT EXISTS source_domain (domain VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (domain, guild_id)) ;
CREATE TABLE IF NOT EXISTS source_message (message TEXT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- TURING
CREATE TABLE IF NOT EXISTS spy_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- TIMER
CREATE TABLE IF NOT EXISTS timer_emoji (emoji VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS timer_end_message (end_message VARCHAR(512) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS timer_first_emoji (emoji VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
-- UTIP
CREATE TABLE IF NOT EXISTS utip_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_message (message TEXT NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_role (role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_timer (user_id VARCHAR(256) NOT NULL, until INTEGER NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (user_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS utip_waiting (user_id VARCHAR(256) NOT NULL, status INTEGER NOT NULL, message_id VARCHAR(256) NOT NULL, valid_by VARCHAR(256), valid_at INTEGER, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (message_id)) ;
-- VOTE
CREATE TABLE IF NOT EXISTS vote_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS vote_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS vote_message (message_id VARCHAR(256) NOT NULL, channel_id VARCHAR(256) NOT NULL, month VARCHAR(2) NOT NULL, year VARCHAR(4) NOT NULL, closed INT NOT NULL default 0, author_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, vote_type VARCHAR(256) NOT NULL, PRIMARY KEY (message_id)) ;
CREATE TABLE IF NOT EXISTS vote_propositions (proposition VARCHAR(512) NOT NULL,emoji VARCHAR(256) NOT NULL, proposition_id INTEGER NOT NULL, author_id VARCHAR(256) NOT NULL, message_id VARCHAR(256) NOT NULL, ballot INTEGER NOT NULL DEFAULT 0) ;
CREATE TABLE IF NOT EXISTS vote_role (role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS vote_time (message_id VARCHAR(256) NOT NULL, started_at INTEGER, proposition_ended_at INTEGER, edit_ended_at INTEGER, vote_ended_at INTEGER, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (message_id)) ;
-- WELCOME
CREATE TABLE IF NOT EXISTS welcome_channel (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_log (channel_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_message (message TEXT NOT NULL, role_id integer not null, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_role (role_id VARCHAR(256) NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS welcome_user (user_id VARCHAR(256) NOT NULL, role_id integer not null, welcomed_at INTEGER NOT NULL, guild_id VARCHAR(256) NOT NULL, PRIMARY KEY (user_id, role_id, guild_id)) ;