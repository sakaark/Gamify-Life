CREATE TYPE HTYPE AS ENUM ('daily', 'weekly', 'monthly');

create table Users(
  username varchar(20) not null,
  uname varchar(30) not null,
  password varchar(20) not null,

  primary key(username)
);

create table LoginStatus(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  loggedin boolean not null default false,

  primary key(username)
);

create table Activity(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  nickname varchar(20) not null,
  aname TEXT not null,
  default_qty real not null default 0,
  active boolean not null default true,
  disuse boolean not null default false,

  primary key(username, nickname)
);

create table IntervalActivity(
  username varchar(20) not null,
  nickname varchar(20) not null,
  qty_start real not null default 0,
  qty_end real not null default 0,
  pts real not null default 0,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  primary key(username, nickname, qty_start),
  check(qty_start <= qty_end)
);

create table ScaleQtyActivity(
  username varchar(20) not null,
  nickname varchar(20) not null,
  qty real not null default 0,
  pts real not null default 0,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  primary key(username, nickname)
);

create table YesNoActivity(
  username varchar(20) not null,
  nickname varchar(20) not null,
  yes_pts real not null default 0,
  no_pts real not null default 0,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  primary key(username, nickname)
);

create table Record(
  username varchar(20) not null,
  nickname varchar(20) not null,
  adate date not null,
  qty real not null default 0,
  
  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  primary key(username, nickname, adate)
);

create table Habit(
  username varchar(20) not null,
  nickname varchar(20) not null,
  hname varchar(20) not null,
  start_date date not null,
  habit_type HTYPE not null default 'daily',
  for_type int not null default 0,
  qty_per_type real not null default 0,
  relax_qty real not null default 0,
  relax_allowed int not null default 0,
  misses_allowed int not null default 0,
  description TEXT null,
  inverse_habit boolean not null default false,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  primary key(hname)  
);

create table Goal(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  gname varchar(20) not null,
  start_date date not null,
  end_date date not null,
  description TEXT null,

  check(start_date <= end_date),
  primary key(username, gname, start_date, end_date)
);

create table GoalAbs(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  gname varchar(20) not null,
  start_date date not null,
  end_date date not null,
  pts real not null default 0,

  foreign key(username, gname, start_date, end_date) references Goal on update cascade
  	  		       		   	     		     on delete cascade,
  primary key(username, gname, start_date, end_date)
);

create table GoalActivity(
  username varchar(20) not null,
  nickname varchar(20) not null,
  gname varchar(20) not null,
  start_date date not null,
  end_date date not null,
  qty real not null default 0,
  inverse_activity boolean not null default false,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  foreign key(username, gname, start_date, end_date) references Goal on update cascade
  	  		       		   	     		     on delete cascade,
  primary key(username, nickname, gname, start_date, end_date)
);

create table Milestone(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  mname varchar(20) not null,
  start_date date not null,
  description TEXT null,

  primary key(username, mname, start_date)
);

create table MilestoneAbs(
  username varchar(20) not null references Users on update cascade
  	   	       	   		   	 on delete cascade,
  mname varchar(20) not null,
  start_date date not null,
  pts real not null default 0,

  foreign key(username, mname, start_date) references Milestone on update cascade
  	  		       		   	      		on delete cascade,
  primary key(username, mname, start_date)
);

create table MilestoneActivity(
  username varchar(20) not null,
  nickname varchar(20) not null,
  mname varchar(20) not null,
  start_date date not null,
  qty real not null default 0,

  foreign key(username, nickname) references Activity on update cascade
  	  			  	     	      on delete cascade,
  foreign key(username, mname, start_date) references Milestone on update cascade
  	  		       		   	      		on delete cascade,
  primary key(username, nickname, mname, start_date)
);

create table TodayLogin(
  date_time timestamp not null primary key
);
