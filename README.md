autobob
=======

A chat bot designed (almost) like a software project!


##Requirements
Python 3.4+ (ohmygod venv)


##Installing!

Even now it is rather simple, make sure you create a venv first

Then run `python setup.py develop`
Now you should have a fully functioning `autobob` command within your venv!
It doesn't do much right now, though. But it will come with time...


## Preemptive FAQ
Q: Why does it not have a fancy personal name?
A: Because, let's face it, everyone gives their chatbot their own names...
Q: Why is it not API-compatible with Will?
A: While Will has a rather good API, it also comes with some shortcomings.
   Some examples include that the reply method was not attached to the message
   object or the fact that it did not maintain a single plugin object instance
   for the bot, which meant that you were forced to hit the external storage
   even for rather ephemeral values.
   This together with the fact that we wanted to provide new features we
   decided that it was a better choice to force the plugin owners to adapt
   their plugins to the new API. The transition should be fairly painless.
Q: Why did you not base this on asyncio?!?
A: Because, well. We're not doing any IO for starters. The scheduler in asyncio
   has a warning attached to it saying that you should not use it for timespans
   longer than 1 day, and well. That is a silly limitation to have when you are
   offering a cron-like scheduler to the users. I would have gotten decent
   thread pool management through executors, but using asyncio with the 
   constraints and requirements imposed actually required more code than
   implementing a custom event loop and using proper queues and parallell
   processing patterns to develop this application.
Q: Parallell processing is terribly difficult! You have probably done it wrong!
A: It's not so hard... calm down now.
