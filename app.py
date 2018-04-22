#!/usr/bin/python

import argparse
import psycopg2
from getpass import getpass
from sys import exit, argv
from datetime import datetime, timedelta
from prettytable import PrettyTable, from_db_cursor

def check_user_pass(num):
    if num == 3:
        return None
    print "Username:",
    username = raw_input()
    password = getpass()
    cur.execute("SELECT uname, username FROM Users WHERE username = %s AND password = %s;", (username, password))
    logged_in_user = cur.fetchall()
    assert(len(logged_in_user) <= 1)
    if(len(logged_in_user) == 1):
        print "Welcome " + logged_in_user[0][0]
        return logged_in_user[0][1]
    else:
        print "Username or password incorrect."
        return check_user_pass(num+1)

def get_password():
    password = getpass()
    print "Retype Password"
    re_password = getpass()
    if password != re_password:
        print "The passwords don't match. Please enter again:"
        return get_password()
    return password

def welcome_user(username):
    cur.execute("SELECT uname FROM Users NATURAL JOIN LoginStatus WHERE username = %s;", (username, ))
    logged_in_user = cur.fetchall()
    assert(len(logged_in_user) == 1)
    print "Welcome " + logged_in_user[0][0]
    return username

def login_user():
    print "Kindly enter your login details:"
    username = check_user_pass(0)
    if username != None:
        cur.execute("UPDATE LoginStatus SET loggedin = %s WHERE username = %s;", (True, username))
        conn.commit()
    return username

def get_username():
    print "Username:",
    username = raw_input()
    cur.execute("SELECT username FROM Users WHERE username = %s;", (username, ))
    length = len(cur.fetchall())
    assert(length <= 1)
    if length != 0:
        print "This username as already been taken. Please choose some other username."
        return get_username()
    return username

def logout(username):
    cur.execute("UPDATE LoginStatus SET loggedin = %s WHERE loggedin = %s", (False, True))
    conn.commit()
    print "Logged out " + username
    return

def get_reply(choices):
    reply = raw_input()
    if reply in choices:
        return reply
    print "Invalid response! Please enter your response again:",
    return get_reply(choices)

def del_user(username):
    cur.execute("DELETE FROM Users WHERE username = %s;", (username, ))
    conn.commit()
    print "User '" + username + "' successfully deleted."
    
def signup_and_login():
    print "Fill the following fields to signup"
    print "Your Full Name:",
    uname = raw_input()
    username = get_username()
    password = get_password()
    cur.execute("INSERT INTO Users VALUES(%s, %s, %s);", (username, uname, password))
    cur.execute("INSERT INTO LoginStatus VALUES(%s, %s);", (username, True))
    conn.commit()
    print "Congratulations!! User " + uname + " created!\nLogged in as " + username + "."
    return username

def get_start_end():
    print "Enter the Starting quantity of Interval:",
    qty_start = float(raw_input())
    print "Enter the Ending quantity of Interval:",
    qty_end = float(raw_input())
    if qty_end < qty_start:
        print "Starting qty can't be greater than ending quantity.\nPlease enter again."
        return get_start_end()
    return (qty_start, qty_end)

def add_main_activity():
    print "Give Activity Name:",
    aname = raw_input()
    print "Give a nickname to refer to the activity:",
    nickname = raw_input()
    print "Give a default qty for the activity:",
    default_qty = float(raw_input())
    print "Should we add this to list of active activities(to be prompted for daily)?(y/n):",
    reply = get_reply(["y","n"])
    if reply == "y":
        active = True
    else:
        active = False
    cur.execute("INSERT INTO Activity VALUES (%s, %s, %s, %s, %s, %s)", (username, nickname, aname, default_qty, active, False))
    return nickname

def edit_main_activity(old_name):
    print "Give New Activity Name:",
    aname = raw_input()
    print "Give a new nickname to refer to the activity:",
    nickname = raw_input()
    print "Give a default qty for the activity:",
    default_qty = float(raw_input())
    print "Should we add this to list of active activities(to be prompted for daily)?(y/n):",
    reply = get_reply(["y","n"])
    if reply == "y":
        active = True
    else:
        active = False
    cur.execute("UPDATE Activity SET username = %s, nickname = %s, aname = %s, default_qty = %s, active = %s WHERE username = %s AND nickname = %s", (username, nickname, aname, default_qty, active, username, old_name))
    return nickname

def check_interval_consistency(nickname, start, end):
    cur.execute(
        """SELECT * FROM IntervalActivity WHERE username = %s and nickname = %s
        and ((qty_start < %s and qty_start >= %s) or (qty_end <= %s and qty_end > %s))""",
        (username, nickname, end, start, end, start))
    if len(cur.fetchall()) != 0:
        return False
    return True

