from autobot import event
from .helpers import DictObj


class Substitutions(DictObj):
    '''
    The substitutions available for application on the matching strings are
    static and only the ones available during the bootstrapping procedure.
    This is roughly after the ALL_MODULES_LOADED event has fired.
    The reason for this is that the regexp patterns are compiled at boot time
    to be more efficient. The static nature of the matching strings is a
    result of this.
    '''
    def __set__(self, key, value):
        if key in self:
            raise KeyError('A substitution already exist for %s', key)
        self[key] = value
        event_args = {'key': key, 'value': value}
        event.trigger(event.SUBSTITUTIONS_ALTERED, self, event_args)

    def add(self, key, value):
        self.__set__(key, value)
