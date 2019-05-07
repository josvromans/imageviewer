==================================================
Image Viewer - organize images as fast as possible
==================================================

Note: this is the first TKinter program I ever made. This is a first try, so feel free
to check it out, but don't expect a robust well tested program at this point.
It does work already for me, I use small images (~400kb).

This ImageViewer is made to organize images as fast as possible.
This means: put images in a subdirectory by pressing one key (and immediately navigate to the next one).

I also want to copy the filename in some cases, since I encode parameters in the filename of my images.
'Ctrl-c' will put the current image name (without extension) to the clipboard, so you can paste it elsewhere.
These kind of actions can easily be adjusted in the code. For example, at some point I will write a few lines to parse the parameters from the filename to trigger an action.
So when I browse through my images, I can launch an action based on the current filename parameters on every image that I approve.


========
Controls
========
<left> and <right> keys to navigate trough image list

[1 - 9] keys will move the current image to the corresponding folder.
By default 1 = delete, 2 = good.
(No real deletion will be done. Only move the file to a folder called 'delete')

<backspace> will undo the last action: put the image back in the main folder

<ctrl-c> will copy the current image name without the extension to the clipboard

<escape> to exit the application


============
Installation
============

.. code-block:: bash

    $ git clone https://github.com/josvromans/imageviewer.git
    $ cd imageviewer/
    $ virtualenv --python=/usr/bin/python3 env
    $ . env/bin/activate
    $ pip install -r requirements.txt

By default, the imageviewer expects a folder called `files` in the root directory.
Make it, and place your images there.

.. code-block:: bash

    $ mkdir files

In case python Tkinter is not installed on your system, install it:

.. code-block:: bash

    $ apt-get install python-tk

Make sure you have a files directory with actual images in it with the allowed extension (jpg by default).
Then launch the program:

.. code-block:: bash

    $ python image_viewer.py


=============
Configuration
=============
For this initial try, you can only change settings in the code.

Only extensions from a specified whitelist will be shown.
Change the following line in "image_viewer.py" if you want to see other extensions than jpg:
```python
DEFAULT_ALLOWED_EXTENSIONS = ['jpg', 'jpeg']
```

The subdirectories are specified in
```python
DEFAULT_ACTION_NAMES = ['delete', 'good']
```
They will be bound to the keys [1 - 9] (don't add more then 9 items in this list).
So if you set this to
```python
DEFAULT_ACTION_NAMES = ['1', '2', '3']
```
and launch the program again. It will make sure there are 3 subdirectories with those names.
And pressing 1 will put the current image in subdirectory called '/1'

The directory will be "/files/" in the root of this project. When you want to point to any other
directory you have to change the "directory_path". For example, you could do something like this:
```python
ImageViewer(master=root, directory_path='/home/your_user_name/images/order_this/')
```


====
TODO
====
Since this is a first try, there are many things to improve, for example:

- Make configuration more user friendly
- Make a key-binding setup in the UI.
- Load a source directory from the UI, by just selecting a directory
- Resize images when changing the window
- Make a decent python package: add a license, packaging, setup etc....
- Add tests
- refactor and restructure code.
- etc