def add_intervals(nickname):
    print "Adding interval for:", nickname
    qty_start, qty_end = get_start_end()
    consistent = check_interval_consistency(nickname, qty_start, qty_end)
    if not consistent:
        print "The entered interval is conflicting with other intervals for this activity.\nDo you wish to enter another interval?(y/n):",
        reply = get_reply(["y", "n"])
        if reply == "y":
            return add_intervals(nickname)
        else:
            return
    print "Enter Points associated with this interval:",
    pts = float(raw_input())
    cur.execute("INSERT INTO IntervalActivity VALUES (%s, %s, %s, %s, %s)", (username, nickname, qty_start, qty_end, pts))
    print "Do you want to enter more intervals for this activity?(y/n):",
    reply = get_reply(["y", "n"])
    if reply == "y":
        return add_intervals(nickname)
    else:
        return

def add_interval_activity():
    print "Adding Interval activity:"
    nickname = add_main_activity()
    add_intervals(nickname)
    conn.commit()

def add_scaling(nickname):
    print "Enter the quantity:",
    qty = float(raw_input())
    print "Enter the points associated with this activity:",
    pts = float(raw_input())
    cur.execute("INSERT INTO ScaleQtyActivity VALUES (%s, %s, %s, %s)", (username, nickname, qty, pts))

def add_scaled_activity():
    print "Adding Interval activity:"
    nickname = add_main_activity()
    add_scaling(nickname)
    conn.commit()

def add_yesno(nickname):
    print "Enter the points to be associated if activity is done:",
    yes_pts = float(raw_input())
    print "Enter the points to be associated if activity is not done:",
    no_pts = float(raw_input())
    cur.execute("INSERT INTO YesNoActivity VALUES (%s, %s, %s, %s)", (username, nickname, yes_pts, no_pts))

def add_yesno_activity():
    print "Adding Interval activity:"
    nickname = add_main_activity()
    add_yesno(nickname)
    conn.commit()    

def add_activity():
    print "What Type of Activity would you like to create?"
    print "1. Interval activity (Different points for qty in different intervals)"
    print "2. Scaled activity (Points are automatically scaled from the value and qty you will specify)"
    print "3. Yes/No activity (You either get the points for doing the activity or not doing it)"
    reply = get_reply(["1","2","3"])
    if reply == "1":
        add_interval_activity()
    elif reply == "2":
        add_scaled_activity()
    else:
        add_yesno_activity()

def delete_old_activity_type(activity):
    cur.execute("DELETE FROM IntervalActivity WHERE username = %s AND nickname = %s;", (username, activity))
    cur.execute("DELETE FROM ScaleQtyActivity WHERE username = %s AND nickname = %s;", (username, activity))
    cur.execute("DELETE FROM YesNoActivity WHERE username = %s AND nickname = %s;", (username, activity))

def edit_activity(activity):
    activity_list = get_all_activities()
    if activity not in activity_list:
        print "Entered activity is not in the activity list. Please enter one of the following activities in another try:"
        print activity_list
        exit(1)
    print "What Type of Activity would you like to convert %s into?" % activity
    print "1. Interval activity (Different points for qty in different intervals)"
    print "2. Scaled activity (Points are automatically scaled from the value and qty you will specify)"
    print "3. Yes/No activity (You either get the points for doing the activity or not doing it)"
    reply = get_reply(["1", "2", "3"])
    delete_old_activity_type(activity)
    nickname = edit_main_activity(activity)
    if reply == "1":
        add_intervals(nickname)
    elif reply == "2":
        add_scaling(nickname)
    else:
        add_yesno(nickname)
    conn.commit()

def add_activities():
    add_activity()
    print "Activity Successflly added!\nDo you want to enter another activity?(y/n):",
    reply = get_reply(["y","n"])
    if reply == "y":
        return add_activities()
    return

def make_list(l):
    to_ret = []
    for tup in l:
        to_ret.append(tup[0])
    return to_ret

def get_all_activities():
    cur.execute("SELECT nickname FROM Activity WHERE username = %s AND disuse = %s;", (username, False))
    return make_list(cur.fetchall())

