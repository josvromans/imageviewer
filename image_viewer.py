import os
import shutil
import sys

from PIL import Image, ImageTk
from tkinter import Canvas, Tk, Label, LEFT, Frame, filedialog, messagebox

from settings import DEFAULT_ACTION_NAMES, DEFAULT_ALLOWED_EXTENSIONS, DEFAULT_BACKGROUND_COLOR, SOURCE_DIRECTORY


TOP_BUTTON_HEIGHT = 50  # for the buttons
MARGIN_BOTTOM = 70  # when there is no margin at the bottom, I can't be sure if the image really stops there
MARGIN_LEFT_RIGHT = 10


def get_image_list(image_dir, allowed_extensions):
    return sorted([
        os.path.join(image_dir, item) for item in os.listdir(image_dir) if item.split('.')[-1].lower() in allowed_extensions
    ])


def move_image(image_path, destination_dir):
    try:
        return shutil.move(image_path, destination_dir)
    except Exception as e:
        print('move image failed')
        print(e)
        return False


def make_directory(base_path, directory_name):
    new_dir_path = os.path.join(base_path, directory_name)

    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)

    return new_dir_path


def copy_to_clipboard(copy_text):
    r = Tk()
    r.withdraw()
    # r.clipboard_clear()
    r.clipboard_append(copy_text)
    r.update()  # now it stays on the clipboard after the window is closed
    # r.destroy()


