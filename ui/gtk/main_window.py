import gi
import threading
import subprocess

from egg.disk_management import Partition

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, GObject, Gtk, GdkPixbuf, GLib
from ui.gtk.main_window_button import MainWindowButton
from egg.language_management import LanguageManagement
from ui.gtk.pages.page import Page
from ui.gtk.pages.language_live_page import LanguageLivePage
from ui.gtk.pages.language_installation_page import LanguageInstallationPage
from ui.gtk.pages.timezone_page import TimezonePage
from ui.gtk.pages.selection_disk_page import SelectionDiskPage
from ui.gtk.pages.partition_disk_page import PartitionDiskPage
from ui.gtk.pages.user_page import UserPage
from ui.gtk.pages.network_page import NetworkPage
from ui.gtk.pages.summary_page import SummarryPage
from egg.install_queue.install_queue import InstallQueue
import os

def orderring_path(paths):
    modified_path = paths
    
    i = 0
    while i < len(paths):
        j = 0
        while j < len(modified_path):
            # Si ma string 1 est plus grande que la string 2 et que l'index 1 est inferieur 2
            # Ou Si ma string 1 est plus petite que la string 2 et que l'index 1 est superieur à 2
            if modified_path[j].mount_point is not paths[i].mount_point and modified_path[j].mount_point.startswith(os.path.abspath(paths[i].mount_point)) and i < j and len(paths[i].mount_point.split(os.path.sep)) > len(modified_path[j].mount_point.split(os.path.sep)):
                current_check = modified_path[i]
                current_to_change = modified_path[j]
                
                modified_path[j] = current_check
                modified_path[i] = current_to_change
                return orderring_path(modified_path)
            elif modified_path[j].mount_point is not paths[i].mount_point and modified_path[j].mount_point.startswith(os.path.abspath(paths[i].mount_point)) and i > j and len(paths[i].mount_point.split(os.path.sep)) < len(modified_path[j].mount_point.split(os.path.sep)):
                current_check = modified_path[i]
                current_to_change = modified_path[j]
                
                modified_path[j] = current_check
                modified_path[i] = current_to_change
                return orderring_path(modified_path)

            j += 1
        i += 1
    return paths


class Handler:
    @staticmethod
    def on_destroy(widget: GObject.Object) -> None:
        Gtk.main_quit()


class Components:
    def __init__(self, builder: Gtk.Builder) -> None:
        self._all_components = {}
        self._builder = builder

    def load_component_main_window(self, config: dict) -> None:
        for component_name in config['window_list_components']:
            self._all_components[component_name] = self._builder.get_object(component_name)

    def set_component(self, component_name: str, component: GObject.Object) -> None:
        self._all_components[component_name] = component

    def get_component(self, component_name: str) -> None:
        return self._all_components[component_name]


class TitleLabel(Gtk.Label):
    _page_id = None

    def __init__(self, page_id: str, sidebar_title: str) -> None:
        Gtk.Label.__init__(self)
        self.set_label(sidebar_title)
        self._page_id = page_id
        self.set_halign(Gtk.Align.START)
        self.get_style_context().add_class('dim-label')
        self.set_property('margin', 6)
        self.set_property('margin-start', 24)
        self.set_property('margin-end', 24)

    def get_page_id(self) -> str:
        return self._page_id