def add_habit():
    activity_list = get_all_activities()
    if len(activity_list) == 0:
        print "No activity to add a habit of. Please enter an activity or make an disusable activity usable."
        exit()
    print "Enter an activity(nickname) from following activities for which you want to make a habit:" 
    print activity_list, ":",
    nickname = get_reply(activity_list)
    print "Enter the description for the habit (if any):",
    description = raw_input()
    print "Give a habit name(unique for each habit):",
    hname = raw_input()
    print "Enter the date for Habit to start (in MM-DD-YYYY format (eg. 7-19-2012)):",
    start_date = raw_input()
    print "Enter the type of habit from the following options:"
    print "(daily, weekly, monthly)"
    habit_type = get_reply(["daily", "weekly", "monthly"])
    print "Is this habit inverse type? (i.e. more you do worse it is)(y/n):",
    reply = get_reply(["y", "n"])
    inv_habit = False if reply == "n" else True
    print "Enter the duration to monitor the making of habit (eg if type is weekly then enter 7 for 7 weeks):",
    for_type = int(raw_input())
    print "Enter the quantity for which you you would consider the habit to be formed (qty per habit type):",
    qty_per_type = float(raw_input())
    print "Enter the relaxed quantity for the habit to be made(optional):",
    relax_qty = raw_input()
    relax_qty = 0 if relax_qty == "" else float(relax_qty)
    print "Enter the relaxes(per habit type) for the habit allowed(optional):",
    relax_allowed = raw_input()
    relax_allowed = 0 if relax_allowed == "" else int(relax_allowed)
    print "Enter the misses allowed for the habit(optional):",
    misses_allowed = raw_input()
    misses_allowed = 0 if misses_allowed == "" else int(misses_allowed)
    cur.execute("INSERT INTO Habit VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, nickname, hname, start_date, habit_type, for_type, 
                                                                                              qty_per_type, relax_qty, relax_allowed, misses_allowed, 
                                                                                              description, inv_habit))
    conn.commit()

def add_main_goal():
    print "Enter Goal name:",
    gname = raw_input()
    print "Enter the Start Date for the goal(MM-DD-YYYY):",
    start_date = raw_input()
    print "Enter the End Date for the goal(MM-DD-YYYY):",
    end_date = raw_input()
    print "Give some description for the goal(optional):"
    description = raw_input()
    cur.execute("INSERT INTO Goal VALUES (%s, %s, %s, %s, %s)", (username, gname, start_date, end_date, description))
    return (gname, start_date, end_date)

def add_abs_goal():
    print "Entering a goal for", username
    gname, start_date, end_date = add_main_goal()
    print "Enter the points you wish to achieve in the above period:",
    pts = float(raw_input())
    cur.execute("INSERT INTO GoalAbs VALUES (%s, %s, %s, %s, %s)", (username, gname, start_date, end_date, pts))
    conn.commit()

def add_activity_goal():
    print "Entering a goal for", username
    print "Enter for which one of the activities do you want to enter the goal:"
    activities = get_all_activities()
    print str(activities) + ":",
    nickname = get_reply(activities)
    gname, start_date, end_date = add_main_goal()
    print "Is this an inverse activity(you want to minimize its amount)(y/n):",
    reply = get_reply(["y", "n"])
    inverse_activity = True if reply == "y" else False
    print "Enter the qty for %s you wish to achieve in the above period:" % nickname,
    qty = float(raw_input())
    cur.execute("INSERT INTO GoalActivity VALUES (%s, %s, %s, %s, %s, %s, %s)", (username, nickname, gname, start_date, end_date, qty, inverse_activity))
    conn.commit()

def add_main_milestone():
    print "Enter Milestone name:",
    mname = raw_input()
    print "Enter the Start Date for the milestone(MM-DD-YYYY):",
    start_date = raw_input()
    print "Give some description for the Milestone(optional):"
    description = raw_input()
    cur.execute("INSERT INTO Milestone VALUES (%s, %s, %s, %s)", (username, mname, start_date, description))
    return (mname, start_date)

def add_abs_milestone():
    print "Entering a Milestone for", username
    mname, start_date  = add_main_milestone()
    print "Enter milstone points:",
    pts = float(raw_input())
    cur.execute("INSERT INTO MilestoneAbs VALUES (%s, %s, %s, %s)", (username, mname, start_date, pts))
    conn.commit()

def add_activity_milestone():
    print "Entering a milestone for", username
    print "Enter for which one of the activities do you want to enter a milestone:"
    activities = get_all_activities()
    print str(activities) + ":",
    nickname = get_reply(activities)
    mname, start_date = add_main_milestone()
    print "Enter the milestone qty for %s:" % nickname,
    qty = float(raw_input())
    cur.execute("INSERT INTO MilestoneActivity VALUES (%s, %s, %s, %s, %s)", (username, nickname, mname, start_date, qty))
    conn.commit()

def add_goal():
    print "Enter the type of goal you want to enter:"
    print "1. Absolute goal in terms of all activities combined."
    print "2. Activity specific goal."
    reply = get_reply(["1", "2"])
    if reply == "1":
        add_abs_goal()
    else:
        add_activity_goal()