class ImageViewer(Canvas):

    def __init__(self, allowed_extensions=None, action_names=None, *args, **kwargs):
        """

        :param directory_path:
        :param allowed_extensions:
        :param action_names:
        """
        super().__init__(*args, **kwargs)

        if SOURCE_DIRECTORY is None:
            # let the user choose a directory, default will be '/files'
            default_directory_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
            directory_path = filedialog.askdirectory(initialdir=default_directory_path)
        else:
            directory_path = SOURCE_DIRECTORY

        if allowed_extensions is None:
            allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS

        if action_names is None:
            action_names = DEFAULT_ACTION_NAMES

        self.directory_path = directory_path
        self.allowed_extensions = allowed_extensions
        self.action_names = action_names
        self.action_counts = [0] * len(self.action_names)
        self.action_destination_dirs = []  # will be set in self.initialize_actions

        self.image_list = get_image_list(image_dir=self.directory_path, allowed_extensions=allowed_extensions)

        assert len(self.image_list) > 0, 'The folder {} contains no images of the format(s) "{}"'.format(
            self.directory_path, ', '.join(allowed_extensions))

        # only sets the initial screensize on startup
        self['width'] = self.winfo_screenwidth()
        self['height'] = self.winfo_screenheight()
        self['bg'] = DEFAULT_BACKGROUND_COLOR

        self.top_frame = Frame(self.master, height=TOP_BUTTON_HEIGHT)
        self.top_frame.pack()

        self.initialize_actions()

        self.master.bind('<Escape>', self._quit)
        self.master.bind('<Left>', self.previous_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<BackSpace>', self.undo_last_action)
        self.master.bind('<Control-c>', self.copy_image_name_to_clipboard)
        # self.master.bind("<Configure>", self.on_resize)  # TODO: find a way to make resize window work nicely

        self.total_images = len(self.image_list)
        self.current_image_index = 0

        self.last_actions = []

        self.image_counter_label = Label(self.top_frame, font=('Helvetica', 16), fg="grey")
        self.image_counter_label.pack(side=LEFT)
        self.show_image()

    def _quit(self, event=None):
        """
        Before quiting, determine if there is a 'delete' folder.
        Only if exactly one has been determined, ask the user if it should be deleted.

        Since tkinter.Canvas has a quit() method, call that first, before sys.exit()
        """
        delete_dirs = [d for d in self.action_destination_dirs if d.lower().endswith('delete')]
        if len(delete_dirs) == 1:
            if messagebox.askyesno("Question", "Delete the 'delete' directory?"):
                try:
                    shutil.rmtree(delete_dirs[0])
                except Exception as e:
                    messagebox.showwarning("Warning", "Something went wrong: {}".format(e))
        self.quit()
        sys.exit()

    def initialize_actions(self):
        """
        For every actions, there should be a corresponding directory.
        The label has to be made, and the event should be bind to a numeric key

        :return:
        """
        for index, action_label in enumerate(self.action_names):
            action_dir_path = make_directory(base_path=self.directory_path, directory_name=action_label)
            self.action_destination_dirs.append(action_dir_path)

            setattr(self, action_label, Label(self.top_frame, text='  {}  '.format(action_label.upper()), font=('Helvetica', 20), fg="black"))
            tk_label = getattr(self, action_label)
            getattr(tk_label, 'pack')(side=LEFT)

            self.master.bind(str(index + 1), self._move_image_action)

    def show_image(self):
        image_path = self.image_list[self.current_image_index]
        pil_image = Image.open(image_path)

        original_width = pil_image.width
        original_height = pil_image.height
        max_height_image = self.winfo_screenheight() - TOP_BUTTON_HEIGHT - MARGIN_BOTTOM
        max_width_image = self.winfo_screenwidth() - 2 * MARGIN_LEFT_RIGHT

        scale_factor_height, scale_factor_width = 1, 1
        if original_height > max_height_image:
            scale_factor_height = max_height_image / original_height

        if original_width > max_width_image:
            scale_factor_width = max_width_image / original_width

        scale_factor = min(scale_factor_width, scale_factor_height)
        if scale_factor != 1:
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            pil_image = pil_image.resize((new_width, new_height))
        else:
            new_width = original_width
            new_height = original_height

        # self.delete(self.find_withtag("bacl"))  # TODO, figure out if need this?

        new_x = int((max_width_image - new_width) / 2)
        new_y = int((TOP_BUTTON_HEIGHT + max_height_image - new_height) / 2)

        img = ImageTk.PhotoImage(pil_image)
        self.allready = self.create_image(new_x, new_y, image=img, anchor='nw', tag="bacl")
        self.image = img

        self.master.title("Image Viewer ({})".format(os.path.split(image_path)[-1]))
        self.update_image_counter_label()
        self.update_labels()

    def copy_image_name_to_clipboard(self, event):
        """
        Take the current image path, and only look at the image name without the extension.
        Put this value in the clipboard, so it can be pasted elsewhere.
        """
        # copy image data to clipboard
        image_path = self.image_list[self.current_image_index]
        image_name = os.path.split(image_path)[-1]
        # file names can hold a point... so split on point to get the extension, but join the first part if needed
        image_data = '.'.join(image_name.split('.')[:-1])
        copy_to_clipboard(image_data)

    def _move_image_action(self, event):
        action_index = int(event.char) - 1
        action = self.action_names[action_index]

        destination_dir = self.action_destination_dirs[action_index]
        new_path = move_image(image_path=self.image_list[self.current_image_index], destination_dir=destination_dir)

        if new_path:
            self.last_actions.append(
                {'action_index': action_index,
                 'action_name': action,
                 'path': new_path}
            )

            self.image_list.pop(self.current_image_index)
            self.total_images -= 1

            if self.total_images == 0:
                # nothing to show, let's quit
                self._quit()

            self.current_image_index = self.current_image_index % self.total_images
            self.action_counts[action_index] += 1
            self.show_image()

    def previous_image(self, event=None):
        self.current_image_index = (self.current_image_index - 1) % self.total_images
        self.show_image()

    def next_image(self, event=None):
        self.current_image_index = (self.current_image_index + 1) % self.total_images
        self.show_image()

    def undo_last_action(self, event):
        if not self.last_actions:
            return

        last_action = self.last_actions.pop()
        from_path = last_action['path']
        action_index = last_action['action_index']
        to_path = self.directory_path
        # print('Put file back from {} to the {}'.format(from_path, to_path))

        new_path = move_image(image_path=from_path, destination_dir=to_path)

        if new_path:
            self.image_list.insert(self.current_image_index, new_path)
            self.total_images += 1
            # dont change self.current_image
            self.action_counts[action_index] -= 1
            self.show_image()
            self.update_labels(undo=True)  # explicitly do it again, so the label will get the undo color

    def update_image_counter_label(self):
        self.image_counter_label['text'] = ' {} / {} '.format(self.current_image_index + 1, self.total_images)

    @property
    def last_action_name(self):
        latest_action_dict = self.last_actions[-1] if self.last_actions else {}
        return latest_action_dict.get('action_name')

    def update_labels(self, undo=False):
        action_color = 'yellow' if undo else 'red'

        for action_index, action_label in enumerate(self.action_names):
            label_color = action_color if action_label == self.last_action_name else 'black'

            tk_label = getattr(self, action_label)
            tk_label['fg'] = label_color
            tk_label['text'] = '  {} ({})  '.format(action_label.upper(), self.action_counts[action_index])


def main():
    root = Tk(className="Image Viewer")
    ImageViewer(master=root).pack(expand="yes", fill="both")

    # root.resizable(width=0, height=0)  # Not Resizable
    # root.resizable()
    root.mainloop()


# Main Function Trigger
if __name__ == '__main__':
    main()


# TODO: use relx rely for relative coordinates, so on window resize, the button position will change
