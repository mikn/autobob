autobot
=======

A chat bot designed (almost) like a software project!


##Requirements
Python 3.4+ (ohmygod venv)


## Installing!

Even now it is rather simple, make sure you create a venv first

Then run `python setup.py develop`
Now you should have a fully functioning `autobot` command within your venv!
It doesn't do much right now, though. You can chat with it on stdin :)
But it will come with time...


## Preemptive FAQ
### Why does it not have a fancy personal name?
Because, let's face it, everyone gives their chatbot their own names...
### Why is it not API-compatible with Will?
While Will has a rather good API, it also comes with some shortcomings.
Some examples include:

1. The reply method is not attached to the message object (so you need to figure out the reply path separately) 
2. Does not maintain a single plugin object instance for the bot, which meant that you were forced to hit the external storage even for rather ephemeral values
3. You cannot attach more than one match decorator to a method, forcing you to write more complex regex or duplicating the method
4. All matchers will always reply in will, so you cannot have a generic matcher to catch phrases that failed more specific ones

This together with the fact that we wanted to provide some new features I decided that it was a better choice to force the plugin owners to adapt their plugins to the new API. The transition should be fairly painless.
### Why did you not base this on asyncio?!?
Because, well. I'm not doing any IO for starters. The scheduler in asyncio has a warning attached to it saying that you should not use it for timespans longer than 1 day, and well. That is a silly limitation to have when you are offering a cron-like scheduler to the users. I would have gotten decent thread pool management through executors, but using asyncio with the constraints and requirements imposed actually required more code than implementing a custom event loop and using proper queues and parallell processing patterns to develop this application.
