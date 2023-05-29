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
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

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
        else:
            print("selection removed for {0}".format(rv.data[index]))


class MD3Card(MDCard):
    '''Implements a material design v3 card.'''
    text = StringProperty()

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class AccountScreen(MDScreen):
    pass

class TreeScreen(MDScreen):
    def load_tree(self, index, trees):
        self.index = index
        self.trees = trees
        print('index: ', index)
        #self.ids.text.text = trees['tree_list'][index]['text']  
    pass

class HomeScreen(MDScreen):
    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
                'Text': [
                    'text',
                    "on_press", lambda x: toast("pressed text"),
                    "on_release", lambda x: print(
                        "stack_buttons")
                ],
                'Image': 'image',
                'Video': [
                    'video', 
                    "on_press", lambda x: self.del_tree_pressed()
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
        style_list = ["elevated", "filled", "outlined"]
        styles = {
            "elevated": "#f6eeee", "filled": "#f4dedc", "outlined": "#f8f5f4"}
        
        card = MD3Card(
                line_color=(0.2, 0.2, 0.2, 0.8),
                style=style_list[index],
                md_bg_color=styles[style_list[index]],
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
                card.text = tree['text']
                card.bind(on_press = lambda widget, trees_index=trees_index, trees=trees: self.edit_tree(trees_index, trees))
                trees_index += 1
                print(card)
                self.ids.box.add_widget(card)
            

    def add_tree_pressed(self):
        toast('tree pressed')
        trees = unpickle_trees()
        if 'tree_list' in trees:
            tree_list = trees['tree_list']
        else:
            tree_list = []
        new_tree = {'text': 'new tree'}
        tree_list.append(new_tree)
        trees['tree_list'] = tree_list
        print(trees)
        pickle_tree(trees)
        self.list_trees()

    def del_tree_pressed(self):
        trees = unpickle_trees()
        if 'tree_list' in trees:
            trees['tree_list'] = []
        pickle_tree(trees)
        self.ids.box.clear_widgets()
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
    
    def on_enter(self):
        Factory.register(self, cls=self)

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
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        return sm
    
    def account_pressed(self):
        self.root.current = 'account'
    
    def choose_color(self):
        self.root.current = 'picker'


Treeso().run()
