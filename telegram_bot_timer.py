import telegram
from datetime import datetime
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, ConversationHandler

updater = Updater('TOKEN', use_context=True)

TYPE = range(1)

def today(update:telegram.Update, context:telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='write down your plan with time frame'
                                                                  '\ne.g.   20:30;Study English   ')
    global today, t_, time_lst, count, schedule_book
    count = 0
    time_lst = []
    schedule_book = {}
    return TYPE

""" Setting planning """
def schedule(update:telegram.Update, context:telegram.ext.CallbackContext):
    global count, record, time_lst, date_td
    today = datetime.now()

    """ Time with hour and mins  """
    t_ = today.strftime("%H:%M")

    """ Date """
    date_td = today.strftime("%Y/%m/%d")

    """ Fill event & time  """
    if update.message.text != "f":
        print(t_)

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

                        if count == 0:
                            record = update.message.text
                        else:
                            record += "," + update.message.text
                        count += 1

                else:
                    update.message.reply_text(f"you cannot plan for the past time!!")
        else:
            update.message.reply_text(text="Please enter with correct format!")

        """ Finish the planning """
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Finish !")
        schedule_book[date_td] = record
        print(record)
        set_reminder(update, context)
        return ConversationHandler.END

def end(update: telegram.Update):
    update.message.reply_text('Finish')
    return ConversationHandler.END

""" Setting schudle """
def set_reminder(update:telegram.Update, context:telegram.ext.CallbackContext):
    global dt, day, event
    now = datetime.now()
    context.bot.send_message(chat_id=update.message.chat_id, text='Setting a timer!')

    """ Extract time, event from dictionary"""
    for day, accidents in schedule_book.items():
        for accident in accidents.split(","):
            time, event = accident.split(";")

            """ Convert time string back to datetime format for time calculation(second) """
            dt = f"{date_td} {time}:00"
            plan_time = datetime.strptime(dt, "%Y/%m/%d %H:%M:%S")
            dur_ = plan_time - now
            dur_in_sec = dur_.total_seconds()
            print(dur_in_sec)
            context.job_queue.run_once(callback_reminder, dur_in_sec, context=update.message.chat_id)

""" Calling reminder """
def callback_reminder(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=context.job.context, text=f"{event}")



conv_td = ConversationHandler(entry_points=[CommandHandler("td", today)],
                              states={
                                  TYPE: [MessageHandler(Filters.text, schedule)],
                              },
                              fallbacks=[CommandHandler("end", end)],
                              )

updater.dispatcher.add_handler(CommandHandler("time", set_reminder))
updater.dispatcher.add_handler(conv_td)

updater.start_polling()
updater.idle()


