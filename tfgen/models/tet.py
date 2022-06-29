import tfgen.const as const


class TET:
    def __init__(self):
        self.table = {}

    def update_event(self, case_id, event_class):
        if case_id not in self.table.keys():
            self.table[case_id] = event_class
            return const.TOKEN_START_OF_TRACE
        elif event_class == const.TOKEN_END_OF_TRACE:
            last_event = self.table[case_id]
            del self.table[case_id]
            return last_event
        elif case_id in self.table.keys():
            last_event = self.table[case_id]
            self.table[case_id] = event_class
            return last_event

