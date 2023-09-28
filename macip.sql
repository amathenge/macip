drop table if exists macip;

create table macip (
    position integer,
    ip varchar(32),
    mac varchar(32),
    machine varchar(64),
    manufacturer varchar(64)
);

drop table if exists log;

create table log (
    id integer primary key autoincrement,
    logtime datetime
);

