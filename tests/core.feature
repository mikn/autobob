Feature: Messaging

        Background: I have a fully running instance

        # Not sure if necessary?
        Scenario: Receiving Message
                When a message is received
                Then event MESSAGE_RECEIVED is triggered

        Scenario: Replying to a message
                Given a Matcher with pattern '^hi', reply 'hello' and channel 'personal'
                When a message containing 'hi' is received on channel 'personal'
                Then a reply containing 'hello' is posted
        # Make this a table with hits and misses

        Scenario: Substitution matching
