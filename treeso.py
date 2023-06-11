# pylint:disable=E0001

#from kivy and kivymd
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.toast import toast
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty, DictProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.color_definitions import colors
from kivymd.uix.tab import MDTabsBase
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivymd.uix.fitimage import FitImage
from kivy.core.window import Window
from kivy.uix.videoplayer import VideoPlayer
from kivymd.uix.filemanager import MDFileManager

#from python
import random
import pickle
import os

#other libraries
from linkpreview import LinkPreview, Link, LinkGrabber

# pickles the current settings


def pickle_settings(settings):
    with open('pickles/settings.pickle', 'wb') as handle:
        pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)


# unpickles the current settings
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
    if 'publicKey' in settings:
        publicKey = settings['publicKey']
        if 'primary_palette' in settings[publicKey]:
            palette = settings[publicKey]['primary_palette']
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
            Picker.change_primary_palette(
                palette=rv.data[index]['tab_color'], hue=rv.data[index]['title'])
        else:
            print("selection removed for {0}".format(rv.data[index]))


class LinkCard(MDCard):
    text = StringProperty()
    source = StringProperty()
    color = StringProperty()


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
    palette = StringProperty()

    def on_enter(self):
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        if publicKey in settings:
            if 'primary_palette' in settings[publicKey]:
                self.palette = settings[publicKey]['primary_palette']
        
