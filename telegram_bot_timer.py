from telegram import Update
from datetime import datetime
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, ConversationHandler, CallbackContext

updater = Updater('ENTER YOUR TG TOKEN', use_context=True)

TYPE = range(1)
def start(update,context):
    update.message.reply_text("Welcome to use this timer, in here 😜, "
                              "\nyou can tell the bot your day planning and it would set reminder to you!"
                              "\n For more help, read in /help ☺️")

def help (update, context):
    update.message.reply_text("For first time to use, "
                              "\ntype the command /today_plan to set your plan 👆"
                              "\n\nFollow the rule:"
                              "\nFill-in time first, followed by  ';'   then fill the event"
                              "\n e.g.    21:00;Sleep"
                              "\n\n Wrong typing pattern would result in nothing"
                              "\nAfter finishing, type f ,"
                              "\n and you will receive a message 'Finish'"
                              "\nand bot sets timer 🥳"
                              )

def today_plan(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='write down your plan with time frame'
                                                                  '\ne.g.   20:30;Study English   ')
    global today, t_, time_lst, count, schedule_book, cal_event
    count = 0
    time_lst = []
    cal_event = []
    schedule_book = {}
    return TYPE

""" Setting planning """
def schedule(update, context):
    global count, record, time_lst, date_td
    today = datetime.now()

    """ Time with hour and mins  """
    t_ = today.strftime("%H:%M")

    """ Date """
    date_td = today.strftime("%Y/%m/%d")

    """ Fill event & time  """
    if update.message.text != "f":

        """ Ensure time and event exists at same time """
        if ";" in update.message.text and update.message.text[0] != ";" and update.message.text[-1] != ";":
            time, event = update.message.text.split(";")
            hour, minute = time.split(":")

            """ Remove unreasonable timeslot """
            if int(hour) <= 23 and int(minute) <= 59:

                """ Ensure time not passed """
                if time > t_:

                    """ Prevent same timeslot """
                    if time not in time_lst:
                        time_lst.append(time)
                        cal_event.append(update.message.text)

                    cal_event.sort()

                else:
                    update.message.reply_text(f"you cannot plan for the past time!!")
        else:
            update.message.reply_text(text="Please enter with correct format!")

        """ Finish the planning """
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Finish !")
        schedule_book[date_td] = cal_event
        set_reminder(update, context)
        return ConversationHandler.END

def end(update):
    update.message.reply_text('Finish')
    return ConversationHandler.END

""" Setting schudle """
def set_reminder(update, context):
    global dt, day, event, time, event
    now = datetime.now()
    context.bot.send_message(chat_id=update.message.chat_id, text='Timer is set!')

    """ Extract time, event from dictionary"""
    for day, accidents in schedule_book.items():
        for accident in accidents:
            time, event = accident.split(";")

            """ Convert time string back to datetime format for time calculation(second) """
            dt = f"{date_td} {time}:00"
            plan_time = datetime.strptime(dt, "%Y/%m/%d %H:%M:%S")
            dur_ = plan_time - now
            dur_in_sec = dur_.total_seconds()
            context.job_queue.run_once(callback_reminder, dur_in_sec, context=update.message.chat_id)

""" Calling reminder """
def callback_reminder(context):
    for day, accidents in schedule_book.items():
        for accident in accidents:
            time, event = accident.split(";")
            today = datetime.now()
            t_ = today.strftime("%H:%M")
            if time == t_:
                context.bot.send_message(chat_id=context.job.context, text=f"Now  is  {time}, You have to  {event}")


conv_td = ConversationHandler(entry_points=[CommandHandler("today_plan", today_plan)],
                              states={
                                  TYPE: [MessageHandler(Filters.text, schedule)],
                              },
                              fallbacks=[CommandHandler("end", end)],
                              )

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", help))
updater.dispatcher.add_handler(conv_td)

updater.start_polling()
updater.idle()
