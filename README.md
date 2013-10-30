heartrate-monitor
=================

Ever had tasks that run on a schedule? Every minute, every 5 minute. Ever had problems when the task for some reason didn't run when it was supposed to?

Do you have a check for that?

The heartrate-monitor does that. It keeps track of when your tasks should run, and if they havn't it will send an email.

Pulse
-------

The idea is that each scheduled task has a heart, and thus a pulse. At the end of each execution of the task it send a pulse to the heart-rate monitor.

Based on these pulses, the heart rate monitor can keep track to see if they are running as expected.

App Engine
---------------

By placing the heart rate monitor on App Engine infrastructure it is isolated from our production environment, which should allow us to better monitor failures in our own infrastructure.

How to set it up
--------------------

Right now the repository does not hold any application name, nor any pubnub keys. In order to set up a heart rate monitor on Google AppEngine, you need to add your application name to the app.yaml file in the root, as well as pubnub credentials in models/__init__.py

How to contribute
----------------------
1. Fork the project
2. Make one or more well commented and clean commits to the repository. You can make a new branch here if you are modifying more than one part or feature.
3. Perform a pull request in github's web interface.

The MIT License
----------------------

Copyright (c) 2013 RemoteX Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
