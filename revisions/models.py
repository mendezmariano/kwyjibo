

class ScriptResult(object):
    """
    
    Container for revision running results. This class is going to be visited
    and the results published depending on who the visitor is.
    
    """

    def __init__(self):
        self.revision = None
        self.exit_value = 0
        self.captured_stdout = ""
    
    def accept(self, visitor):
        visitor.visit(self)

    def __str__(self):
        return "ScriptResult: <{revision}> // finished[{exit_value}]".format(revision = self.revision, exit_value = self.exit_value)