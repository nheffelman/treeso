from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.toast import toast
import os
from kivymd.uix.screenmanager import ScreenManager
import pickle
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.color_definitions import colors
from kivymd.uix.tab import MDTabsBase
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.label import MDLabel
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget

#pickles the current settings
def pickle_settings(settings):
    with open('pickles/settings.pickle', 'wb') as handle:
        pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)


#unpickles the current settings
def unpickle_settings():
    if os.path.exists('pickles/settings.pickle'):
        with open('pickles/settings.pickle', 'rb') as handle:
            settings = pickle.load(handle)

    else:
        settings = {}  
    return settings

# pickles tree
def pickle_tree(trees):
    with open('pickles/trees.pickle', 'wb') as handle:
        pickle.dump(trees, handle, protocol=pickle.HIGHEST_PROTOCOL)


# unpickles treed
def unpickle_trees():
    if os.path.exists('pickles/trees.pickle'):
        with open('pickles/trees.pickle', 'rb') as handle:
            trees = pickle.load(handle)
        print('here')
    else:
        trees = {}
        print('not here')
    return trees

class Tab(MDBoxLayout, MDTabsBase):
    pass


class ItemColor(RecycleDataViewBehavior, MDBoxLayout):
    text = StringProperty()
    color = ListProperty()
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(ItemColor, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(ItemColor, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            print(rv.data[index], 'index', rv.data[index]['title'], 'title')
            Picker.change_primary_palette(palette=rv.data[index]['tab_color'],hue=rv.data[index]['title'])
        else:
            print("selection removed for {0}".format(rv.data[index]))
        


class MD3Card(MDCard):
    '''Implements a material design v3 card.'''
    text = StringProperty()

class NameLabel(ButtonBehavior, MDLabel):
    pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class AccountScreen(MDScreen):
    pass

class TreeScreen(MDScreen):
    text = StringProperty()

    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
                'text': [
                    'text',
                    "on_release", lambda x: self.add_text()
                ],
                'Link': ['link', 
                          "on_press",lambda x: self.add_link_url()],
                'Video': [
                    'video', 
                    "on_press", lambda x: print('video pressed')
                ],
                'Tree': [
                    'assets/treeso.jpg',
                    "on_press", lambda x: self.add_tree_pressed()
                ]
            },
            root_button_anim=True,
        ))

    def load_tree(self, index, trees):
        self.index = index
        self.trees = trees
        print('index: ', index)
        trees = unpickle_trees()
        tree=trees['tree_list'][index]
        print(tree)
        for leaf in tree['text']:
            card = self.manager.get_screen('home').get_card(0)
            card.text = leaf
            card.bind(on_press = lambda widget: self.edit_text(text=leaf))
            #namelabel = NameLabel(text=leaf, valign='top', halign='center', 
                                  #on_press=lambda x: self.edit_text(text=leaf))
            self.ids.leaves.add_widget(card)
            

    def edit_text(self, text="", add_text=False):
        print('edit text')
        self.ids.topbar.left_action_items = [['close', lambda x: self.cancel_edit()]]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        textinput = MDTextField(id='textinput',multiline=True, halign='center', text=text)
        self.ids.box.add_widget(textinput)
        widget = Widget()
        self.ids.box.add_widget(widget)
        self.ids.topbar.right_action_items = [['check', lambda x, textinput=textinput : self.save_text(textinput, add_text)]]

    def cancel_edit(self):
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=self.text, valign='top', halign='center', 
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.box.remove_widget(self.ids.leaves.children[0])
        self.ids.box.remove_widget(self.ids.leaves.children[0])
        self.ids.box.add_widget(namelabel)
        widget = Widget()
        self.ids.box.add_widget(widget)
    def home(self):
        self.ids.leaves.clear_widgets()
        self.manager.current = 'home'

    def save_text(self, textinput, add_text):
        trees = unpickle_trees()
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
            if add_text:
                tree_list[self.index]['text'].append(textinput.text)
            else:
                tree_list[self.index]['text'][0] = textinput.text
            trees['tree_list'] = tree_list
            pickle_tree(trees)
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=textinput.text, valign='top', halign='center', 
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.add_widget(namelabel)
        widget = Widget()
        self.ids.box.add_widget(widget)

    #function adds more text to the tree
    def add_text(self):
        self.edit_text(add_text=True)

    def add_link_url(self):
        print('edit text')
        self.ids.topbar.left_action_items = [['close', lambda x: self.cancel_edit()]]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        textinput = MDTextField(id='textinput', halign='center', text=self.text)
        self.ids.box.add_widget(textinput)
        widget = Widget()
        self.ids.box.add_widget(widget)
        self.ids.topbar.right_action_items = [['check', lambda x, textinput=textinput : self.save_link(textinput)]]

    def save_link(self, textinput):
        trees = unpickle_trees()
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
            if 'links' in tree_list[self.index]:
                tree = tree_list[self.index]
                tree['links'].append(textinput.text)
                tree_list[self.index] = tree
            else:
                tree = tree_list[self.index]
                tree['links'] = [textinput.text]
                tree_list[self.index] = tree
            trees['tree_list'] = tree_list
            pickle_tree(trees)
            self.reload()

    def reload(self):
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=self.text, valign='top', halign='center', 
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.add_widget(namelabel)
        widget = Widget()
        self.ids.box.add_widget(widget)

    def del_tree(self):
        print('del tree')
        trees = unpickle_trees()
        tree_list = trees['tree_list']
        tree_list.remove(tree_list[self.index])
        trees['tree_list'] = tree_list
        pickle_tree(trees)
        self.manager.current = 'home'

    def add_tree_pressed(self):
        toast('tree pressed')
        """trees = unpickle_trees()
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
        else:
            tree_list = []
        new_tree = {'PostFound': {'text': 'new tree'}}
        tree_list.append(new_tree)
        trees['tree_list'] = tree_list
        print(trees)
        pickle_tree(trees)
        self.list_trees()"""
    
    
        
