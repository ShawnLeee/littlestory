import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models import LSUser, LSPost

app = create_app(os.getenv('FLASK_CONFIG') or 'development')
manager = Manager(app)
migirate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, LSUser=LSUser, LSPost=LSPost)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # app.run()
    # app.run(threaded=True)
    manager.run()