def add_milestone():
    print "Enter the type of milestone you want to enter:"
    print "1. Absolute milestone in terms of all activities combined."
    print "2. Activity specific milestone."
    reply = get_reply(["1", "2"])
    if reply == "1":
        add_abs_milestone()
    else:
        add_activity_milestone()

def add_habits():
    add_habit()
    print "Habit Successfully added!\nDo you want to enter another habit?(y/n):",
    reply = get_reply(["y", "n"])
    if reply == "y":
        return add_habits()
    return

def add_goals():
    add_goal()
    print "Goal Successfully added!\nDo you want to enter another goal?(y/n):",
    reply = get_reply(["y", "n"])
    if reply == "y":
        return add_goals()
    return

def add_milestones():
    add_milestone()
    print "Milestone Successfully added!\nDo you want to enter another milestone?(y/n):",
    reply = get_reply(["y", "n"])
    if reply == "y":
        return add_milestones()
    return

def get_active_activities():
    cur.execute("SELECT nickname FROM Activity WHERE username = %s AND active = %s;", (username, True))
    return make_list(cur.fetchall())

def check_existence_in_record(nickname, today):
    cur.execute("SELECT * FROM Record WHERE username = %s and nickname = %s and adate = %s;", (username, nickname, today))
    result = cur.fetchall()
    assert(len(result) <= 1)
    if len(result) == 1:
        return
    cur.execute("SELECT default_qty FROM Activity WHERE username = %s and nickname = %s;", (username, nickname))
    result = cur.fetchall()
    assert(len(result) == 1)
    cur.execute("INSERT INTO Record VALUES (%s, %s, %s, %s);", (username, nickname, today, result[0][0]))
    conn.commit()
    return

def enter_in_record(date, nickname, value):
    check_existence_in_record(nickname, date)
    cur.execute("UPDATE Record SET qty = %s WHERE username = %s and nickname = %s and adate = %s;", (value, username, nickname, date))
    conn.commit()
    return

def add_in_record(date, nickname, value):
    check_existence_in_record(nickname, date)
    cur.execute("SELECT qty FROM Record WHERE username = %s and nickname = %s and adate = %s;", (username, nickname, date))
    result = cur.fetchall()
    assert(len(result) == 1)
    cur.execute("UPDATE Record SET qty = %s WHERE username = %s and nickname = %s and adate = %s;", (value + result[0][0], username, nickname, date))
    conn.commit()
    return

def add_record_for(date):
    if date > datetime.now().date():
        print "Logging for future dates is not allowed."
        exit(1)
    activities = get_active_activities()
    print "Entering daily log for:", username
    print "(enter qty to add to existing, $qty to set qty for that acttivity, leave blank to keep it same(default if not enetered))"
    for activity in activities:
        print activity + ":",
        qty = raw_input()
        if qty == "":
            check_existence_in_record(activity, date)
            continue
        if qty[0] == "$":
            enter_in_record(date, activity, float(qty[1:]))
        else:
            add_in_record(date, activity, float(qty))

def add_activity_log(activity, date):
    date = datetime.strptime(date, "%m-%d-%Y").date()
    if date > datetime.now().date():
        print "Logging for future dates is not allowed."
        exit(1)
    activity_list = get_all_activities()
    if activity not in activity_list:
        print "This activity is not present in your activity list.\nFollowing is your activity list:"
        print activity_list
    print "Enter qty for activity %s:" % activity,
    qty = raw_input()
    if qty == "":
        check_existence_in_record(activity, date)
        return
    if qty[0] == "$":
        enter_in_record(date, activity, float(qty[1:]))
    else:
        add_in_record(date, activity, float(qty))

def get_periodic_activity_score(nickname, date, no_days):
    end_period = date + timedelta(days=no_days)
    tot_qty = 0
    while date < end_period:
        check_existence_in_record(nickname, date)        
        cur.execute("SELECT qty FROM DayActivityQtyPoints WHERE adate = %s AND username = %s AND nickname = %s;", (date, username, nickname))
        result = cur.fetchall()
        assert(len(result) == 1)
        tot_qty += result[0][0]
        date += timedelta(days=1)
    return tot_qty