class TreeScreen(MDScreen):
    text = StringProperty()
    index = NumericProperty()
    tree = DictProperty()
    postImage = ListProperty([])
    postVideo = ListProperty([])
    mediaType = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            preview=True,
            select_path=self.select_path
        )

    def file_manager_open(self):
        # output manager to the screen
        self.file_manager.show(os.path.expanduser("~"))

        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''
        if self.mediaType == 'video':
            self.postVideo.append(path)
            video = VideoPlayer(source=path, state='pause',
                                options={'allow_stretch': True})
            video.on_image_overlay_play = 'assets/preview.png'
            self.ids.main.add_widget(video)
        if self.mediaType == 'image':
            self.postImage.append(path)
            img = FitImage(source=path)
            self.ids.main.add_widget(img)
        self.mediaType = ''
        self.exit_manager()
        # toast(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    # function to add a video to the post
    def select_video(self):
        self.mediaType = "video"
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    # function to add an image to the post
    def select_image(self):
        self.mediaType = "image"
        # output manager to the screen
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    def on_enter(self):
        self.add_widget(MDFloatingActionButtonSpeedDial(
            data={
                'text': [
                    'text',
                    "on_release", lambda x: self.add_text(self.tree)
                ],
                'Link': ['link',
                         "on_press", lambda x: self.add_link_url(self.tree, add_link=True)],
                'Image': [
                    'image',
                    "on_press", lambda x: self.add_image(self.tree, add_image=True)],
                'Video': [
                    'video',
                    "on_press", lambda x: self.add_video(self.tree, add_video=True)],
                'Tree': [
                    'assets/treeso.jpg',
                    "on_press", lambda x: self.add_tree_pressed(
                        self.tree, add_tree=True)
                ]
            },
            root_button_anim=True,
        ))

    def load_tree(self, tree):
        settings = unpickle_settings()
        publicKey = settings['publicKey']
        bgcolor = get_color()
        print('color', bgcolor)
        trees = unpickle_trees()
        if 'id' in tree:
            tree = trees[publicKey][tree['id']]
        self.tree = tree
        print(tree)
        leaves = MDBoxLayout(orientation='vertical',
                             id='leaves',
                             adaptive_height=True,
                             padding="17dp",
                             spacing="17dp")
        leafIndex = 0
        s = ScrollView(do_scroll_x=False)
        box = MDBoxLayout(id='box', orientation='vertical',
                          adaptive_height=True, spacing='16dp')
        # m = MDLabel(text=str(tree))
        # self.ids.main.add_widget(m)
        print(tree)

        for leaf in tree['leaves']:

            if leaf.get('kind') == 'text':
                card = self.manager.get_screen('home').get_card(0)
                print('kind text', leaf['text'])
                # card.text = leaf['text'][:100]
                card.bind(on_press=lambda widget, tree=tree, leafIndex=leafIndex, leaf=leaf: self.edit_text(
                    tree=tree, text=leaf['text'], leafIndex=leafIndex, add_text=False))

                card.ids.label._label.refresh()
                m = MDLabel(text='test')
                t = leaf['text'][:83]
                t = " ".join(t.splitlines())
                m.text = t
                m.size_hint_y = 1
                m.size_hint_x = .73
                m.pos = ('12dp', '3dp')
                m._label.refresh()
                m.allow_selection = True
                m.allow_copy = True

                card.ids.rel.add_widget(m)
                leaves.add_widget(card)
            if leaf.get('kind') == 'link':
                linkcard = LinkCard()
                linkcard.text = leaf['link'][8:26]
                linkcard.color = bgcolor

                if 'image_url' in leaf:
                    linkcard.source = str(leaf['image_url'])

                linkcard.bind(on_press=lambda widget, tree=tree, leafIndex=leafIndex, leaf=leaf: self.add_link_url(
                    tree=tree, text=leaf['link'], leafIndex=leafIndex, add_link=False))
                leaves.add_widget(linkcard)
            if leaf.get('kind') == 'image':
                card = ImageCard()
                card.source = leaf['path']
                card.bind(on_press=lambda widget, tree=tree, leafIndex=leafIndex, leaf=leaf: self.add_image(
                    tree=tree, leafIndex=leafIndex, add_image=False))
                leaves.add_widget(card)
            if leaf.get('kind') == 'video':
                card = LinkCard()
                card.source = 'assets/preview.png'
                card.text = os.path.basename(leaf['path'][48:])
                card.bind(on_press=lambda widget, tree=tree, leafIndex=leafIndex, leaf=leaf: self.add_video(
                    tree=tree, leafIndex=leafIndex, add_video=False))
                leaves.add_widget(card)
            if leaf.get('is_branch'):
                # m = MDLabel(text=str(leaf))
                # self.ids.main.add_widget(m)
                print(leaf)
                branch = trees[publicKey][leaf['id']]
                card = self.manager.get_screen('home').get_card(0)
                # print('kind text', leaf['text'] )
                card.text = branch['leaves'][0]['text'][:18]
                card.bind(on_press=lambda widget,
                          branch=branch: self.treecardPressed(branch))
                leaves.add_widget(card)
            leafIndex += 1

        box.add_widget(leaves)
        widget = Widget()
        box.add_widget(widget)
        s.add_widget(box)
        self.ids.main.add_widget(s)

    def edit_text(self, tree, text="", leafIndex=0, add_text=False):
        print('edit text')
        self.ids.topbar.left_action_items = [
            ['close', lambda x: self.cancel_edit(tree)]]
        self.ids.main.clear_widgets()
        textinput = MDTextField(id='textinput', multiline=True, text=text, pos_hint={
                                "center_y": 0.9, "center_x": .5},)

        self.ids.main.add_widget(textinput)
        widget = Widget()
        self.ids.main.add_widget(widget)
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex)],
                                              ['check', lambda x, textinput=textinput, tree=tree: self.save_text(tree, textinput, leafIndex, add_text)]]

    def del_leaf(self, tree, leafIndex):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else:
            print('no public key')
            return
        treeDict = trees[publicKey]
        if 'is_branch' in tree['leaves'][leafIndex]:
            if tree['leaves'][leafIndex]['is_branch']:
                treeDict.remove(treeDict['leaves']['leafIndex']['id'])
        tree['leaves'].remove(tree['leaves'][leafIndex])
        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)
        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        self.ids.main.clear_widgets()
        self.load_tree(tree)

    def cancel_edit(self, tree):
        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=self.text, valign='top', halign='center',
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.main.clear_widgets()
        self.load_tree(tree)

    def home(self):
        self.ids.main.clear_widgets()
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
            tree['leaves'][leafIndex] = {
                'kind': 'text', 'text': textinput.text}

        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]

        self.ids.main.clear_widgets()
        self.load_tree(tree)

    # function adds more text to the tree
    def add_text(self, tree):
        self.edit_text(tree, add_text=True)

    def add_link_url(self, tree, text="", leafIndex=0, add_link=False):
        print('edit link')
        self.ids.topbar.left_action_items = [
            ['close', lambda x: self.cancel_edit(tree)]]

        self.ids.main.clear_widgets()
        textinput = MDTextField(id='textinput', multiline=True, text=text, pos_hint={
                                "center_y": 0.9, "center_x": .5},)

        self.ids.main.add_widget(textinput)
        widget = Widget()
        self.ids.main.add_widget(widget)
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex)],
                                              ['check', lambda x, textinput=textinput, tree=tree: self.save_link(tree, textinput, leafIndex, add_link)]]

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

        # get link preview
        url = textinput.text
        grabber = LinkGrabber(
            initial_timeout=20,
            maxsize=1048576,
            receive_timeout=10,
            chunk_size=1024,
        )
        try: 
            content, url = grabber.get_content(url)
            link = Link(url, content)
        except:
            link = None

        # if link is good try to get preview
        preview = None
        if link:            
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
        else:
            leaf['title'] = textinput.text
            toast('no preview available')

        if add_link:
            tree['leaves'].append(leaf)
        else:
            tree['leaves'][leafIndex] = leaf

        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]

        self.ids.main.clear_widgets()
        self.load_tree(tree)

    # when user presses add image on fab, opens up a file chooser
    def add_image(self, tree, leafIndex=0, add_image=False):
        print('edit image')
        self.ids.topbar.left_action_items = [
            ['close', lambda x: self.cancel_edit(tree)]]

        self.ids.main.clear_widgets()
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex)],
                                              ['check', lambda x, tree=tree: self.save_image(tree, leafIndex, add_image)]]
        self.mediaType = "image"
        self.file_manager.preview = True
        # output manager to the screen
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    # saves user choice of image from file chooser to dict tree and pickles
    def save_image(self, tree, leafIndex, add_link):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else:
            print('no public key')
            return
        treeDict = trees[publicKey]
        leaf = {}
        print('self.postImage', self.postImage)
        if self.postImage == []:
            self.del_leaf(tree, leafIndex)
            return
        leaf['path'] = self.postImage[0]
        leaf['kind'] = 'image'
        print("leaf", leaf)
        if add_link:
            tree['leaves'].append(leaf)
        else:
            tree['leaves'][leafIndex] = leaf

        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]

        self.ids.main.clear_widgets()
        self.load_tree(tree)

    # when user presses add video on fab, opens up a file chooser
    def add_video(self, tree, leafIndex=0, add_video=False):
        print('edit image')
        self.ids.topbar.left_action_items = [
            ['close', lambda x: self.cancel_edit(tree)]]

        self.ids.main.clear_widgets()
        self.ids.topbar.right_action_items = [['delete', lambda x, tree=tree, leafIndex=leafIndex: self.del_leaf(tree, leafIndex)],
                                              ['check', lambda x, tree=tree: self.save_video(tree, leafIndex, add_video)]]
        self.mediaType = "video"
        self.file_manager.preview = False
        # output manager to the screen
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    # saves user choice of video from file chooser to dict tree and pickles
    def save_video(self, tree, leafIndex, add_link):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else:
            print('no public key')
            return
        treeDict = trees[publicKey]
        leaf = {}
        print('self.postVideo', self.postVideo)
        if self.postVideo == []:
            self.del_leaf(tree, leafIndex)
            return
        leaf['path'] = self.postVideo[0]
        leaf['kind'] = 'video'
        print("leaf", leaf)
        if add_link:
            tree['leaves'].append(leaf)
        else:
            tree['leaves'][leafIndex] = leaf

        treeDict[tree['id']] = dict(tree)
        trees[publicKey] = treeDict
        pickle_tree(trees)

        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]

        self.ids.main.clear_widgets()
        self.load_tree(tree)

    def reload(self):
        self.ids.topbar.left_action_items = [
            ['arrow-left', lambda x: self.home()]]
        self.ids.topbar.right_action_items = [['delete', lambda x: self.del_tree()],
                                              ['dots-vertical']]
        namelabel = NameLabel(text=self.text, valign='top', halign='center',
                              on_press=lambda x: self.edit_text(self.text))
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.remove_widget(self.ids.box.children[0])
        self.ids.box.add_widget(namelabel)
        widget = Widget()
        self.ids.box.add_widget(widget)

    def del_tree(self, tree):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        else:
            print('no public key')
            return
        treeDict = trees[publicKey]
        branch = treeDict[tree['id']]
        parent = None
        if 'parent' in branch:
            parent = treeDict[branch['parent']]
        
        #iterate through all branches in branch to add for removal
        branches_to_remove = []        
        branches_to_remove.append(branch['id'])
        more_branches = []
        more_branches.append(branch)
        while more_branches:
            temp_leaf = more_branches.pop()
            print(temp_leaf, 'temp branch')
            branch_from_leaf = treeDict[temp_leaf['id']]
            for leaf in branch_from_leaf['leaves']:
                if 'is_branch' in leaf:
                    if leaf['is_branch'] == True:
                        more_branches.append(leaf)
                        branches_to_remove.append(leaf['id'])
        print('branches to remove', branches_to_remove)
        #remove branches from treeDict
        for branch_id in branches_to_remove:
            treeDict.pop(branch_id)     


        
        # remove branch from parent
        new_leaves = []
        if parent:
            for leaf in parent['leaves']:
                if 'id' in leaf:
                    if leaf['id'] != branch['id']:
                        new_leaves.append(leaf)
                else:
                    new_leaves.append(leaf)
                    parent['leaves'] = new_leaves
                treeDict[parent['id']] = parent
        trees[publicKey] = treeDict
        pickle_tree(trees)
        self.ids.main.clear_widgets()
        self.manager.current = 'home'

    def add_tree_pressed(self, tree, leafIndex=0, add_tree=True):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        branch = {}
        id = random.randint(0, 1000000)
        if publicKey in trees:
            treesDict = trees[publicKey]
        else:
            treesDict = {}
            print('no trees')
        # add branch to parent
        branch['id'] = id
        branch['is_branch'] = True
        branch['parent'] = tree['id']
        if add_tree:
            tree['leaves'].append(branch)
        else:
            tree['leaves'][leafIndex] = branch
        
        treesDict[tree['id']] = dict(tree)
        print('this will be new treesDict without adding new branch to dict', treesDict)
        trees[publicKey] = treesDict
        pickle_tree(trees)
        # add new branch to trees dict
        trees = unpickle_trees()
        treesDict = trees[publicKey]
        leaves = []
        leaf = {'kind': 'text', 'text': 'new tree'}
        leaves.append(leaf)
        branch['leaves'] = leaves
        treesDict[id] = branch
        print('this is new treeesDict after adding new branch to dict', treesDict)
        #add  treedict to user public key
        trees[publicKey] = treesDict
        #store in tree pickle
        pickle_tree(trees)
        self.ids.main.clear_widgets()
        self.load_tree(tree)

    def treecardPressed(self, branch):
        self.ids.main.clear_widgets()
        self.load_tree(branch)


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
        # trees={}
        # pickle_tree(trees)
        self.list_trees()

    
    def get_card(self, index):
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        if publicKey in settings:
            if 'primary_palette' in settings[publicKey]:
                palette = settings[publicKey]['primary_palette']
            else:
                palette = "Orange"
            if 'primary_hue' in settings[publicKey]:
                hue = settings[publicKey]['primary_hue']
            else:
                hue = "500"
        else:
            palette = "Orange"
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
        # unpickle settings and get user settings
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        print(settings)

        self.ids.box.clear_widgets()
        trees = unpickle_trees()

    
        if publicKey in trees:
            treeDict = trees[publicKey]
            print('treedict:', treeDict)
            index = 0
            lab = MDLabel(text=str(treeDict))
            # self.ids.box.add_widget(lab)
            for id, tree in treeDict.items():
                print('each tree', tree)
                if 'is_branch' in tree:
                    if tree['is_branch'] == True:
                        continue
                card = self.get_card(index)
                index += 1
                if index > 2:
                    index = 0
                if tree['leaves'] != []:
                    card.text = tree['leaves'][0]['text']
                    card.bind(on_press=lambda widget,
                              tree=tree: self.edit_tree(tree))
                    print(card)
                    self.ids.box.add_widget(card)

    def add_tree_pressed(self):
        trees = unpickle_trees()
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
        if publicKey in trees:
            print(trees)

        if publicKey in trees:
            treesDict = trees[publicKey]
        else:
            treesDict = {}
            print('no trees')
        id = random.randint(0, 1000000)
        new_tree = {}
        leaves = []
        leaf = {'kind': 'text', 'text': 'new tree'}
        leaves.append(leaf)
        new_tree['leaves'] = leaves
        new_tree['id'] = id

        treesDict[id] = new_tree

        trees[publicKey] = treesDict
        pickle_tree(trees)
        toast('new tree pickled')
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
        # app.theme_cls.primary_dark_hue = hue
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
            if publicKey in settings:
                settings[publicKey]['primary_palette'] = palette
                settings[publicKey]['primary_hue'] = hue
                print('hue', hue)
                pickle_settings(settings)
            else:
                settings[publicKey] = {}
                settings[publicKey]['primary_palette'] = palette
                settings[publicKey]['primary_hue'] = hue
                pickle_settings(settings)

    def on_switch_active(self, switch, value):
        settings = unpickle_settings()
        if value:
            print('The checkbox', switch, 'is active')
            app = MDApp.get_running_app()
            app.theme_cls.theme_style = "Dark"
            self.theme_style = "Dark"
            if 'publicKey' in settings:
                publicKey = settings['publicKey']
                if publicKey in settings:
                    settings[publicKey]['theme_style'] = "Dark"
                else:
                    settings[publicKey] = {}
                    settings[publicKey]['theme_style'] = "Dark"
                pickle_settings(settings)
                            
        else:
            app = MDApp.get_running_app()
            app.theme_cls.theme_style = "Light"
            self.theme_style = "Light"
            if 'publicKey' in settings:
                publicKey = settings['publicKey']
                if publicKey in settings:
                    settings[publicKey]['theme_style'] = "Light"
                else:
                    settings[publicKey] = {}
                    settings[publicKey]['theme_style'] = "Light"
                pickle_settings(settings)
            
            print('The checkbox', switch, 'is inactive')

        
    def on_enter(self):
        Factory.register(self, cls=self)

        # get user color settings
        settings = unpickle_settings()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
            if publicKey not in settings:
                settings[publicKey] = {}

            if 'primary_palette' in settings[publicKey]:
                self.primary_palette = settings[publicKey]['primary_palette']
            else:
                self.primary_palette = "Orange"
            if 'primary_hue' in settings[publicKey]:
                self.primary_hue = settings[publicKey]['primary_hue']
            else:
                self.primary_hue = "500"
            if 'theme_style' in settings[publicKey]:
                self.theme_style = settings[publicKey]['theme_style']
            else:
                self.theme_style = "Dark"

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
                    # "on_touch_down": self.on_touch_down()
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
        
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
            if publicKey not in settings:
                settings[publicKey] = {}
            # get user color settings
            if 'primary_palette' in settings[publicKey]:
                self.theme_cls.primary_palette = settings[publicKey]['primary_palette']
            else:
                self.theme_cls.primary_palette = "Orange"
            if 'primary_hue' in settings[publicKey]:
                print('adding hue', settings[publicKey]['primary_hue'])
                self.theme_cls.primary_light_hue = settings[publicKey]['primary_hue']
                self.theme_cls.primary_dark_hue = settings[publicKey]['primary_hue']
            else:
                self.theme_cls.primary_hue = "500"

            if 'theme_style' in settings[publicKey]:
                self.theme_cls.theme_style = settings[publicKey]['theme_style']
            else:
                self.theme_cls.theme_style = "Dark"

        return sm

    def home(self):
        self.root.current = 'home'

    def account_pressed(self):
        self.root.current = 'account'

    def choose_color(self):
        self.root.current = 'picker'

    def clear_trees(self):
        settings = unpickle_settings()
        trees = unpickle_trees()
        if 'publicKey' in settings:
            publicKey = settings['publicKey']
            trees[publicKey] = {}
            pickle_tree(trees)
            
    
Treeso().run()