class HomeScreen(MDScreen):
    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
                'text': [
                    'text',
                    "on_press", lambda x: toast("pressed text"),
                    "on_release", lambda x: print(
                        "stack_buttons")
                ],
                'Image': 'image',
                'Video': [
                    'video', 
                    "on_press", lambda x: print('video pressed')
                ],
                'Tree': [
                    'assets/treeso.jpg',
                    "on_press", lambda x: self.add_tree_pressed()
                ]
            },
            root_button_anim=True,
        ))

        self.list_trees()

    def get_card(self, index):
        settings=unpickle_settings()
        if 'primary_palette' in settings:
            palette = settings['primary_palette']
        else:
            palette = "Orange"
        if 'primary_hue' in settings:
            hue = settings['primary_hue']
        else:
            hue = "500"
        style_list = ["elevated", "filled", "outlined"]
        styles = {
            "elevated": "#f6eeee", "filled": "#f4dedc", "outlined": "#f8f5f4"}
        
        card = MD3Card(
                line_color=(0.2, 0.2, 0.2, 0.8),
                style=style_list[index],
                md_bg_color=colors[palette][hue],
                shadow_offset=(0, -1),
            )
        return card
            
    def list_trees(self):
        #unpickle settings and get user settings
        settings = unpickle_settings()
        """user={}
        user['username'] = 'nathan'
        settings['users'] = [user]
        pickle_settings(settings)"""
        if 'users' in settings:
            user = settings['users'][0]
            username = user['username']
        print(settings)

        self.ids.box.clear_widgets()
        trees = unpickle_trees()
        
        index = 0
        print(trees)
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
            trees_index = 0
            for tree in tree_list:
                card = self.get_card(index)
                index += 1
                if index > 2:
                    index = 0   
                card.text = tree['text'][0]
                card.bind(on_press = lambda widget, trees_index=trees_index, trees=trees: self.edit_tree(trees_index, trees))
                trees_index += 1
                print(card)
                self.ids.box.add_widget(card)
       

    def add_tree_pressed(self):
        toast('tree pressed')
        trees = unpickle_trees()
        print(trees)
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
        else:
            tree_list = []
        new_tree = {}
        textlist = []
        textlist.append('new tree')
        new_tree['text'] = textlist
        new_tree['index '] = len(tree_list)
        tree_list.append(new_tree)
        trees['tree_list'] = tree_list
        print(trees)
        pickle_tree(trees)
        self.list_trees()

    def edit_tree(self, index, trees):
        print(index, 'tree index')
        print(trees)
        self.manager.current = 'tree'
        self.manager.get_screen('tree').load_tree(index, trees)