def check_periodic_habit(habit, no_days):
    nickname = habit[1]
    hname = habit[2]
    start_date = habit[3]
    for_type = habit[5]
    qty_per_type = habit[6]
    relax_qty = habit[7]
    relax_allowed = habit[8]
    misses_allowed = habit[9]
    inverse_habit = habit[11]
    failed = False
    date = start_date
    done = 0
    now_date = datetime.now().date()
    while done < for_type and date + timedelta(no_days-1) <= now_date:
        qty = get_periodic_activity_score(nickname, date, no_days)
        if not inverse_habit:
            if qty < qty_per_type:
                if qty < relax_qty:
                    misses_allowed -= 1
                    if misses_allowed < 0:
                        failed = True
                        break
                    date += timedelta(days=no_days)
                    continue
                else:
                    relax_allowed -= 1
                    if relax_allowed < 0:
                        relax_allowed += 1
                        misses_allowed -= 1
                        if misses_allowed < 0:
                            failed = True
                            break
                        date += timedelta(days=no_days)
                        continue
        else:
            if qty > qty_per_type:
                if qty > relax_qty:
                    misses_allowed -= 1
                    if misses_allowed < 0:
                        failed = True
                        break
                    date += timedelta(days=no_days)
                    continue
                else:
                    relax_allowed -= 1
                    if relax_allowed < 0:
                        relax_allowed += 1
                        misses_allowed -= 1
                        if misses_allowed < 0:
                            failed = True
                            break
                        date += timedelta(days=no_days)
                        continue
        date += timedelta(days=no_days)
        done += 1
    if done == for_type:
        accomplished_habits.add_row([hname, nickname, start_date, habit[4], date-timedelta(days=1), qty_per_type])
    elif start_date > now_date:
        tostart_habits.add_row([hname, nickname, start_date, habit[4], for_type, qty_per_type, relax_qty, relax_allowed, misses_allowed])
    elif date + timedelta(no_days-1) > now_date:
        done_till = 0
        if date <= now_date:
            done_till = get_periodic_activity_score(nickname, date, (now_date-date).days+1)
        else:
            prev = date-timedelta(days=no_days)
            done_till = get_periodic_activity_score(nickname, prev, (now_date-prev).days+1)
        if done_till <= qty_per_type:
            progressing_habits.add_row([hname, nickname, start_date, habit[4], done, for_type-done, relax_allowed, misses_allowed, qty_per_type, qty_per_type - done_till])
        else:
            progressing_habits.add_row([hname, nickname, start_date, habit[4], done, for_type-done, relax_allowed, misses_allowed, qty_per_type, "Exc: "+str(done_till-qty_per_type)])
    else:
        failed_habits.add_row([hname, nickname, start_date, habit[4], date, qty_per_type])

def check_for_habits():
    cur.execute("SELECT * FROM Habit;")
    habit_list = cur.fetchall()
    for habit in habit_list:
        if habit[4] == "daily":
            check_periodic_habit(habit, 1)
        elif habit[4] == "weekly":
            check_periodic_habit(habit, 7)
        elif habit[4] == "monthly":
            check_periodic_habit(habit, 30)
    if len(progressing_habits._rows) != 0:
        print "\nProgressing Habits:"
        print progressing_habits
    if len(accomplished_habits._rows) != 0:
        print "\nAccomplished Habits:"
        print accomplished_habits
    if len(failed_habits._rows) != 0:
        print "\nFailed Habits:"
        print failed_habits
    if len(tostart_habits._rows) != 0:
        print "\nHabits yet to be started:"
        print tostart_habits
 
def check_for_actgoal(actgoal):
    nickname = actgoal[1]
    gname = actgoal[2]
    start_date = actgoal[3]
    end_date = actgoal[4]
    goal_qty = actgoal[5]
    inverse_activity = actgoal[6]
    now_date = datetime.now().date()
    sub_date = now_date if now_date < end_date else end_date
    achieved_qty = get_periodic_activity_score(nickname, start_date, (sub_date-start_date).days + 1)
    if not inverse_activity:
        if achieved_qty >= goal_qty:
            accomplished_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])
        elif start_date > now_date:
            tostart_goals.add_row([gname, nickname, start_date, end_date, goal_qty])
        elif end_date >= now_date:
            progressing_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])
        elif end_date < now_date:
            failed_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])
    else:
        if achieved_qty <= goal_qty and end_date < now_date:
            accomplished_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])
        elif start_date > now_date:
            tostart_goals.add_row([gname, nickname, start_date, end_date, goal_qty])
        elif end_date >= now_date:
            progressing_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])
        elif end_date < now_date:
            failed_goals.add_row([gname, nickname, start_date, end_date, goal_qty, achieved_qty])

def check_for_absgoal(absgoal):
    gname = absgoal[1]
    start_date = absgoal[2]
    end_date = absgoal[3]
    goal_pts = absgoal[4]
    now_date = datetime.now().date()
    achieved_pts = get_total_period_score(start_date, end_date)
    if achieved_pts >= goal_pts:
        accomplished_goals.add_row([gname, "All Activities", start_date, end_date, goal_pts, achieved_pts])
    elif start_date > now_date:
        tostart_goals.add_row(gname, nickname, start_date, end_date, goal_pts)
    elif end_date >= now_date:
        progressing_goals.add_row([gname, "All Activities", start_date, end_date, goal_pts, achieved_pts])
    elif end_date < now_date:
        failed_goals.add_row([gname, "All Activities", start_date, end_date, goal_pts, achieved_pts])

