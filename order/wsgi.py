#!/usr/bin/env python
# encoding: utf-8
from order import webapp

app = webapp.app
webapp.setup()
app.logger.info("App started. Version: %(GIT_VERSION)s", app.config)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
