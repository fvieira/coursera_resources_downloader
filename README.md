Features
--------

  * Download resources such as videos or pdfs from Coursera in batch using the `dl-res` sub-command.
  * No need to grab cookies manually, just provide your username and password to the script and it will authenticate automatically.
  * Files downloaded are named after their respective lecture in the lectures page and organized in folders named after their respective course.
  * Allows filtering which types of resources (video, pdf, pptx, txt, subs) are to be downloaded.
  * Supports downloading multiple editions of the same course.
  * The `list-courses` sub-command shows available courses and the identifiers required for downloading the resources.
  * Resources can be downloaded from multiple resources courses at once by providing multiple identifiers.
  * Works both in Linux and Windows.


Installation
------------

Coursera is just a script so you can run it without installing, all that is required is that you have the required dependencies installed.
If you're not sure you can install them with: `sudo pip install -r requirements.txt`

A setup.py is also provided, although all it does is copying coursera to your PATH so you can run it anywhere.

Usage
-----

To start using the script run it as `./coursera -h` to see the help message.

If you are in a hurry, you can just skip it and run `./coursera dl-res crypto,algo 'your.email@example.com' 'your_password'` to start downloading videos from your courses (which are crypto and algo in the example).