def get_total_period_score(start_date, end_date):
    cur.execute("SELECT sum(points) FROM DayPoints WHERE username = %s AND adate >= %s AND adate <= %s;", (username, start_date, end_date))
    result = cur.fetchall()
    assert(len(result) <= 1)
    if len(result) == 0 or result[0][0] == None:
        return 0
    return result[0][0]

def check_for_goals():
    cur.execute("SELECT * FROM GoalActivity;")
    actgoal_list = cur.fetchall()
    for actgoal in actgoal_list:
        check_for_actgoal(actgoal)
    cur.execute("SELECT * FROM GoalAbs;")
    absgoal_list = cur.fetchall()
    for absgoal in absgoal_list:
        check_for_absgoal(absgoal)
    if len(progressing_goals._rows) != 0:
        print "\nProgressing Goals:"
        print progressing_goals
    if len(accomplished_goals._rows) != 0:
        print "\nAccomplished Goals:"
        print accomplished_goals
    if len(failed_goals._rows) != 0:
        print "\nFailed Goals:"
        print failed_goals
    if len(tostart_goals._rows) != 0:
        print "\nGoals yet to be started:"
        print tostart_goals

def check_for_absmile(absmile):
    mname = absmile[1]
    start_date = absmile[2]
    mile_pts = absmile[3]
    now_date = datetime.now().date()
    my_pts = get_total_period_score(start_date, now_date)
    if my_pts < mile_pts:
        progressing_milestones.add_row([mname, "All Activities", start_date, mile_pts, my_pts])
    else:
        accomplished_milestones.add_row([mname, "All Activities", start_date, mile_pts, my_pts])

def check_for_actmile(actmile):
    nickname = actmile[1]
    mname = actmile[2]
    start_date = actmile[3]
    mile_qty = actmile[4]
    now_date = datetime.now().date()
    my_qty = get_periodic_activity_score(nickname, start_date, (now_date-start_date).days + 1)
    if my_qty < mile_qty:
        progressing_milestones.add_row([mname, nickname, start_date, mile_qty, my_qty])
    else:
        accomplished_milestones.add_row([mname, nickname, start_date, mile_qty, my_qty])    

def check_for_milestones():
    cur.execute("SELECT * FROM MilestoneActivity;")
    actmile_list = cur.fetchall()
    for actmile in actmile_list:
        check_for_actmile(actmile)
    cur.execute("SELECT * FROM MilestoneAbs;")
    absmile_list = cur.fetchall()
    for absmile in absmile_list:
        check_for_absmile(absmile)
    if len(progressing_milestones._rows) != 0:
        print "\nProgressing Milestones:"
        print progressing_milestones
    if len(accomplished_milestones._rows) != 0:
        print "\nAccomplished Milestones:"
        print accomplished_milestones

def show_log_for(date):
    cur.execute("SELECT adate as date, nickname as activity, qty, points FROM DayActivityQtyPoints WHERE adate = %s AND username = %s;", (date, username))
    table = from_db_cursor(cur)
    print "\nLog for %s" % str(date)
    print table

def show_sum_for(start_date, end_date):
    cur.execute("SELECT adate as date, points FROM DayPoints WHERE username = %s AND adate >= %s AND adate <= %s;", (username, start_date, end_date))
    table = from_db_cursor(cur)
    if start_date != end_date:
        print "\nLog from %s to %s" % (str(start_date), str(end_date))
    else:
        print "\nLog for %s" % str(start_date)
    print table

def get_highscore():
    cur.execute("SELECT max(points) FROM DayPoints WHERE username = %s;", (username,))
    result = cur.fetchall()
    assert(len(result) <= 1)
    maxp = result[0][0] if len(result) == 1 else 0
    conn.commit()
    cur.execute("SELECT adate as date, points FROM DayPoints WHERE points = %s AND username = %s;", (maxp, username))
    print "\nThe highscore(s) till now is(are):"
    print from_db_cursor(cur)

def get_lowscore():
    cur.execute("SELECT min(points) FROM DayPoints WHERE username = %s AND adate != %s;", (username, datetime.now().date()))
    result = cur.fetchall()
    assert(len(result) <= 1)
    maxp = result[0][0] if len(result) == 1 else 0
    conn.commit()
    cur.execute("SELECT adate as date, points FROM DayPoints WHERE points = %s AND username = %s;", (maxp, username))
    print "\nThe minimum score(s) till now is(are):"
    print from_db_cursor(cur)

