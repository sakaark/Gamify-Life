create view DayActivityIntervalQtyPoints as
select adate, username, nickname, qty, pts as points
from Record natural join IntervalActivity
where (qty >= qty_start and qty <= qty_end);

create view DayActivityScaledQtyPoints as
select adate, username, nickname, Record.qty as qty, pts*(Record.qty/ScaleQtyActivity.qty) as points
from Record join ScaleQtyActivity using (username, nickname);

create view DayActivityYesQtyPoints as
select adate, username, nickname, qty, yes_pts as points
from Record join YesNoActivity using (username, nickname)
where qty != 0.0;

create view DayActivityNoQtyPoints as
select adate, username, nickname, qty, no_pts as points
from Record join YesNoActivity using (username, nickname)
where qty = 0.0;

create view DayActivityQtyPoints as
(select * from DayActivityIntervalQtyPoints)
union
(select * from DayActivityScaledQtyPoints)
union
(select * from DayActivityYesQtyPoints)
union
(select * from DayActivityNoQtyPoints);

create view DayPoints as
select username, adate, sum(points) as points
from DayActivityQtyPoints
group by username, adate;
