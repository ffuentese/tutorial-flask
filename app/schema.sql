drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

-- Comments

drop table if exists comments;
create table comments (
  id integer primary key autoincrement,
  name text not null,
  'text' text not null,
  entry_id integer not null,
  FOREIGN KEY(entry_id) REFERENCES entries(id)
);