def print_all_activities():
    cur.execute("SELECT aname, nickname, qty_start, qty_end, pts FROM IntervalActivity NATURAL JOIN Activity WHERE username = %s;", (username,))
    int_activities = from_db_cursor(cur)
    if len(int_activities._rows) != 0:
        print "\nInterval Activities for %s are:" % username
        print int_activities
    cur.execute("SELECT aname, nickname, qty, pts FROM ScaleQtyActivity NATURAL JOIN Activity WHERE username = %s;", (username,))
    sc_activities = from_db_cursor(cur)
    if len(sc_activities._rows) != 0:
        print "\nScaled Activities for %s are:" % username
        print sc_activities
    cur.execute("SELECT aname, nickname, yes_pts, no_pts FROM YesNoActivity NATURAL JOIN Activity WHERE username = %s;", (username,))
    yn_activities = from_db_cursor(cur)
    if len(yn_activities._rows) != 0:
        print "\nYesNo Activities for %s are:" % username
        print yn_activities
    if len(int_activities._rows) == 0 and len(sc_activities._rows) == 0 and len(yn_activities._rows) == 0:
        print "No Activities for %s" % username

def call_actions_for_users():
    """checks login and other info over here"""
    cur.execute("SELECT * FROM LoginStatus WHERE loggedin = true;")
    logged_in_users = cur.fetchall()
    logged_no = len(logged_in_users)
    assert(logged_no <= 1)
    if args.logout:
        if logged_no != 1:
            print "No one is logged in! Can't logout!"
            exit()
        logout(logged_in_users[0][0])
        exit()
    if logged_no == 1:
        if args.signup:
            print "User already logged in. Please logout and then signup."
            exit()
        username = welcome_user(logged_in_users[0][0])
    else:
        if args.signup:
            username = signup_and_login()
        else:
            username  = login_user()
            if username == None:
                print "Exiting. If you wish to sign up use -su command line option."
                exit()
    if args.deleteacc:
        print "Are you sure you want to delete your account(y/n).(All your info including all your activities will be permanently lost.):",
        reply = get_reply(["y","n"])
        if reply == "y":
            del_user(username)
            exit()
        else:
            print "Be careful next time! Bye"
            exit()
    return username

def call_actions_for_activity():
    if args.addactivity:
        add_activities()
    if args.editactivity:
        edit_activity(args.editactivity)
        print "Edited activity successfully."
    if args.seeall:
        print_all_activities()

def call_actions_for_habits():
    if args.addhabit:
        add_habits()
    if args.checkhabits:
        check_for_habits()

def call_actions_for_goals():
    if args.addgoal:
        add_goals()
    if args.checkgoals:
        check_for_goals()

def call_actions_for_milestones():
    if args.addmilestone:
        add_milestones()
    if args.checkmilestones:
        check_for_milestones()

def call_actions_for_records():
    if args.dailylog:
        cur.execute("SELECT * FROM TodayLogin;")
        result = cur.fetchall()
        if len(result) == 0:
            print "No log added today.\nPoints table till now is:"
        else:
            print "Last entry at", str(result[0][0])
        show_log_for(datetime.now().date())
        show_sum_for(datetime.now().date(), datetime.now().date())
        print ""
        add_record_for(datetime.now().date())
        cur.execute("DELETE FROM TodayLogin;")
        cur.execute("INSERT INTO TodayLogin VALUES (%s);", (datetime.now(),))
        conn.commit()
        print "Today's log added!"
    if args.specificlog:
        date = datetime.strptime(args.specificlog, "%m-%d-%Y").date()
        add_record_for(date)
        print "Log for", date, "added!"
    if args.activitylog:
        add_activity_log(args.activitylog[0], args.activitylog[1])
        print "Log for", args.activitylog[1], "for activity", args.activitylog[0], "added!"
    if args.showtoday:
        show_log_for(datetime.now().date())
        show_sum_for(datetime.now().date(), datetime.now().date())
    if args.showdate:
        date = datetime.strptime(args.showdate, '%m-%d-%Y').date()
        show_log_for(date)
        show_sum_for(date, date)
    if args.showsums:
        show_sum_for(datetime.strptime(args.showsums[0], '%m-%d-%Y').date(), datetime.strptime(args.showsums[1], '%m-%d-%Y').date())
    if args.highscore:
        get_highscore()
    if args.lowscore:
        get_lowscore()

def get_args(sub_type):
    if len(argv) < 2:
        return parser.parse_args([sub_type])
    if argv[1] == sub_type:
        if len(argv) < 2:
            return parser.parse_args([sub_type])
        return parser.parse_args([sub_type]+argv[2:])
    else:
        return parser.parse_args([sub_type])

