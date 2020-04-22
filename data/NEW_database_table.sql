-- CONFIGURATION
CREATE TABLE IF NOT EXISTS config_lang (language_code TEXT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (guild_id)) ;
CREATE TABLE IF NOT EXISTS config_cog (cog_name TEXT NOT NULL, status BOOLEAN NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (cog_name, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_role (role_id INT NOT NULL, permission INT NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_command_banned_role (command TEXT NOT NULL, ends_at INTEGER, role_id INTEGER NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (command, role_id, guild_id)) ;
CREATE TABLE IF NOT EXISTS config_command_banned_user (command TEXT NOT NULL, ends_at INTEGER, member_id INTEGER NOT NULL, guild_id INT NOT NULL, PRIMARY KEY (command, member_id, guild_id)) ;