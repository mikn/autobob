Feature: Scheduler Thread
    Because scheduling is not very hard we implement
    our own scheduling thread mechanism with a slow
    loop and customizable FPS for some reason

    Scenario Outline: Setting the scheduler resolution
       Given I set the scheduler resolution to <resolution>
        Then I expect that the loops per second is <fps>

        Examples: Resolution to FPS
            | resolution | fps |
            | 0.1        | 10  |
            | 0.5        | 2   |

    Scenario Outline: Scheduler with a queue
        Given I have a scheduler thread
         When I add <number_of_events>
         Then <number_of_events> is executed

    Scenario Outline: Schedule an event
        Given I have a scheduler thread
         When I add an event scheduled at <time>
         Then Event happens at <time>

    Scenario Outline: Sets of events
