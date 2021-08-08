from app import create_app, db
from app.models import User, Event, Task, Host, Activity
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    function to access context ojects in shell
    """
    return {
        'db': db, 'User': User, 'Event': Event, 'Task': Task, 'Host': Host, 'Activity': Activity}
