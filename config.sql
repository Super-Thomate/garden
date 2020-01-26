drop table config_role ;
drop table config_prefix ;
drop table config_url ;
drop table config_delay ;
drop table config_do ;
drop table config_log ;

-- CREATE TABLE IF NOT EXISTS `config_role` (`role_id` VARCHAR(256) NOT NULL,`permission` INT NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`role_id`)) ;
-- CREATE TABLE IF NOT EXISTS `config_prefix` (`prefix` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`prefix`, `guild_id`)) ;
-- CREATE TABLE IF NOT EXISTS `config_url` (`url` VARCHAR(512) NOT NULL, `type_url` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_url`, `guild_id`)) ;
-- CREATE TABLE IF NOT EXISTS `config_delay` (`delay` INTEGER NOT NULL, `type_delay` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_delay`, `guild_id`)) ;
-- CREATE TABLE IF NOT EXISTS `config_do` (`do` INTEGER NOT NULL, `type_do` VARCHAR(128) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`type_delay`, `guild_id`)) ;
-- CREATE TABLE IF NOT EXISTS `config_log` (`channel_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`)) ;

-- , "494812563016777729":{"roles":["ModoBot","Bénévoles","Modosdudiscord","Fondateur-admin","Pèsedanslegame","Modosstagiaires","Touristesbienveillant.e.s","Equipedelaplateforme"],"prefixes":["!","?","-"],"create_url":{"invitation":"https://admin.realms-of-fantasy.net/bot.php","gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"},"invite_delay":"6 months","do_invite":1,"do_token":0,"nickname_delay":"1 week"}
-- , "228638115928080386":{"roles":["Responsables", 598129943125164063],"prefixes":["!","?","-"],"create_url":{"invitation":"https://admin.realms-of-fantasy.net/bot.php","gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"},"invite_delay":"6 months","do_invite":1,"do_token":0,"nickname_delay":"1 week"}
--  , "283243816448819200":{"roles":[580062847900450867,283247966490460160,283245747694993410,507978584342659082],"prefixes":["!","?","-"],"create_url":{"invitation":"https://admin.realms-of-fantasy.net/bot.php","gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"},"invite_delay":"6 months","do_invite":1,"do_token":0,"nickname_delay":"1 week"}
-- SUF 283243816448819200
-- AR 415598765873954836
-- ROF 228638115928080386
-- FI 494812563016777729
-- LION
insert into config_role
(`role_id` ,`permission` , `guild_id` )
values
  ('580062847900450867', 1, '283243816448819200')
, ('283247966490460160', 1, '283243816448819200')
, ('283245747694993410', 1, '283243816448819200')
, ('507978584342659082', 1, '283243816448819200')
, ('598129943125164063', 1, '228638115928080386')
;
insert into config_prefix
(`prefix`, `guild_id` )
values
  ('!', '283243816448819200')-
, ('?', '283243816448819200')
, ('-', '283243816448819200')
, ('!', '228638115928080386')
, ('?', '228638115928080386')
, ('-', '228638115928080386')
, ('!', '494812563016777729')
, ('?', '494812563016777729')
, ('-', '494812563016777729')
;
insert into config_url
(`url`, `type_url` , `guild_id` )
values
  ('https://admin.realms-of-fantasy.net/bot.php', 'invite', '283243816448819200')
, ('https://admin.realms-of-fantasy.net/bot.php', 'invite', '228638115928080386')
, ('https://admin.realms-of-fantasy.net/bot.php', 'invite', '494812563016777729')
;
insert into config_delay
(`url`, `type_url` , `guild_id` )
values
  (15552000, 'invite', '283243816448819200')
, (1209600, 'nickanme', '283243816448819200')
, (1209600, 'nickanme', '494812563016777729')
, (15552000, 'invite', '228638115928080386')
, (15552000, 'invite', '494812563016777729')
;
insert into config_do
(`do`, `type_do` , `guild_id` )
values
  (1, 'invite', '283243816448819200')
, (1, 'invite', '228638115928080386')
, (1, 'invite', '494812563016777729')
;
-- LOTUS BLANC
insert into config_role
(`role_id` ,`permission` , `guild_id` )
values
  ('580062847900450867', 1, '415598765873954836')
, ('283247966490460160', 1, '415598765873954836')
, ('283245747694993410', 1, '415598765873954836')
, ('507978584342659082', 1, '415598765873954836')
, ('598129943125164063', 1, '228638115928080386')
;
insert into config_prefix
(`prefix`, `guild_id` )
values
  ('!', '415598765873954836')-
, ('?', '415598765873954836')
, ('-', '415598765873954836')
, ('!', '228638115928080386')
, ('?', '228638115928080386')
, ('-', '228638115928080386')
, ('!', '494812563016777729')
, ('?', '494812563016777729')
, ('-', '494812563016777729')
;
insert into config_url
(`url`, `type_url` , `guild_id` )
values
  ('https://admin.realms-of-fantasy.net/bot-AR.php?', 'invite', '415598765873954836')
, ('https://admin.realms-of-fantasy.net/bot-AR.php?', 'invite', '228638115928080386')
, ('https://admin.realms-of-fantasy.net/bot-AR.php?', 'invite', '494812563016777729')
;
insert into config_delay
(`url`, `type_url` , `guild_id` )
values
  (1209600, 'nickanme', '415598765873954836')
, (1209600, 'nickanme', '494812563016777729')
;
insert into config_do
(`do`, `type_do` , `guild_id` )
values
  (1, 'token', '415598765873954836')
, (1, 'token', '228638115928080386')
, (1, 'token', '494812563016777729')
;

