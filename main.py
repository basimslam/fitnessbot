import textbase
from textbase.message import Message
from textbase import models
import os
from typing import List
import datetime
from datetime import date


# Load your OpenAI API key
models.OpenAI.api_key = "enter your api key"
# or from environment variable:
# models.OpenAI.api_key = os.getenv("OPENAI_API_KEY")
#s = open("data.txt",w)
# Prompt for GPT-3.5 Turbo
prompt1 = """The content inside the quotes is the only information you have about the user.
Your other job is to respond with pass when there is no new information added.
and to print values of 4 fields: Name, Height, Weight, Gender. when new information is added
By default, they are all NIL
You need to compare this information with the newly entered message by the user. 
Only If the newly entered data has any new information which wasn't previously known regarding these, respond with a updated list of 4 fields. 
There should only be one value for each field. Those values should be the latest one. If no value is available for a field, mark it as NIL. 
separate each feature with a comma. for example: Name : Basim, Height : 7m
if there are no new information about these fields,you should only respond with "pass". 
If there is a change in name, all the other values become NIL. 
"""

prompt2 = """You are a helpful fitness assistant whose only job is to help the user regarding physical fitness.
If the user is trying to go into other matters not related to physical fitness, you should remind them you are only here to make them fit.
But casually chatting when the user is mentally down is okay.
Check the Already Known Information and ask the users for fields marked as NIL
You will be making the Meal Plan and Workout plan according to user's needs. When making meal plans, always consider user's dietary restrictions.
If there are no dietary restrictions, mark it as None. Add dietary restrcitions, purpose in the end of response when making meal plans
Do not ask more than one question at a time.
Keep asking questions until you have enough information to make workout plan and dietary plans.
When making workout plans, make it in a format of Monday : set of exercises, Tuesday : etc
do not include any other texts. just workout plan and details are enough
Include workout purpose in the end end of the response if you are making workout plan.
"""

prompt3 = """ Your job is to find the next upcoming workout and meal from the provided data.
Use the current time to determine which meal is next. eg: if it is midnight, next meal will be breakfast. 
Dont ask the user what day it is. It is already provided in this prompt
Use the day to figure out what today's workout plan is
Only Reply with the next mealplan and workout plan for the day from the provided data. 
Your reply should have both the workout and name of upcoming meal in a single sentence.
"""

@textbase.chatbot("talking-bot")
def on_message(message_history: List[Message], state: dict = None):
    """Your chatbot logic here
    message_history: List of user messages
    state: A dictionary to store any stateful information

    Return a string with the bot_response or a tuple of (bot_response: str, new_state: dict)
    """
    if not os.path.exists("data.txt"):
        fw = open("data.txt", "w")
        fw.close()
    fr = open("data.txt", "r")
    s = fr.read()
    fr.close()
    current_time = datetime.datetime.now().time()
    today = date.today()
    if today.weekday() == 0:
        day = "Monday"
    elif today.weekday() == 1:
        day = " Tuesday"
    elif today.weekday() == 2:
        day = "Wednesday"
    elif today.weekday() == 3:
        day = "Thursday"
    elif today.weekday() == 4:
        day = "Friday"
    elif today.weekday() == 5:
        day = "Saturday"
    else:
        day = "Sunday"
    flag = 0
    if os.path.exists("workout.txt") and os.path.exists("mealplan.txt"):
        f1 = open("workout.txt","r")
        f2 = open("mealplan.txt","r")
        flag = 1
        workout = f1.read()
        mealplan = f2.read()
        prompt = " If the current time is : " + str(current_time) + " Today is " + day + " " + prompt3 + " Workout Plan : " + workout + " Mealplan :" + mealplan
    elif os.path.exists("workout.txt"):
        prompt ="Start every conversation with greeting the user and asking the user if you should start planning a meal plan." + prompt2
    elif os.path.exists("mealplan.txt"):
        prompt = "Start every conversation with greeting the user and asking the user if you should start planning a workout plan." + prompt2
    else:
        prompt = "Start every conversation with greeting the user and asking the user if they need a workout plan or a meal plan" + prompt2

    if state is None or "counter" not in state:
        state = {"counter": 0}
    else:
        state["counter"] += 1

    # # Generate GPT-3.5 Turbo response
    if flag == 1:
        bot_response = models.OpenAI.generate(
            system_prompt="\"" + s + "\"" + prompt,
            message_history=message_history,
            model="gpt-3.5-turbo",
            max_tokens=1000
        )
        return bot_response,state

    bot_response = models.OpenAI.generate(
        system_prompt="\""+open("data.txt").read() + "\"" + prompt1 ,
        message_history=message_history,
        model="gpt-3.5-turbo",
        max_tokens = 1000
    )

    if bot_response.lower() != "pass":
        x = bot_response
        fw = open("data.txt","w")
        fw.seek(0)
        fw.write(x)
        fw.close()

    fr = open("data.txt", "r")
    s = fr.read()
    fr.close()
    bot_response = models.OpenAI.generate(
        system_prompt= prompt,
        message_history=message_history,
        model="gpt-3.5-turbo",
        max_tokens=1000
    )
    if "workout" in bot_response.lower() and ("day 1" in bot_response.lower() or "monday" in bot_response.lower()):
        fw = open("workout.txt","w")
        fw.seek(0)
        fw.write(bot_response)
        fw.close()
    elif "meal plan" in bot_response.lower() and ("breakfast" in bot_response.lower() or "meal 1" in bot_response.lower()):
        fw = open("mealplan.txt", "w")
        fw.seek(0)
        fw.write(bot_response)
        fw.close()

    return bot_response ,state


