# for each action in DEFAULT_ACTION_NAMES, a subdirectory will be made, and an action will be attached
# to the keys [1-9]. By default, pressing '1' will put an image in a directory called 'delete', and pressing
# '2' will put an image in a directory called 'good'. Of course you can name these anything you want,
# but currently, the code (and the interface) will not handle more then 9 options.
DEFAULT_ACTION_NAMES = ['delete', 'good']

# only images with an extension in DEFAULT_ALLOWED_EXTENSIONS will be shown
DEFAULT_ALLOWED_EXTENSIONS = ['jpg', 'jpeg']
DEFAULT_BACKGROUND_COLOR = 'black'

# if the SOURCE_DIRECTORY is None, the user has to select a directory in a filedialog (default will be /files)
# if the SOURCE_DIRECTORY is set to an existing directory path, the file dialog will be skipped, and the
# defined SOURCE_DIRECTORY will be used immediately
SOURCE_DIRECTORY = None
