Feature: Scheduler Thread
    Because scheduling is not very hard we implement
    our own scheduling thread mechanism with a slow
    loop and customizable FPS for some reason

    Scenario: Setting the scheduler resolution
        Given I set the scheduler resolution to <resolution>
         Then I expect that the loops per second is <fps>