class MainWindowGtk:

    def __init__(self, locale_general: LanguageManagement, config_general: dict, config_main_window: dict) -> None:
        GObject.threads_init()
        Gdk.threads_init()

        self._locale_general = locale_general
        self._config_general = config_general
        self._config_main_window = config_main_window
        self._settings = Gtk.Settings.get_default()
        self._pages = list()
        self._page_index = 0
        self._builder = Gtk.Builder()
        self._builder.add_from_file(self._config_main_window['window_xml_file'])

        self._builder.connect_signals(
            {
                'onDestroy': Handler.on_destroy,
                'onButtonExit': Handler.on_destroy
            })
        self._component = Components(self._builder)

        self._component.load_component_main_window(self._config_main_window)
        self._component.get_component('main_window').set_default_size(int(self._config_main_window['window_size_x']),
                                                                      int(self._config_main_window['window_size_y']))
        self._component.get_component('main_window').set_title(self._config_general['os_name'])
        self._component.get_component('main_window_bot_left_label').set_label('')
        pix_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self._config_main_window['window_logo_bot_path'],
                                                          76, 76, False)
        self._component.get_component('main_window_bot_left_logo').set_from_pixbuf(pix_buf)
        if self._config_main_window['window_fullscreen']:
            self._component.get_component('main_window').fullscreen()
        ltr = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self._component.get_component('main_window_right_stack').set_transition_type(ltr)
        self._settings.set_property('gtk-application-prefer-dark-theme', True)
        self.register_all_pages()
        self.load_lang()
        self.update_page()
        
        self._component.get_component('main_window_prev_btn').connect('clicked', lambda x: self.prev_page_btn())
        self._component.get_component('main_window_next_btn').connect('clicked', lambda x: self.next_page_btn())
        self._component.get_component('main_window').show_all()
        GLib.idle_add(self.prepare_all_long_tasks_page)

    def set_title(self, message: str) -> None:
        self._component.get_component('main_window_header_right_label').set_halign(Gtk.Align.START)
        self._component.get_component('main_window_header_right_label').set_label(
            u'<span font-size=\'x-large\'>{}</span>'.format(message))

    def register_all_pages(self) -> None:
        all_pages = [
            LanguageLivePage(self._locale_general, self._config_general),
            LanguageInstallationPage(self._locale_general, self._config_general),
            TimezonePage(self._locale_general, self._config_general),
            SelectionDiskPage(self._locale_general, self._config_general),
            PartitionDiskPage(self._locale_general, self._config_general),
            UserPage(self._locale_general, self._config_general),
            NetworkPage(self._locale_general, self._config_general),
            SummarryPage(self._locale_general, self._config_general)
        ]
        # Add pages in the stack
        for current_page in all_pages:
            current_page.load_win(self)
            self._component.get_component('main_window_right_stack').add_named(
                current_page._components.get_component('general_box'), current_page.get_page_id())
            self._component.get_component('main_window_left_list_text_box').pack_start(
                TitleLabel(current_page.get_page_id(), current_page.get_page_sidebar_title()), False, False, 0)
            self._pages.append(current_page)
    
    def current_page(self) -> Page:
        return self._pages[self._page_index]

    def load_lang(self) -> None:
        component = self._component.get_component('main_window_left_list_text_box')
        for label in component.get_children():
            component.remove(label)

        # Load pages labels with the current on the left box
        for current_page in self._pages:
            label_in_box = TitleLabel(current_page.get_page_id(), current_page.get_page_sidebar_title())
            if label_in_box.get_page_id() == self.current_page().get_page_id():
                label_in_box.get_style_context().remove_class('dim-label')
            else:
                label_in_box.get_style_context().add_class('dim-label')
            self._component.get_component('main_window_left_list_text_box').pack_start(label_in_box, False,
                                                                                       False, 0)
            current_page.refresh_ui_language()
        self._component.get_component('main_window_left_list_text_box').show_all()

        self.set_title(self.current_page().get_page_title())
        self._component.get_component('main_window_prev_btn').set_label(
            self._locale_general.translate_msg('main_window', 'bot_right_prev_btn'))
        if self._page_index is not None and self._page_index == len(self._pages):
            self._component.get_component('main_window_next_btn').set_label(self._locale_general.translate_msg('main_window', 'bot_right_install_btn'))
        else:
            self._component.get_component('main_window_next_btn').set_label(self._locale_general.translate_msg('main_window', 'bot_right_next_btn'))
        self._component.get_component('main_window_header_right_quit_btn').set_label(
            self._locale_general.translate_msg('main_window', 'top_right_quit_btn'))

    def next_page_btn(self) -> None:
        idx = self._page_index + 1

        if idx == len(self._pages):
            self.raven_os_install()
        if idx >= len(self._pages):
            return
        self._page_index = idx
        self.update_page()

    def prev_page_btn(self) -> None:
        idx = self._page_index - 1
        if idx < 0:
            return
        self._page_index = idx
        self.update_page()

    def update_page(self) -> None:
        self.set_title(self.current_page().get_page_title())

        if self._page_index == 1:
            self.set_keyboard("language_installation_page")
        else:
            self.set_keyboard("language_live_page")

        self.set_button_action_visibility(MainWindowButton.NEXT, self._page_index != len(self._pages) - 1)
        self.set_button_action_visibility(MainWindowButton.PREV, self._page_index != 0)
        self.set_button_visibility(MainWindowButton.NEXT, self._page_index == len(self._pages) - 1)
        self.set_button_visibility(MainWindowButton.PREV, self._page_index == 0)

        if self._page_index == len(self._pages) - 1:
            self._component.get_component('main_window_next_btn').set_label(self._locale_general.translate_msg('main_window', 'bot_right_install_btn'))
            self.set_button_action_visibility(MainWindowButton.NEXT, True)
            self.set_button_visibility(MainWindowButton.NEXT, False)
        else:            
            self._component.get_component('main_window_next_btn').set_label(self._locale_general.translate_msg('main_window', 'bot_right_next_btn'))

        self.current_page().load_page()
        # Update the current page icon
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.current_page().get_page_icon(), 50, 50, False)
        self._component.get_component('main_window_top_left_logo').set_from_pixbuf(pixbuf)

        # Update the current highlight page label
        for label in self._component.get_component('main_window_left_list_text_box').get_children():
            if label.get_page_id() == self.current_page().get_page_id():
                label.get_style_context().remove_class('dim-label')
            else:
                label.get_style_context().add_class('dim-label')
        self._component.get_component('main_window_right_stack').set_visible_child_name(
            self.current_page().get_page_id())

    def set_button_action_visibility(self, button: MainWindowButton, status: bool) -> None:
        self._component.get_component(button.value).set_sensitive(status)

    def set_button_visibility(self, button: MainWindowButton, hidden: bool) -> None:
        if hidden:
            self._component.get_component(button.value).hide()
        else:
            self._component.get_component(button.value).show_all()

    def init_background_tasks(self) -> None:
        for page in self._pages:
            try:
                page.long_task()
            except Exception as e:
                pass

    def prepare_all_long_tasks_page(self) -> bool:
        self.set_button_action_visibility(MainWindowButton.NEXT, False)
        thread = threading.Thread(target=self.init_background_tasks)
        thread.daemon = True
        thread.start()
        return False

    def set_keyboard(self, key):
        if "keyboard" in self._config_general[key] and self._config_general[key]["keyboard"] != None:
            try:
                subprocess.check_call("setxkbmap {}".format(self._config_general[key]["keyboard"]), shell=True)
            except Exception as e:
                pass

    def raven_os_install(self):
        InstallQueue().execAll()
        
        #Exec formatage
        InstallQueue().execAll()

        self._config_general['partition_disk']['partitions'] = orderring_path(self._config_general['partition_disk']['partitions'])
        # print(paths)
        # unmanaged = self._config_general["selection_disk_page"]["current_disk_service"].to_unmanaged()
        # unmanaged.add_partition(Partition.Filesystem.EXT4, Partition.Type.PARTITION_NORMAL, 300, "MB")
        # InstallQueue().execAll()
        
    def launch(self) -> None:
        Gtk.main()