conn = psycopg2.connect("dbname=project user=postgres host=localhost password=wrongpassword")
cur = conn.cursor()
parser = argparse.ArgumentParser(description="Process the arguments.")
sub_parsers = parser.add_subparsers()

parser_user = sub_parsers.add_parser("user")
group_user = parser_user.add_mutually_exclusive_group()
group_user.add_argument("-su", "--signup", help="Use this option to signup", action="store_true")
group_user.add_argument("-lo", "--logout", help="Use this option to logout", action="store_true")
group_user.add_argument("-da", "--deleteacc", help="Use this option to delete an account", action="store_true")
args = get_args("user")
username = call_actions_for_users()

parser_activity = sub_parsers.add_parser("activity")
group_activity = parser_activity.add_mutually_exclusive_group()
group_activity.add_argument("-aa", "--addactivity", help="use this option to add items to inventory", action="store_true")
group_activity.add_argument("-ea", "--editactivity", help="use this option to add items to inventory", type=str)
parser_activity.add_argument("-sa", "--seeall", help="use this option to see all the activities ", action="store_true")
args = get_args("activity")
call_actions_for_activity()

failed_habits = PrettyTable(["Habit Name", "Activity", "Start date", "Type", "Failed on", "Periodic Amt"])
progressing_habits = PrettyTable(["Habit Name", "Activity", "Start Date", "Type", "Done", "Remaining", "Relaxes Left", "Misses Left", "Amt", "Amt Left"])
accomplished_habits = PrettyTable(["Habit Name", "Activity", "Start date", "Type", "Accomplished On", "Periodic Amt"])
tostart_habits = PrettyTable(["Habit Name", "Activity", "Start date", "Type", "For", "Amt", "Relaxed Amt", "Relax Allowed", "Misses Allowed"])
parser_habit = sub_parsers.add_parser("habit")
parser_habit.add_argument("-ah", "--addhabit", help="user this option to add a habit", action="store_true")
parser_habit.add_argument("-ch", "--checkhabits", help="Use this option to check habit progress", action="store_true")
args = get_args("habit")
call_actions_for_habits()

failed_goals = PrettyTable(["Goal Name", "Activity", "Start Date", "End Date", "Goal Amt", "Goal", "Achieved"])
accomplished_goals = PrettyTable(["Goal Name", "Activity", "Start Date", "End Date", "Goal", "Achieved"])
progressing_goals = PrettyTable(["Goal Name", "Activity", "Start Date", "End Date", "Goal", "Current Total"])
tostart_goals = PrettyTable(["Goal Name", "Activity", "Start Date", "End Date", "Goal"])
parser_goal = sub_parsers.add_parser("goal")
parser_goal.add_argument("-ag", "--addgoal", help="user this option to add a habit", action="store_true")
parser_goal.add_argument("-cg", "--checkgoals", help="Use this option to check goal progress", action="store_true")
args = get_args("goal")
call_actions_for_goals()

accomplished_milestones = PrettyTable(["Milestone Name", "Activity", "Start Date", "Milestone", "Achieved"])
progressing_milestones = PrettyTable(["Milestone Name", "Activity", "Start Date", "Milestone", "Current Total"])
parser_milestone = sub_parsers.add_parser("milestone")
parser_milestone.add_argument("-am", "--addmilestone", help="user this option to add a habit", action="store_true")
parser_milestone.add_argument("-cm", "--checkmilestones", help="Use this option to check milestone progress", action="store_true")
args = get_args("milestone")
call_actions_for_milestones()

parser_record = sub_parsers.add_parser("record")
group_record = parser_record.add_mutually_exclusive_group()
group_record.add_argument("-dl", "--dailylog", help="Use it to set quantities for various activities which are marked active", action = "store_true", required=False)
group_record.add_argument("-sl", "--specificlog", help="Use it to set quantities for various activities which are marked active for a specified date(mm-dd-yyyy)", type=str, required=False)
group_record.add_argument("-al", "--activitylog", help="Use it to set quantities for various activities which are marked active for a specified date(mm-dd-yyyy)", type=str, nargs = 2, required=False)
parser_record.add_argument("-sd", "--showdate", help="use it to show the points of various activities on that date", type=str)
parser_record.add_argument("-st", "--showtoday", help="use it to show the points of various activities today", action = "store_true")
parser_record.add_argument("-ss", "--showsums", help="use it to show the total points on a range of days", type=str, nargs = 2)
parser_record.add_argument("-hs", "--highscore", help="use it to know the highest score till now", action="store_true")
parser_record.add_argument("-ls", "--lowscore", help="use it to know the lowest score till now", action="store_true")
args = get_args("record")
call_actions_for_records()
conn.close()