class Picker(MDScreen):
    title = "Colors definitions"
    
    def build(self):        
        return self.screen
    
    def home(self):
        self.manager.current = 'home'
        
    def change_primary_palette(palette, hue):
        print(palette, hue)
        app = MDApp.get_running_app()
        app.theme_cls.primary_palette = palette
        app.theme_cls.primary_hue = hue
        #app.theme_cls.primary_dark_hue = hue
        settings = unpickle_settings()
        settings['primary_palette'] = palette
        settings['primary_hue'] = hue
        print('hue', hue)
        pickle_settings(settings)

    def on_switch_active(self, switch, value):
        settings = unpickle_settings()
        if value:
            print('The checkbox', switch, 'is active')
            app = MDApp.get_running_app()
            app.theme_cls.theme_style = "Dark"
            self.theme_style = "Dark"
            settings['theme_style'] = "Dark"
        else:
            app = MDApp.get_running_app()
            app.theme_cls.theme_style = "Light"
            self.theme_style = "Light"
            settings['theme_style'] = "Light"
            print('The checkbox', switch, 'is inactive')
            
            
        pickle_settings(settings)
    def on_enter(self):
        Factory.register(self, cls=self)

        #get user color settings 
        settings = unpickle_settings()

        if 'primary_palette' in settings:
            self.primary_palette = settings['primary_palette']
        else:
            primary_palette = "Orange"
        if 'theme_style' in settings:
            self.theme_style = settings['theme_style']
            
        else:
            self.theme_style = "Dark"
        if 'primary_hue' in settings:
            self.primary_hue = settings['primary_hue']
        else:
            self.primary_hue = "500"
        

        for name_tab in colors.keys():
            tab = Tab(title=name_tab)
            self.ids.android_tabs.add_widget(tab)

        

        self.on_tab_switch(
            None,
            None,
            None,
            self.ids.android_tabs.ids.layout.children[-1].text,
        )
        return self
    
    
    
    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tabs_label, tab_text
    ):
        self.ids.rv.data = []
        if not tab_text:
            tab_text = 'Red'
        for value_color in colors[tab_text]:
            self.ids.rv.data.append(
                {
                    "viewclass": "ItemColor",
                    "tab_color": tab_text,
                    "md_bg_color": colors[tab_text][value_color],
                    "title": value_color,
                    #"on_touch_down": self.on_touch_down()
                }
            )
        
    
class Treeso(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TreeScreen(name='tree'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(Picker(name='picker'))

        settings = unpickle_settings()
        #settings['primary_palette'] = "Orange"

        #get user color settings
        if 'primary_palette' in settings:
            self.theme_cls.primary_palette = settings['primary_palette']            
        else: 
            self.theme_cls.primary_palette = "Orange"            
        if 'primary_hue' in settings:
            print('adding hue', settings['primary_hue'])
            self.theme_cls.primary_light_hue = settings['primary_hue']
            self.theme_cls.primary_dark_hue = settings['primary_hue']
        else:
            self.theme_cls.primary_hue = "500"
        
        if 'theme_style' in settings:
            self.theme_cls.theme_style = settings['theme_style']
        else:
            self.theme_cls.theme_style = "Dark"
        
        
        
        return sm
    
    def home(self):
        self.root.current = 'home'
    
    def account_pressed(self):
        self.root.current = 'account'
    
    def choose_color(self):
        self.root.current = 'picker'


Treeso().run()
