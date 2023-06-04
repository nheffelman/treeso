#pylint:disable=E0001
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
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty, DictProperty
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
from linkpreview import LinkPreview, Link, LinkGrabber
from kivymd.uix.fitimage import FitImage
import random


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

# pickles trees
def pickle_tree(trees):
    with open('pickles/trees.pickle', 'wb') as handle:
        pickle.dump(trees, handle, protocol=pickle.HIGHEST_PROTOCOL)


# unpickles trees
def unpickle_trees():
    if os.path.exists('pickles/trees.pickle'):
        with open('pickles/trees.pickle', 'rb') as handle:
            trees = pickle.load(handle)
        print('here')
    else:
        trees = {}
        print('not here')
    return trees

def get_color():
    settings = unpickle_settings()
    if 'primary_palette' in settings:
        palette = settings['primary_palette']
    else:
        palette = "Orange"
    return palette

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
        
class ImageCard(MDCard):
    text = StringProperty()
    source = StringProperty()
    color = StringProperty()

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
    index = NumericProperty()
    tree = DictProperty()
    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
                'text': [
                    'text',
                    "on_release", lambda x: self.add_text(self.tree)
                ],
                'Link': ['link', 
                          "on_press",lambda x: self.add_link_url(self.tree, add_link=True)],
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

    def load_tree(self, tree):
        bgcolor = get_color()
        print('color', bgcolor)
        self.tree = tree
        leaves =  MDBoxLayout(orientation='vertical',
            id='leaves',
            adaptive_height=True,
            spacing="56dp")
        leafIndex=0

        for leaf in tree['leaves']:
            
                       
            if leaf.get('kind') == 'text':
                card = self.manager.get_screen('home').get_card(0)
                print('kind text', leaf['text'] )
                card.text = leaf['text'][:18]
                card.bind(on_press = lambda widget , tree=tree, leafIndex=leafIndex, leaf=leaf: self.edit_text(tree=tree, text=leaf['text'], leafIndex=leafIndex, add_text=False))
                leaves.add_widget(card)
            if leaf.get('kind') == 'link':
                linkcard = ImageCard()
                linkcard.text = leaf['link'][8:26]
                linkcard.color = bgcolor
                
                if 'image_url' in leaf:
                    linkcard.source = str(leaf['image_url']) 
                    
                linkcard.bind(on_press = lambda widget , tree=tree, leafIndex=leafIndex, leaf=leaf: self.add_link_url(tree=tree, text=leaf['link'], leafIndex=leafIndex, add_link=False))
                leaves.add_widget(linkcard)
            leafIndex += 1
        self.ids.box.add_widget(leaves)
        widget = Widget()
        self.ids.box.add_widget(widget)

    def edit_text(self, tree, text="", leafIndex=0, add_text=False):
        print('edit text')
        self.ids.topbar.left_action_items = [['close', lambda x: self.cancel_edit(tree)]]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        textinput = MDTextField(id='textinput',multiline=True, halign='center', text=text)
        self.ids.box.add_widget(textinput)
        widget = Widget()
        self.ids.box.add_widget(widget)
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex) ],
                                              ['check', lambda x, textinput=textinput, tree=tree : self.save_text(tree, textinput, leafIndex, add_text)]]
        
    def del_leaf(self, tree, leafIndex):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else: 
            print('no public key')
            return
        treeDict = trees[publicKey]
        tree['leaves'].remove(tree['leaves'][leafIndex])
        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.load_tree(tree)

    def cancel_edit(self, tree):
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=self.text, valign='top', halign='center', 
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.load_tree(tree)
    def home(self):
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.manager.current = 'home'

    def save_text(self, tree, textinput, leafIndex, add_text):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else: 
            print('no public key')
            return
        treeDict = trees[publicKey]
        if add_text:

            tree['leaves'].append({'kind': 'text', 'text': textinput.text})
            
        else:
            tree['leaves'][leafIndex] = {'kind': 'text', 'text': textinput.text}  
             
        
        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.load_tree(tree)

    #function adds more text to the tree
    def add_text(self, tree):
        self.edit_text(tree, add_text=True)

    def add_link_url(self, tree, text="", leafIndex=0, add_link=False):
        print('edit link')
        self.ids.topbar.left_action_items = [['close', lambda x: self.cancel_edit(tree)]]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        textinput = MDTextField(id='textinput',multiline=True, halign='center', text=text)
        self.ids.box.add_widget(textinput)
        widget = Widget()
        self.ids.box.add_widget(widget)
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex) ],
                                            ['check', lambda x, textinput=textinput, tree=tree : self.save_link(tree, textinput, leafIndex, add_link)]]

    def save_link(self, tree, textinput, leafIndex, add_link):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else: 
            print('no public key')
            return
        treeDict = trees[publicKey]
        leaf = {}
        leaf['link'] = textinput.text
        leaf['kind'] = 'link'
        
        #get link preview
        url = textinput.text
        grabber = LinkGrabber(
            initial_timeout=20,
            maxsize=1048576,
            receive_timeout=10,
            chunk_size=1024,
        )
        content, url = grabber.get_content(url)
        link = Link(url, content)
        
        try:
            preview = LinkPreview(link)
        except:
            preview = None
        if preview:
            
            if preview.image:
                leaf['image_url'] = preview.image
            if preview.title:
                leaf['title'] = preview.title            
            if preview.description:
                leaf['description'] = preview.description[128:]
            
        if add_link:
            tree['leaves'].append(leaf)
        else:
            tree['leaves'][leafIndex] = leaf
             
        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

            
        self.ids.topbar.left_action_items = [['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.load_tree(tree)

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
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else: 
            print('no public key')
            return
        treeDict = trees[publicKey]
        treeDict.pop(self.tree['id'])
        trees[publicKey] = treeDict
        pickle_tree(trees)
        self.manager.current = 'home'
        

    def add_tree_pressed(self):
        toast('tree pressed')
        
        
class HomeScreen(MDScreen):
    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
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
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        print(settings)

        self.ids.box.clear_widgets()
        trees = unpickle_trees()
 
        print(trees)
        if publicKey in trees:
            treeDict = trees[publicKey]
            print('treedict:', treeDict)
            index = 0 
            lab = MDLabel(text=str(treeDict))
            #self.ids.box.add_widget(lab)
            for id, tree in treeDict.items():
                print('each tree', tree)
                card = self.get_card(index)
                index += 1
                if index > 2:
                    index = 0   
                if tree['leaves'] != []:
                    card.text = tree['leaves'][0]['text']
                    card.bind(on_press = lambda widget, tree=tree: self.edit_tree(tree))
                    print(card)
                    self.ids.box.add_widget(card)
       

    def add_tree_pressed(self):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        if publicKey in trees:
            print(trees)
        new_tree = {}
        id = random.randint(0, 1000000)
        if publicKey in trees:
            treesDict = trees[publicKey]
        else:
            treesDict = {}
            print('no trees')
        leaves = []
        leaf = {'kind': 'text', 'text': 'new tree'}
        leaves.append(leaf)
        new_tree['leaves'] = leaves
        new_tree['id'] = id
        
        treesDict[id] = new_tree
        
        trees[publicKey] = treesDict
        pickle_tree(trees)
        
        self.list_trees()

    def edit_tree(self, tree):
        print(tree)
        self.manager.current = 'tree'
        self.manager.get_screen('tree').load_tree(tree)

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
